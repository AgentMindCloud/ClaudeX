"""Tests for ``GrokClient.chat_stream`` + SSE + tool-call assembly."""

import json
from typing import AsyncIterator

import pytest

from frok.clients import (
    GrokClient,
    GrokError,
    GrokMessage,
    HttpError,
    StreamChunk,
    ToolCall,
)
from frok.clients.grok import _iter_sse_events, _merge_tool_call_delta, _SSE_DONE
from frok.safety import SafetyRuleSet
from frok.telemetry import InMemorySink, Tracer


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _delta(content: str | None = None, tool_calls=None, finish_reason=None) -> bytes:
    choice: dict = {"delta": {}, "index": 0}
    if content is not None:
        choice["delta"]["content"] = content
    if tool_calls is not None:
        choice["delta"]["tool_calls"] = tool_calls
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    payload = {"choices": [choice]}
    return f"data: {json.dumps(payload)}\n".encode("utf-8")


def _done() -> bytes:
    return b"data: [DONE]\n"


def _stub_stream(lines: list[bytes], *, status: int = 200):
    async def transport(*, method, url, headers, body, timeout):
        async def _iter() -> AsyncIterator[bytes]:
            for line in lines:
                yield line

        return status, {}, _iter()

    transport.calls: list = []  # type: ignore[attr-defined]
    return transport


def _stub_stream_capturing(lines, *, status=200):
    """Stub streaming transport that records the POST body for assertions."""
    calls: list = []

    async def transport(*, method, url, headers, body, timeout):
        calls.append(
            {
                "url": url,
                "method": method,
                "body": json.loads(body.decode("utf-8")),
                "headers": dict(headers),
            }
        )

        async def _iter() -> AsyncIterator[bytes]:
            for line in lines:
                yield line

        return status, {}, _iter()

    transport.calls = calls  # type: ignore[attr-defined]
    return transport


# ---------------------------------------------------------------------------
# _iter_sse_events helper
# ---------------------------------------------------------------------------
def test_iter_sse_events_yields_parsed_json():
    line = b'data: {"choices": [{"delta": {"content": "hi"}}]}\n'
    events = list(_iter_sse_events(line))
    assert len(events) == 1
    assert events[0]["choices"][0]["delta"]["content"] == "hi"


def test_iter_sse_events_done_sentinel():
    events = list(_iter_sse_events(b"data: [DONE]\n"))
    assert events == [_SSE_DONE]


def test_iter_sse_events_ignores_non_data_and_blanks():
    assert list(_iter_sse_events(b"\n")) == []
    assert list(_iter_sse_events(b": keep-alive\n")) == []


def test_iter_sse_events_swallows_malformed_json():
    # A stray malformed chunk shouldn't poison the whole stream.
    assert list(_iter_sse_events(b"data: {not json}\n")) == []


# ---------------------------------------------------------------------------
# _merge_tool_call_delta helper
# ---------------------------------------------------------------------------
def test_merge_tool_call_delta_assembles_fragments():
    accum: list[dict] = []
    _merge_tool_call_delta(accum, {
        "index": 0,
        "id": "call_1",
        "function": {"name": "ad"},
    })
    _merge_tool_call_delta(accum, {
        "index": 0,
        "function": {"name": "d", "arguments": '{"a":'},
    })
    _merge_tool_call_delta(accum, {
        "index": 0,
        "function": {"arguments": '2}'},
    })
    assert accum == [{"id": "call_1", "name": "add", "arguments": '{"a":2}'}]


def test_merge_tool_call_delta_grows_list_for_new_index():
    accum: list[dict] = []
    _merge_tool_call_delta(accum, {"index": 2, "function": {"name": "x"}})
    assert len(accum) == 3
    assert accum[2]["name"] == "x"
    assert accum[0]["name"] == "" and accum[1]["name"] == ""


# ---------------------------------------------------------------------------
# chat_stream: basic text streaming
# ---------------------------------------------------------------------------
async def test_chat_stream_yields_deltas_then_final():
    transport = _stub_stream_capturing(
        [
            _delta("Hello"),
            _delta(", "),
            _delta("world!"),
            _delta(finish_reason="stop"),
            _done(),
        ]
    )
    client = GrokClient(
        api_key="k",
        transport=None,
        streaming_transport=transport,
    )
    chunks = []
    async for chunk in client.chat_stream([GrokMessage("user", "greet me")]):
        chunks.append(chunk)

    deltas = [c.delta for c in chunks if not c.is_final]
    assert deltas == ["Hello", ", ", "world!"]
    final = chunks[-1]
    assert final.is_final
    assert final.delta == ""
    assert final.finish_reason == "stop"
    assert final.response is not None
    assert final.response.content == "Hello, world!"
    # Request carried stream=True.
    assert transport.calls[0]["body"]["stream"] is True


async def test_chat_stream_request_includes_sse_accept_header():
    transport = _stub_stream_capturing([_delta("ok"), _done()])
    client = GrokClient(
        api_key="k",
        streaming_transport=transport,
    )
    async for _ in client.chat_stream([GrokMessage("user", "ping")]):
        pass
    assert transport.calls[0]["headers"]["Accept"] == "text/event-stream"
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer k"


async def test_chat_stream_final_arrives_even_without_done_sentinel():
    # Some servers end the stream by closing the connection; no [DONE].
    transport = _stub_stream(
        [_delta("the "), _delta("end"), _delta(finish_reason="stop")]
    )
    client = GrokClient(api_key="k", streaming_transport=transport)
    chunks = []
    async for chunk in client.chat_stream([GrokMessage("user", "q")]):
        chunks.append(chunk)
    assert chunks[-1].is_final
    assert chunks[-1].response.content == "the end"


