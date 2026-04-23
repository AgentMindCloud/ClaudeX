"""Structured telemetry events + pluggable sinks.

An `Event` is the one canonical shape everything in Frok emits. A sink
is any object with `.emit(event)`. Four built-ins:

* `NullSink`   — default. Zero cost; tracers fast-path around it.
* `InMemorySink` — collects events in a list. Used by tests + the
  forthcoming §2 #8 eval harness to diff runs.
* `JsonlSink`  — append-only newline-delimited JSON. Good for replay.
* `MultiSink`  — fan-out to several sinks at once.

Events are deliberately small and flat so they survive round-tripping
through JSON and can be loaded into pandas / sqlite with no ceremony.
"""

from __future__ import annotations

import io
import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Protocol, runtime_checkable

SPAN_START = "span.start"
SPAN_END = "span.end"
EVENT = "event"


@dataclass
class Event:
    ts: float  # epoch seconds, float
    trace_id: str
    span_id: str
    parent_span_id: str | None
    kind: str  # SPAN_START | SPAN_END | EVENT
    name: str
    duration_ms: float | None = None
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, sort_keys=True)


@runtime_checkable
class TelemetrySink(Protocol):
    def emit(self, event: Event) -> None: ...


class NullSink:
    """Discards everything. Tracers detect this and skip work entirely."""

    def emit(self, event: Event) -> None:  # noqa: D401
        return None


@dataclass
class InMemorySink:
    events: list[Event] = field(default_factory=list)

    def emit(self, event: Event) -> None:
        self.events.append(event)

    # ---- query helpers used by tests + the eval harness ------------------
    def find(
        self,
        *,
        name: str | None = None,
        kind: str | None = None,
    ) -> list[Event]:
        return [
            e
            for e in self.events
            if (name is None or e.name == name) and (kind is None or e.kind == kind)
        ]

    def spans(self, *, name: str | None = None) -> list[Event]:
        return [e for e in self.find(kind=SPAN_END) if name is None or e.name == name]

    def errors(self) -> list[Event]:
        return [e for e in self.events if e.error is not None]

    def clear(self) -> None:
        self.events.clear()


class JsonlSink:
    """Append-only JSONL sink. Thread-safe. `close()` or use as a cm."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: io.TextIOBase = self.path.open("a", encoding="utf-8")
        self._lock = threading.Lock()

    def emit(self, event: Event) -> None:
        line = event.to_json()
        with self._lock:
            self._fh.write(line)
            self._fh.write("\n")
            self._fh.flush()

    def close(self) -> None:
        with self._lock:
            if not self._fh.closed:
                self._fh.close()

    def __enter__(self) -> "JsonlSink":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


@dataclass
class MultiSink:
    sinks: tuple[TelemetrySink, ...]

    def __init__(self, *sinks: TelemetrySink):
        self.sinks = tuple(sinks)

    def emit(self, event: Event) -> None:
        for s in self.sinks:
            s.emit(event)


def read_jsonl(path: str | Path) -> Iterable[Event]:
    """Replay helper — yields `Event`s from a JsonlSink file."""
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            yield Event(**d)
