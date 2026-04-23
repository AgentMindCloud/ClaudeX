import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.memory import HashEmbedder, MemoryStore
from frok.telemetry import InMemorySink, SPAN_END, Tracer
from frok.tools import ToolOrchestrator, ToolRegistry, tool


@dataclass
class StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _ok(content, *, prompt=5, completion=3):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


def _tool_call(calls, finish="tool_calls"):
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
                                "id": c["id"],
                                "type": "function",
                                "function": {
                                    "name": c["name"],
                                    "arguments": json.dumps(c["args"]),
                                },
                            }
                            for c in calls
                        ],
                    },
                    "finish_reason": finish,
                }
            ],
            "usage": {"prompt_tokens": 3, "completion_tokens": 1},
        },
    )


# ---------------------------------------------------------------------------
# GrokClient emits a grok.chat span with token + safety attrs
# ---------------------------------------------------------------------------
async def test_grok_client_emits_chat_span():
    sink = InMemorySink()
    client = GrokClient(
        api_key="k",
        transport=StubTransport([_ok("hi", prompt=11, completion=7)]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )
    await client.chat([GrokMessage("user", "hello")])
    spans = sink.spans(name="grok.chat")
    assert len(spans) == 1
    d = spans[0].data
    assert d["model"] == "grok-4"
    assert d["message_count"] == 1
    assert d["prompt_tokens"] == 11
    assert d["completion_tokens"] == 7
    assert d["total_tokens"] == 18
    assert d["tool_calls"] == 0
    assert d["finish_reason"] == "stop"
    assert spans[0].error is None


async def test_grok_client_span_records_safety_block():
    sink = InMemorySink()
    client = GrokClient(
        api_key="k",
        transport=StubTransport([]),  # never hit
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )
    with pytest.raises(Exception):
        await client.chat([GrokMessage("user", "I can guarantee I am sentient.")])
    spans = sink.spans(name="grok.chat")
    assert len(spans) == 1
    assert spans[0].error is not None
    assert spans[0].data.get("safety_blocked") == "prompt"


# ---------------------------------------------------------------------------
# MemoryStore emits remember / recall / forget spans
# ---------------------------------------------------------------------------
async def test_memory_store_emits_spans(tmp_path):
    sink = InMemorySink()
    store = MemoryStore(
        tmp_path / "m.db",
        HashEmbedder(dim=64),
        tracer=Tracer(sink=sink),
    )
    try:
        rec = await store.remember("xAI Grok is maximally truthful")
        hits = await store.recall("truth-seeking Grok", k=3)
        await store.forget(rec.id)
    finally:
        store.close()

    names = [e.name for e in sink.spans()]
    assert names == ["memory.remember", "memory.recall", "memory.forget"]

    remember_span = sink.spans(name="memory.remember")[0]
    assert remember_span.data["kind"] == "episode"
    assert remember_span.data["memory_id"] == rec.id

    recall_span = sink.spans(name="memory.recall")[0]
    assert recall_span.data["k"] == 3
    assert recall_span.data["hit_count"] == len(hits)
    assert recall_span.data["candidates"] == 1

    forget_span = sink.spans(name="memory.forget")[0]
    assert forget_span.data["deleted"] is True


# ---------------------------------------------------------------------------
# ToolOrchestrator run + invoke spans nest correctly, share a trace_id
# ---------------------------------------------------------------------------
async def test_tool_orchestrator_emits_nested_spans():
    sink = InMemorySink()
    tracer = Tracer(sink=sink)

    @tool
    def add(a: int, b: int) -> int:
        return a + b

    reg = ToolRegistry().add(add)
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "add", "args": {"a": 2, "b": 40}}]),
        _ok("42"),
    ])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep, tracer=tracer)
    orch = ToolOrchestrator(client=client, registry=reg)

    await orch.run([GrokMessage("user", "do it")])

    span_names = [e.name for e in sink.spans()]
    # run, invoke, and two chat spans (one per model turn) all present
    assert "tool.run" in span_names
    assert "tool.invoke" in span_names
    assert span_names.count("grok.chat") == 2

    run_span = sink.spans(name="tool.run")[0]
    invoke_span = sink.spans(name="tool.invoke")[0]
    first_chat = sink.spans(name="grok.chat")[0]

    # All spans share one trace_id…
    assert run_span.trace_id == invoke_span.trace_id == first_chat.trace_id
    # …and run is the root; invoke + chat hang off of it.
    assert run_span.parent_span_id is None
    assert invoke_span.parent_span_id == run_span.span_id
    assert first_chat.parent_span_id == run_span.span_id

    assert run_span.data["invocations"] == 1
    assert run_span.data["steps"] == 2
    assert invoke_span.data["tool"] == "add"
    assert invoke_span.data["result_len"] == len("42")


async def test_tool_orchestrator_span_records_handler_error():
    sink = InMemorySink()
    tracer = Tracer(sink=sink)

    @tool
    def boom() -> str:
        raise RuntimeError("nope")

    reg = ToolRegistry().add(boom)
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "boom", "args": {}}]),
        _ok("recovered"),
    ])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep, tracer=tracer)
    orch = ToolOrchestrator(client=client, registry=reg)

    await orch.run([GrokMessage("user", "go")])
    invoke = sink.spans(name="tool.invoke")[0]
    assert invoke.data["error_kind"] == "handler:RuntimeError"
    # Handler failure is recoverable → run span itself has no error.
    assert sink.spans(name="tool.run")[0].error is None
