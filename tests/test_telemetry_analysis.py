import json

from frok.telemetry import (
    SPAN_END,
    SPAN_START,
    Event,
    JsonlSink,
    build_tree,
    read_jsonl,
    render_tree,
    summarize,
    summary_to_json,
    summary_to_markdown,
)


def _end(
    name,
    *,
    span_id,
    trace_id="t1",
    parent=None,
    duration=10.0,
    error=None,
    ts=1000.0,
    **data,
):
    return Event(
        ts=ts,
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent,
        kind=SPAN_END,
        name=name,
        duration_ms=duration,
        data=dict(data),
        error=error,
    )


# ---------------------------------------------------------------------------
# build_tree
# ---------------------------------------------------------------------------
def test_build_tree_nests_parents_and_sorts_by_start():
    events = [
        _end("team.run", span_id="r", ts=1000.0, duration=50.0),
        _end("team.hop", span_id="h1", parent="r", ts=1010.0, duration=10.0),
        _end("team.hop", span_id="h2", parent="r", ts=1020.0, duration=10.0),
        _end("grok.chat", span_id="c1", parent="h1", ts=1011.0, duration=5.0),
    ]
    roots = build_tree(events)
    assert [r.span_id for r in roots] == ["r"]
    root = roots[0]
    assert [c.span_id for c in root.children] == ["h1", "h2"]
    assert [c.span_id for c in root.children[0].children] == ["c1"]


def test_build_tree_ignores_span_start_events():
    events = [
        Event(
            ts=0.0,
            trace_id="t",
            span_id="s",
            parent_span_id=None,
            kind=SPAN_START,
            name="x",
        ),
        _end("x", span_id="s", duration=1.0),
    ]
    roots = build_tree(events)
    assert len(roots) == 1


def test_build_tree_handles_orphaned_parent_as_root():
    events = [_end("leaf", span_id="a", parent="missing")]
    roots = build_tree(events)
    assert [r.span_id for r in roots] == ["a"]


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------
def test_summarize_aggregates_name_stats():
    events = [
        _end("grok.chat", span_id="a", duration=10.0, total_tokens=5),
        _end("grok.chat", span_id="b", duration=30.0, total_tokens=7),
        _end("grok.chat", span_id="c", duration=20.0, total_tokens=2, error="boom"),
    ]
    s = summarize(events)
    assert s.event_count == 3
    assert s.span_count == 3
    assert s.trace_count == 1
    stat = s.name_stats["grok.chat"]
    assert stat.count == 3
    assert stat.total_ms == 60.0
    assert stat.mean_ms == 20.0
    assert stat.p50_ms == 20.0
    assert stat.error_count == 1
    assert stat.max_ms == 30.0


def test_summarize_lists_errors_in_start_order():
    events = [
        _end("a", span_id="1", ts=1000.0, duration=10.0, error="one"),
        _end("a", span_id="2", ts=999.5, duration=5.0, error="two"),
        _end("a", span_id="3", ts=998.0, duration=1.0),
    ]
    s = summarize(events)
    assert [n.error for n in s.errors] == ["two", "one"]


def test_summarize_top_tools_sorts_by_count_then_total_ms():
    events = [
        _end("tool.invoke", span_id="a", duration=1.0, tool="search"),
        _end("tool.invoke", span_id="b", duration=5.0, tool="search"),
        _end("tool.invoke", span_id="c", duration=100.0, tool="send"),
        _end("tool.invoke", span_id="d", duration=3.0, tool="add", error="x"),
    ]
    s = summarize(events)
    order = [t.tool for t in s.top_tools]
    assert order == ["search", "send", "add"]  # count desc, tiebreak by total
    search = next(t for t in s.top_tools if t.tool == "search")
    assert search.count == 2
    assert search.total_ms == 6.0
    assert search.mean_ms == 3.0
    add = next(t for t in s.top_tools if t.tool == "add")
    assert add.errors == 1


def test_summarize_handles_empty_events():
    s = summarize([])
    assert s.event_count == 0
    assert s.span_count == 0
    assert s.trace_count == 0
    assert s.name_stats == {}
    assert s.top_tools == []
    assert s.errors == []


def test_summarize_counts_unique_traces():
    events = [
        _end("a", span_id="1", trace_id="alpha"),
        _end("a", span_id="2", trace_id="alpha"),
        _end("a", span_id="3", trace_id="beta"),
    ]
    assert summarize(events).trace_count == 2


# ---------------------------------------------------------------------------
# renderers
# ---------------------------------------------------------------------------
def test_render_tree_indents_children():
    events = [
        _end("root", span_id="r", duration=10.0),
        _end("leaf", span_id="l", parent="r", duration=3.0),
    ]
    text = render_tree(build_tree(events))
    lines = text.splitlines()
    assert lines[0].startswith("- root")
    assert "10.0 ms" in lines[0]
    assert lines[1].startswith("  - leaf")
    assert "3.0 ms" in lines[1]


def test_render_tree_marks_errors():
    events = [_end("bad", span_id="b", duration=2.0, error="kaboom")]
    assert "ERROR: kaboom" in render_tree(build_tree(events))


def test_summary_to_markdown_has_all_sections():
    events = [
        _end("grok.chat", span_id="c1", duration=5.0),
        _end("tool.invoke", span_id="t1", duration=3.0, tool="add", error="oops"),
    ]
    md = summary_to_markdown(summarize(events))
    assert "# Frok Trace Report" in md
    assert "## Span durations by name" in md
    assert "## Top tool invocations" in md
    assert "## Errors" in md
    assert "tool.invoke" in md
    assert "add" in md
    assert "oops" in md


def test_summary_to_markdown_can_include_tree(tmp_path):
    events = [
        _end("team.run", span_id="r", duration=10.0),
        _end("team.hop", span_id="h", parent="r", ts=1001.0, duration=5.0),
    ]
    md = summary_to_markdown(
        summarize(events), include_tree=True, roots=build_tree(events)
    )
    assert "## Trace tree" in md
    assert "- team.run" in md
    assert "- team.hop" in md


def test_summary_to_json_is_jsonifiable():
    events = [
        _end("grok.chat", span_id="c", duration=5.0, total_tokens=2),
        _end("tool.invoke", span_id="t", duration=3.0, tool="add"),
    ]
    data = summary_to_json(summarize(events), top=5)
    # must round-trip through json
    roundtrip = json.loads(json.dumps(data))
    assert roundtrip["span_count"] == 2
    assert any(s["name"] == "grok.chat" for s in roundtrip["name_stats"])
    assert roundtrip["top_tools"][0]["tool"] == "add"


# ---------------------------------------------------------------------------
# end-to-end with JsonlSink capture
# ---------------------------------------------------------------------------
def test_jsonl_capture_reloads_and_summarizes(tmp_path):
    path = tmp_path / "trace.jsonl"
    with JsonlSink(path) as sink:
        sink.emit(_end("grok.chat", span_id="c1", duration=2.5, total_tokens=4))
        sink.emit(
            _end(
                "tool.invoke",
                span_id="t1",
                duration=1.0,
                tool="search",
                error="nope",
            )
        )
    events = list(read_jsonl(path))
    s = summarize(events)
    assert s.span_count == 2
    assert s.name_stats["tool.invoke"].error_count == 1
    assert s.top_tools[0].tool == "search"
