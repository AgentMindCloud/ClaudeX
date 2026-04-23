"""Baseline-trace diffing against an observed run.

The baseline is a captured `JsonlSink` file from a prior, trusted run.
The diff answers: did the candidate call the same tools in the same
order? Did token cost move? Did new errors appear?

A diff carrying `regressed=True` escalates into an overall case failure
in the runner.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..telemetry import SPAN_END, Event, read_jsonl
from .case import Observation


def _chat_tokens(events: list[Event]) -> int:
    return sum(
        int(e.data.get("total_tokens", 0) or 0)
        for e in events
        if e.kind == SPAN_END and e.name == "grok.chat"
    )


def _tool_order(events: list[Event]) -> list[str]:
    # Ends are emitted inner-first, so sort on start time for user order.
    invokes = [
        e for e in events if e.kind == SPAN_END and e.name == "tool.invoke"
    ]
    invokes.sort(key=lambda e: e.ts - (e.duration_ms or 0.0) / 1000.0)
    return [e.data.get("tool", "") for e in invokes]


def _error_count(events: list[Event]) -> int:
    return sum(1 for e in events if e.kind == SPAN_END and e.error is not None)


def diff_against_baseline(obs: Observation, baseline_path: str | Path) -> dict[str, Any]:
    baseline = list(read_jsonl(baseline_path))

    b_tools = _tool_order(baseline)
    o_tools = _tool_order(obs.events)

    b_tokens = _chat_tokens(baseline)
    o_tokens = obs.total_tokens

    b_errors = _error_count(baseline)
    o_errors = _error_count(obs.events)

    tool_order_match = b_tools == o_tools
    new_errors = max(0, o_errors - b_errors)

    return {
        "path": str(baseline_path),
        "tool_order_match": tool_order_match,
        "baseline_tools": b_tools,
        "observed_tools": o_tools,
        "baseline_tokens": b_tokens,
        "observed_tokens": o_tokens,
        "token_delta": o_tokens - b_tokens,
        "baseline_errors": b_errors,
        "observed_errors": o_errors,
        "new_errors": new_errors,
        # A regression is anything that matters for trust: tools diverged
        # or a new error appeared. Token deltas alone do not regress a run.
        "regressed": (not tool_order_match) or new_errors > 0,
    }
