"""Tests for ``frok trace inspect <jsonl>``."""

import json
from pathlib import Path

from frok.cli import build_parser, main
from frok.telemetry import SPAN_END, Event, JsonlSink


def _end(name, *, span_id, **data):
    return Event(
        ts=1000.0,
        trace_id=data.pop("trace_id", "t1"),
        span_id=span_id,
        parent_span_id=data.pop("parent", None),
        kind=SPAN_END,
        name=name,
        duration_ms=data.pop("duration", 5.0),
        data=data,
        error=data.pop("error", None) if False else None,
    )


def _write_jsonl(path: Path, events: list[Event]) -> Path:
    with JsonlSink(path) as sink:
        for e in events:
            sink.emit(e)
    return path


def _sample_events() -> list[Event]:
    return [
        Event(
            ts=1000.0,
            trace_id="t1",
            span_id="r",
            parent_span_id=None,
            kind=SPAN_END,
            name="tool.run",
            duration_ms=100.0,
            data={"hops": 2},
        ),
        Event(
            ts=1001.0,
            trace_id="t1",
            span_id="c1",
            parent_span_id="r",
            kind=SPAN_END,
            name="grok.chat",
            duration_ms=50.0,
            data={"total_tokens": 14},
        ),
        Event(
            ts=1002.0,
            trace_id="t1",
            span_id="i1",
            parent_span_id="r",
            kind=SPAN_END,
            name="tool.invoke",
            duration_ms=8.0,
            data={"tool": "add"},
        ),
        Event(
            ts=1003.0,
            trace_id="t1",
            span_id="i2",
            parent_span_id="r",
            kind=SPAN_END,
            name="tool.invoke",
            duration_ms=12.0,
            data={"tool": "search"},
            error="timeout",
        ),
    ]


# ---------------------------------------------------------------------------
# parser contract
# ---------------------------------------------------------------------------
def test_parser_has_trace_inspect_subcommand():
    parser = build_parser()
    ns = parser.parse_args(["trace", "inspect", "x.jsonl", "--tree", "--top", "5"])
    assert ns.command == "trace"
    assert ns.trace_command == "inspect"
    assert ns.jsonl_path == Path("x.jsonl")
    assert ns.tree is True
    assert ns.top == 5


# ---------------------------------------------------------------------------
# happy-path markdown + json output
# ---------------------------------------------------------------------------
def test_inspect_prints_markdown_summary(tmp_path, capsys):
    path = _write_jsonl(tmp_path / "t.jsonl", _sample_events())
    assert main(["trace", "inspect", str(path)]) == 0
    out = capsys.readouterr().out
    assert "# Frok Trace Report" in out
    assert "tool.invoke" in out
    assert "## Errors" in out
    assert "timeout" in out
    assert "search" in out


def test_inspect_json_flag_emits_parsable_json(tmp_path, capsys):
    path = _write_jsonl(tmp_path / "t.jsonl", _sample_events())
    assert main(["trace", "inspect", str(path), "--json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["span_count"] == 4
    assert data["trace_count"] == 1
    tools = {t["tool"] for t in data["top_tools"]}
    assert tools == {"add", "search"}
    assert data["errors"][0]["error"] == "timeout"


def test_inspect_tree_flag_appends_tree_block(tmp_path, capsys):
    path = _write_jsonl(tmp_path / "t.jsonl", _sample_events())
    assert main(["trace", "inspect", str(path), "--tree"]) == 0
    out = capsys.readouterr().out
    assert "## Trace tree" in out
    # children indented under root
    tree_block = out.split("## Trace tree", 1)[1]
    assert "- tool.run" in tree_block
    assert "  - grok.chat" in tree_block


def test_inspect_output_flag_writes_file(tmp_path, capsys):
    path = _write_jsonl(tmp_path / "t.jsonl", _sample_events())
    dest = tmp_path / "nested" / "report.md"
    assert main(["trace", "inspect", str(path), "-o", str(dest)]) == 0
    assert capsys.readouterr().out == ""
    assert "# Frok Trace Report" in dest.read_text(encoding="utf-8")


def test_inspect_top_flag_limits_rows(tmp_path, capsys):
    events = _sample_events()
    # Add a bunch more errored spans to exceed a small top limit.
    for i in range(5):
        events.append(
            Event(
                ts=2000.0 + i,
                trace_id="t1",
                span_id=f"x{i}",
                parent_span_id=None,
                kind=SPAN_END,
                name="noise",
                duration_ms=1.0,
                data={},
                error=f"err{i}",
            )
        )
    path = _write_jsonl(tmp_path / "t.jsonl", events)
    main(["trace", "inspect", str(path), "--json", "--top", "2"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data["errors"]) == 2


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_inspect_missing_file_is_cli_error(tmp_path, capsys):
    assert main(["trace", "inspect", str(tmp_path / "missing.jsonl")]) == 2
    assert "not found" in capsys.readouterr().err


def test_inspect_empty_file_is_cli_error(tmp_path, capsys):
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")
    assert main(["trace", "inspect", str(path)]) == 2
    assert "empty" in capsys.readouterr().err


def test_inspect_malformed_file_is_cli_error(tmp_path, capsys):
    path = tmp_path / "bad.jsonl"
    path.write_text("not valid json\n", encoding="utf-8")
    assert main(["trace", "inspect", str(path)]) == 2
    assert "cannot read" in capsys.readouterr().err
