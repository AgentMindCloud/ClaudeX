"""Async xAI/Grok Chat Completions client.

Design notes:
  * Zero hard dependencies — the transport is a protocol so we can stub it
    in tests and swap in httpx/aiohttp in production by passing a callable
    that returns (status, headers, body_bytes).
  * Safety rules from ``frok.safety`` run as pre-flight (prompt) and
    post-flight (response) guards by default. Callers can pass their own
    ruleset or disable by passing ``SafetyRuleSet(rules=())``.
  * Retries use exponential backoff with jitter on 429/5xx. 4xx other than
    429 are raised immediately — they signal a caller bug, not a transient.
"""

from __future__ import annotations

import asyncio
import json
import random
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol

from ..safety.rules import SafetyRuleSet, default_ruleset
from ..telemetry import Tracer

DEFAULT_BASE_URL = "https://api.x.ai/v1"
DEFAULT_MODEL = "grok-4"
DEFAULT_TIMEOUT_S = 60.0
DEFAULT_MAX_RETRIES = 4


@dataclass(frozen=True)
class ToolCall:
    """A single function call request emitted by the model."""

    id: str
    name: str
    arguments: str  # raw JSON string as produced by the model

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": self.arguments},
        }

    @classmethod
    def from_payload(cls, data: dict[str, Any]) -> "ToolCall":
        fn = data.get("function") or {}
        return cls(
            id=str(data.get("id") or ""),
            name=str(fn.get("name") or ""),
            arguments=fn.get("arguments") or "{}",
        )


@dataclass(frozen=True)
class GrokMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: str | None = None
    tool_calls: tuple[ToolCall, ...] | None = None
    tool_call_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {"role": self.role}
        if self.tool_calls:
            # OpenAI/xAI convention: assistant tool-call messages carry null
            # content alongside the `tool_calls` array.
            out["content"] = self.content or None
            out["tool_calls"] = [c.to_payload() for c in self.tool_calls]
        else:
            out["content"] = self.content
        if self.name is not None:
            out["name"] = self.name
        if self.tool_call_id is not None:
            out["tool_call_id"] = self.tool_call_id
        return out


@dataclass
class GrokResponse:
    model: str
    content: str
    raw: dict[str, Any]
    prompt_tokens: int = 0
    completion_tokens: int = 0
    safety_findings: list[Any] = field(default_factory=list)
    tool_calls: tuple[ToolCall, ...] | None = None
    finish_reason: str | None = None

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class GrokError(RuntimeError):
    """Raised for caller-facing failures (safety block, bad request, …)."""


class HttpError(GrokError):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status = status
        self.body = body


class Transport(Protocol):
    async def __call__(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout: float,
    ) -> tuple[int, dict[str, str], bytes]: ...


RetrySleep = Callable[[float], Awaitable[None]]


@dataclass
class GrokClient:
    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    timeout_s: float = DEFAULT_TIMEOUT_S
    max_retries: int = DEFAULT_MAX_RETRIES
    transport: Transport | None = None
    safety: SafetyRuleSet = field(default_factory=default_ruleset)
    sleep: RetrySleep = asyncio.sleep
    tracer: Tracer = field(default_factory=Tracer)

    # Aggregate cost accounting across the client lifetime.
    prompt_tokens_total: int = 0
    completion_tokens_total: int = 0

    async def chat(
        self,
        messages: list[GrokMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> GrokResponse:
        if not messages:
            raise GrokError("messages must not be empty")

        async with self.tracer.span(
            "grok.chat",
            model=self.model,
            message_count=len(messages),
            has_tools=tools is not None,
        ) as span:
            # Pre-flight: apply safety rules to every inbound message.
            guarded: list[GrokMessage] = []
            pre_findings: list[Any] = []
            for m in messages:
                result = self.safety.apply(m.content)
                pre_findings.extend(result.findings)
                if result.blocked:
                    span.set(
                        safety_blocked="prompt",
                        safety_findings=len(pre_findings),
                    )
                    raise GrokError(
                        f"prompt blocked by safety rule(s): "
                        f"{[f.rule for f in result.findings if f.severity >= 40]}"
                    )
                guarded.append(
                    GrokMessage(
                        role=m.role,
                        content=result.text,
                        name=m.name,
                        tool_calls=m.tool_calls,
                        tool_call_id=m.tool_call_id,
                    )
                )

            payload: dict[str, Any] = {
                "model": self.model,
                "messages": [m.to_payload() for m in guarded],
            }
            if tools is not None:
                payload["tools"] = tools
            if temperature is not None:
                payload["temperature"] = temperature
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            if extra:
                payload.update(extra)

            raw = await self._post("/chat/completions", payload)
            content, tool_calls, finish_reason = _extract_message(raw)

            # Post-flight: rewrite model output through the same ruleset.
            post = self.safety.apply(content)
            if post.blocked:
                span.set(
                    safety_blocked="response",
                    safety_findings=len(pre_findings) + len(post.findings),
                )
                raise GrokError(
                    f"response blocked by safety rule(s): "
                    f"{[f.rule for f in post.findings if f.severity >= 40]}"
                )

            usage = raw.get("usage") or {}
            prompt_tokens = int(usage.get("prompt_tokens", 0))
            completion_tokens = int(usage.get("completion_tokens", 0))
            self.prompt_tokens_total += prompt_tokens
            self.completion_tokens_total += completion_tokens

            span.set(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                tool_calls=len(tool_calls) if tool_calls else 0,
                finish_reason=finish_reason or "",
                safety_findings=len(pre_findings) + len(post.findings),
            )

            return GrokResponse(
                model=raw.get("model", self.model),
                content=post.text,
                raw=raw,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                safety_findings=pre_findings + post.findings,
                tool_calls=tool_calls,
                finish_reason=finish_reason,
            )

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.transport is None:
            raise GrokError(
                "no transport configured; pass transport=... or use a "
                "production adapter"
            )
        url = f"{self.base_url.rstrip('/')}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "frok-client/0.2",
        }
        body = json.dumps(payload).encode("utf-8")

        delay = 0.5
        last_err: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                status, _hdrs, resp_body = await self.transport(
                    method="POST",
                    url=url,
                    headers=headers,
                    body=body,
                    timeout=self.timeout_s,
                )
            except asyncio.TimeoutError as exc:
                last_err = exc
                if attempt == self.max_retries:
                    raise GrokError("request timed out after retries") from exc
            else:
                if 200 <= status < 300:
                    return json.loads(resp_body.decode("utf-8") or "{}")
                if status == 429 or 500 <= status < 600:
                    last_err = HttpError(status, resp_body.decode("utf-8", "replace"))
                    if attempt == self.max_retries:
                        raise last_err
                else:
                    raise HttpError(status, resp_body.decode("utf-8", "replace"))

            jitter = random.uniform(0, delay / 2)
            await self.sleep(delay + jitter)
            delay = min(delay * 2, 16.0)

        # Unreachable, but keeps type-checkers happy.
        assert last_err is not None
        raise last_err


def _extract_message(
    raw: dict[str, Any],
) -> tuple[str, tuple[ToolCall, ...] | None, str | None]:
    try:
        choice = raw["choices"][0]
        msg = choice["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GrokError(f"malformed response: {raw!r}") from exc
    content = msg.get("content") or ""
    raw_calls = msg.get("tool_calls") or []
    calls = tuple(ToolCall.from_payload(c) for c in raw_calls) if raw_calls else None
    finish_reason = choice.get("finish_reason")
    return content, calls, finish_reason
