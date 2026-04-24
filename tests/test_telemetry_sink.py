import json

import pytest

from frok.telemetry import (
    EVENT,
    SPAN_END,
    SPAN_START,
    Event,
    InMemorySink,
    JsonlSink,
    MultiSink,
    NullSink,
    TelemetrySink,
    read_jsonl,
)


def _ev(name="n", kind=EVENT, **kw):
    return Event(
        ts=1.0,
        trace_id="t1",
        span_id="s1",
        parent_span_id=None,
        kind=kind,
        name=name,
        **kw,
    )


def test_event_to_json_is_stable_and_reparses():
    e = _ev(name="grok.chat", kind=SPAN_END, duration_ms=12.5, data={"tokens": 42})
    s = e.to_json()
    d = json.loads(s)
    assert d["name"] == "grok.chat"
    assert d["duration_ms"] == 12.5
    assert d["data"] == {"tokens": 42}


def test_null_sink_is_a_sink():
    assert isinstance(NullSink(), TelemetrySink)
    NullSink().emit(_ev())  # no raise


def test_in_memory_sink_collects_and_queries():
    s = InMemorySink()
    s.emit(_ev(name="a", kind=SPAN_START))
    s.emit(_ev(name="a", kind=SPAN_END))
    s.emit(_ev(name="b", kind=EVENT))
    assert len(s.events) == 3
    assert [e.name for e in s.find(kind=SPAN_END)] == ["a"]
    assert [e.name for e in s.spans()] == ["a"]
    assert s.spans(name="a")[0].kind == SPAN_END
    s.clear()
    assert s.events == []


def test_in_memory_sink_errors_filter():
    s = InMemorySink()
    s.emit(_ev(name="ok", kind=SPAN_END))
    s.emit(_ev(name="bad", kind=SPAN_END, error="boom"))
    assert [e.name for e in s.errors()] == ["bad"]


def test_multi_sink_fans_out():
    a = InMemorySink()
    b = InMemorySink()
    m = MultiSink(a, b)
    m.emit(_ev(name="x"))
    assert a.events == b.events != []


def test_jsonl_sink_roundtrip(tmp_path):
    path = tmp_path / "trace.jsonl"
    with JsonlSink(path) as sink:
        sink.emit(_ev(name="one", kind=SPAN_START))
        sink.emit(_ev(name="one", kind=SPAN_END, duration_ms=1.0))

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    replayed = list(read_jsonl(path))
    assert [e.name for e in replayed] == ["one", "one"]
    assert replayed[1].kind == SPAN_END
    assert replayed[1].duration_ms == 1.0


def test_jsonl_sink_close_is_idempotent(tmp_path):
    s = JsonlSink(tmp_path / "x.jsonl")
    s.emit(_ev())
    s.close()
    s.close()  # no raise
