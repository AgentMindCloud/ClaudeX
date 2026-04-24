"""Tests for ``frok eval summarize --diff-against <DIR>``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main
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


def _mkdirs(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    return a, b


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_diff_against_shape():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "eval",
            "summarize",
            "a-dir",
            "--diff-against",
            "b-dir",
            "--json",
            "--fail-on-regression",
        ]
    )
    assert ns.command == "eval"
    assert ns.eval_command == "summarize"
    assert ns.directory == Path("a-dir")
    assert ns.diff_against == Path("b-dir")
    assert ns.json is True
    assert ns.fail_on_regression is True


# ---------------------------------------------------------------------------
# clean match
# ---------------------------------------------------------------------------
def test_clean_match_prints_markdown_and_exits_zero(tmp_path, capsys):
    a, b = _mkdirs(tmp_path)
    for d in (a, b):
        _write(d / "alpha.jsonl", [_chat("c", tokens=5)])
        _write(d / "beta.jsonl", [_invoke("t", "add", ts=2.0)])

    assert (
        main(
            [
                "eval",
                "summarize",
                str(a),
                "--diff-against",
                str(b),
                "--fail-on-regression",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "# Frok Eval Directory Diff" in out
    assert "Regressed cases: 0" in out
    assert "match" in out
    # Clean diff → no details section.
    assert "## Regression details" not in out


# ---------------------------------------------------------------------------
# regression: tool-order divergence
# ---------------------------------------------------------------------------
def test_tool_order_divergence_regresses_under_flag(tmp_path, capsys):
    a, b = _mkdirs(tmp_path)
    _write(a / "tool.jsonl", [_invoke("1", "add", ts=1.0), _invoke("2", "search", ts=2.0)])
    _write(b / "tool.jsonl", [_invoke("1", "search", ts=1.0), _invoke("2", "add", ts=2.0)])

    # Default: exit 0.
    assert main(["eval", "summarize", str(a), "--diff-against", str(b)]) == 0
    # With --fail-on-regression: exit 1.
    assert (
        main(
            [
                "eval",
                "summarize",
                str(a),
                "--diff-against",
                str(b),
                "--fail-on-regression",
            ]
        )
        == 1
    )
    out = capsys.readouterr().out
    # Details only rendered in the second invocation — take that text.
    assert "## Regression details" in out


# ---------------------------------------------------------------------------
# slug divergence: only_in_a / only_in_b
# ---------------------------------------------------------------------------
def test_slug_divergence_flagged_in_output_and_regresses(tmp_path, capsys):
    a, b = _mkdirs(tmp_path)
    _write(a / "shared.jsonl", [_chat("c")])
    _write(a / "legacy.jsonl", [_chat("c")])
    _write(b / "shared.jsonl", [_chat("c")])
    _write(b / "new-one.jsonl", [_chat("c")])

    code = main(
        [
            "eval",
            "summarize",
            str(a),
            "--diff-against",
            str(b),
            "--fail-on-regression",
            "--json",
        ]
    )
    assert code == 1  # slug divergence regresses
    data = json.loads(capsys.readouterr().out)
    assert data["only_in_a"] == ["legacy"]
    assert data["only_in_b"] == ["new-one"]
    assert data["regressed"] is True
    assert [m["name"] for m in data["matched"]] == ["shared"]


# ---------------------------------------------------------------------------
# token-only delta does NOT regress
# ---------------------------------------------------------------------------
def test_token_only_delta_clean_under_fail_on_regression(tmp_path):
    a, b = _mkdirs(tmp_path)
    _write(a / "chat.jsonl", [_chat("c", tokens=10)])
    _write(b / "chat.jsonl", [_chat("c", tokens=100)])

    code = main(
        [
            "eval",
            "summarize",
            str(a),
            "--diff-against",
            str(b),
            "--fail-on-regression",
        ]
    )
    assert code == 0


# ---------------------------------------------------------------------------
# -o and --json output hooks
# ---------------------------------------------------------------------------
def test_output_flag_writes_file(tmp_path, capsys):
    a, b = _mkdirs(tmp_path)
    _write(a / "c.jsonl", [_chat("c")])
    _write(b / "c.jsonl", [_chat("c")])
    dest = tmp_path / "nested" / "diff.md"
    assert (
        main(
            [
                "eval",
                "summarize",
                str(a),
                "--diff-against",
                str(b),
                "-o",
                str(dest),
            ]
        )
        == 0
    )
    assert capsys.readouterr().out == ""
    assert "# Frok Eval Directory Diff" in dest.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_missing_diff_against_dir_is_cli_error(tmp_path, capsys):
    a = tmp_path / "a"
    a.mkdir()
    _write(a / "c.jsonl", [_chat("c")])
    code = main(
        [
            "eval",
            "summarize",
            str(a),
            "--diff-against",
            str(tmp_path / "missing"),
        ]
    )
    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_not_a_directory_is_cli_error(tmp_path, capsys):
    a = tmp_path / "a"
    a.mkdir()
    _write(a / "c.jsonl", [_chat("c")])
    f = tmp_path / "file.txt"
    f.write_text("not a dir", encoding="utf-8")
    code = main(
        ["eval", "summarize", str(a), "--diff-against", str(f)]
    )
    assert code == 2
    assert "not a directory" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# single-dir path still works when --diff-against is absent
# ---------------------------------------------------------------------------
def test_summarize_without_diff_against_keeps_single_dir_behaviour(tmp_path, capsys):
    a = tmp_path / "a"
    a.mkdir()
    _write(a / "c.jsonl", [_chat("c", tokens=5)])
    assert main(["eval", "summarize", str(a), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    # Single-dir summary shape, not directory-diff shape.
    assert "cases" in data
    assert "directory" in data
    assert "matched" not in data
