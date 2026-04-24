"""Tests for per-call model overrides on GrokClient + EvalCase."""

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, EvalRunner
from frok.telemetry import InMemorySink, Tracer
from frok.tools import ToolOrchestrator, ToolRegistry, tool


# ---------------------------------------------------------------------------
# stubs
# ---------------------------------------------------------------------------
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


def _ok(text="ok", *, model="grok-4"):
    return (
        200,
        {
            "model": model,
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        },
    )


def _sse(*, content=None, finish_reason=None):
    choice = {"delta": {}, "index": 0}
    if content is not None:
        choice["delta"]["content"] = content
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return f"data: {json.dumps({'choices': [choice]})}\n".encode("utf-8")


def _stream_transport(lines):
    calls: list = []

    async def transport(*, method, url, headers, body, timeout):
        calls.append(json.loads(body.decode("utf-8")))

        async def _iter() -> AsyncIterator[bytes]:
            for line in lines:
                yield line

        return 200, {}, _iter()

    transport.calls = calls  # type: ignore[attr-defined]
    return transport


# ---------------------------------------------------------------------------
# GrokClient.chat: model precedence
# ---------------------------------------------------------------------------
async def test_chat_uses_client_default_model_when_no_kwarg():
    transport = _StubTransport([_ok()])
    client = GrokClient(
        api_key="k", model="grok-4", transport=transport, sleep=_noop_sleep
    )
    await client.chat([GrokMessage("user", "hi")])
    assert transport.calls[0]["model"] == "grok-4"


async def test_chat_kwarg_overrides_client_default_model():
    transport = _StubTransport([_ok()])
    client = GrokClient(
        api_key="k", model="grok-4", transport=transport, sleep=_noop_sleep
    )
    await client.chat([GrokMessage("user", "hi")], model="grok-4-fast")
    assert transport.calls[0]["model"] == "grok-4-fast"


