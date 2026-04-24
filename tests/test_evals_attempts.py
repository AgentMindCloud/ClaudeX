"""Tests for ``EvalResult.attempts`` surfacing.

Covers the pure data types (field default, to_summary, to_markdown) and
the CLI plumbing (retry loop → attempts count on result).
"""

import json
from pathlib import Path

import pytest

from frok.cli import main
from frok.clients.grok import GrokResponse
from frok.evals import EvalReport, EvalResult
from frok.evals.case import Observation, Score


# ---------------------------------------------------------------------------
# data helpers
# ---------------------------------------------------------------------------
def _obs(events: list | None = None, *, error: str | None = None) -> Observation:
    return Observation(
        final_response=GrokResponse(content="ok", model="grok-4", raw={}),
        messages=[],
        invocations=[],
        events=events or [],
        error=error,
    )


def _result(
    name: str = "c",
    *,
    passed: bool = True,
    attempts: int = 1,
    retry_budget: int | None = None,
    repeats: int = 1,
    repeat: int = 0,
) -> EvalResult:
    # Default budget tracks attempts so the ratio stays sane in direct
    # construction tests; the CLI sets both explicitly.
    if retry_budget is None:
        retry_budget = max(attempts, 1)
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
# EvalResult: field default + to_summary gating
# ---------------------------------------------------------------------------
def test_result_attempts_defaults_to_one():
    r = _result()
    assert r.attempts == 1


def test_result_summary_omits_attempts_when_one():
    r = _result()
    assert "attempts" not in r.to_summary()


def test_result_summary_includes_attempts_when_greater_than_one():
    r = _result(attempts=3)
    assert r.to_summary()["attempts"] == 3


# ---------------------------------------------------------------------------
# EvalReport: _has_retries, totals, summary gating
# ---------------------------------------------------------------------------
def test_report_has_retries_false_when_all_default():
    rep = EvalReport(results=[_result("a"), _result("b")])
    assert rep._has_retries is False
    assert rep.total_attempts == 2
    assert rep.retried_cases == 0


def test_report_has_retries_true_when_any_above_one():
    rep = EvalReport(results=[_result("a"), _result("b", attempts=2)])
    assert rep._has_retries is True
    assert rep.total_attempts == 3
    assert rep.retried_cases == 1


def test_report_summary_omits_retry_fields_when_no_retries():
    rep = EvalReport(results=[_result("a")])
    out = rep.to_summary()
    assert "total_attempts" not in out
    assert "retried_cases" not in out


def test_report_summary_includes_retry_fields_when_any():
    rep = EvalReport(
        results=[_result("a"), _result("b", attempts=3, passed=False)]
    )
    out = rep.to_summary()
    assert out["total_attempts"] == 4
    assert out["retried_cases"] == 1


# ---------------------------------------------------------------------------
# markdown flat: column appears only when retries happen
# ---------------------------------------------------------------------------
def test_markdown_flat_omits_attempts_column_by_default():
    rep = EvalReport(results=[_result("a"), _result("b")])
    md = rep.to_markdown()
    assert "Attempts" not in md
    assert "Retried cases" not in md


def test_markdown_flat_includes_attempts_column_when_retried():
    # a: budget=3 never used (attempts=1); b: budget=3 exhausted-but-won.
    rep = EvalReport(
        results=[
            _result("a", attempts=1, retry_budget=3),
            _result("b", attempts=3, retry_budget=3),
        ]
    )
    md = rep.to_markdown()
    assert "Attempts/Budget" in md
    assert "Retried cases: 1 (used 4 of 6 attempts)" in md
    # Row shows attempts/budget ratio per result.
    row_b = next(line for line in md.splitlines() if line.startswith("| b "))
    cells = [c.strip() for c in row_b.split("|")]
    # cells[0]=='', cells[1]=='b', cells[2]=='PASS', cells[3]=='3/3', ...
    assert cells[3] == "3/3"


