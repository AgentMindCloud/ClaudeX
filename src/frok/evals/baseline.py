"""Baseline-trace diffing — single-observation and two-capture.

Two entry points sit on top of the same core diff:

* `diff_against_baseline(obs, path)` — live `Observation` vs a captured
  `JsonlSink` file. Used by the eval runner to escalate a
  ``regressed=True`` diff into a case failure. Preserves legacy dict
  keys (``baseline_tools`` / ``observed_tools`` / …) so existing
  scorers and reports are unchanged.
* `diff_event_streams(a, b, *, a_label, b_label)` — raw two-sided
  comparison over event lists. Used by ``frok eval diff`` to A/B two
  captures without a live run. Labels parametrise the key names so
  callers can choose ``"a"/"b"`` or ``"baseline"/"observed"`` or
  whatever reads cleanest.

A diff where the tool-call order diverges or a new error appears in
the second side carries ``regressed=True``. Token deltas alone do
not regress — a chattier answer that's still correct should not
fail CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..telemetry import SPAN_END, Event, read_jsonl
from .case import Observation


def _chat_tokens(events: Iterable[Event]) -> int:
    return sum(
        int(e.data.get("total_tokens", 0) or 0)
        for e in events
        if e.kind == SPAN_END and e.name == "grok.chat"
    )


def _tool_order(events: Iterable[Event]) -> list[str]:
    # Ends are emitted inner-first, so sort on start time for user order.
    invokes = [
        e for e in events if e.kind == SPAN_END and e.name == "tool.invoke"
    ]
    invokes.sort(key=lambda e: e.ts - (e.duration_ms or 0.0) / 1000.0)
    return [e.data.get("tool", "") for e in invokes]


def _error_count(events: Iterable[Event]) -> int:
    return sum(1 for e in events if e.kind == SPAN_END and e.error is not None)


def _span_count(events: Iterable[Event]) -> int:
    return sum(1 for e in events if e.kind == SPAN_END)


def diff_event_streams(
    a_events: Iterable[Event],
    b_events: Iterable[Event],
    *,
    a_label: str = "a",
    b_label: str = "b",
) -> dict[str, Any]:
    """Diff two raw event streams.

    ``a`` is the reference side (e.g. "baseline" / "before"); ``b`` is
    the candidate (e.g. "observed" / "after"). ``regressed`` reports
    whether ``b`` diverged in a way that matters for trust.
    """
    a_list = list(a_events)
    b_list = list(b_events)

    a_tools = _tool_order(a_list)
    b_tools = _tool_order(b_list)

    a_tokens = _chat_tokens(a_list)
    b_tokens = _chat_tokens(b_list)

    a_errors = _error_count(a_list)
    b_errors = _error_count(b_list)

    a_spans = _span_count(a_list)
    b_spans = _span_count(b_list)

    tool_order_match = a_tools == b_tools
    new_errors = max(0, b_errors - a_errors)

    return {
        "tool_order_match": tool_order_match,
        f"{a_label}_tools": a_tools,
        f"{b_label}_tools": b_tools,
        f"{a_label}_tokens": a_tokens,
        f"{b_label}_tokens": b_tokens,
        "token_delta": b_tokens - a_tokens,
        f"{a_label}_errors": a_errors,
        f"{b_label}_errors": b_errors,
        "new_errors": new_errors,
        f"{a_label}_spans": a_spans,
        f"{b_label}_spans": b_spans,
        "span_delta": b_spans - a_spans,
        "regressed": (not tool_order_match) or new_errors > 0,
    }


def diff_against_baseline(
    obs: Observation, baseline_path: str | Path
) -> dict[str, Any]:
    baseline = list(read_jsonl(baseline_path))
    diff = diff_event_streams(
        baseline, obs.events, a_label="baseline", b_label="observed"
    )
    diff["path"] = str(baseline_path)
    return diff


def diff_to_markdown(
    diff: dict[str, Any],
    *,
    a_label: str = "a",
    b_label: str = "b",
    a_path: str | Path | None = None,
    b_path: str | Path | None = None,
) -> str:
    """Render a `diff_event_streams` dict as a compact Markdown report."""

    def _get(key: str) -> Any:
        return diff[key]

    a_tag = f"`{a_path}`" if a_path is not None else f"`{a_label}`"
    b_tag = f"`{b_path}`" if b_path is not None else f"`{b_label}`"

    lines = [
        "# Frok Eval Diff",
        "",
        f"- {a_label}: {a_tag} — {_get(f'{a_label}_spans')} spans",
        f"- {b_label}: {b_tag} — {_get(f'{b_label}_spans')} spans",
        f"- Regressed: {'**yes**' if diff['regressed'] else 'no'}",
        "",
        "## Tool-call order",
        f"- Match: {'yes' if diff['tool_order_match'] else '**no**'}",
        f"- {a_label}: {_get(f'{a_label}_tools')!r}",
        f"- {b_label}: {_get(f'{b_label}_tools')!r}",
        "",
        "## Tokens",
        f"- {a_label}: {_get(f'{a_label}_tokens')}",
        f"- {b_label}: {_get(f'{b_label}_tokens')}",
        f"- Delta ({b_label} − {a_label}): {diff['token_delta']:+d}",
        "",
        "## Errors",
        f"- {a_label}: {_get(f'{a_label}_errors')}",
        f"- {b_label}: {_get(f'{b_label}_errors')}",
        f"- New in {b_label}: {diff['new_errors']}",
        "",
    ]
    return "\n".join(lines)
