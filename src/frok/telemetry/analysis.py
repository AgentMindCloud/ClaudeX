"""Post-hoc trace analysis: reconstruct tree + aggregate stats.

Consumes an iterable of `Event`s (typically from `read_jsonl` replaying a
`JsonlSink` capture) and produces two artefacts:

* a `list[TraceNode]` tree keyed on `parent_span_id`, and
* a `TraceSummary` with per-name duration stats, errored-span list, and
  top-tool aggregates.

Used by ``frok trace inspect``; also callable as a library for tests /
notebooks / ad-hoc diagnostics.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Iterable

from .sink import SPAN_END, Event


# ---------------------------------------------------------------------------
# types
# ---------------------------------------------------------------------------
@dataclass
class TraceNode:
    span_id: str
    trace_id: str
    parent_span_id: str | None
    name: str
    duration_ms: float
    error: str | None
    data: dict
    start_ts: float
    children: list["TraceNode"] = field(default_factory=list)


@dataclass(frozen=True)
class NameStats:
    name: str
    count: int
    total_ms: float
    mean_ms: float
    p50_ms: float
    p95_ms: float
    max_ms: float
    error_count: int


@dataclass(frozen=True)
class ToolStat:
    tool: str
    count: int
    total_ms: float
    mean_ms: float
    errors: int


@dataclass
class TraceSummary:
    event_count: int
    span_count: int
    trace_count: int
    errors: list[TraceNode]
    name_stats: dict[str, NameStats]
    top_tools: list[ToolStat]


# ---------------------------------------------------------------------------
# tree reconstruction
# ---------------------------------------------------------------------------
def _nodes_from(events: Iterable[Event]) -> dict[str, TraceNode]:
    nodes: dict[str, TraceNode] = {}
    for e in events:
        if e.kind != SPAN_END:
            continue
        duration = float(e.duration_ms or 0.0)
        nodes[e.span_id] = TraceNode(
            span_id=e.span_id,
            trace_id=e.trace_id,
            parent_span_id=e.parent_span_id,
            name=e.name,
            duration_ms=duration,
            error=e.error,
            data=dict(e.data),
            start_ts=e.ts - duration / 1000.0,
        )
    return nodes


def build_tree(events: Iterable[Event]) -> list[TraceNode]:
    nodes = _nodes_from(events)
    roots: list[TraceNode] = []
    for node in nodes.values():
        parent = nodes.get(node.parent_span_id) if node.parent_span_id else None
        if parent is not None:
            parent.children.append(node)
        else:
            roots.append(node)
    for n in nodes.values():
        n.children.sort(key=lambda c: c.start_ts)
    roots.sort(key=lambda r: r.start_ts)
    return roots


# ---------------------------------------------------------------------------
# stats
# ---------------------------------------------------------------------------
def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    # Linear-interpolation percentile (same as numpy default).
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def summarize(events: Iterable[Event]) -> TraceSummary:
    events_list = list(events)
    span_ends = [e for e in events_list if e.kind == SPAN_END]
    nodes = _nodes_from(span_ends)

    # per-name stats
    by_name: dict[str, list[Event]] = {}
    for e in span_ends:
        by_name.setdefault(e.name, []).append(e)

    name_stats: dict[str, NameStats] = {}
    for name, group in by_name.items():
        durations = [float(e.duration_ms or 0.0) for e in group]
        name_stats[name] = NameStats(
            name=name,
            count=len(group),
            total_ms=sum(durations),
            mean_ms=statistics.fmean(durations) if durations else 0.0,
            p50_ms=_percentile(durations, 50),
            p95_ms=_percentile(durations, 95),
            max_ms=max(durations) if durations else 0.0,
            error_count=sum(1 for e in group if e.error),
        )

    # tool stats — only tool.invoke spans
    tool_groups: dict[str, list[Event]] = {}
    for e in span_ends:
        if e.name != "tool.invoke":
            continue
        tool = str(e.data.get("tool") or "<unknown>")
        tool_groups.setdefault(tool, []).append(e)

    top_tools: list[ToolStat] = []
    for tool, group in tool_groups.items():
        durs = [float(e.duration_ms or 0.0) for e in group]
        top_tools.append(
            ToolStat(
                tool=tool,
                count=len(group),
                total_ms=sum(durs),
                mean_ms=statistics.fmean(durs) if durs else 0.0,
                errors=sum(1 for e in group if e.error),
            )
        )
    # Most-invoked first, tie-break by total time.
    top_tools.sort(key=lambda t: (-t.count, -t.total_ms))

    errors = [nodes[e.span_id] for e in span_ends if e.error]
    # Stable: sort errors by start_ts.
    errors.sort(key=lambda n: n.start_ts)

    return TraceSummary(
        event_count=len(events_list),
        span_count=len(span_ends),
        trace_count=len({e.trace_id for e in span_ends}),
        errors=errors,
        name_stats=name_stats,
        top_tools=top_tools,
    )


# ---------------------------------------------------------------------------
# renderers
# ---------------------------------------------------------------------------
def render_tree(roots: list[TraceNode], *, indent: str = "  ") -> str:
    lines: list[str] = []

    def visit(node: TraceNode, depth: int) -> None:
        err = f"  ERROR: {node.error}" if node.error else ""
        lines.append(
            f"{indent * depth}- {node.name} ({node.duration_ms:.1f} ms){err}"
        )
        for c in node.children:
            visit(c, depth + 1)

    for r in roots:
        visit(r, 0)
    return "\n".join(lines)


def summary_to_markdown(
    summary: TraceSummary,
    *,
    top: int = 20,
    include_tree: bool = False,
    roots: list[TraceNode] | None = None,
) -> str:
    lines = [
        "# Frok Trace Report",
        "",
        f"- Events: {summary.event_count}",
        f"- Spans: {summary.span_count}",
        f"- Traces: {summary.trace_count}",
        f"- Errored spans: {len(summary.errors)}",
        "",
        "## Span durations by name",
        "",
        "| Name | Count | Total ms | Mean ms | p50 | p95 | Max | Errors |",
        "|------|------:|---------:|--------:|----:|----:|----:|-------:|",
    ]
    sorted_stats = sorted(summary.name_stats.values(), key=lambda s: -s.total_ms)
    for s in sorted_stats:
        lines.append(
            f"| {s.name} | {s.count} | {s.total_ms:.1f} | {s.mean_ms:.1f} | "
            f"{s.p50_ms:.1f} | {s.p95_ms:.1f} | {s.max_ms:.1f} | {s.error_count} |"
        )

    if summary.top_tools:
        lines += [
            "",
            "## Top tool invocations",
            "",
            "| Tool | Count | Total ms | Mean ms | Errors |",
            "|------|------:|---------:|--------:|-------:|",
        ]
        for t in summary.top_tools[:top]:
            lines.append(
                f"| {t.tool} | {t.count} | {t.total_ms:.1f} | {t.mean_ms:.1f} | {t.errors} |"
            )

    if summary.errors:
        lines += [
            "",
            "## Errors",
            "",
        ]
        for n in summary.errors[:top]:
            lines.append(
                f"- `{n.name}` ({n.duration_ms:.1f} ms, trace={n.trace_id}): {n.error}"
            )

    if include_tree and roots:
        lines += ["", "## Trace tree", "", "```", render_tree(roots), "```"]

    return "\n".join(lines)


def summary_to_json(summary: TraceSummary, *, top: int = 20) -> dict:
    return {
        "event_count": summary.event_count,
        "span_count": summary.span_count,
        "trace_count": summary.trace_count,
        "errors": [
            {
                "name": n.name,
                "trace_id": n.trace_id,
                "span_id": n.span_id,
                "duration_ms": n.duration_ms,
                "error": n.error,
            }
            for n in summary.errors[:top]
        ],
        "name_stats": [
            {
                "name": s.name,
                "count": s.count,
                "total_ms": s.total_ms,
                "mean_ms": s.mean_ms,
                "p50_ms": s.p50_ms,
                "p95_ms": s.p95_ms,
                "max_ms": s.max_ms,
                "error_count": s.error_count,
            }
            for s in sorted(summary.name_stats.values(), key=lambda s: -s.total_ms)
        ],
        "top_tools": [
            {
                "tool": t.tool,
                "count": t.count,
                "total_ms": t.total_ms,
                "mean_ms": t.mean_ms,
                "errors": t.errors,
            }
            for t in summary.top_tools[:top]
        ],
    }
