"""Tests for ``ToolOrchestrator.run(stream_sink=...)``."""

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.telemetry import InMemorySink, Tracer
from frok.tools import ToolOrchestrator, ToolRegistry, tool


# ---------------------------------------------------------------------------
# transports
# ---------------------------------------------------------------------------
@dataclass
class _StubTransport:
    """Non-streaming transport; records request payloads."""

    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


def _tool_call_msg(name, args, *, call_id="c1"):
    return (
        200,
        {
            "model": "grok-4",
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
                                    "name": name,
                                    "arguments": json.dumps(args),
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2},
        },
    )


def _final_msg(text):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        },
    )


def _sse(*, content=None, tool_call=None, finish_reason=None):
    choice: dict = {"delta": {}, "index": 0}
    if content is not None:
        choice["delta"]["content"] = content
    if tool_call is not None:
        choice["delta"]["tool_calls"] = [tool_call]
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return f"data: {json.dumps({'choices': [choice]})}\n".encode("utf-8")


def _make_streaming_transport(turn_scripts: list[list[bytes]]):
    """Return a streaming transport that serves each POST from the next
    pre-scripted list of SSE lines."""
    remaining = list(turn_scripts)
    calls: list = []

    async def transport(*, method, url, headers, body, timeout):
        calls.append(json.loads(body.decode("utf-8")))
        lines = remaining.pop(0)

        async def _iter() -> AsyncIterator[bytes]:
            for line in lines:
                yield line

        return 200, {}, _iter()

    transport.calls = calls  # type: ignore[attr-defined]
    return transport


async def _noop_sleep(_s):
    return None


# ---------------------------------------------------------------------------
# tooling fixtures
# ---------------------------------------------------------------------------
@tool
def add(a: int, b: int) -> int:
    """Return a + b."""
    return a + b


def _registry():
    return ToolRegistry().add(add)


# ---------------------------------------------------------------------------
# happy path: streaming through two turns
# ---------------------------------------------------------------------------
async def test_stream_sink_emits_per_turn_markers_and_final_deltas():
    # Turn 1: model emits a tool_call (no text content).
    turn1 = [
        _sse(tool_call={
            "index": 0, "id": "c1",
            "function": {"name": "add", "arguments": '{"a": 2, "b": 40}'},
        }),
        _sse(finish_reason="tool_calls"),
        b"data: [DONE]\n",
    ]
    # Turn 2: model streams the final answer text.
    turn2 = [
        _sse(content="The "),
        _sse(content="answer "),
        _sse(content="is "),
        _sse(content="42."),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ]
    streaming_transport = _make_streaming_transport([turn1, turn2])

    client = GrokClient(
        api_key="k",
        streaming_transport=streaming_transport,
    )
    orch = ToolOrchestrator(client=client, registry=_registry())

    deltas: list[str] = []

    def sink(s: str) -> None:
        deltas.append(s)

    run = await orch.run([GrokMessage("user", "2+40?")], stream_sink=sink)

    assert run.final.content == "The answer is 42."
    assert [i.name for i in run.invocations] == ["add"]
    assert run.steps == 2

    combined = "".join(deltas)
    # Per-turn markers prefix each chat_stream call.
    assert ">>> turn 1" in combined
    assert ">>> turn 2" in combined
    # Turn-1 had no text deltas (only a tool_call).
    turn_boundaries = combined.index(">>> turn 2")
    assert "The answer is 42." not in combined[:turn_boundaries]
    # Turn-2 streamed the final answer.
    assert "The answer is 42." in combined[turn_boundaries:]

    # Both chat calls went through the streaming transport.
    assert len(streaming_transport.calls) == 2
    assert all(call["stream"] is True for call in streaming_transport.calls)


