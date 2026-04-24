"""Tests for the `tool_choice` plumbing: GrokClient, config, EvalCase."""

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.config import (
    ClientConfig,
    FrokConfig,
    build_client,
    load_config,
)
from frok.config.render import to_env, to_json, to_toml
from frok.evals import AnswerContains, EvalCase, EvalRunner, ToolCalled
from frok.telemetry import Tracer
from frok.tools import ToolOrchestrator, ToolRegistry, tool


# ---------------------------------------------------------------------------
# GrokClient.chat + chat_stream: tool_choice precedence
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


def _ok(text="ok"):
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
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        },
    )


async def test_chat_omits_tool_choice_by_default():
    transport = _StubTransport([_ok()])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    await client.chat([GrokMessage("user", "hi")])
    assert "tool_choice" not in transport.calls[0]


async def test_chat_explicit_tool_choice_passes_through():
    transport = _StubTransport([_ok()])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    await client.chat([GrokMessage("user", "hi")], tool_choice="none")
    assert transport.calls[0]["tool_choice"] == "none"


async def test_chat_client_default_applies_when_kwarg_absent():
    transport = _StubTransport([_ok()])
    client = GrokClient(
        api_key="k",
        transport=transport,
        sleep=_noop_sleep,
        tool_choice="required",
    )
    await client.chat([GrokMessage("user", "hi")])
    assert transport.calls[0]["tool_choice"] == "required"


async def test_chat_explicit_kwarg_wins_over_client_default():
    transport = _StubTransport([_ok()])
    client = GrokClient(
        api_key="k",
        transport=transport,
        sleep=_noop_sleep,
        tool_choice="none",
    )
    await client.chat(
        [GrokMessage("user", "hi")],
        tool_choice={"type": "function", "function": {"name": "add"}},
    )
    assert transport.calls[0]["tool_choice"] == {
        "type": "function",
        "function": {"name": "add"},
    }


# ---------------------------------------------------------------------------
# chat_stream honours tool_choice the same way
# ---------------------------------------------------------------------------
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


