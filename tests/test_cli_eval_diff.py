"""Tests for ``frok eval diff <a.jsonl> <b.jsonl>``."""

import json
from pathlib import Path

from frok.cli import build_parser, main
from frok.telemetry import SPAN_END, Event, JsonlSink


def _chat(span_id, *, ts=1000.0, tokens=10, error=None):
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


def _write(path: Path, events: list[Event]) -> Path:
    with JsonlSink(path) as sink:
        for e in events:
            sink.emit(e)
    return path


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_eval_diff_shape():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "eval",
            "diff",
            "a.jsonl",
            "b.jsonl",
            "--json",
            "-o",
            "out.md",
            "--fail-on-regression",
        ]
    )
    assert ns.command == "eval"
    assert ns.eval_command == "diff"
    assert ns.a == Path("a.jsonl")
    assert ns.b == Path("b.jsonl")
    assert ns.json is True
    assert ns.output == Path("out.md")
    assert ns.fail_on_regression is True


# ---------------------------------------------------------------------------
# happy path — identical captures diff cleanly
# ---------------------------------------------------------------------------
def test_identical_captures_not_regressed(tmp_path, capsys):
    events = [_chat("c1", tokens=10), _invoke("t1", "add", ts=1001.0)]
    a = _write(tmp_path / "a.jsonl", events)
    b = _write(tmp_path / "b.jsonl", list(events))
    assert main(["eval", "diff", str(a), str(b)]) == 0
    out = capsys.readouterr().out
    assert "# Frok Eval Diff" in out
    assert "Regressed: no" in out
    assert "Match: yes" in out


# ---------------------------------------------------------------------------
# tool-order divergence → regressed → non-zero exit under --fail-on-regression
# ---------------------------------------------------------------------------
def test_tool_order_divergence_regresses(tmp_path, capsys):
    a = _write(
        tmp_path / "a.jsonl",
        [_invoke("1", "add", ts=1.0), _invoke("2", "search", ts=2.0)],
    )
    b = _write(
        tmp_path / "b.jsonl",
        [_invoke("1", "search", ts=1.0), _invoke("2", "add", ts=2.0)],
    )
    # Default: always exit 0.
    assert main(["eval", "diff", str(a), str(b)]) == 0
    out = capsys.readouterr().out
    assert "**yes**" in out  # regressed
    # With --fail-on-regression: exit 1.
    assert (
        main(["eval", "diff", str(a), str(b), "--fail-on-regression"]) == 1
    )


def test_clean_diff_returns_zero_under_fail_on_regression(tmp_path):
    events = [_chat("c1", tokens=10)]
    a = _write(tmp_path / "a.jsonl", events)
    b = _write(tmp_path / "b.jsonl", list(events))
    assert main(["eval", "diff", str(a), str(b), "--fail-on-regression"]) == 0


# ---------------------------------------------------------------------------
# --json emits parseable JSON including paths
# ---------------------------------------------------------------------------
def test_json_flag_parseable_with_paths(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_chat("c", tokens=5)])
    b = _write(tmp_path / "b.jsonl", [_chat("c", tokens=20)])
    assert main(["eval", "diff", str(a), str(b), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["a_path"] == str(a)
    assert data["b_path"] == str(b)
    assert data["token_delta"] == 15
    assert data["regressed"] is False


# ---------------------------------------------------------------------------
# -o writes file + suppresses stdout
# ---------------------------------------------------------------------------
def test_output_flag_writes_file(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_chat("c", tokens=10)])
    b = _write(tmp_path / "b.jsonl", [_chat("c", tokens=10)])
    dest = tmp_path / "nested" / "diff.md"
    assert main(["eval", "diff", str(a), str(b), "-o", str(dest)]) == 0
    assert capsys.readouterr().out == ""
    assert "# Frok Eval Diff" in dest.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_missing_file_is_cli_error(tmp_path, capsys):
    b = _write(tmp_path / "b.jsonl", [_chat("c")])
    assert main(["eval", "diff", str(tmp_path / "missing.jsonl"), str(b)]) == 2
    assert "not found" in capsys.readouterr().err


def test_empty_file_is_cli_error(tmp_path, capsys):
    a = tmp_path / "empty.jsonl"
    a.write_text("", encoding="utf-8")
    b = _write(tmp_path / "b.jsonl", [_chat("c")])
    assert main(["eval", "diff", str(a), str(b)]) == 2
    assert "empty" in capsys.readouterr().err


def test_malformed_file_is_cli_error(tmp_path, capsys):
    a = tmp_path / "bad.jsonl"
    a.write_text("not valid json\n", encoding="utf-8")
    b = _write(tmp_path / "b.jsonl", [_chat("c")])
    assert main(["eval", "diff", str(a), str(b)]) == 2
    assert "cannot read" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# regression: new error in b, same tool order
# ---------------------------------------------------------------------------
def test_new_error_in_b_regresses(tmp_path, capsys):
    a = _write(tmp_path / "a.jsonl", [_chat("c", tokens=10)])
    b = _write(tmp_path / "b.jsonl", [_chat("c", tokens=10, error="timeout")])
    code = main(["eval", "diff", str(a), str(b), "--fail-on-regression", "--json"])
    assert code == 1
    data = json.loads(capsys.readouterr().out)
    assert data["regressed"] is True
    assert data["new_errors"] == 1