async def test_chat_response_model_falls_back_to_effective_when_server_silent():
    # Server payload with no `model` field → client falls back to whatever
    # it actually sent (the override, not the client default).
    server_payload = (
        200,
        {
            # intentionally no "model" key
            "choices": [
                {
                    "message": {"role": "assistant", "content": "ok"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        },
    )
    transport = _StubTransport([server_payload])
    client = GrokClient(
        api_key="k", model="grok-4", transport=transport, sleep=_noop_sleep
    )
    resp = await client.chat([GrokMessage("user", "hi")], model="grok-4-fast")
    assert resp.model == "grok-4-fast"


# ---------------------------------------------------------------------------
# chat_stream: model kwarg
# ---------------------------------------------------------------------------
async def test_chat_stream_uses_model_kwarg():
    transport = _stream_transport([
        _sse(content="hi"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ])
    client = GrokClient(api_key="k", model="grok-4", streaming_transport=transport)
    async for chunk in client.chat_stream(
        [GrokMessage("user", "hi")], model="grok-4-fast"
    ):
        if chunk.is_final:
            assert chunk.response.model == "grok-4-fast"
    assert transport.calls[0]["model"] == "grok-4-fast"


async def test_chat_stream_uses_client_default_without_kwarg():
    transport = _stream_transport([
        _sse(content="hi"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ])
    client = GrokClient(api_key="k", model="grok-4", streaming_transport=transport)
    async for _ in client.chat_stream([GrokMessage("user", "hi")]):
        pass
    assert transport.calls[0]["model"] == "grok-4"


# ---------------------------------------------------------------------------
# Telemetry: span reflects the effective model
# ---------------------------------------------------------------------------
async def test_chat_span_reports_effective_model_from_kwarg():
    sink = InMemorySink()
    transport = _StubTransport([_ok()])
    client = GrokClient(
        api_key="k",
        model="grok-4",
        transport=transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )
    await client.chat([GrokMessage("user", "hi")], model="grok-4-fast")
    span = sink.spans(name="grok.chat")[0]
    assert span.data["model"] == "grok-4-fast"


async def test_chat_stream_span_reports_effective_model_from_kwarg():
    sink = InMemorySink()
    transport = _stream_transport([
        _sse(content="hi"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ])
    client = GrokClient(
        api_key="k",
        model="grok-4",
        streaming_transport=transport,
        tracer=Tracer(sink=sink),
    )
    async for _ in client.chat_stream(
        [GrokMessage("user", "hi")], model="grok-4-fast"
    ):
        pass
    span = sink.spans(name="grok.chat_stream")[0]
    assert span.data["model"] == "grok-4-fast"


# ---------------------------------------------------------------------------
# ToolOrchestrator.model flows through every turn
# ---------------------------------------------------------------------------
async def test_orchestrator_model_overrides_each_turn():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    def _tc(call_id):
        return (
            200,
            {
                "model": "grok-4-fast",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": call_id,
                                    "type": "function",
                                    "function": {
                                        "name": "add",
                                        "arguments": '{"a":1,"b":1}',
                                    },
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            },
        )

    transport = _StubTransport([_tc("c1"), _ok("2", model="grok-4-fast")])
    client = GrokClient(
        api_key="k", model="grok-4", transport=transport, sleep=_noop_sleep
    )
    orch = ToolOrchestrator(
        client=client,
        registry=ToolRegistry().add(add),
        model="grok-4-fast",
    )
    await orch.run([GrokMessage("user", "1+1?")])
    assert [c["model"] for c in transport.calls] == ["grok-4-fast", "grok-4-fast"]


async def test_orchestrator_defaults_to_client_model_without_override():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    transport = _StubTransport([_ok("2")])
    client = GrokClient(
        api_key="k", model="grok-4", transport=transport, sleep=_noop_sleep
    )
    orch = ToolOrchestrator(client=client, registry=ToolRegistry().add(add))
    await orch.run([GrokMessage("user", "1+1?")])
    assert transport.calls[0]["model"] == "grok-4"


# ---------------------------------------------------------------------------
# EvalCase.model flows through the runner, both paths
# ---------------------------------------------------------------------------
async def test_eval_case_model_reaches_wire_on_no_tools_path():
    transport = _StubTransport([_ok("hi", model="grok-4-fast")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            model="grok-4",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="pinned-model",
        messages=[GrokMessage("user", "hi")],
        model="grok-4-fast",
        scorers=[AnswerContains("hi")],
    )
    await EvalRunner(client_factory=factory).run_case(case)
    assert transport.calls[0]["model"] == "grok-4-fast"


async def test_eval_case_model_reaches_wire_on_tools_path():
    @tool
    def noop() -> str:
        return "ok"

    transport = _StubTransport([_ok("hi", model="grok-4-fast")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            model="grok-4",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="pinned-model-tools",
        messages=[GrokMessage("user", "hi")],
        tools=[noop],
        model="grok-4-fast",
        scorers=[AnswerContains("hi")],
    )
    await EvalRunner(client_factory=factory).run_case(case)
    assert transport.calls[0]["model"] == "grok-4-fast"


async def test_eval_case_model_none_falls_back_to_client_default():
    transport = _StubTransport([_ok("hi")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            model="grok-4",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="default-model",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hi")],
    )
    await EvalRunner(client_factory=factory).run_case(case)
    assert transport.calls[0]["model"] == "grok-4"


async def test_eval_case_model_via_streaming_path():
    transport = _stream_transport([
        _sse(content="streamed"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            model="grok-4",
            streaming_transport=transport,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="pinned-model-stream",
        messages=[GrokMessage("user", "hi")],
        model="grok-4-fast",
        scorers=[AnswerContains("streamed")],
    )
    captured: list[str] = []
    result = await EvalRunner(client_factory=factory).run_case(
        case, stream_sink=captured.append
    )
    assert result.passed
    assert transport.calls[0]["model"] == "grok-4-fast"
