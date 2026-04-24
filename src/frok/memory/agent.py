"""MemoryAgent — GrokClient + MemoryStore for long-running context.

Each `chat()` turn:
  1. Run the user message through the client's safety rules so PII never
     lands in the store.
  2. Recall the top-k prior memories similar to the sanitized message
     (optionally filtered by kind / time).
  3. Inject recalled context as a system message, send the turn through
     the underlying `GrokClient.chat`.
  4. Store the sanitized user turn and the assistant response so the
     next call can recall them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..clients.grok import GrokClient, GrokMessage, GrokResponse
from .store import MemoryRecord, MemoryStore

USER_KIND = "user_message"
ASSISTANT_KIND = "assistant_message"


@dataclass
class MemoryAgent:
    client: GrokClient
    store: MemoryStore
    recall_k: int = 5
    recall_kind: str | None = None
    min_score: float = 0.1
    system_prompt: str | None = None
    recall_header: str = "Relevant prior context (most-similar first):"

    async def chat(
        self,
        user_text: str,
        *,
        extra_messages: Sequence[GrokMessage] = (),
    ) -> GrokResponse:
        # Sanitize before anything leaves the process boundary.
        sanitized = self.client.safety.apply(user_text)
        if sanitized.blocked:
            # Let the client raise with a consistent error; do not store.
            return await self.client.chat([GrokMessage("user", user_text)])

        clean_user = sanitized.text
        recalled = await self.store.recall(
            clean_user,
            k=self.recall_k,
            kind=self.recall_kind,
            min_score=self.min_score,
        )

        messages: list[GrokMessage] = []
        if self.system_prompt:
            messages.append(GrokMessage("system", self.system_prompt))
        if recalled:
            messages.append(GrokMessage("system", _format_recall(self.recall_header, recalled)))
        messages.extend(extra_messages)
        messages.append(GrokMessage("user", clean_user))

        resp = await self.client.chat(messages)

        await self.store.remember(clean_user, kind=USER_KIND)
        await self.store.remember(
            resp.content,
            kind=ASSISTANT_KIND,
            metadata={
                "model": resp.model,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
            },
        )
        return resp


def _format_recall(header: str, records: list[MemoryRecord]) -> str:
    lines = [header]
    for r in records:
        stamp = r.created_at.date().isoformat()
        score = f"{r.score:.2f}" if r.score is not None else "n/a"
        lines.append(f"- [{stamp} · {r.kind} · sim={score}] {r.content}")
    return "\n".join(lines)
