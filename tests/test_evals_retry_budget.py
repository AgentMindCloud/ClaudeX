"""Tests for ``EvalResult.retry_budget`` — the attempts / budget ratio
surfaced in the eval report. Complements test_evals_attempts which
covers attempts alone.
"""

import json
from pathlib import Path

import pytest

from frok.cli import main
from frok.clients.grok import GrokResponse
from frok.evals import EvalReport, EvalResult
from frok.evals.case import Observation, Score


def _obs() -> Observation:
    return Observation(
        final_response=GrokResponse(content="ok", model="grok-4", raw={}),
        messages=[],
        invocations=[],
        events=[],
        error=None,
    )


def _result(
    name: str = "c",
    *,
    passed: bool = True,
    attempts: int = 1,
    retry_budget: int = 1,
    repeats: int = 1,
    repeat: int = 0,
) -> EvalResult:
    return EvalResult(
        case=name,
        passed=passed,
        scores=[Score.ok("s")] if passed else [Score.fail("s", "nope")],
        observation=_obs(),
        repeat=repeat,
        repeats=repeats,
        attempts=attempts,
        retry_budget=retry_budget,
    )


# ---------------------------------------------------------------------------
# field default + to_summary gating
# ---------------------------------------------------------------------------
def test_budget_defaults_to_one():
    assert _result().retry_budget == 1


def test_summary_omits_budget_when_one():
    assert "retry_budget" not in _result().to_summary()


def test_summary_includes_budget_when_above_one():
    r = _result(attempts=1, retry_budget=5)
    assert r.to_summary()["retry_budget"] == 5


# ---------------------------------------------------------------------------
# report-level properties + summary surfacing
# ---------------------------------------------------------------------------
def test_report_has_retry_budget_when_any_above_one():
    rep = EvalReport(
        results=[_result("a"), _result("b", attempts=1, retry_budget=4)]
    )
    assert rep._has_retry_budget is True
    assert rep.total_budget == 5


def test_report_summary_surfaces_budget_when_allocated_but_unused():
    # Budget=4 on one case, never-retried (attempts=1). Summary should
    # still surface the allocation — operator gets "used 2 of 5 attempts"
    # even though no retry actually happened.
    rep = EvalReport(
        results=[_result("a"), _result("b", attempts=1, retry_budget=4)]
    )
    out = rep.to_summary()
    assert out["total_attempts"] == 2
    assert out["total_budget"] == 5
    assert out["retried_cases"] == 0


def test_report_summary_clean_when_no_budget_anywhere():
    rep = EvalReport(results=[_result("a"), _result("b")])
    out = rep.to_summary()
    assert "total_attempts" not in out
    assert "total_budget" not in out
    assert "retried_cases" not in out


# ---------------------------------------------------------------------------
# markdown surfacing: attempts/budget column
# ---------------------------------------------------------------------------
def test_flat_markdown_shows_attempts_over_budget():
    # a: budget=3 used 1; b: budget=3 used 3 (exhausted but won).
    rep = EvalReport(
        results=[
            _result("a", attempts=1, retry_budget=3),
            _result("b", attempts=3, retry_budget=3),
        ]
    )
    md = rep.to_markdown()
    assert "Attempts/Budget" in md
    # Summary line uses "used X of Y attempts" phrasing.
    assert "Retried cases: 1 (used 4 of 6 attempts)" in md
    # Each row shows its own ratio.
    lines = md.splitlines()
    row_a = next(line for line in lines if line.startswith("| a "))
    row_b = next(line for line in lines if line.startswith("| b "))
    cells_a = [c.strip() for c in row_a.split("|")]
    cells_b = [c.strip() for c in row_b.split("|")]
    assert cells_a[3] == "1/3"
    assert cells_b[3] == "3/3"


def test_flat_markdown_budget_only_surfaces_when_allocated():
    # No budget > 1 anywhere — column stays hidden.
    rep = EvalReport(results=[_result("a"), _result("b")])
    md = rep.to_markdown()
    assert "Attempts/Budget" not in md
    assert "Retried cases" not in md


