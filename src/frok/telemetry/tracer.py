"""Tracer — contextvar-scoped span/event emitter over a `TelemetrySink`.

Spans nest through `contextvars` so an inner span (e.g. a tool invocation)
automatically inherits its parent's `trace_id` and records its
`parent_span_id`. The Tracer fast-paths around `NullSink` so the default
`Tracer()` instance added to every Frok component is effectively free.
"""

from __future__ import annotations

import contextlib
import secrets
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable

from .sink import EVENT, SPAN_END, SPAN_START, Event, NullSink, TelemetrySink

_current_trace: ContextVar[str | None] = ContextVar("frok_trace_id", default=None)
_current_span: ContextVar[str | None] = ContextVar("frok_span_id", default=None)


def _default_id() -> str:
    return secrets.token_hex(8)


@dataclass
class SpanHandle:
    """Mutable span-attrs accumulator passed to `async with tracer.span(...)`."""

    _data: dict[str, Any] = field(default_factory=dict)
    _error: str | None = None

    def set(self, **kwargs: Any) -> None:
        self._data.update(kwargs)

    def fail(self, reason: str) -> None:
        """Mark the span as errored without re-raising.

        Use when a caller catches an exception but the work the span
        represented still failed (e.g. a tool handler that raised but
        the orchestrator recovered). The reason lands on the span.end
        event's ``error`` field so default scorers like
        ``NoErrors`` can catch it.
        """
        self._error = reason

    @property
    def data(self) -> dict[str, Any]:
        return dict(self._data)

    @property
    def error(self) -> str | None:
        return self._error


@dataclass
class Tracer:
    sink: TelemetrySink = field(default_factory=NullSink)
    clock: Callable[[], float] = time.time
    id_gen: Callable[[], str] = _default_id

    # ------------------------------------------------------------------ span
    @contextlib.asynccontextmanager
    async def span(
        self,
        name: str,
        *,
        trace_id: str | None = None,
        **attrs: Any,
    ) -> AsyncIterator[SpanHandle]:
        if isinstance(self.sink, NullSink):
            # Fast path: nothing consumes events, so skip all allocation.
            yield SpanHandle()
            return

        t_id = trace_id or _current_trace.get() or self.id_gen()
        parent = _current_span.get()
        s_id = self.id_gen()

        trace_tok = _current_trace.set(t_id)
        span_tok = _current_span.set(s_id)

        start_ts = self.clock()
        handle = SpanHandle(_data=dict(attrs))
        self.sink.emit(
            Event(
                ts=start_ts,
                trace_id=t_id,
                span_id=s_id,
                parent_span_id=parent,
                kind=SPAN_START,
                name=name,
                data=dict(attrs),
            )
        )

        error: str | None = None
        try:
            yield handle
        except BaseException as exc:
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            end_ts = self.clock()
            self.sink.emit(
                Event(
                    ts=end_ts,
                    trace_id=t_id,
                    span_id=s_id,
                    parent_span_id=parent,
                    kind=SPAN_END,
                    name=name,
                    duration_ms=(end_ts - start_ts) * 1000.0,
                    data=handle.data,
                    error=error or handle.error,
                )
            )
            _current_span.reset(span_tok)
            _current_trace.reset(trace_tok)

    # ----------------------------------------------------------------- event
    def event(self, name: str, **attrs: Any) -> None:
        if isinstance(self.sink, NullSink):
            return
        t_id = _current_trace.get() or self.id_gen()
        s_id = _current_span.get() or ""
        self.sink.emit(
            Event(
                ts=self.clock(),
                trace_id=t_id,
                span_id=s_id,
                parent_span_id=None,
                kind=EVENT,
                name=name,
                data=dict(attrs),
            )
        )


def null_tracer() -> Tracer:
    """Explicit no-op tracer. Same as `Tracer()` but clearer at call sites."""
    return Tracer(sink=NullSink())


def current_trace_id() -> str | None:
    return _current_trace.get()


def current_span_id() -> str | None:
    return _current_span.get()
