import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.tools import (
    ToolError,
    ToolOrchestrator,
    ToolRegistry,
    tool,
)


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


def _final(text):
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


def _tool_call(calls):
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
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 4, "completion_tokens": 2},
        },
    )


def _client(transport):
    return GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)


# ---------------------------------------------------------------------------
# happy path: single tool call then final answer
# ---------------------------------------------------------------------------
async def test_single_tool_call_round_trip():
    @tool
    def add(a: int, b: int) -> int:
        """Return a+b."""
        return a + b

    reg = ToolRegistry().add(add)
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "add", "args": {"a": 2, "b": 40}}]),
        _final("The answer is 42."),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    run = await orch.run([GrokMessage("user", "what is 2 + 40?")])

    assert run.final.content == "The answer is 42."
    assert run.steps == 2
    assert [i.name for i in run.invocations] == ["add"]
    assert run.invocations[0].result == "42"

    # Second request must echo the assistant tool_calls + tool result.
    second = transport.calls[1]["messages"]
    roles = [m["role"] for m in second]
    assert roles == ["user", "assistant", "tool"]
    assert second[1]["tool_calls"][0]["function"]["name"] == "add"
    assert second[2]["tool_call_id"] == "c1"
    assert second[2]["content"] == "42"


async def test_tools_spec_is_sent_on_every_step():
    @tool
    def ping() -> str:
        return "pong"

    reg = ToolRegistry().add(ping)
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "ping", "args": {}}]),
        _final("done"),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    await orch.run([GrokMessage("user", "go")])
    for call in transport.calls:
        assert call.get("tools")
        assert call["tools"][0]["function"]["name"] == "ping"
        assert call["tool_choice"] == "auto"


# ---------------------------------------------------------------------------
# parallel calls in a single turn
# ---------------------------------------------------------------------------
async def test_parallel_tool_calls_in_order():
    order = []

    @tool
    async def step(name: str) -> str:
        order.append(name)
        return f"did:{name}"

    reg = ToolRegistry().add(step)
    transport = StubTransport([
        _tool_call([
            {"id": "c1", "name": "step", "args": {"name": "first"}},
            {"id": "c2", "name": "step", "args": {"name": "second"}},
        ]),
        _final("ok"),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    run = await orch.run([GrokMessage("user", "go")])
    assert order == ["first", "second"]
    assert [i.result for i in run.invocations] == ["did:first", "did:second"]


# ---------------------------------------------------------------------------
# errors: bad args, bad tool name, handler raising — all surfaced to model
# ---------------------------------------------------------------------------
async def test_bad_arguments_are_reported_back_to_model():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    reg = ToolRegistry().add(add)
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "add", "args": {"a": "oops", "b": 2}}]),
        _final("caller bug noted"),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    run = await orch.run([GrokMessage("user", "go")])
    inv = run.invocations[0]
    assert inv.error is not None
    assert "expected integer" in inv.result
    assert run.final.content == "caller bug noted"


async def test_handler_exception_is_surfaced_not_raised():
    @tool
    def boom() -> str:
        raise RuntimeError("kaboom")

    reg = ToolRegistry().add(boom)
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "boom", "args": {}}]),
        _final("recovered"),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    run = await orch.run([GrokMessage("user", "go")])
    assert "RuntimeError: kaboom" in run.invocations[0].result
    assert run.final.content == "recovered"


async def test_unknown_tool_is_surfaced():
    reg = ToolRegistry()
    transport = StubTransport([
        _tool_call([{"id": "c1", "name": "missing", "args": {}}]),
        _final("ok"),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    run = await orch.run([GrokMessage("user", "go")])
    assert "unknown tool" in run.invocations[0].result


# ---------------------------------------------------------------------------
# dry-run: side-effectful tools are stubbed, read-only tools execute
# ---------------------------------------------------------------------------
async def test_dry_run_stubs_side_effects():
    executed = []

    @tool(side_effects=True)
    def publish(text: str) -> str:
        executed.append(text)
        return "posted"

    @tool(side_effects=False)
    def read(key: str) -> str:
        return f"val:{key}"

    reg = ToolRegistry().add(publish, read)
    transport = StubTransport([
        _tool_call([
            {"id": "c1", "name": "publish", "args": {"text": "hello world"}},
            {"id": "c2", "name": "read", "args": {"key": "x"}},
        ]),
        _final("done"),
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg, dry_run=True)
    run = await orch.run([GrokMessage("user", "go")])
    assert executed == []  # publish never ran
    assert "[dry-run]" in run.invocations[0].result
    assert run.invocations[1].result == "val:x"


# ---------------------------------------------------------------------------
# loop guard
# ---------------------------------------------------------------------------
async def test_loop_exits_on_max_steps():
    @tool
    def ping() -> str:
        return "pong"

    reg = ToolRegistry().add(ping)
    # Model keeps calling the tool forever.
    transport = StubTransport([
        _tool_call([{"id": f"c{i}", "name": "ping", "args": {}}]) for i in range(10)
    ])
    orch = ToolOrchestrator(client=_client(transport), registry=reg, max_steps=3)
    with pytest.raises(ToolError, match="max_steps=3"):
        await orch.run([GrokMessage("user", "loop")])


async def test_system_prompt_is_prepended_once():
    @tool
    def ping() -> str:
        return "pong"

    reg = ToolRegistry().add(ping)
    transport = StubTransport([_final("hi")])
    orch = ToolOrchestrator(client=_client(transport), registry=reg)
    await orch.run(
        [GrokMessage("user", "hello")],
        system="You are Frok, a truth-seeking assistant.",
    )
    sent = transport.calls[0]["messages"]
    assert sent[0]["role"] == "system"
    assert "truth-seeking" in sent[0]["content"]
    assert sent[1]["role"] == "user"
