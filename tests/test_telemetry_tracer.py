import asyncio
import itertools

import pytest

from frok.telemetry import (
    EVENT,
    SPAN_END,
    SPAN_START,
    InMemorySink,
    NullSink,
    Tracer,
    current_span_id,
    current_trace_id,
)


def _tracer(sink):
    counter = itertools.count()
    return Tracer(sink=sink, clock=lambda: 10.0 + next(counter), id_gen=_id_factory())


def _id_factory():
    counter = itertools.count()
    return lambda: f"id{next(counter)}"


async def test_span_emits_start_and_end_with_duration():
    sink = InMemorySink()
    t = _tracer(sink)
    async with t.span("work", k=1) as span:
        span.set(hit=True)

    kinds = [e.kind for e in sink.events]
    assert kinds == [SPAN_START, SPAN_END]
    end = sink.events[1]
    assert end.duration_ms is not None and end.duration_ms > 0
    assert end.data == {"k": 1, "hit": True}
    assert end.error is None


async def test_nested_spans_inherit_trace_and_track_parent():
    sink = InMemorySink()
    t = _tracer(sink)
    async with t.span("outer"):
        outer_trace = current_trace_id()
        outer_span = current_span_id()
        async with t.span("inner"):
            assert current_trace_id() == outer_trace
            assert current_span_id() != outer_span

    ends = [e for e in sink.events if e.kind == SPAN_END]
    assert [e.name for e in ends] == ["inner", "outer"]
    inner = next(e for e in sink.events if e.kind == SPAN_START and e.name == "inner")
    outer = next(e for e in sink.events if e.kind == SPAN_START and e.name == "outer")
    assert inner.trace_id == outer.trace_id
    assert inner.parent_span_id == outer.span_id
    assert outer.parent_span_id is None


async def test_span_captures_exception_and_reraises():
    sink = InMemorySink()
    t = _tracer(sink)
    with pytest.raises(RuntimeError, match="boom"):
        async with t.span("bad"):
            raise RuntimeError("boom")
    end = sink.find(kind=SPAN_END)[0]
    assert end.error == "RuntimeError: boom"
    # Context vars cleared.
    assert current_trace_id() is None
    assert current_span_id() is None


async def test_event_attaches_current_trace_and_span():
    sink = InMemorySink()
    t = _tracer(sink)
    async with t.span("outer"):
        t.event("fact.recorded", source="unit-test")
    ev = sink.find(kind=EVENT)[0]
    assert ev.data == {"source": "unit-test"}
    assert ev.trace_id != ""
    assert ev.span_id != ""


async def test_null_sink_fast_path_emits_nothing():
    sink = NullSink()
    t = Tracer(sink=sink)
    async with t.span("work") as span:
        span.set(x=1)
        t.event("noise")
    # Nothing to assert on the sink (null), but no crashes + context stays clean.
    assert current_trace_id() is None
    assert current_span_id() is None


async def test_explicit_trace_id_honoured():
    sink = InMemorySink()
    t = _tracer(sink)
    async with t.span("seeded", trace_id="abc-123"):
        pass
    assert sink.events[0].trace_id == "abc-123"


def test_with_added_sink_collapses_null_and_extends_multi():
    from frok.telemetry import MultiSink, NullSink, Tracer, with_added_sink

    a = InMemorySink()
    b = InMemorySink()
    c = InMemorySink()

    # NullSink base → result uses only the extra.
    t1 = with_added_sink(Tracer(sink=NullSink()), a)
    assert t1.sink is a

    # Plain sink base → 2-element MultiSink.
    t2 = with_added_sink(Tracer(sink=a), b)
    assert isinstance(t2.sink, MultiSink)
    assert t2.sink.sinks == (a, b)

    # MultiSink base → extended in order.
    t3 = with_added_sink(Tracer(sink=MultiSink(a, b)), c)
    assert isinstance(t3.sink, MultiSink)
    assert t3.sink.sinks == (a, b, c)


def test_with_added_sink_preserves_clock_and_id_gen():
    from frok.telemetry import InMemorySink, Tracer, with_added_sink

    clock = lambda: 42.0
    id_gen = lambda: "zzz"
    t = Tracer(sink=InMemorySink(), clock=clock, id_gen=id_gen)
    t2 = with_added_sink(t, InMemorySink())
    assert t2.clock is clock
    assert t2.id_gen is id_gen
