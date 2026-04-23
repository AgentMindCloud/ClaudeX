"""Eval case + observation + result types.

A `Scorer` is any callable that takes `(case, observation)` and returns a
`Score`. Scorers can be sync or async; the runner awaits as needed.

`Observation` wraps everything the runner captured from one case
execution (final response, tool invocations, telemetry events, any
raised error). Convenience properties pull commonly-used aggregates out
of the telemetry stream so scorers don't each have to re-implement them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Sequence, Union

from ..clients.grok import GrokMessage, GrokResponse
from ..telemetry import SPAN_END, Event
from ..tools.orchestrator import ToolInvocation
from ..tools.registry import Tool


@dataclass(frozen=True)
class Score:
    name: str
    passed: bool
    detail: str = ""
    measure: float | int | str | None = None

    @classmethod
    def ok(cls, name: str, *, measure: float | int | str | None = None) -> "Score":
        return cls(name=name, passed=True, measure=measure)

    @classmethod
    def fail(cls, name: str, detail: str, *, measure: float | int | str | None = None) -> "Score":
        return cls(name=name, passed=False, detail=detail, measure=measure)


Scorer = Callable[["EvalCase", "Observation"], Union[Score, Awaitable[Score]]]


@dataclass
class EvalCase:
    name: str
    messages: list[GrokMessage]
    tools: list[Tool] = field(default_factory=list)
    system: str | None = None
    scorers: list[Scorer] = field(default_factory=list)
    max_steps: int = 8
    dry_run: bool = False
    baseline: Path | str | None = None  # path to a JsonlSink trace


@dataclass
class Observation:
    final_response: GrokResponse | None
    messages: list[GrokMessage]
    invocations: list[ToolInvocation]
    events: list[Event]
    error: str | None = None

    # -------- convenience aggregates over the event stream --------
    def span_ends(self, *, name: str | None = None) -> list[Event]:
        return [
            e
            for e in self.events
            if e.kind == SPAN_END and (name is None or e.name == name)
        ]

    @property
    def chat_spans(self) -> list[Event]:
        return self.span_ends(name="grok.chat")

    @property
    def tool_invoke_spans(self) -> list[Event]:
        return self.span_ends(name="tool.invoke")

    @property
    def root_span(self) -> Event | None:
        roots = [e for e in self.span_ends() if e.parent_span_id is None]
        return roots[0] if roots else None

    @property
    def total_tokens(self) -> int:
        return sum(int(e.data.get("total_tokens", 0) or 0) for e in self.chat_spans)

    @property
    def total_latency_ms(self) -> float:
        root = self.root_span
        return float(root.duration_ms or 0.0) if root else 0.0

    @property
    def answer(self) -> str:
        return self.final_response.content if self.final_response else ""

    @property
    def tool_call_order(self) -> list[str]:
        return [i.name for i in self.invocations]


@dataclass
class EvalResult:
    case: str
    passed: bool
    scores: list[Score]
    observation: Observation
    baseline_diff: dict[str, Any] | None = None

    @property
    def failed_scores(self) -> list[Score]:
        return [s for s in self.scores if not s.passed]

    def to_summary(self) -> dict[str, Any]:
        return {
            "case": self.case,
            "passed": self.passed,
            "scores": {s.name: s.passed for s in self.scores},
            "tokens": self.observation.total_tokens,
            "latency_ms": round(self.observation.total_latency_ms, 2),
            "error": self.observation.error,
            "baseline_diff": self.baseline_diff,
        }


@dataclass
class EvalReport:
    results: list[EvalResult]

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total_tokens(self) -> int:
        return sum(r.observation.total_tokens for r in self.results)

    @property
    def total_latency_ms(self) -> float:
        return sum(r.observation.total_latency_ms for r in self.results)

    def to_summary(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "failed": self.failed,
            "total": len(self.results),
            "total_tokens": self.total_tokens,
            "total_latency_ms": round(self.total_latency_ms, 2),
            "cases": [r.to_summary() for r in self.results],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Frok Eval Report",
            "",
            f"- Passed: {self.passed} / {len(self.results)}",
            f"- Failed: {self.failed}",
            f"- Total tokens: {self.total_tokens}",
            f"- Total time: {self.total_latency_ms:.1f} ms",
            "",
            "| Case | Result | Tokens | ms | Failed scorers |",
            "|------|--------|--------|----|----------------|",
        ]
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            failed = ", ".join(s.name for s in r.failed_scores) or "-"
            lines.append(
                f"| {r.case} | {status} | {r.observation.total_tokens} | "
                f"{r.observation.total_latency_ms:.1f} | {failed} |"
            )
        lines.append("")

        for r in self.results:
            if r.passed:
                continue
            lines.append(f"## FAIL: {r.case}")
            for s in r.failed_scores:
                lines.append(f"- **{s.name}**: {s.detail}")
            if r.observation.error:
                lines.append(f"- Run error: `{r.observation.error}`")
            if r.baseline_diff and r.baseline_diff.get("regressed", False):
                lines.append(f"- Baseline regression: {r.baseline_diff}")
            lines.append("")

        return "\n".join(lines)