async def test_chat_stream_passes_tool_choice_kwarg():
    transport = _stream_transport([
        _sse(content="hi"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ])
    client = GrokClient(api_key="k", streaming_transport=transport)
    async for _ in client.chat_stream(
        [GrokMessage("user", "hi")], tool_choice="none"
    ):
        pass
    assert transport.calls[0]["tool_choice"] == "none"


async def test_chat_stream_honours_client_default_tool_choice():
    transport = _stream_transport([
        _sse(content="hi"),
        _sse(finish_reason="stop"),
        b"data: [DONE]\n",
    ])
    client = GrokClient(
        api_key="k", streaming_transport=transport, tool_choice="required"
    )
    async for _ in client.chat_stream([GrokMessage("user", "hi")]):
        pass
    assert transport.calls[0]["tool_choice"] == "required"


# ---------------------------------------------------------------------------
# ToolOrchestrator: passes its configured tool_choice to each turn
# ---------------------------------------------------------------------------
async def test_orchestrator_forwards_tool_choice_on_every_turn():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    def _tool_call_response(call_id):
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
                                        "name": "add",
                                        "arguments": '{"a":2,"b":40}',
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

    transport = _StubTransport([_tool_call_response("c1"), _ok("42")])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    orch = ToolOrchestrator(
        client=client,
        registry=ToolRegistry().add(add),
        tool_choice="required",
    )
    await orch.run([GrokMessage("user", "2+40?")])

    # Both request bodies carry tool_choice=required.
    assert [c["tool_choice"] for c in transport.calls] == ["required", "required"]


async def test_orchestrator_default_tool_choice_is_auto():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    transport = _StubTransport([_ok("42")])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    orch = ToolOrchestrator(client=client, registry=ToolRegistry().add(add))
    await orch.run([GrokMessage("user", "2+40?")])
    assert transport.calls[0]["tool_choice"] == "auto"


# ---------------------------------------------------------------------------
# EvalCase.tool_choice flows through the runner to the orchestrator
# ---------------------------------------------------------------------------
async def test_eval_case_tool_choice_reaches_orchestrator():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    transport = _StubTransport([_ok("42")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="pinned",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        tool_choice="none",
        scorers=[AnswerContains("42")],
    )
    runner = EvalRunner(client_factory=factory)
    await runner.run_case(case)
    assert transport.calls[0]["tool_choice"] == "none"


async def test_eval_case_tool_choice_accepts_specific_function_dict():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    transport = _StubTransport([_ok("42")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    pinned = {"type": "function", "function": {"name": "add"}}
    case = EvalCase(
        name="pinned-fn",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        tool_choice=pinned,
        scorers=[AnswerContains("42")],
    )
    await EvalRunner(client_factory=factory).run_case(case)
    assert transport.calls[0]["tool_choice"] == pinned


# ---------------------------------------------------------------------------
# Config: ClientConfig.tool_choice through env, file, and builder
# ---------------------------------------------------------------------------
def test_client_config_tool_choice_defaults_to_none():
    cfg = ClientConfig()
    assert cfg.tool_choice is None


def test_config_env_sets_string_tool_choice():
    cfg = load_config(env={"FROK_CLIENT_TOOL_CHOICE": "required"})
    assert cfg.client.tool_choice == "required"


def test_config_file_accepts_dict_tool_choice(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(
        json.dumps({"client": {"tool_choice": {
            "type": "function",
            "function": {"name": "add"},
        }}}),
        encoding="utf-8",
    )
    cfg = load_config(file=path)
    assert cfg.client.tool_choice == {
        "type": "function",
        "function": {"name": "add"},
    }


def test_build_client_propagates_tool_choice():
    cfg = load_config(
        cli={"client.api_key": "k", "client.tool_choice": "required"}
    )
    client = build_client(cfg)
    assert client.tool_choice == "required"


def test_build_client_tool_choice_none_by_default():
    cfg = load_config(cli={"client.api_key": "k"})
    client = build_client(cfg)
    assert client.tool_choice is None


# ---------------------------------------------------------------------------
# render: tool_choice survives TOML / JSON / env serialisation
# ---------------------------------------------------------------------------
def test_render_json_includes_string_tool_choice():
    cfg = load_config(cli={"client.tool_choice": "required"})
    data = json.loads(to_json(cfg))
    assert data["client"]["tool_choice"] == "required"


def test_render_json_includes_dict_tool_choice():
    pinned = {"type": "function", "function": {"name": "add"}}
    cfg = load_config(cli={"client.tool_choice": pinned})
    data = json.loads(to_json(cfg))
    assert data["client"]["tool_choice"] == pinned


def test_render_toml_inline_table_for_dict_tool_choice():
    pinned = {"type": "function", "function": {"name": "add"}}
    cfg = load_config(cli={"client.tool_choice": pinned})
    text = to_toml(cfg)
    # Uses inline-table syntax for the dict.
    assert "tool_choice = {" in text
    # tomllib can round-trip it.
    import tomllib

    parsed = tomllib.loads(text)
    assert parsed["client"]["tool_choice"] == pinned


def test_render_env_json_encodes_dict_tool_choice():
    pinned = {"type": "function", "function": {"name": "add"}}
    cfg = load_config(cli={"client.tool_choice": pinned})
    text = to_env(cfg)
    # Shell-injectable JSON body.
    line = next(
        line for line in text.splitlines() if line.startswith("FROK_CLIENT_TOOL_CHOICE=")
    )
    payload = line.split("=", 1)[1]
    assert json.loads(payload) == pinned


def test_render_env_passes_string_tool_choice_through():
    cfg = load_config(cli={"client.tool_choice": "required"})
    assert "FROK_CLIENT_TOOL_CHOICE=required" in to_env(cfg)


def test_render_toml_comments_out_unset_tool_choice():
    cfg = load_config()  # default None
    text = to_toml(cfg)
    assert "# tool_choice  (unset)" in text
