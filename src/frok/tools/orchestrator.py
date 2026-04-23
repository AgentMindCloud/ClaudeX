"""Tool-use dispatch loop wrapping `GrokClient.chat`.

Runs until the model returns a plain (non-tool-calling) assistant message
or `max_steps` is hit. On each tool call: validate arguments against the
tool's JSON Schema, invoke the handler (or its dry-run stub), and feed
the result back as a `role="tool"` message. The loop is deliberately
synchronous per-step — parallel tool calls from a single turn are
executed in order to keep ordering deterministic; a future variant can
use `asyncio.gather` once callers need it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Sequence

from ..clients.grok import GrokClient, GrokMessage, GrokResponse, ToolCall
from .registry import ToolArgumentError, ToolError, ToolRegistry


@dataclass
class ToolInvocation:
    call_id: str
    name: str
    arguments: dict[str, Any]
    result: str
    error: str | None = None


@dataclass
class ToolRun:
    final: GrokResponse
    messages: list[GrokMessage]
    invocations: list[ToolInvocation] = field(default_factory=list)
    steps: int = 0


@dataclass
class ToolOrchestrator:
    client: GrokClient
    registry: ToolRegistry
    max_steps: int = 8
    dry_run: bool = False
    tool_choice: str | dict[str, Any] = "auto"
    temperature: float | None = None
    max_tokens: int | None = None

    async def run(
        self,
        messages: Sequence[GrokMessage],
        *,
        system: str | None = None,
    ) -> ToolRun:
        async with self.client.tracer.span(
            "tool.run",
            max_steps=self.max_steps,
            dry_run=self.dry_run,
            tool_count=len(self.registry.tools),
        ) as run_span:
            convo: list[GrokMessage] = []
            if system:
                convo.append(GrokMessage("system", system))
            convo.extend(messages)

            invocations: list[ToolInvocation] = []
            tools_spec = self.registry.spec()
            extra: dict[str, Any] = {}
            if self.tool_choice is not None:
                extra["tool_choice"] = self.tool_choice

            for step in range(1, self.max_steps + 1):
                resp = await self.client.chat(
                    convo,
                    tools=tools_spec,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    extra=extra or None,
                )
                if not resp.has_tool_calls:
                    run_span.set(
                        steps=step,
                        invocations=len(invocations),
                        finish_reason=resp.finish_reason or "",
                    )
                    return ToolRun(
                        final=resp,
                        messages=convo,
                        invocations=invocations,
                        steps=step,
                    )

                assert resp.tool_calls is not None  # for type-checkers
                convo.append(
                    GrokMessage(
                        role="assistant",
                        content=resp.content,
                        tool_calls=resp.tool_calls,
                    )
                )
                for call in resp.tool_calls:
                    inv = await self._invoke(call)
                    invocations.append(inv)
                    convo.append(
                        GrokMessage(
                            role="tool",
                            content=inv.result,
                            tool_call_id=call.id,
                            name=call.name,
                        )
                    )

            run_span.set(
                steps=self.max_steps,
                invocations=len(invocations),
                exhausted=True,
            )
            raise ToolError(
                f"tool loop exceeded max_steps={self.max_steps}; "
                f"last invocations={[i.name for i in invocations[-self.max_steps:]]}"
            )

    async def _invoke(self, call: ToolCall) -> ToolInvocation:
        async with self.client.tracer.span(
            "tool.invoke",
            tool=call.name,
            call_id=call.id,
            dry_run=self.dry_run,
        ) as span:
            try:
                parsed_args = json.loads(call.arguments) if call.arguments else {}
            except json.JSONDecodeError as exc:
                span.set(error_kind="arguments_not_json")
                return ToolInvocation(
                    call_id=call.id,
                    name=call.name,
                    arguments={},
                    result=f"error: arguments are not valid JSON: {exc}",
                    error=str(exc),
                )

            try:
                result = await self.registry.dispatch(
                    call.name, parsed_args, dry_run=self.dry_run
                )
            except ToolArgumentError as exc:
                span.set(error_kind="argument_schema")
                return ToolInvocation(
                    call_id=call.id,
                    name=call.name,
                    arguments=parsed_args,
                    result=f"error: {exc}",
                    error=str(exc),
                )
            except ToolError as exc:
                span.set(error_kind="registry")
                return ToolInvocation(
                    call_id=call.id,
                    name=call.name,
                    arguments=parsed_args,
                    result=f"error: {exc}",
                    error=str(exc),
                )
            except Exception as exc:
                # Surface handler failures back to the model so it can recover,
                # rather than crashing the orchestrator loop.
                span.set(error_kind=f"handler:{type(exc).__name__}")
                return ToolInvocation(
                    call_id=call.id,
                    name=call.name,
                    arguments=parsed_args,
                    result=f"error: {type(exc).__name__}: {exc}",
                    error=str(exc),
                )

            span.set(result_len=len(result))
            return ToolInvocation(
                call_id=call.id,
                name=call.name,
                arguments=parsed_args,
                result=result,
            )
