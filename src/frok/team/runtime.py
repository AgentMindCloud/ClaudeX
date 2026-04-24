"""Lightweight multi-agent runtime.

A `TeamRuntime` is a loop. It takes an initial `TeamMessage` addressed
to a named `Role`, hands the growing transcript to that role, lets a
`Router` choose the next recipient, and repeats until the router
returns ``None`` (clean termination) or ``max_hops`` trips (error).

Deliberately small: no role hierarchy, no DSL for inter-role protocols,
no implicit "supervisor". Roles are plain async callables
``(transcript) -> str``; routers are plain callables
``(reply, transcript) -> next_role_name | None``. Everything composes:
a role can itself wrap a `MemoryAgent`, a `ToolOrchestrator`, a
`MultimodalAdapter`, or any bare `GrokClient`.

All hops emit telemetry spans so `§2 #8` eval cases can regress on
team behaviour through the same `InMemorySink` they already use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping

from ..clients.grok import GrokClient, GrokMessage
from ..telemetry import Tracer


class TeamError(RuntimeError):
    """Raised for unknown roles, exceeded hop budgets, etc."""


@dataclass(frozen=True)
class TeamMessage:
    from_: str
    to: str
    content: str
    meta: Mapping[str, Any] = field(default_factory=dict)
    step: int = 0


RoleFn = Callable[[list[TeamMessage]], Awaitable[str]]


@dataclass
class Role:
    name: str
    respond: RoleFn
    description: str = ""


# Router signature: (reply, transcript) -> next_role_name_or_None
Router = Callable[[TeamMessage, list[TeamMessage]], "str | None"]


@dataclass
class TeamRun:
    transcript: list[TeamMessage]
    final: TeamMessage
    hops: int
    terminated: str  # "router" | "max_hops"


@dataclass
class TeamRuntime:
    roles: dict[str, Role]
    router: Router
    tracer: Tracer = field(default_factory=Tracer)
    max_hops: int = 20

    async def run(self, initial: TeamMessage) -> TeamRun:
        if initial.to not in self.roles:
            raise TeamError(f"unknown role in initial message: {initial.to!r}")

        transcript: list[TeamMessage] = [initial]
        current = initial
        hops = 0

        async with self.tracer.span(
            "team.run",
            team_size=len(self.roles),
            initial_to=initial.to,
            max_hops=self.max_hops,
        ) as run_span:
            while hops < self.max_hops:
                hops += 1
                if current.to not in self.roles:
                    raise TeamError(f"unknown role: {current.to!r}")
                role = self.roles[current.to]

                async with self.tracer.span(
                    "team.hop",
                    role=current.to,
                    from_=current.from_,
                    hop=hops,
                ) as hop_span:
                    relevant = [
                        m for m in transcript if m.to == role.name or m.to == "all"
                    ]
                    reply_text = await role.respond(relevant)
                    hop_span.set(reply_len=len(reply_text))

                # Ask the router who this reply goes to. The probe carries
                # the sender + text so routers that key off `from_` /
                # `content` work naturally; `to` is filled in once decided.
                probe = TeamMessage(
                    from_=role.name, to="", content=reply_text, step=hops
                )
                next_to = self.router(probe, transcript)
                routed = TeamMessage(
                    from_=role.name,
                    to=next_to or "user",
                    content=reply_text,
                    step=hops,
                )
                transcript.append(routed)

                if next_to is None:
                    run_span.set(hops=hops, terminated="router")
                    return TeamRun(
                        transcript=transcript,
                        final=routed,
                        hops=hops,
                        terminated="router",
                    )

                current = routed

            run_span.set(hops=hops, terminated="max_hops")
            raise TeamError(
                f"max_hops={self.max_hops} exceeded; last role={current.to!r}"
            )


# ---------------------------------------------------------------------------
# role adapters — wrap common shapes into a `Role`
# ---------------------------------------------------------------------------
def chat_role_from_client(
    name: str,
    client: GrokClient,
    *,
    system: str | None = None,
    description: str = "",
) -> Role:
    """Turn a bare `GrokClient` into a Role by flattening the transcript into
    alternating user / assistant messages. The role's own prior replies
    come back as `assistant`; everything else is `user`-tagged with
    ``[sender→recipient]`` prefixes so the model knows who said what."""

    async def respond(transcript: list[TeamMessage]) -> str:
        msgs: list[GrokMessage] = []
        if system:
            msgs.append(GrokMessage("system", system))
        for m in transcript:
            role = "assistant" if m.from_ == name else "user"
            prefix = f"[{m.from_}->{m.to}]"
            msgs.append(GrokMessage(role, f"{prefix} {m.content}"))
        resp = await client.chat(msgs)
        return resp.content

    return Role(name=name, respond=respond, description=description)


def echo_role(name: str, *, prefix: str = "") -> Role:
    """Deterministic role for tests and wiring checks. Replies with the most
    recent inbound content, optionally prefixed."""

    async def respond(transcript: list[TeamMessage]) -> str:
        last = transcript[-1].content
        return f"{prefix}{last}" if prefix else last

    return Role(name=name, respond=respond, description="echo")
