"""Tests for ``frok eval summarize <dir>``."""

import json
from pathlib import Path

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


def _invoke(span_id, tool, *, error=None, ts=1001.0):
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


def _populate(tmp_path: Path) -> Path:
    d = tmp_path / "captures"
    d.mkdir()
    _write(d / "safety-a.jsonl", [_chat("c", tokens=10)])
    _write(
        d / "tool-add.jsonl",
        [_chat("c", tokens=50), _invoke("t", "add")],
    )
    _write(
        d / "tool-boom.jsonl",
        [_chat("c", tokens=5), _invoke("t", "send", error="nope")],
    )
    return d


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_eval_summarize_shape():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "eval",
            "summarize",
            "/tmp/baselines",
            "--json",
            "-o",
            "/tmp/out",
            "--top",
            "3",
            "--fail-on-errors",
        ]
    )
    assert ns.command == "eval"
    assert ns.eval_command == "summarize"
    assert ns.directory == Path("/tmp/baselines")
    assert ns.json is True
    assert ns.output == Path("/tmp/out")
    assert ns.top == 3
    assert ns.fail_on_errors is True


# ---------------------------------------------------------------------------
# happy paths (markdown + json)
# ---------------------------------------------------------------------------
def test_markdown_output_has_all_cases(tmp_path, capsys):
    d = _populate(tmp_path)
    assert main(["eval", "summarize", str(d)]) == 0
    out = capsys.readouterr().out
    assert "# Frok Eval Directory Summary" in out
    for name in ("safety-a", "tool-add", "tool-boom"):
        assert name in out
    assert "### Tools with errors" in out
    assert "send" in out


def test_json_output_parseable(tmp_path, capsys):
    d = _populate(tmp_path)
    assert main(["eval", "summarize", str(d), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["directory"] == str(d)
    assert {c["name"] for c in data["cases"]} == {
        "safety-a",
        "tool-add",
        "tool-boom",
    }
    assert data["total_errors"] == 1
    assert data["tool_counts"] == {"add": 1, "send": 1}


def test_output_flag_writes_to_file(tmp_path, capsys):
    d = _populate(tmp_path)
    dest = tmp_path / "nested" / "report.md"
    assert main(["eval", "summarize", str(d), "-o", str(dest)]) == 0
    assert capsys.readouterr().out == ""
    assert "# Frok Eval Directory Summary" in dest.read_text(encoding="utf-8")


def test_top_flag_limits_leader_rows(tmp_path, capsys):
    d = tmp_path / "d"
    d.mkdir()
    for i in range(6):
        _write(d / f"case-{i:02d}.jsonl", [_chat(f"c{i}", tokens=i)])
    main(["eval", "summarize", str(d), "--json", "--top", "2"])
    data = json.loads(capsys.readouterr().out)
    # Slowest only has top-N
    assert len(data["slowest"]) == 2
    assert len(data["heaviest_tokens"]) == 2
    # Per-case rollup is NOT limited — all 6 appear.
    assert len(data["cases"]) == 6


# ---------------------------------------------------------------------------
# --fail-on-errors
# ---------------------------------------------------------------------------
def test_fail_on_errors_returns_1_when_any_error(tmp_path):
    d = _populate(tmp_path)
    assert main(["eval", "summarize", str(d)]) == 0  # default exit 0
    assert main(["eval", "summarize", str(d), "--fail-on-errors"]) == 1


def test_fail_on_errors_returns_0_when_clean(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    _write(d / "clean.jsonl", [_chat("c", tokens=5)])
    assert main(["eval", "summarize", str(d), "--fail-on-errors"]) == 0


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_missing_directory_is_cli_error(tmp_path, capsys):
    assert main(["eval", "summarize", str(tmp_path / "missing")]) == 2
    assert "directory not found" in capsys.readouterr().err


def test_not_a_directory_is_cli_error(tmp_path, capsys):
    f = tmp_path / "file.jsonl"
    f.write_text("{}", encoding="utf-8")
    assert main(["eval", "summarize", str(f)]) == 2
    assert "not a directory" in capsys.readouterr().err


def test_empty_directory_is_cli_error(tmp_path, capsys):
    d = tmp_path / "empty"
    d.mkdir()
    assert main(["eval", "summarize", str(d)]) == 2
    assert "no .jsonl captures" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# interop: feed frok run --capture-baseline output directly
# ---------------------------------------------------------------------------
_CASE_FILE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text, *, prompt=5, completion=3):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {"message": {"role": "assistant", "content": text},
                 "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("42"), _final("42")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(name="alpha", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("42")]),
    EvalCase(name="beta", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("42")]),
]
'''


def test_interop_with_capture_baseline_directory(tmp_path, capsys):
    case_file = tmp_path / "cases.py"
    case_file.write_text(_CASE_FILE, encoding="utf-8")
    baselines = tmp_path / "baselines"
    assert (
        main(
            ["run", str(case_file), "--capture-baseline", str(baselines)]
        )
        == 0
    )
    # Fresh capsys read between invocations.
    capsys.readouterr()
    assert main(["eval", "summarize", str(baselines), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    names = {c["name"] for c in data["cases"]}
    assert names == {"alpha", "beta"}
