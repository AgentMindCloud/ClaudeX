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
    # Pins the model's tool-selection behaviour when `tools` is set.
    # ``None`` leaves the decision to the orchestrator's default
    # ("auto"); ``"none"`` / ``"required"`` / a specific function dict
    # force the model. Ignored on cases with no tools.
    tool_choice: str | dict[str, Any] | None = None
    # Per-case model override. ``None`` defers to ``client.model``
    # (set via FROK_CLIENT_MODEL or ClientConfig.model). Useful for
    # comparing a case across model versions without scaffolding two
    # whole clients.
    model: str | None = None
    # Hard wall-clock cap per case. ``None`` means "no timeout". When
    # set, the runner wraps case execution in ``asyncio.wait_for``; on
    # timeout the case fails with a `TimeoutError` Observation.error
    # rather than hanging the whole suite. Catches truly-stuck runs
    # that `LatencyWithin` / `LatencyDeltaWithin` can only assert on
    # AFTER completion.
    timeout_s: float | None = None
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
    repeat: int = 0  # 0-based index of this run within the case's repeats
    repeats: int = 1  # total repeats requested for this case
    # Number of runner invocations that produced this result. 1 is the
    # baseline (no retry); higher means the CLI retry loop re-ran the
    # case (see `frok run --retry N`). Surfaced so flaky cases stay
    # visible in the verdict doc even when retries masked the failure.
    attempts: int = 1
    # Total attempts the retry loop was permitted to spend on this
    # result, i.e. ``args.retry + 1`` when the case was eligible for
    # retries, else 1. Combined with ``attempts``, this gives an
    # "attempts / budget" ratio — a softer flake signal than the
    # binary retried/not-retried flag ("3/5" means we caught it on
    # attempt 3 out of 5 allowed).
    retry_budget: int = 1

    @property
    def failed_scores(self) -> list[Score]:
        return [s for s in self.scores if not s.passed]

    def to_summary(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "case": self.case,
            "passed": self.passed,
            "scores": {s.name: s.passed for s in self.scores},
            "tokens": self.observation.total_tokens,
            "latency_ms": round(self.observation.total_latency_ms, 2),
            "error": self.observation.error,
            "baseline_diff": self.baseline_diff,
        }
        if self.repeats > 1:
            out["repeat"] = self.repeat
            out["repeats"] = self.repeats
        if self.attempts > 1:
            out["attempts"] = self.attempts
        if self.retry_budget > 1:
            out["retry_budget"] = self.retry_budget
        return out


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

    # -- repeat-aware groupings -----------------------------------------
    @property
    def by_case(self) -> dict[str, list[EvalResult]]:
        groups: dict[str, list[EvalResult]] = {}
        for r in self.results:
            groups.setdefault(r.case, []).append(r)
        return groups

    @property
    def case_pass_rates(self) -> dict[str, float]:
        return {
            name: sum(1 for r in results if r.passed) / len(results)
            for name, results in self.by_case.items()
        }

    @property
    def total_cases(self) -> int:
        return len(self.by_case)

    @property
    def passed_cases(self) -> int:
        return sum(1 for rate in self.case_pass_rates.values() if rate == 1.0)

    @property
    def failed_cases(self) -> int:
        return sum(1 for rate in self.case_pass_rates.values() if rate == 0.0)

    @property
    def flaky_cases(self) -> int:
        return sum(1 for rate in self.case_pass_rates.values() if 0.0 < rate < 1.0)

    @property
    def _has_repeats(self) -> bool:
        return any(r.repeats > 1 for r in self.results)

    @property
    def _has_retries(self) -> bool:
        """True when any result consumed more than one attempt."""
        return any(r.attempts > 1 for r in self.results)

    @property
    def _has_retry_budget(self) -> bool:
        """True when any result was allocated a retry budget > 1."""
        return any(r.retry_budget > 1 for r in self.results)

    @property
    def total_attempts(self) -> int:
        return sum(r.attempts for r in self.results)

    @property
    def total_budget(self) -> int:
        return sum(r.retry_budget for r in self.results)

    @property
    def retried_cases(self) -> int:
        """Count of cases where any repeat needed more than one attempt."""
        return sum(
            1
            for results in self.by_case.values()
            if any(r.attempts > 1 for r in results)
        )

    def to_summary(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "passed": self.passed,
            "failed": self.failed,
            "total": len(self.results),
            "total_tokens": self.total_tokens,
            "total_latency_ms": round(self.total_latency_ms, 2),
            "cases": [r.to_summary() for r in self.results],
        }
        if self._has_repeats:
            out["total_cases"] = self.total_cases
            out["passed_cases"] = self.passed_cases
            out["failed_cases"] = self.failed_cases
            out["flaky_cases"] = self.flaky_cases
            out["case_pass_rates"] = self.case_pass_rates
        if self._has_retries or self._has_retry_budget:
            out["total_attempts"] = self.total_attempts
            out["retried_cases"] = self.retried_cases
            out["total_budget"] = self.total_budget
        return out

    def to_markdown(self) -> str:
        if not self._has_repeats:
            return self._to_markdown_flat()
        return self._to_markdown_aggregated()

    def _to_markdown_flat(self) -> str:
        show_attempts = self._has_retries or self._has_retry_budget
        lines = [
            "# Frok Eval Report",
            "",
            f"- Passed: {self.passed} / {len(self.results)}",
            f"- Failed: {self.failed}",
            f"- Total tokens: {self.total_tokens}",
            f"- Total time: {self.total_latency_ms:.1f} ms",
        ]
        if show_attempts:
            lines.append(
                f"- Retried cases: {self.retried_cases} "
                f"(used {self.total_attempts} of {self.total_budget} "
                f"attempts)"
            )
        lines.append("")
        if show_attempts:
            lines.append(
                "| Case | Result | Attempts/Budget | Tokens | ms | "
                "Failed scorers |"
            )
            lines.append(
                "|------|--------|-----------------|-------:|---:|"
                "----------------|"
            )
        else:
            lines.append("| Case | Result | Tokens | ms | Failed scorers |")
            lines.append("|------|--------|--------|----|----------------|")
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            failed = ", ".join(s.name for s in r.failed_scores) or "-"
            if show_attempts:
                lines.append(
                    f"| {r.case} | {status} | {r.attempts}/{r.retry_budget} "
                    f"| {r.observation.total_tokens} | "
                    f"{r.observation.total_latency_ms:.1f} | {failed} |"
                )
            else:
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

    def _to_markdown_aggregated(self) -> str:
        rates = self.case_pass_rates
        show_attempts = self._has_retries or self._has_retry_budget
        lines = [
            "# Frok Eval Report",
            "",
            f"- Cases passed: {self.passed_cases} / {self.total_cases}",
            f"- Flaky cases: {self.flaky_cases}",
            f"- Failed cases: {self.failed_cases}",
            f"- Total runs: {len(self.results)} "
            f"({self.passed} passed, {self.failed} failed)",
            f"- Total tokens: {self.total_tokens}",
            f"- Total time: {self.total_latency_ms:.1f} ms",
        ]
        if show_attempts:
            lines.append(
                f"- Retried cases: {self.retried_cases} "
                f"(used {self.total_attempts} of {self.total_budget} "
                f"attempts)"
            )
        lines.append("")
        if show_attempts:
            lines.append(
                "| Case | Pass rate | Passed | Result | Attempts/Budget | "
                "Tokens | ms | Failed scorers |"
            )
            lines.append(
                "|------|----------:|-------:|--------|-----------------|"
                "-------:|---:|----------------|"
            )
        else:
            lines.append(
                "| Case | Pass rate | Passed | Result | Tokens | ms | "
                "Failed scorers |"
            )
            lines.append(
                "|------|----------:|-------:|--------|-------:|---:|"
                "----------------|"
            )
        for name, results in self.by_case.items():
            total = len(results)
            passed = sum(1 for r in results if r.passed)
            rate = rates[name]
            if rate == 1.0:
                verdict = "PASS"
            elif rate == 0.0:
                verdict = "FAIL"
            else:
                verdict = "FLAKY"
            failed_scorer_names = sorted(
                {s.name for r in results for s in r.failed_scores}
            )
            failed = ", ".join(failed_scorer_names) or "-"
            tokens = sum(r.observation.total_tokens for r in results)
            ms = sum(r.observation.total_latency_ms for r in results)
            attempts_total = sum(r.attempts for r in results)
            budget_total = sum(r.retry_budget for r in results)
            if show_attempts:
                lines.append(
                    f"| {name} | {rate * 100:.0f}% | {passed}/{total} | "
                    f"{verdict} | {attempts_total}/{budget_total} | "
                    f"{tokens} | {ms:.1f} | {failed} |"
                )
            else:
                lines.append(
                    f"| {name} | {rate * 100:.0f}% | {passed}/{total} | "
                    f"{verdict} | {tokens} | {ms:.1f} | {failed} |"
                )
        lines.append("")

        # Per-case detail only for non-all-passing cases.
        for name, results in self.by_case.items():
            if rates[name] == 1.0:
                continue
            header = "FLAKY" if 0.0 < rates[name] < 1.0 else "FAIL"
            lines.append(f"## {header}: {name} ({rates[name] * 100:.0f}%)")
            for r in results:
                if r.passed:
                    lines.append(f"- repeat {r.repeat}: PASS")
                    continue
                fails = ", ".join(s.name for s in r.failed_scores) or "run error"
                lines.append(f"- repeat {r.repeat}: FAIL ({fails})")
                if r.observation.error:
                    lines.append(f"  - run error: `{r.observation.error}`")
            lines.append("")
        return "\n".join(lines)

        return "\n".join(lines)