def test_aggregated_markdown_shows_summed_attempts_over_summed_budget():
    # Two repeats of 'a', each with budget=4. First used 1, second used 4.
    rep = EvalReport(
        results=[
            _result("a", repeat=0, repeats=2, attempts=1, retry_budget=4),
            _result("a", repeat=1, repeats=2, attempts=4, retry_budget=4),
        ]
    )
    md = rep.to_markdown()
    assert "Attempts/Budget" in md
    assert "Retried cases: 1 (used 5 of 8 attempts)" in md
    row = next(line for line in md.splitlines() if line.startswith("| a "))
    cells = [c.strip() for c in row.split("|")]
    # Cells after "| a | 100% | 2/2 | PASS |": attempts/budget = 5/8
    assert cells[5] == "5/8"


# ---------------------------------------------------------------------------
# CLI plumbing: retry loop stamps retry_budget onto the result
# ---------------------------------------------------------------------------
_FLAKY_TEMPLATE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list

    async def __call__(self, *, method, url, headers, body, timeout):
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


_responses_a = [_final(t) for t in __RESPONSES_A__]
_responses_b = [_final(t) for t in __RESPONSES_B__]


def make_client(config, sink):
    src = _responses_a if _responses_a else _responses_b
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([src.pop(0)]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="__NAME_A__",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
    EvalCase(
        name="__NAME_B__",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


def _two(
    tmp_path: Path,
    *,
    name_a: str,
    name_b: str,
    responses_a: list[str],
    responses_b: list[str],
) -> Path:
    body = (
        _FLAKY_TEMPLATE
        .replace("__NAME_A__", name_a)
        .replace("__NAME_B__", name_b)
        .replace("__RESPONSES_A__", "[" + ", ".join(repr(r) for r in responses_a) + "]")
        .replace("__RESPONSES_B__", "[" + ", ".join(repr(r) for r in responses_b) + "]")
    )
    path = tmp_path / "cases.py"
    path.write_text(body, encoding="utf-8")
    return path


def _run(tmp_path: Path, case_file: Path, *extra: str) -> dict:
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(case_file),
            *extra,
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    return json.loads(summary.read_text(encoding="utf-8"))


def _case(data: dict, name: str) -> dict:
    return next(c for c in data["cases"] if c["case"] == name)


def test_cli_retry_sets_budget_to_retry_plus_one(tmp_path):
    # --retry 3 → budget == 4 on matched case.
    path = _two(
        tmp_path,
        name_a="flaky",
        name_b="ignored",
        responses_a=["nope", "nope", "nope", "nope"],
        responses_b=["ok"],
    )
    data = _run(tmp_path, path, "--retry", "3")
    assert _case(data, "flaky")["retry_budget"] == 4
    # The other case was also retry-eligible (no --retry-on filter).
    assert _case(data, "ignored")["retry_budget"] == 4


def test_cli_retry_on_leaves_non_matched_budget_at_one(tmp_path):
    path = _two(
        tmp_path,
        name_a="flaky-net",
        name_b="deterministic",
        responses_a=["nope", "ok"],
        responses_b=["ok"],
    )
    data = _run(tmp_path, path, "--retry", "3", "--retry-on", "flaky-*")
    # Matched case: budget=4.
    assert _case(data, "flaky-net")["retry_budget"] == 4
    # Non-matched: budget omitted from summary because == 1.
    assert _case(data, "deterministic").get("retry_budget") is None


def test_cli_report_markdown_shows_attempts_over_budget_row(tmp_path):
    # End-to-end: --retry 2 -o out.md, case passes attempt 2 → "2/3" in md.
    path = _two(
        tmp_path,
        name_a="flaky",
        name_b="also",
        responses_a=["nope", "ok"],
        responses_b=["ok"],
    )
    md_path = tmp_path / "report.md"
    code = main(["run", str(path), "--retry", "2", "-o", str(md_path)])
    assert code == 0
    md = md_path.read_text(encoding="utf-8")
    assert "Attempts/Budget" in md
    # flaky row shows 2/3; also row shows 1/3.
    flaky_row = next(line for line in md.splitlines() if "flaky" in line)
    also_row = next(
        line for line in md.splitlines() if line.startswith("| also ")
    )
    assert "2/3" in flaky_row
    assert "1/3" in also_row