# ---------------------------------------------------------------------------
# markdown aggregated: column appears only when retries happen
# ---------------------------------------------------------------------------
def test_markdown_aggregated_omits_attempts_when_clean():
    # Two repeats, no retries → aggregated form, no Attempts column.
    rep = EvalReport(
        results=[
            _result("a", repeat=0, repeats=2),
            _result("a", repeat=1, repeats=2),
        ]
    )
    md = rep.to_markdown()
    assert "Pass rate" in md  # aggregated header, confirms form
    assert "Attempts" not in md
    assert "Retried cases" not in md


def test_markdown_aggregated_includes_attempts_when_retried():
    # Two repeats, both with budget=4; first attempts=1, second attempts=4.
    rep = EvalReport(
        results=[
            _result("a", repeat=0, repeats=2, attempts=1, retry_budget=4),
            _result("a", repeat=1, repeats=2, attempts=4, retry_budget=4),
        ]
    )
    md = rep.to_markdown()
    assert "Attempts/Budget" in md
    assert "Retried cases: 1 (used 5 of 8 attempts)" in md
    # Per-case totals summed across repeats: 5 attempts / 8 budget.
    row = next(line for line in md.splitlines() if line.startswith("| a "))
    # Cells: | a | 100% | 2/2 | PASS | 5/8 | tokens | ms | failed |
    cells = [c.strip() for c in row.split("|")]
    assert cells[5] == "5/8"


# ---------------------------------------------------------------------------
# CLI plumbing: retry loop records attempt count on the result
# ---------------------------------------------------------------------------
_FLAKY_TEMPLATE = '''
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

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


_responses = [_final(t) for t in __RESPONSES__]


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_responses.pop(0)]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="target",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


def _flaky(tmp_path: Path, responses: list[str]) -> Path:
    pyreps = "[" + ", ".join(repr(r) for r in responses) + "]"
    body = _FLAKY_TEMPLATE.replace("__RESPONSES__", pyreps)
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


def test_cli_no_retry_leaves_attempts_at_one(tmp_path):
    # No --retry; failing case should have attempts omitted from summary.
    path = _flaky(tmp_path, ["nope"])
    data = _run(tmp_path, path)
    assert data["cases"][0].get("attempts") is None
    assert "total_attempts" not in data


def test_cli_retry_pass_first_attempts_one(tmp_path):
    # --retry 3 but case passes on attempt 1 → attempts stays at 1,
    # but retry_budget surfaces as 4 (the CLI-allocated allowance).
    path = _flaky(tmp_path, ["ok"])
    data = _run(tmp_path, path, "--retry", "3")
    assert data["cases"][0].get("attempts") is None  # omitted when 1
    assert data["cases"][0]["retry_budget"] == 4
    assert data["total_attempts"] == 1
    assert data["total_budget"] == 4
    assert data["retried_cases"] == 0


def test_cli_retry_fail_then_succeed_records_attempts(tmp_path):
    # Two fails then a pass → attempts == 3.
    path = _flaky(tmp_path, ["nope", "nope", "ok"])
    data = _run(tmp_path, path, "--retry", "2")
    assert data["passed"] == 1
    assert data["cases"][0]["attempts"] == 3
    assert data["total_attempts"] == 3
    assert data["retried_cases"] == 1


def test_cli_retry_exhausted_records_attempts(tmp_path):
    # All three fail → attempts == retry+1 == 3.
    path = _flaky(tmp_path, ["nope", "nope", "nope"])
    data = _run(tmp_path, path, "--retry", "2")
    assert data["failed"] == 1
    assert data["cases"][0]["attempts"] == 3
    assert data["total_attempts"] == 3


def test_cli_timeout_short_circuit_leaves_attempts_one(tmp_path):
    # Timeout fires → retry short-circuits → attempts stays at 1 (omitted).
    path = tmp_path / "slow.py"
    path.write_text(
        '''
import asyncio

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, NoErrors
from frok.telemetry import Tracer


async def _slow_transport(*, method, url, headers, body, timeout):
    await asyncio.sleep(5.0)
    return 200, {}, b"{}"


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_slow_transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="slow",
        messages=[GrokMessage("user", "q")],
        scorers=[NoErrors()],
    ),
]
''',
        encoding="utf-8",
    )
    data = _run(tmp_path, path, "--timeout-s", "0.05", "--retry", "5")
    # Exactly one attempt ran: timeouts short-circuit before retries.
    assert data["cases"][0].get("attempts") is None
