"""Tests for ``frok run --stream``."""

import json
from pathlib import Path

import pytest

from frok.cli import main


_STREAM_CASE_FILE = '''
import json
from dataclasses import dataclass, field
from typing import AsyncIterator

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


def _sse(*, content=None, finish_reason=None):
    choice = {"delta": {}, "index": 0}
    if content is not None:
        choice["delta"]["content"] = content
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return f"data: {json.dumps({'choices': [choice]})}\\n".encode("utf-8")


async def _stub_streaming(*, method, url, headers, body, timeout):
    lines = [
        _sse(content="Hello"),
        _sse(content=", "),
        _sse(content="stream!"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\\n",
    ]

    async def _iter():
        for line in lines:
            yield line

    return 200, {}, _iter()


async def _noop_sleep(_s):
    return None


def _final(text):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {"message": {"role": "assistant", "content": text},
                 "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        },
    )


def make_client(config, sink):
    # Non-stream transport is still required for cases with tools; we
    # don't exercise it in the --stream tests below.
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("Hello, stream!")]),
        streaming_transport=_stub_streaming,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="stream-greeting",
        messages=[GrokMessage("user", "greet me")],
        scorers=[AnswerContains("Hello"), NoErrors()],
    ),
]
'''


def _write_case(tmp_path: Path) -> Path:
    path = tmp_path / "cases.py"
    path.write_text(_STREAM_CASE_FILE, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_stream_default_false():
    from frok.cli import build_parser

    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.stream is False


def test_parser_stream_accepts_flag():
    from frok.cli import build_parser

    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py", "--stream"])
    assert ns.stream is True


# ---------------------------------------------------------------------------
# --stream writes deltas + per-case header to stderr
# ---------------------------------------------------------------------------
def test_stream_writes_deltas_and_header_to_stderr(tmp_path, capsys):
    case = _write_case(tmp_path)
    code = main(
        [
            "run",
            str(case),
            "--stream",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    captured = capsys.readouterr()
    assert ">>> stream-greeting" in captured.err
    # Each delta from the stub stream appears in stderr.
    assert "Hello" in captured.err
    assert ", " in captured.err
    assert "stream!" in captured.err
    # Stdout is suppressed when -o is set.
    assert captured.out == ""


def test_stream_preserves_final_response_for_scorers(tmp_path, capsys):
    case = _write_case(tmp_path)
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(case),
            "--stream",
            "-o",
            str(tmp_path / "r.md"),
            "--summary-json",
            str(summary),
            "--fail-on-regression",
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    # Scorers saw the assembled final content.
    assert data["passed"] == 1
    assert data["cases"][0]["scores"]["answer_contains['Hello']"] is True


# ---------------------------------------------------------------------------
# tools case: --stream silently falls back to non-stream
# ---------------------------------------------------------------------------
_TOOLS_STREAM_CASE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors, ToolCalled
from frok.telemetry import Tracer
from frok.tools import tool


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


def _tool_call(name, args, *, call_id):
    return (200, {"model": "grok-4", "choices": [{
        "message": {"role": "assistant", "content": None, "tool_calls": [{
            "id": call_id, "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)},
        }]},
        "finish_reason": "tool_calls",
    }], "usage": {"prompt_tokens": 5, "completion_tokens": 2}})


def _final(text):
    return (200, {"model": "grok-4", "choices": [{
        "message": {"role": "assistant", "content": text},
        "finish_reason": "stop",
    }], "usage": {"prompt_tokens": 10, "completion_tokens": 3}})


@tool
def add(a: int, b: int) -> int:
    return a + b


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([
            _tool_call("add", {"a": 2, "b": 40}, call_id="c1"),
            _final("answer is 42"),
        ]),
        # streaming_transport intentionally absent — if the runner tried
        # to stream, chat_stream would error.
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="tools-stream-fallback",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[AnswerContains("42"), ToolCalled("add", times=1), NoErrors()],
    ),
]
'''


def test_stream_falls_back_silently_when_case_has_tools(tmp_path, capsys):
    # The case has tools but NO streaming_transport — the orchestrator
    # falls back to the non-stream chat path silently. The case-level
    # header still prints (from run_cmd), but no per-turn markers or
    # deltas should appear.
    path = tmp_path / "tools.py"
    path.write_text(_TOOLS_STREAM_CASE, encoding="utf-8")
    code = main(
        [
            "run",
            str(path),
            "--stream",
            "-o",
            str(tmp_path / "r.md"),
            "--fail-on-regression",
        ]
    )
    assert code == 0
    captured = capsys.readouterr()
    assert ">>> tools-stream-fallback" in captured.err
    assert ">>> turn " not in captured.err  # no per-turn markers
    assert "answer is 42" not in captured.err


# ---------------------------------------------------------------------------
# tools case WITH streaming_transport: --stream flows through each turn
# ---------------------------------------------------------------------------
_TOOLS_STREAM_CASE_WITH_STREAMING = '''
import json
from dataclasses import dataclass, field
from typing import AsyncIterator

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors, ToolCalled
from frok.telemetry import Tracer
from frok.tools import tool


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


def _sse(*, content=None, tool_call=None, finish_reason=None):
    choice = {"delta": {}, "index": 0}
    if content is not None:
        choice["delta"]["content"] = content
    if tool_call is not None:
        choice["delta"]["tool_calls"] = [tool_call]
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return f"data: {json.dumps({'choices': [choice]})}\\n".encode("utf-8")


_TURN1 = [
    _sse(tool_call={
        "index": 0,
        "id": "c1",
        "function": {"name": "add", "arguments": json.dumps({"a": 2, "b": 40})},
    }),
    _sse(finish_reason="tool_calls"),
    b"data: [DONE]\\n",
]

_TURN2 = [
    _sse(content="The "),
    _sse(content="answer "),
    _sse(content="is 42."),
    _sse(finish_reason="stop"),
    b"data: [DONE]\\n",
]


async def _streaming_transport(*, method, url, headers, body, timeout):
    turns = [_TURN1, _TURN2]
    # Rotate by popping from a module-level cursor so consecutive calls serve
    # subsequent turn scripts.
    global _cursor
    try:
        _cursor
    except NameError:
        _cursor = 0
    lines = turns[_cursor]
    _cursor += 1

    async def _iter() -> AsyncIterator[bytes]:
        for line in lines:
            yield line

    return 200, {}, _iter()


async def _noop_sleep(_s):
    return None


@tool
def add(a: int, b: int) -> int:
    return a + b


def make_client(config, sink):
    # Non-stream transport is a safety net; the streaming path takes over.
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([]),
        streaming_transport=_streaming_transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="tools-stream-live",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[
            AnswerContains("42"),
            ToolCalled("add", times=1),
            NoErrors(),
        ],
    ),
]
'''


def test_stream_flows_through_tool_orchestrator_when_streaming_transport_set(
    tmp_path, capsys
):
    path = tmp_path / "tools_stream.py"
    path.write_text(_TOOLS_STREAM_CASE_WITH_STREAMING, encoding="utf-8")
    code = main(
        [
            "run",
            str(path),
            "--stream",
            "-o",
            str(tmp_path / "r.md"),
            "--fail-on-regression",
        ]
    )
    assert code == 0
    err = capsys.readouterr().err
    # Case header, per-turn markers for both turns, and the turn-2 deltas.
    assert ">>> tools-stream-live" in err
    assert ">>> turn 1" in err
    assert ">>> turn 2" in err
    # Turn-1 produced no text content; turn-2 streamed the answer.
    turn2_idx = err.index(">>> turn 2")
    assert "The answer is 42." in err[turn2_idx:]


# ---------------------------------------------------------------------------
# --stream + --jobs > 1 is a CliError
# ---------------------------------------------------------------------------
def test_stream_with_jobs_gt_one_is_cli_error(tmp_path, capsys):
    case = _write_case(tmp_path)
    code = main(["run", str(case), "--stream", "--jobs", "2"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--stream" in err and "--jobs" in err
    assert "interleave" in err


def test_stream_with_jobs_one_is_allowed(tmp_path):
    case = _write_case(tmp_path)
    assert (
        main(
            [
                "run",
                str(case),
                "--stream",
                "--jobs",
                "1",
                "-o",
                str(tmp_path / "r.md"),
            ]
        )
        == 0
    )


# ---------------------------------------------------------------------------
# no streaming_transport in make_client surfaces as a case error
# ---------------------------------------------------------------------------
_NO_STREAM_TRANSPORT_CASE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase
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


def _final(text):
    return (200, {"model": "grok-4", "choices": [{
        "message": {"role": "assistant", "content": text},
        "finish_reason": "stop",
    }], "usage": {"prompt_tokens": 5, "completion_tokens": 3}})


def make_client(config, sink):
    # No streaming_transport — --stream will surface chat_stream's error.
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("hi")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="no-stream-transport",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hi")],
    ),
]
'''


def test_stream_without_streaming_transport_surfaces_as_case_error(tmp_path, capsys):
    path = tmp_path / "no_stream.py"
    path.write_text(_NO_STREAM_TRANSPORT_CASE, encoding="utf-8")
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--stream",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0  # default exit 0 even on case failure
    data = json.loads(summary.read_text(encoding="utf-8"))
    # The error propagated into Observation.error; case fails because no
    # final_response was produced.
    assert data["failed"] == 1
    err = data["cases"][0]["error"]
    assert err is not None
    assert "no streaming_transport" in err
