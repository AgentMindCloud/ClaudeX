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

from dataclasses import dataclass, field
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


def _root_duration_ms(events: Iterable[Event]) -> float:
    """Duration of the first root span (``parent_span_id is None``),
    matching `Observation.total_latency_ms` semantics so live + captured
    runs compare apples-to-apples.
    """
    for e in events:
        if e.kind == SPAN_END and e.parent_span_id is None:
            return float(e.duration_ms or 0.0)
    return 0.0


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

    a_latency = _root_duration_ms(a_list)
    b_latency = _root_duration_ms(b_list)

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
        f"{a_label}_latency_ms": a_latency,
        f"{b_label}_latency_ms": b_latency,
        "latency_delta_ms": b_latency - a_latency,
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


# ---------------------------------------------------------------------------
# directory-level diff (`frok eval summarize --diff-against <DIR>`)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CaseDiff:
    """One matched case, with its `diff_event_streams` payload."""

    name: str
    a_path: str
    b_path: str
    diff: dict[str, Any]

    @property
    def regressed(self) -> bool:
        return bool(self.diff.get("regressed"))


@dataclass
class DirectoryDiff:
    a: str
    b: str
    matched: list[CaseDiff] = field(default_factory=list)
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)

    @property
    def regressed_cases(self) -> int:
        return sum(1 for m in self.matched if m.regressed)

    @property
    def regressed(self) -> bool:
        # A directory diff regresses if any matched case regressed OR slugs
        # diverged between the two sides. An operator explicitly opting into
        # --diff-against probably wants to know about both kinds.
        return (
            self.regressed_cases > 0
            or bool(self.only_in_a)
            or bool(self.only_in_b)
        )


def _load_captures(directory: Path) -> dict[str, tuple[Path, list[Event]]]:
    if not directory.is_dir():
        raise NotADirectoryError(f"not a directory: {directory}")
    out: dict[str, tuple[Path, list[Event]]] = {}
    for path in sorted(directory.glob("*.jsonl")):
        events = list(read_jsonl(path))
        if events:
            out[path.stem] = (path, events)
    return out


def diff_directories(
    a_dir: str | Path, b_dir: str | Path
) -> DirectoryDiff:
    """Walk two directories of `<slug>.jsonl` captures and diff each
    matching case pair.

    Slugs present in only one side are returned in ``only_in_a`` /
    ``only_in_b``. The ``regressed`` roll-up flips when any matched
    case regresses OR the slug sets diverge.
    """
    a_path = Path(a_dir)
    b_path = Path(b_dir)
    a_caps = _load_captures(a_path)
    b_caps = _load_captures(b_path)

    matched_names = sorted(set(a_caps) & set(b_caps))
    matched = [
        CaseDiff(
            name=name,
            a_path=str(a_caps[name][0]),
            b_path=str(b_caps[name][0]),
            diff=diff_event_streams(
                a_caps[name][1], b_caps[name][1], a_label="a", b_label="b"
            ),
        )
        for name in matched_names
    ]

    return DirectoryDiff(
        a=str(a_path),
        b=str(b_path),
        matched=matched,
        only_in_a=sorted(set(a_caps) - set(b_caps)),
        only_in_b=sorted(set(b_caps) - set(a_caps)),
    )


def directory_diff_to_markdown(dd: DirectoryDiff) -> str:
    lines = [
        "# Frok Eval Directory Diff",
        "",
        f"- a: `{dd.a}`",
        f"- b: `{dd.b}`",
        f"- Matched: {len(dd.matched)} "
        f"| Only in a: {len(dd.only_in_a)} "
        f"| Only in b: {len(dd.only_in_b)}",
        f"- Regressed cases: {dd.regressed_cases}",
        "",
    ]

    if dd.matched:
        lines += [
            "## Per-case diffs",
            "",
            "| Case | Tool order | Δ tokens | New errors | Regressed |",
            "|------|-----------|---------:|-----------:|:----------|",
        ]
        for m in dd.matched:
            d = m.diff
            tool_state = "match" if d["tool_order_match"] else "**diverged**"
            delta = d["token_delta"]
            delta_str = f"{delta:+d}"
            lines.append(
                f"| {m.name} | {tool_state} | {delta_str} "
                f"| {d['new_errors']} | {'**yes**' if m.regressed else '-'} |"
            )
        lines.append("")

    if dd.only_in_a:
        lines += ["## Only in a", ""] + [f"- `{n}`" for n in dd.only_in_a] + [""]
    if dd.only_in_b:
        lines += ["## Only in b", ""] + [f"- `{n}`" for n in dd.only_in_b] + [""]

    regressed = [m for m in dd.matched if m.regressed]
    if regressed:
        lines += ["## Regression details", ""]
        for m in regressed:
            d = m.diff
            lines.append(f"### `{m.name}`")
            lines.append(f"- a tools: {d['a_tools']!r}")
            lines.append(f"- b tools: {d['b_tools']!r}")
            lines.append(
                f"- a errors: {d['a_errors']} → b errors: {d['b_errors']} "
                f"({d['new_errors']} new)"
            )
            lines.append(
                f"- tokens: {d['a_tokens']} → {d['b_tokens']} "
                f"(Δ {d['token_delta']:+d})"
            )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def directory_diff_to_json(dd: DirectoryDiff) -> dict[str, Any]:
    return {
        "a": dd.a,
        "b": dd.b,
        "regressed": dd.regressed,
        "regressed_cases": dd.regressed_cases,
        "only_in_a": dd.only_in_a,
        "only_in_b": dd.only_in_b,
        "matched": [
            {
                "name": m.name,
                "a_path": m.a_path,
                "b_path": m.b_path,
                "regressed": m.regressed,
                "diff": m.diff,
            }
            for m in dd.matched
        ],
    }
