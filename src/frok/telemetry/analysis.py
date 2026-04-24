"""Post-hoc trace analysis: reconstruct tree + aggregate stats.

Consumes an iterable of `Event`s (typically from `read_jsonl` replaying a
`JsonlSink` capture) and produces:

* a `list[TraceNode]` tree keyed on `parent_span_id`,
* a `TraceSummary` with per-name duration stats, errored-span list, and
  top-tool aggregates, and
* for an entire directory of captures: a `DirectorySummary` with a
  per-case rollup and cross-case leaders.

Used by ``frok trace inspect`` and ``frok eval summarize``; also callable
as a library for tests / notebooks / ad-hoc diagnostics.
"""

from __future__ import annotations

from pathlib import Path

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


# ---------------------------------------------------------------------------
# directory-level aggregation (`frok eval summarize <dir>`)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CaseSummary:
    """Per-capture rollup for a single `<slug>.jsonl` file."""

    name: str
    path: str
    spans: int
    total_tokens: int
    error_count: int
    duration_ms: float  # sum of root-span durations
    tool_counts: dict[str, int]
    errored_tool_counts: dict[str, int]


@dataclass
class DirectorySummary:
    directory: str
    cases: list[CaseSummary]

    @property
    def total_spans(self) -> int:
        return sum(c.spans for c in self.cases)

    @property
    def total_tokens(self) -> int:
        return sum(c.total_tokens for c in self.cases)

    @property
    def total_errors(self) -> int:
        return sum(c.error_count for c in self.cases)

    @property
    def tool_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.cases:
            for k, v in c.tool_counts.items():
                out[k] = out.get(k, 0) + v
        return out

    @property
    def errored_tool_counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.cases:
            for k, v in c.errored_tool_counts.items():
                out[k] = out.get(k, 0) + v
        return out

    def slowest(self, n: int = 5) -> list[CaseSummary]:
        return sorted(self.cases, key=lambda c: -c.duration_ms)[:n]

    def heaviest_tokens(self, n: int = 5) -> list[CaseSummary]:
        return sorted(self.cases, key=lambda c: -c.total_tokens)[:n]

    def most_errors(self, n: int = 5) -> list[CaseSummary]:
        return sorted(
            (c for c in self.cases if c.error_count > 0),
            key=lambda c: -c.error_count,
        )[:n]


def _summarize_events(name: str, path: Path, events: list[Event]) -> CaseSummary:
    summary = summarize(events)
    roots = [
        n for n in _nodes_from(events).values() if n.parent_span_id is None
    ]
    duration = sum(n.duration_ms for n in roots)

    tool_counts: dict[str, int] = {}
    errored_tool_counts: dict[str, int] = {}
    for t in summary.top_tools:
        tool_counts[t.tool] = t.count
        if t.errors:
            errored_tool_counts[t.tool] = t.errors

    return CaseSummary(
        name=name,
        path=str(path),
        spans=summary.span_count,
        total_tokens=sum(
            int(e.data.get("total_tokens", 0) or 0)
            for e in events
            if e.kind == SPAN_END and e.name == "grok.chat"
        ),
        error_count=len(summary.errors),
        duration_ms=duration,
        tool_counts=tool_counts,
        errored_tool_counts=errored_tool_counts,
    )


def summarize_directory(directory: str | Path) -> DirectorySummary:
    """Walk ``<dir>/*.jsonl`` and return a per-case rollup."""
    d = Path(directory)
    if not d.is_dir():
        raise NotADirectoryError(f"not a directory: {directory}")
    cases: list[CaseSummary] = []
    for path in sorted(d.glob("*.jsonl")):
        # Import here to avoid pulling `read_jsonl` at module top — keeps
        # analysis importable without the sink module in odd test envs.
        from .sink import read_jsonl

        events = list(read_jsonl(path))
        if not events:
            continue
        cases.append(_summarize_events(path.stem, path, events))
    return DirectorySummary(directory=str(d), cases=cases)


def dir_summary_to_markdown(
    summary: DirectorySummary, *, top: int = 5
) -> str:
    lines = [
        "# Frok Eval Directory Summary",
        "",
        f"- Directory: `{summary.directory}`",
        f"- Cases: {len(summary.cases)}",
        f"- Total spans: {summary.total_spans}",
        f"- Total tokens: {summary.total_tokens}",
        f"- Total errors: {summary.total_errors}",
        "",
        "## Per-case rollup",
        "",
        "| Case | Spans | Tokens | Errors | Duration ms | Tools |",
        "|------|------:|-------:|-------:|------------:|-------|",
    ]
    for c in summary.cases:
        tools = (
            ", ".join(f"{name}:{count}" for name, count in sorted(c.tool_counts.items()))
            or "-"
        )
        lines.append(
            f"| {c.name} | {c.spans} | {c.total_tokens} | {c.error_count} | "
            f"{c.duration_ms:.1f} | {tools} |"
        )

    if summary.cases:
        lines += ["", "## Cross-case leaders", "", "### Slowest cases"]
        for i, c in enumerate(summary.slowest(top), 1):
            lines.append(f"{i}. `{c.name}` — {c.duration_ms:.1f} ms")

        lines += ["", "### Heaviest token use"]
        for i, c in enumerate(summary.heaviest_tokens(top), 1):
            lines.append(f"{i}. `{c.name}` — {c.total_tokens} tokens")

        most_err = summary.most_errors(top)
        if most_err:
            lines += ["", "### Most-errored cases"]
            for i, c in enumerate(most_err, 1):
                lines.append(f"{i}. `{c.name}` — {c.error_count} errored spans")

        errored_tools = summary.errored_tool_counts
        if errored_tools:
            lines += ["", "### Tools with errors (aggregate)"]
            for name, count in sorted(errored_tools.items(), key=lambda kv: -kv[1])[:top]:
                lines.append(f"- `{name}` — {count}")

        tools = summary.tool_counts
        if tools:
            lines += ["", "### Top tools by invocation count (aggregate)"]
            for name, count in sorted(tools.items(), key=lambda kv: -kv[1])[:top]:
                lines.append(f"- `{name}` — {count}")

    return "\n".join(lines) + "\n"


def dir_summary_to_json(
    summary: DirectorySummary, *, top: int = 5
) -> dict[str, Any]:
    return {
        "directory": summary.directory,
        "total_spans": summary.total_spans,
        "total_tokens": summary.total_tokens,
        "total_errors": summary.total_errors,
        "cases": [
            {
                "name": c.name,
                "path": c.path,
                "spans": c.spans,
                "total_tokens": c.total_tokens,
                "error_count": c.error_count,
                "duration_ms": c.duration_ms,
                "tool_counts": c.tool_counts,
                "errored_tool_counts": c.errored_tool_counts,
            }
            for c in summary.cases
        ],
        "slowest": [
            {"name": c.name, "duration_ms": c.duration_ms}
            for c in summary.slowest(top)
        ],
        "heaviest_tokens": [
            {"name": c.name, "total_tokens": c.total_tokens}
            for c in summary.heaviest_tokens(top)
        ],
        "most_errors": [
            {"name": c.name, "error_count": c.error_count}
            for c in summary.most_errors(top)
        ],
        "tool_counts": summary.tool_counts,
        "errored_tool_counts": summary.errored_tool_counts,
    }
