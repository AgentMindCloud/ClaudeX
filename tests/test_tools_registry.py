import json

import pytest

from frok.tools import (
    Tool,
    ToolArgumentError,
    ToolError,
    ToolRegistry,
    tool,
)


def test_tool_decorator_infers_schema_and_description():
    @tool
    async def search(query: str, limit: int = 5) -> str:
        """Search the web for a query."""
        return f"{query}:{limit}"

    assert isinstance(search, Tool)
    assert search.name == "search"
    assert search.description == "Search the web for a query."
    assert search.parameters["required"] == ["query"]
    assert search.parameters["properties"]["query"] == {"type": "string"}


def test_tool_decorator_overrides_fields():
    @tool(name="send", description="Send a message", side_effects=True)
    def send_message(channel: str, body: str) -> dict:
        return {"channel": channel, "body": body}

    assert send_message.name == "send"
    assert send_message.description == "Send a message"


def test_registry_spec_and_duplicate_guard():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    reg = ToolRegistry().add(add)
    spec = reg.spec()
    assert spec[0]["type"] == "function"
    assert spec[0]["function"]["name"] == "add"
    with pytest.raises(ToolError, match="duplicate"):
        reg.add(add)


async def test_dispatch_validates_and_calls_sync_and_async():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    @tool
    async def ping(msg: str) -> str:
        return f"pong:{msg}"

    reg = ToolRegistry().add(add, ping)
    assert await reg.dispatch("add", {"a": 2, "b": 3}) == "5"
    assert await reg.dispatch("add", '{"a": 2, "b": 3}') == "5"
    assert await reg.dispatch("ping", {"msg": "hi"}) == "pong:hi"


async def test_dispatch_unknown_tool_raises():
    reg = ToolRegistry()
    with pytest.raises(ToolError, match="unknown tool"):
        await reg.dispatch("missing", {})


async def test_dispatch_rejects_bad_types():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    reg = ToolRegistry().add(add)
    with pytest.raises(ToolArgumentError, match="expected integer"):
        await reg.dispatch("add", {"a": "x", "b": 2})


async def test_dispatch_rejects_missing_required():
    @tool
    def add(a: int, b: int) -> int:
        return a + b

    reg = ToolRegistry().add(add)
    with pytest.raises(ToolArgumentError, match="missing required property 'b'"):
        await reg.dispatch("add", {"a": 1})


async def test_dispatch_rejects_invalid_json_string():
    @tool
    def noop(x: int = 0) -> int:
        return x

    reg = ToolRegistry().add(noop)
    with pytest.raises(ToolArgumentError, match="not valid JSON"):
        await reg.dispatch("noop", "{not json}")


async def test_dry_run_side_effect_tool_returns_stub_without_calling():
    called = []

    @tool(side_effects=True)
    def delete(path: str) -> str:
        called.append(path)
        return "deleted"

    reg = ToolRegistry().add(delete)
    out = await reg.dispatch("delete", {"path": "/tmp/x"}, dry_run=True)
    assert "[dry-run]" in out
    assert "delete" in out
    assert called == []


async def test_dry_run_honours_custom_stub():
    @tool(dry_run_handler=lambda path: f"would delete {path}")
    def delete(path: str) -> str:  # pragma: no cover (not invoked in dry-run)
        raise AssertionError("should not run in dry-run")

    reg = ToolRegistry().add(delete)
    out = await reg.dispatch("delete", {"path": "/tmp/x"}, dry_run=True)
    assert out == "would delete /tmp/x"


async def test_dry_run_passes_through_readonly_tools():
    @tool(side_effects=False)
    def read(path: str) -> str:
        return f"contents of {path}"

    reg = ToolRegistry().add(read)
    out = await reg.dispatch("read", {"path": "/etc/hostname"}, dry_run=True)
    assert out == "contents of /etc/hostname"


async def test_dispatch_stringifies_structured_results():
    @tool
    def stats() -> dict:
        return {"users": 42, "ok": True}

    reg = ToolRegistry().add(stats)
    out = await reg.dispatch("stats", {})
    assert json.loads(out) == {"users": 42, "ok": True}