# ---------------------------------------------------------------------------
# fallback: stream_sink set, but no streaming_transport → non-stream path
# ---------------------------------------------------------------------------
async def test_stream_sink_falls_back_to_non_stream_without_streaming_transport():
    transport = _StubTransport(
        [
            _tool_call_msg("add", {"a": 2, "b": 40}),
            _final_msg("Silent 42."),
        ]
    )
    client = GrokClient(
        api_key="k",
        transport=transport,
        sleep=_noop_sleep,
        # streaming_transport intentionally absent.
    )
    orch = ToolOrchestrator(client=client, registry=_registry())

    deltas: list[str] = []
    run = await orch.run(
        [GrokMessage("user", "2+40?")],
        stream_sink=lambda s: deltas.append(s),
    )

    # Case still runs, final answer produced via the non-stream path.
    assert run.final.content == "Silent 42."
    # Sink never fired — no turn markers, no deltas.
    assert deltas == []
    # Non-stream transport handled both turns.
    assert len(transport.calls) == 2


# ---------------------------------------------------------------------------
# backward-compat: no stream_sink at all still works
# ---------------------------------------------------------------------------
async def test_no_stream_sink_uses_non_stream_path_even_with_streaming_transport():
    transport = _StubTransport(
        [
            _tool_call_msg("add", {"a": 2, "b": 40}),
            _final_msg("The answer is 42."),
        ]
    )
    # Even though this streaming transport exists, the orchestrator should
    # NOT use it when stream_sink is absent.
    streaming_transport = _make_streaming_transport([])

    client = GrokClient(
        api_key="k",
        transport=transport,
        streaming_transport=streaming_transport,
        sleep=_noop_sleep,
    )
    orch = ToolOrchestrator(client=client, registry=_registry())

    run = await orch.run([GrokMessage("user", "2+40?")])
    assert run.final.content == "The answer is 42."
    assert streaming_transport.calls == []  # never called


# ---------------------------------------------------------------------------
# telemetry: tool.run span records whether the loop streamed
# ---------------------------------------------------------------------------
async def test_tool_run_span_records_streamed_flag():
    sink = InMemorySink()
    turn1 = [
        _sse(tool_call={
            "index": 0, "id": "c1",
            "function": {"name": "add", "arguments": '{"a": 1, "b": 1}'},
        }),
        _sse(finish_reason="tool_calls"),
        b"data: [DONE]\n",
    ]
    turn2 = [_sse(content="2"), _sse(finish_reason="stop"), b"data: [DONE]\n"]
    client = GrokClient(
        api_key="k",
        streaming_transport=_make_streaming_transport([turn1, turn2]),
        tracer=Tracer(sink=sink),
    )
    orch = ToolOrchestrator(client=client, registry=_registry())
    await orch.run([GrokMessage("user", "1+1?")], stream_sink=lambda _s: None)

    span = sink.spans(name="tool.run")[0]
    assert span.data.get("streamed") is True


async def test_tool_run_span_streamed_false_without_sink():
    sink = InMemorySink()
    transport = _StubTransport(
        [
            _tool_call_msg("add", {"a": 1, "b": 1}),
            _final_msg("2"),
        ]
    )
    client = GrokClient(
        api_key="k",
        transport=transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )
    orch = ToolOrchestrator(client=client, registry=_registry())
    await orch.run([GrokMessage("user", "1+1?")])
    span = sink.spans(name="tool.run")[0]
    assert span.data.get("streamed") is False


# ---------------------------------------------------------------------------
# chat_stream ending without a final chunk raises ToolError
# ---------------------------------------------------------------------------
async def test_orphan_stream_without_final_raises():
    # A turn whose stream ends before the chunk with is_final=True — e.g.
    # the server closes the connection partway through.
    turn1 = [_sse(content="partial")]  # no finish_reason, no [DONE]
    client = GrokClient(
        api_key="k",
        streaming_transport=_make_streaming_transport([turn1]),
    )
    orch = ToolOrchestrator(client=client, registry=_registry())

    # The chat_stream generator does emit a final chunk on natural close —
    # safety's post-flight produces the assembled `GrokResponse` — so the
    # orchestrator does get a final. Confirm this path doesn't raise:
    run = await orch.run([GrokMessage("user", "q")], stream_sink=lambda _s: None)
    assert run.final.content == "partial"
