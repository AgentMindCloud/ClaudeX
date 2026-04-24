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
from typing import Any, Callable, Sequence

from ..clients.grok import GrokClient, GrokMessage, GrokResponse, ToolCall
from .registry import ToolArgumentError, ToolError, ToolRegistry


StreamSink = Callable[[str], None]


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
        stream_sink: StreamSink | None = None,
    ) -> ToolRun:
        """Drive the tool-use loop.

        ``stream_sink``: if set AND the underlying client has a
        ``streaming_transport``, each turn is issued via
        ``chat_stream`` and its content deltas are forwarded to the
        sink, prefixed with a ``>>> turn N`` marker. Without a
        streaming transport we fall back to the non-stream
        ``chat()`` path silently — the sink caller can pass it
        unconditionally without probing the client first.
        """
        use_stream = (
            stream_sink is not None and self.client.streaming_transport is not None
        )
        async with self.client.tracer.span(
            "tool.run",
            max_steps=self.max_steps,
            dry_run=self.dry_run,
            tool_count=len(self.registry.tools),
            streamed=use_stream,
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
                if use_stream:
                    assert stream_sink is not None
                    stream_sink(f"\n>>> turn {step}\n")
                    resp = await self._streamed_turn(
                        convo, tools_spec, extra, stream_sink
                    )
                else:
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

    async def _streamed_turn(
        self,
        convo: Sequence[GrokMessage],
        tools_spec: list[dict[str, Any]],
        extra: dict[str, Any],
        stream_sink: StreamSink,
    ) -> GrokResponse:
        final: GrokResponse | None = None
        async for chunk in self.client.chat_stream(
            list(convo),
            tools=tools_spec,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            extra=extra or None,
        ):
            if chunk.delta:
                stream_sink(chunk.delta)
            if chunk.is_final:
                final = chunk.response
        if final is None:
            raise ToolError(
                "chat_stream ended without yielding a final chunk during "
                "the tool-use loop"
            )
        return final

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
                span.fail(str(exc))
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
                span.fail(str(exc))
                return ToolInvocation(
                    call_id=call.id,
                    name=call.name,
                    arguments=parsed_args,
                    result=f"error: {exc}",
                    error=str(exc),
                )
            except ToolError as exc:
                span.set(error_kind="registry")
                span.fail(str(exc))
                return ToolInvocation(
                    call_id=call.id,
                    name=call.name,
                    arguments=parsed_args,
                    result=f"error: {exc}",
                    error=str(exc),
                )
            except Exception as exc:
                # Surface handler failures back to the model so it can recover,
                # rather than crashing the orchestrator loop. The span itself
                # is still marked errored so eval scorers can catch it.
                span.set(error_kind=f"handler:{type(exc).__name__}")
                span.fail(f"{type(exc).__name__}: {exc}")
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