# ---------------------------------------------------------------------------
# chat_stream: safety
# ---------------------------------------------------------------------------
async def test_chat_stream_preflight_blocks_unsafe_prompt():
    transport = _stub_stream([_delta("never"), _done()])
    client = GrokClient(api_key="k", streaming_transport=transport)
    agen = client.chat_stream([GrokMessage("user", "I can guarantee I am sentient.")])
    with pytest.raises(GrokError, match="prompt blocked"):
        async for _ in agen:
            pass


async def test_chat_stream_rewrites_prompt_pii_before_send():
    transport = _stub_stream_capturing([_delta("ok"), _done()])
    client = GrokClient(api_key="k", streaming_transport=transport)
    async for _ in client.chat_stream(
        [GrokMessage("user", "contact alice@example.com")]
    ):
        pass
    sent = transport.calls[0]["body"]["messages"][0]["content"]
    assert "alice@example.com" not in sent
    assert "[REDACTED_EMAIL]" in sent


async def test_chat_stream_postflight_blocks_unsafe_accumulated_content():
    transport = _stub_stream(
        [
            _delta("I can "),
            _delta("guarantee "),
            _delta("this answer."),
            _done(),
        ]
    )
    client = GrokClient(api_key="k", streaming_transport=transport)
    collected: list[str] = []
    with pytest.raises(GrokError, match="response blocked"):
        async for chunk in client.chat_stream([GrokMessage("user", "hi")]):
            collected.append(chunk.delta)
    # Deltas were yielded live — the block fires AFTER the stream completes.
    assert "".join(collected) == "I can guarantee this answer."


async def test_chat_stream_empty_ruleset_skips_safety():
    transport = _stub_stream(
        [_delta("I can guarantee anything."), _done()]
    )
    client = GrokClient(
        api_key="k",
        streaming_transport=transport,
        safety=SafetyRuleSet(rules=()),
    )
    chunks = [c async for c in client.chat_stream([GrokMessage("user", "hi")])]
    assert chunks[-1].response.content == "I can guarantee anything."


# ---------------------------------------------------------------------------
# chat_stream: error paths
# ---------------------------------------------------------------------------
async def test_chat_stream_requires_streaming_transport():
    client = GrokClient(api_key="k")
    with pytest.raises(GrokError, match="no streaming_transport"):
        async for _ in client.chat_stream([GrokMessage("user", "hi")]):
            pass


async def test_chat_stream_requires_non_empty_messages():
    client = GrokClient(api_key="k", streaming_transport=_stub_stream([]))
    with pytest.raises(GrokError, match="must not be empty"):
        async for _ in client.chat_stream([]):
            pass


async def test_chat_stream_raises_on_non_2xx_status():
    transport = _stub_stream(
        [b'{"error": "nope"}'],
        status=401,
    )
    client = GrokClient(api_key="k", streaming_transport=transport)
    with pytest.raises(HttpError) as exc:
        async for _ in client.chat_stream([GrokMessage("user", "hi")]):
            pass
    assert exc.value.status == 401


# ---------------------------------------------------------------------------
# chat_stream: tool-call streaming
# ---------------------------------------------------------------------------
async def test_chat_stream_assembles_streamed_tool_calls():
    transport = _stub_stream(
        [
            _delta(tool_calls=[{"index": 0, "id": "c1", "function": {"name": "ad"}}]),
            _delta(tool_calls=[{"index": 0, "function": {"name": "d"}}]),
            _delta(tool_calls=[{
                "index": 0,
                "function": {"arguments": '{"a": '},
            }]),
            _delta(tool_calls=[{"index": 0, "function": {"arguments": "42}"}}]),
            _delta(finish_reason="tool_calls"),
            _done(),
        ]
    )
    client = GrokClient(api_key="k", streaming_transport=transport)
    final: StreamChunk | None = None
    async for chunk in client.chat_stream([GrokMessage("user", "go")]):
        if chunk.is_final:
            final = chunk
    assert final is not None
    assert final.finish_reason == "tool_calls"
    assert final.tool_calls == (ToolCall(id="c1", name="add", arguments='{"a": 42}'),)
    assert final.response.tool_calls == final.tool_calls


# ---------------------------------------------------------------------------
# chat_stream: telemetry
# ---------------------------------------------------------------------------
async def test_chat_stream_emits_span_with_expected_attrs():
    sink = InMemorySink()
    transport = _stub_stream([_delta("Hello"), _delta(" world"), _done()])
    client = GrokClient(
        api_key="k",
        streaming_transport=transport,
        tracer=Tracer(sink=sink),
    )
    async for _ in client.chat_stream([GrokMessage("user", "q")]):
        pass
    spans = sink.spans(name="grok.chat_stream")
    assert len(spans) == 1
    data = spans[0].data
    assert data["model"] == "grok-4"
    assert data["message_count"] == 1
    assert data["chunks"] == 2
    assert data["content_chars"] == len("Hello world")


async def test_chat_stream_span_records_safety_block():
    sink = InMemorySink()
    transport = _stub_stream([])  # never hit
    client = GrokClient(
        api_key="k",
        streaming_transport=transport,
        tracer=Tracer(sink=sink),
    )
    with pytest.raises(GrokError):
        async for _ in client.chat_stream(
            [GrokMessage("user", "I can guarantee anything.")]
        ):
            pass
    span = sink.spans(name="grok.chat_stream")[0]
    assert span.data.get("safety_blocked") == "prompt"
    assert span.error is not None
