"""Tests for `diff_directories` + directory diff renderers."""

import json
from pathlib import Path

import pytest

from frok.evals import (
    CaseDiff,
    DirectoryDiff,
    diff_directories,
    directory_diff_to_json,
    directory_diff_to_markdown,
)
from frok.telemetry import SPAN_END, Event, JsonlSink


def _chat(span_id, *, tokens=10, error=None, ts=1000.0):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=5.0,
        data={"total_tokens": tokens},
        error=error,
    )


def _invoke(span_id, tool, *, ts=1001.0, error=None):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=None,
        kind=SPAN_END,
        name="tool.invoke",
        duration_ms=1.0,
        data={"tool": tool},
        error=error,
    )


def _write(path: Path, events) -> Path:
    with JsonlSink(path) as sink:
        for e in events:
            sink.emit(e)
    return path


def _dir(tmp_path, name):
    d = tmp_path / name
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# diff_directories
# ---------------------------------------------------------------------------
def test_identical_directories_not_regressed(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    for d in (a, b):
        _write(d / "alpha.jsonl", [_chat("c", tokens=10)])
        _write(d / "beta.jsonl", [_invoke("i", "add", ts=2.0)])

    dd = diff_directories(a, b)
    assert isinstance(dd, DirectoryDiff)
    assert [m.name for m in dd.matched] == ["alpha", "beta"]
    assert dd.only_in_a == []
    assert dd.only_in_b == []
    assert dd.regressed_cases == 0
    assert dd.regressed is False
    assert all(m.regressed is False for m in dd.matched)


def test_added_and_removed_slugs_tracked(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    _write(a / "shared.jsonl", [_chat("c")])
    _write(a / "legacy.jsonl", [_chat("c")])
    _write(b / "shared.jsonl", [_chat("c")])
    _write(b / "new-case.jsonl", [_chat("c")])

    dd = diff_directories(a, b)
    assert [m.name for m in dd.matched] == ["shared"]
    assert dd.only_in_a == ["legacy"]
    assert dd.only_in_b == ["new-case"]
    # Slug divergence alone regresses the directory diff — operators using
    # --diff-against probably want to know cases appeared/disappeared.
    assert dd.regressed is True


def test_matched_case_regresses_when_tool_order_diverges(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    _write(a / "tool.jsonl", [_invoke("1", "add", ts=1.0), _invoke("2", "search", ts=2.0)])
    _write(b / "tool.jsonl", [_invoke("1", "search", ts=1.0), _invoke("2", "add", ts=2.0)])

    dd = diff_directories(a, b)
    [m] = dd.matched
    assert m.regressed is True
    assert dd.regressed_cases == 1
    assert dd.regressed is True


def test_token_only_delta_does_not_regress(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    _write(a / "chat.jsonl", [_chat("c", tokens=10)])
    _write(b / "chat.jsonl", [_chat("c", tokens=99)])

    dd = diff_directories(a, b)
    [m] = dd.matched
    assert m.regressed is False
    assert m.diff["token_delta"] == 89
    assert dd.regressed is False


def test_new_error_in_b_regresses_matched_case(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    _write(a / "err.jsonl", [_chat("c", tokens=10)])
    _write(b / "err.jsonl", [_chat("c", tokens=10, error="nope")])

    dd = diff_directories(a, b)
    [m] = dd.matched
    assert m.regressed is True
    assert m.diff["new_errors"] == 1


def test_empty_capture_files_are_skipped(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    (a / "empty.jsonl").write_text("", encoding="utf-8")
    _write(a / "real.jsonl", [_chat("c")])
    _write(b / "real.jsonl", [_chat("c")])

    dd = diff_directories(a, b)
    assert [m.name for m in dd.matched] == ["real"]
    assert dd.only_in_a == []  # empty file is ignored entirely


def test_missing_directories_raise(tmp_path):
    with pytest.raises(NotADirectoryError):
        diff_directories(tmp_path / "missing-a", tmp_path / "missing-b")


# ---------------------------------------------------------------------------
# renderers
# ---------------------------------------------------------------------------
def test_markdown_has_expected_sections(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    # Matched-clean + matched-regressed + only-in-a.
    _write(a / "clean.jsonl", [_chat("c", tokens=5)])
    _write(b / "clean.jsonl", [_chat("c", tokens=5)])
    _write(
        a / "regressed.jsonl",
        [_invoke("1", "add", ts=1.0), _invoke("2", "search", ts=2.0)],
    )
    _write(
        b / "regressed.jsonl",
        [_invoke("1", "search", ts=1.0), _invoke("2", "add", ts=2.0)],
    )
    _write(a / "legacy.jsonl", [_chat("c")])

    md = directory_diff_to_markdown(diff_directories(a, b))
    assert "# Frok Eval Directory Diff" in md
    assert "## Per-case diffs" in md
    assert "## Only in a" in md
    assert "`legacy`" in md
    assert "## Regression details" in md
    assert "**diverged**" in md


def test_markdown_hides_empty_sections(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    _write(a / "only.jsonl", [_chat("c")])
    _write(b / "only.jsonl", [_chat("c")])
    md = directory_diff_to_markdown(diff_directories(a, b))
    assert "## Only in a" not in md
    assert "## Only in b" not in md
    assert "## Regression details" not in md


def test_json_output_round_trips(tmp_path):
    a = _dir(tmp_path, "a")
    b = _dir(tmp_path, "b")
    _write(a / "shared.jsonl", [_chat("c", tokens=5)])
    _write(b / "shared.jsonl", [_chat("c", tokens=20)])
    _write(b / "added.jsonl", [_chat("c")])

    data = json.loads(json.dumps(directory_diff_to_json(diff_directories(a, b))))
    assert data["only_in_a"] == []
    assert data["only_in_b"] == ["added"]
    assert [m["name"] for m in data["matched"]] == ["shared"]
    assert data["regressed"] is True  # slug divergence
    assert data["matched"][0]["diff"]["token_delta"] == 15
