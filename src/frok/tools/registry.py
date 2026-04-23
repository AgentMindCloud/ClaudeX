"""Tool registry: declare tools, dispatch calls, emit xAI/OpenAI specs."""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable

from .schema import SchemaError, infer_schema, validate

ToolHandler = Callable[..., Any]


class ToolError(RuntimeError):
    """Raised on registry lookup / dispatch errors."""


class ToolArgumentError(ToolError):
    """Raised when a model's tool-call arguments fail schema validation."""


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler
    dry_run_handler: ToolHandler | None = None
    side_effects: bool = True

    def to_spec(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def tool(
    _fn: ToolHandler | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    parameters: dict[str, Any] | None = None,
    dry_run_handler: ToolHandler | None = None,
    side_effects: bool = True,
) -> Any:
    """Decorator turning a function into a `Tool`.

    Usage::

        @tool
        async def search(query: str, limit: int = 5) -> str: ...

        @tool(name="send", description="Send a message")
        async def send_message(channel: str, body: str) -> dict: ...
    """

    def wrap(fn: ToolHandler) -> Tool:
        return Tool(
            name=name or fn.__name__,
            description=description or _docstring_summary(fn),
            parameters=parameters if parameters is not None else infer_schema(fn),
            handler=fn,
            dry_run_handler=dry_run_handler,
            side_effects=side_effects,
        )

    if _fn is not None:  # used as plain @tool without parentheses
        return wrap(_fn)
    return wrap


def _docstring_summary(fn: ToolHandler) -> str:
    doc = (fn.__doc__ or "").strip()
    if not doc:
        return fn.__name__
    return doc.split("\n", 1)[0].strip()


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def add(self, *items: Tool) -> "ToolRegistry":
        for t in items:
            if t.name in self.tools:
                raise ToolError(f"duplicate tool name: {t.name}")
            self.tools[t.name] = t
        return self

    def __contains__(self, name: str) -> bool:
        return name in self.tools

    def names(self) -> list[str]:
        return list(self.tools)

    def spec(self) -> list[dict[str, Any]]:
        return [t.to_spec() for t in self.tools.values()]

    async def dispatch(
        self,
        name: str,
        arguments_json: str | dict[str, Any],
        *,
        dry_run: bool = False,
    ) -> str:
        tool_obj = self.tools.get(name)
        if tool_obj is None:
            raise ToolError(f"unknown tool: {name}")

        args = _parse_arguments(arguments_json)
        try:
            validate(args, tool_obj.parameters, path=f"args<{name}>")
        except SchemaError as exc:
            raise ToolArgumentError(str(exc)) from exc

        handler: ToolHandler
        if dry_run and tool_obj.side_effects:
            if tool_obj.dry_run_handler is not None:
                handler = tool_obj.dry_run_handler
            else:
                return _format_dry_run(name, args)
        else:
            handler = tool_obj.handler

        result = handler(**args)
        if inspect.isawaitable(result):
            result = await result  # type: ignore[assignment]
        return _stringify(result)


def _parse_arguments(raw: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ToolArgumentError(f"arguments are not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ToolArgumentError(
            f"arguments must decode to an object, got {type(parsed).__name__}"
        )
    return parsed


def _format_dry_run(name: str, args: dict[str, Any]) -> str:
    return f"[dry-run] {name}({json.dumps(args, sort_keys=True)})"


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    try:
        return json.dumps(value, default=str)
    except TypeError:
        return str(value)


__all__ = [
    "Tool",
    "ToolArgumentError",
    "ToolError",
    "ToolHandler",
    "ToolRegistry",
    "tool",
]
