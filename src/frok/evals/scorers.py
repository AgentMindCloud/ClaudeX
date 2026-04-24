"""Built-in scorers for truthfulness + tool-behavior regressions.

All scorers are plain dataclasses with `__call__(case, obs) -> Score`.
Keep them pure: no I/O, no mutation of inputs. Compose them in
`EvalCase.scorers`.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from ..telemetry import read_jsonl
from .baseline import diff_event_streams
from .case import EvalCase, Observation, Score


# ---------------------------------------------------------------------------
# answer / truthfulness
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AnswerContains:
    substring: str
    case_sensitive: bool = False

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        name = f"answer_contains[{self.substring!r}]"
        content = obs.answer
        hay = content if self.case_sensitive else content.lower()
        needle = self.substring if self.case_sensitive else self.substring.lower()
        if needle in hay:
            return Score.ok(name)
        return Score.fail(name, f"answer={content!r}")


@dataclass(frozen=True)
class AnswerMatches:
    pattern: str
    flags: int = 0

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        name = f"answer_matches[{self.pattern!r}]"
        if re.search(self.pattern, obs.answer, self.flags):
            return Score.ok(name)
        return Score.fail(name, f"answer={obs.answer!r}")


@dataclass(frozen=True)
class AnswerAbsent:
    """Fails if `substring` is present — guards against known-wrong answers."""

    substring: str
    case_sensitive: bool = False

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        name = f"answer_absent[{self.substring!r}]"
        content = obs.answer
        hay = content if self.case_sensitive else content.lower()
        needle = self.substring if self.case_sensitive else self.substring.lower()
        if needle in hay:
            return Score.fail(name, f"disallowed substring present: answer={content!r}")
        return Score.ok(name)


@dataclass(frozen=True)
class AnswerLength:
    """Assert the assembled response length stays within a range.

    Complements `AnswerContains` / `AnswerMatches` (content) with a
    *shape* check. Catches prompt regressions that start producing one-
    word replies (set ``min_chars``) or runaway prompts that emit long
    preambles before the actual answer (set ``max_chars``). At least one
    bound is required; both can be set for a closed range. Character-
    based (not tokens); operators who need token-level gating layer
    ``TokensWithin`` alongside.
    """

    min_chars: int | None = None
    max_chars: int | None = None

    def __post_init__(self) -> None:
        if self.min_chars is None and self.max_chars is None:
            raise ValueError(
                "AnswerLength requires at least one of min_chars or max_chars"
            )
        if self.min_chars is not None and self.min_chars < 0:
            raise ValueError(f"min_chars must be >= 0, got {self.min_chars}")
        if self.max_chars is not None and self.max_chars < 0:
            raise ValueError(f"max_chars must be >= 0, got {self.max_chars}")
        if (
            self.min_chars is not None
            and self.max_chars is not None
            and self.min_chars > self.max_chars
        ):
            raise ValueError(
                f"min_chars ({self.min_chars}) > max_chars ({self.max_chars})"
            )

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        bounds: list[str] = []
        if self.min_chars is not None:
            bounds.append(f">={self.min_chars}")
        if self.max_chars is not None:
            bounds.append(f"<={self.max_chars}")
        sname = f"answer_length[{','.join(bounds)}]"

        length = len(obs.answer)
        if self.min_chars is not None and length < self.min_chars:
            return Score.fail(
                sname,
                f"length {length} < min {self.min_chars}",
                measure=length,
            )
        if self.max_chars is not None and length > self.max_chars:
            return Score.fail(
                sname,
                f"length {length} > max {self.max_chars}",
                measure=length,
            )
        return Score.ok(sname, measure=length)


@dataclass(frozen=True)
class NoSafetyBlocks:
    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        name = "no_safety_blocks"
        blocked = [
            e for e in obs.chat_spans if e.data.get("safety_blocked") is not None
        ]
        if not blocked:
            return Score.ok(name)
        kinds = sorted({e.data.get("safety_blocked") for e in blocked})
        return Score.fail(name, f"safety blocks: {kinds}")


# ---------------------------------------------------------------------------
# tool-behavior
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ToolCalled:
    name_: str
    times: int | None = None  # exact count when provided

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"tool_called[{self.name_!r}]"
        observed = [i for i in obs.invocations if i.name == self.name_]
        if self.times is None:
            if observed:
                return Score.ok(sname, measure=len(observed))
            return Score.fail(sname, f"tool {self.name_!r} was not invoked")
        if len(observed) == self.times:
            return Score.ok(sname, measure=len(observed))
        return Score.fail(
            sname,
            f"expected {self.times} calls, got {len(observed)}",
            measure=len(observed),
        )


@dataclass(frozen=True)
class ToolNotCalled:
    name_: str

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"tool_not_called[{self.name_!r}]"
        observed = [i for i in obs.invocations if i.name == self.name_]
        if not observed:
            return Score.ok(sname)
        return Score.fail(sname, f"unexpected {len(observed)} call(s) to {self.name_!r}")


@dataclass(frozen=True)
class ToolArgsSubset:
    """Passes if at least one call to `name_` had args ⊇ `expected`."""

    name_: str
    expected: dict[str, Any]

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"tool_args_subset[{self.name_!r}]"
        hits = [i for i in obs.invocations if i.name == self.name_]
        if not hits:
            return Score.fail(sname, f"tool {self.name_!r} not invoked")
        for inv in hits:
            if all(inv.arguments.get(k) == v for k, v in self.expected.items()):
                return Score.ok(sname)
        seen = [inv.arguments for inv in hits]
        return Score.fail(sname, f"no call matched {self.expected!r}; seen {seen!r}")


@dataclass(frozen=True)
class ToolArgsMatch:
    """Passes if at least one call to ``name_`` has arguments matching a regex.

    * ``field=None`` (default) — regex is applied to the JSON-serialised
      arguments dict (``json.dumps(args, sort_keys=True)``). Use for
      "something anywhere in the args".
    * ``field="<key>"`` — regex is applied to ``str(args[field])``.
      Missing keys don't match. Use for "the ``query`` field contains the
      user's question", etc.

    Matching uses ``re.search`` so partial matches work. Pass ``flags``
    (e.g. ``re.IGNORECASE``) through for the usual knobs. An invalid
    regex fails the scorer cleanly rather than raising from the runner.
    """

    name_: str
    regex: str
    field: str | None = None
    flags: int = 0

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = (
            f"tool_args_match[{self.name_!r}"
            + (f":{self.field}" if self.field else "")
            + "]"
        )
        hits = [i for i in obs.invocations if i.name == self.name_]
        if not hits:
            return Score.fail(sname, f"tool {self.name_!r} not invoked")
        try:
            pattern = re.compile(self.regex, self.flags)
        except re.error as exc:
            return Score.fail(sname, f"invalid regex {self.regex!r}: {exc}")
        seen: list[str] = []
        for inv in hits:
            if self.field is None:
                haystack = json.dumps(inv.arguments, sort_keys=True, default=str)
            else:
                if self.field not in inv.arguments:
                    seen.append("<missing>")
                    continue
                haystack = str(inv.arguments[self.field])
            seen.append(haystack)
            if pattern.search(haystack):
                return Score.ok(sname, measure=haystack)
        return Score.fail(
            sname,
            f"no call matched {self.regex!r}; seen {seen!r}",
        )


@dataclass(frozen=True)
class ToolSequence:
    """Passes if the observed tool order starts with `expected`."""

    expected: tuple[str, ...]

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"tool_sequence[{list(self.expected)}]"
        observed = obs.tool_call_order
        if observed[: len(self.expected)] == list(self.expected):
            return Score.ok(sname)
        return Score.fail(sname, f"observed order {observed!r}")


# ---------------------------------------------------------------------------
# perf / trace
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TokensWithin:
    max_total: int

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"tokens_within[{self.max_total}]"
        used = obs.total_tokens
        if used <= self.max_total:
            return Score.ok(sname, measure=used)
        return Score.fail(sname, f"used {used} > max {self.max_total}", measure=used)


@dataclass(frozen=True)
class LatencyWithin:
    """Wall-clock ceiling: fail unless the case's root-span duration stays
    within ``max_ms``. Complements ``TokensWithin`` (cost) with a latency
    gate — cheap way to catch a prompt / tool-use pattern that quietly
    doubled wall-clock time on a model swap.

    Reads ``obs.total_latency_ms``, which is the duration of the case's
    root span (e.g. ``tool.run`` for tools cases, ``grok.chat`` for
    no-tools cases). A case whose run errored before a root span closed
    reports 0.0 ms and passes any non-negative threshold — the right
    signal is ``NoErrors``, not a latency assertion.
    """

    max_ms: float

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"latency_within[{self.max_ms}]"
        actual = obs.total_latency_ms
        if actual <= self.max_ms:
            return Score.ok(sname, measure=actual)
        return Score.fail(
            sname,
            f"latency {actual:.1f} ms > max {self.max_ms} ms",
            measure=actual,
        )


@dataclass(frozen=True)
class InvocationsWithin:
    """Total-tool-invocation ceiling. Complements ``ToolCalled(..., times=N)``
    (per-tool exact count) with an aggregate "don't loop forever" cap —
    catches a prompt regression that starts over-calling tools without
    needing one scorer per tool.

    Counts ``len(obs.invocations)`` — every tool call the orchestrator
    actually dispatched (regardless of which tool). Cases without tools
    report 0 invocations and pass any non-negative threshold.
    """

    max_count: int

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"invocations_within[{self.max_count}]"
        count = len(obs.invocations)
        if count <= self.max_count:
            return Score.ok(sname, measure=count)
        return Score.fail(
            sname,
            f"{count} tool invocations > max {self.max_count}",
            measure=count,
        )


def _load_baseline_diff(
    case: EvalCase, sname: str, obs: Observation
) -> "Score | dict[str, Any]":
    """Shared loader for baseline-aware scorers. Returns a Score on
    error / missing-baseline paths, or the diff dict on success."""
    if case.baseline is None:
        return Score.fail(
            sname,
            "no baseline attached to case; set case.baseline (or pass "
            "--use-baseline on the CLI) to use this scorer",
        )
    try:
        baseline_events = list(read_jsonl(case.baseline))
    except FileNotFoundError:
        return Score.fail(sname, f"baseline file not found: {case.baseline}")
    except Exception as exc:  # pragma: no cover — defensive
        return Score.fail(sname, f"cannot load baseline {case.baseline}: {exc}")
    return diff_event_streams(
        baseline_events,
        obs.events,
        a_label="baseline",
        b_label="observed",
    )


@dataclass(frozen=True)
class TokenDeltaWithin:
    """Baseline-aware token-drift gate.

    Requires ``case.baseline`` to be set (via ``--use-baseline`` or
    explicit ``EvalCase(baseline=Path(...))``). Loads the baseline
    JSONL, computes ``observed_tokens - baseline_tokens``, and passes
    iff ``abs(delta) <= max_delta``.

    Symmetric by design: catches prompt changes that quietly doubled
    tokens (positive delta) *and* prompt changes that collapsed the
    answer to a one-liner (negative delta, which often signals a
    regression the model is bailing on). The existing baseline differ
    reports the delta but never gates CI on it; this scorer does.
    """

    max_delta: int

    def __post_init__(self) -> None:
        if self.max_delta < 0:
            raise ValueError(
                f"max_delta must be >= 0, got {self.max_delta}"
            )

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"token_delta_within[{self.max_delta}]"
        result = _load_baseline_diff(case, sname, obs)
        if isinstance(result, Score):
            return result
        diff = result
        delta = int(diff["token_delta"])
        if abs(delta) <= self.max_delta:
            return Score.ok(sname, measure=delta)
        return Score.fail(
            sname,
            f"token delta {delta:+d} exceeds max ±{self.max_delta} "
            f"(baseline={diff['baseline_tokens']}, observed={diff['observed_tokens']})",
            measure=delta,
        )


@dataclass(frozen=True)
class LatencyDeltaWithin:
    """Baseline-aware wall-clock-drift gate. Mirrors ``TokenDeltaWithin``
    but on the case's root-span ``duration_ms``.

    Requires ``case.baseline``. Computes
    ``observed_latency_ms - baseline_latency_ms`` from the root span of
    each side (matching `Observation.total_latency_ms` semantics).
    Passes iff ``abs(delta_ms) <= max_ms``.

    Symmetric: catches prompts that slow down *and* prompts that
    finish suspiciously fast (often a sign the model bailed early).
    """

    max_ms: float

    def __post_init__(self) -> None:
        if self.max_ms < 0:
            raise ValueError(f"max_ms must be >= 0, got {self.max_ms}")

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"latency_delta_within[{self.max_ms}]"
        result = _load_baseline_diff(case, sname, obs)
        if isinstance(result, Score):
            return result
        diff = result
        delta = float(diff["latency_delta_ms"])
        if abs(delta) <= self.max_ms:
            return Score.ok(sname, measure=delta)
        return Score.fail(
            sname,
            f"latency delta {delta:+.1f} ms exceeds max ±{self.max_ms} ms "
            f"(baseline={diff['baseline_latency_ms']:.1f}, "
            f"observed={diff['observed_latency_ms']:.1f})",
            measure=delta,
        )


@dataclass(frozen=True)
class NoErrors:
    """Fails if any span recorded an error OR the run itself raised."""

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = "no_errors"
        if obs.error is not None:
            return Score.fail(sname, f"run error: {obs.error}")
        bad = [e for e in obs.span_ends() if e.error is not None]
        if bad:
            details = ", ".join(f"{e.name}:{e.error}" for e in bad[:3])
            return Score.fail(sname, f"{len(bad)} span errors: {details}")
        return Score.ok(sname)


@dataclass(frozen=True)
class ResponseModelIs:
    """Fails unless the assembled ``GrokResponse.model`` matches exactly.

    Complements ``EvalCase.model=...`` — the case pins the request; this
    scorer proves the *response* came from the expected model. Catches
    silent mid-flight model swaps on the provider side that a request-
    only pin can't detect.
    """

    expected: str

    def __call__(self, case: EvalCase, obs: Observation) -> Score:
        sname = f"response_model_is[{self.expected!r}]"
        if obs.final_response is None:
            return Score.fail(
                sname,
                "no final response — run failed before a model could be reported",
            )
        actual = obs.final_response.model
        if actual == self.expected:
            return Score.ok(sname, measure=actual)
        return Score.fail(
            sname,
            f"expected model {self.expected!r}, got {actual!r}",
            measure=actual,
        )
