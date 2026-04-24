"""Tests for `summarize_directory` + dir_summary renderers."""

import json
from pathlib import Path

import pytest

from frok.telemetry import (
    SPAN_END,
    CaseSummary,
    DirectorySummary,
    Event,
    JsonlSink,
    dir_summary_to_json,
    dir_summary_to_markdown,
    summarize_directory,
)


def _chat(span_id, *, tokens=10, error=None, ts=1000.0, duration=5.0):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=duration,
        data={"total_tokens": tokens},
        error=error,
    )


def _invoke(span_id, tool, *, parent=None, error=None, ts=1001.0, duration=1.0):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=parent,
        kind=SPAN_END,
        name="tool.invoke",
        duration_ms=duration,
        data={"tool": tool},
        error=error,
    )


def _root(span_id, *, duration, ts=999.0):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=None,
        kind=SPAN_END,
        name="tool.run",
        duration_ms=duration,
        data={},
    )


def _write(path: Path, events) -> Path:
    with JsonlSink(path) as sink:
        for e in events:
            sink.emit(e)
    return path


# ---------------------------------------------------------------------------
# summarize_directory
# ---------------------------------------------------------------------------
def test_summarize_directory_walks_all_jsonl_files(tmp_path):
    _write(tmp_path / "case-a.jsonl", [_chat("c1", tokens=10)])
    _write(tmp_path / "case-b.jsonl", [_chat("c1", tokens=20)])
    (tmp_path / "not-a-capture.txt").write_text("ignore me", encoding="utf-8")

    summary = summarize_directory(tmp_path)
    assert isinstance(summary, DirectorySummary)
    assert [c.name for c in summary.cases] == ["case-a", "case-b"]
    assert summary.total_tokens == 30
    assert summary.total_spans == 2
    assert summary.total_errors == 0


def test_summarize_directory_requires_a_directory(tmp_path):
    with pytest.raises(NotADirectoryError):
        summarize_directory(tmp_path / "missing")


def test_summarize_directory_skips_empty_jsonl(tmp_path):
    (tmp_path / "empty.jsonl").write_text("", encoding="utf-8")
    _write(tmp_path / "real.jsonl", [_chat("c1", tokens=5)])
    summary = summarize_directory(tmp_path)
    assert [c.name for c in summary.cases] == ["real"]


# ---------------------------------------------------------------------------
# CaseSummary fields
# ---------------------------------------------------------------------------
def test_case_summary_counts_tokens_and_errors(tmp_path):
    _write(
        tmp_path / "c.jsonl",
        [
            _chat("c1", tokens=7),
            _chat("c2", tokens=3, error="boom"),
            _invoke("t1", "add"),
            _invoke("t2", "add", error="oops"),
            _invoke("t3", "search"),
        ],
    )
    [case] = summarize_directory(tmp_path).cases
    assert case.total_tokens == 10
    assert case.error_count == 2  # one chat error + one tool error
    assert case.tool_counts == {"add": 2, "search": 1}
    assert case.errored_tool_counts == {"add": 1}
    assert case.spans == 5


def test_case_duration_sums_root_spans(tmp_path):
    # Two root spans + nested children — duration = 100 + 20, nested 5 excluded.
    _write(
        tmp_path / "c.jsonl",
        [
            _root("r1", duration=100.0, ts=1000.0),
            _invoke("child", "add", parent="r1", duration=5.0, ts=1000.1),
            _root("r2", duration=20.0, ts=1100.0),
        ],
    )
    [case] = summarize_directory(tmp_path).cases
    assert case.duration_ms == pytest.approx(120.0)


# ---------------------------------------------------------------------------
# DirectorySummary aggregates + leader methods
# ---------------------------------------------------------------------------
def test_directory_aggregates_tools_across_cases(tmp_path):
    _write(tmp_path / "a.jsonl", [_invoke("1", "add"), _invoke("2", "search")])
    _write(tmp_path / "b.jsonl", [_invoke("1", "add"), _invoke("2", "add", error="x")])
    summary = summarize_directory(tmp_path)
    assert summary.tool_counts == {"add": 3, "search": 1}
    assert summary.errored_tool_counts == {"add": 1}


def test_slowest_orders_by_duration_desc(tmp_path):
    _write(tmp_path / "fast.jsonl", [_root("r", duration=10.0)])
    _write(tmp_path / "medium.jsonl", [_root("r", duration=50.0)])
    _write(tmp_path / "slow.jsonl", [_root("r", duration=200.0)])
    summary = summarize_directory(tmp_path)
    assert [c.name for c in summary.slowest(2)] == ["slow", "medium"]


def test_heaviest_tokens_orders_desc(tmp_path):
    _write(tmp_path / "small.jsonl", [_chat("c", tokens=5)])
    _write(tmp_path / "big.jsonl", [_chat("c", tokens=200)])
    _write(tmp_path / "medium.jsonl", [_chat("c", tokens=50)])
    summary = summarize_directory(tmp_path)
    assert [c.name for c in summary.heaviest_tokens()] == ["big", "medium", "small"]


def test_most_errors_filters_zero_errors(tmp_path):
    _write(tmp_path / "clean.jsonl", [_chat("c")])
    _write(tmp_path / "one-err.jsonl", [_chat("c", error="x")])
    _write(tmp_path / "two-err.jsonl", [_chat("a", error="x"), _chat("b", error="y")])
    summary = summarize_directory(tmp_path)
    ranked = summary.most_errors()
    assert [c.name for c in ranked] == ["two-err", "one-err"]


# ---------------------------------------------------------------------------
# renderers
# ---------------------------------------------------------------------------
def test_markdown_has_expected_sections(tmp_path):
    _write(tmp_path / "case.jsonl", [_chat("c", tokens=5), _invoke("t", "add")])
    md = dir_summary_to_markdown(summarize_directory(tmp_path))
    assert "# Frok Eval Directory Summary" in md
    assert "## Per-case rollup" in md
    assert "## Cross-case leaders" in md
    assert "### Slowest cases" in md
    assert "### Heaviest token use" in md
    assert "### Top tools" in md
    assert "case" in md  # case name in the table


def test_markdown_hides_empty_leader_sections(tmp_path):
    _write(tmp_path / "clean.jsonl", [_chat("c", tokens=5)])
    md = dir_summary_to_markdown(summarize_directory(tmp_path))
    # No errored tools or most-errored cases when everything is clean.
    assert "Tools with errors" not in md
    assert "Most-errored cases" not in md


def test_markdown_empty_directory_still_has_header():
    md = dir_summary_to_markdown(DirectorySummary(directory="/tmp/empty", cases=[]))
    assert "# Frok Eval Directory Summary" in md
    assert "## Cross-case leaders" not in md  # hidden when there are no cases


def test_json_output_is_round_trippable(tmp_path):
    _write(
        tmp_path / "c.jsonl",
        [_chat("c", tokens=5), _invoke("t", "add", error="x")],
    )
    data = dir_summary_to_json(summarize_directory(tmp_path), top=3)
    # Must round-trip through json stdlib.
    data = json.loads(json.dumps(data, default=str))
    assert data["total_tokens"] == 5
    assert data["total_errors"] == 1
    assert data["cases"][0]["name"] == "c"
    assert data["tool_counts"] == {"add": 1}
    assert data["errored_tool_counts"] == {"add": 1}
