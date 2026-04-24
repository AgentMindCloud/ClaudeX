"""Built-in routers for `TeamRuntime`.

A router is any callable ``(reply, transcript) -> next_role_name |
None``. Return ``None`` to terminate the run. Three built-ins:

* ``pipeline_router(["a", "b", "c"])`` — static linear pipeline,
  terminates after the last role in the sequence replies.
* ``callback_router(fn)`` — identity; a typing helper so call sites
  read consistently.
* ``loop_until(predicate, next_=...)`` — keep routing to ``next_``
  until ``predicate(reply)`` is true.
"""

from __future__ import annotations

from typing import Callable, Sequence

from .runtime import Router, TeamMessage


def pipeline_router(sequence: Sequence[str]) -> Router:
    seq = list(sequence)
    if not seq:
        raise ValueError("pipeline_router requires at least one role")
    idx_of = {name: i for i, name in enumerate(seq)}

    def route(reply: TeamMessage, transcript: list[TeamMessage]) -> str | None:
        i = idx_of.get(reply.from_)
        if i is None:
            return seq[0]
        if i + 1 < len(seq):
            return seq[i + 1]
        return None

    return route


def callback_router(
    fn: Callable[[TeamMessage, list[TeamMessage]], str | None],
) -> Router:
    return fn


def loop_until(
    predicate: Callable[[TeamMessage], bool],
    *,
    next_: str,
    max_rounds: int | None = None,
) -> Router:
    """Route to ``next_`` until ``predicate(reply)`` is true.

    When ``max_rounds`` is set, terminates after that many replies even
    if the predicate never fires; the runtime's own ``max_hops`` still
    applies as a hard safety net.
    """

    def route(reply: TeamMessage, transcript: list[TeamMessage]) -> str | None:
        if predicate(reply):
            return None
        if max_rounds is not None:
            # `transcript` has not been appended with this hop's reply yet,
            # so count prior replies from this sender + 1 for the current.
            sent = 1 + sum(1 for m in transcript if m.from_ == reply.from_)
            if sent >= max_rounds:
                return None
        return next_

    return route
