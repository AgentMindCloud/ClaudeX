"""Tests for the EvalReport repeat-aware surface."""

from frok.clients.grok import GrokResponse
from frok.evals import EvalReport, EvalResult, Observation, Score


def _result(case: str, passed: bool, *, repeat: int = 0, repeats: int = 1) -> EvalResult:
    return EvalResult(
        case=case,
        passed=passed,
        scores=[Score(name="x", passed=passed)],
        observation=Observation(
            final_response=GrokResponse(model="m", content="", raw={}),
            messages=[],
            invocations=[],
            events=[],
        ),
        repeat=repeat,
        repeats=repeats,
    )


def _report(*results: EvalResult) -> EvalReport:
    return EvalReport(results=list(results))


# ---------------------------------------------------------------------------
# defaults (no repeats): existing shape preserved
# ---------------------------------------------------------------------------
def test_default_repeat_fields():
    r = _result("x", True)
    assert r.repeat == 0
    assert r.repeats == 1


def test_single_repeat_markdown_uses_flat_format():
    report = _report(_result("alpha", True), _result("beta", False))
    md = report.to_markdown()
    assert "# Frok Eval Report" in md
    # Flat-format headline line: "- Passed: 1 / 2"
    assert "Passed: 1 / 2" in md
    # No pass-rate column or aggregate headline.
    assert "Pass rate" not in md
    assert "Cases passed" not in md


def test_single_repeat_summary_is_unchanged():
    report = _report(_result("alpha", True))
    data = report.to_summary()
    assert "case_pass_rates" not in data  # only surfaced when repeats > 1
    assert "total_cases" not in data


# ---------------------------------------------------------------------------
# by_case / case_pass_rates
# ---------------------------------------------------------------------------
def test_by_case_groups_results():
    report = _report(
        _result("a", True, repeat=0, repeats=2),
        _result("a", False, repeat=1, repeats=2),
        _result("b", True, repeat=0, repeats=2),
        _result("b", True, repeat=1, repeats=2),
    )
    groups = report.by_case
    assert list(groups) == ["a", "b"]
    assert [r.repeat for r in groups["a"]] == [0, 1]


def test_pass_rates_mix_of_flaky_all_pass_all_fail():
    report = _report(
        # a: flaky (1/3)
        _result("a", True, repeat=0, repeats=3),
        _result("a", False, repeat=1, repeats=3),
        _result("a", False, repeat=2, repeats=3),
        # b: all pass
        _result("b", True, repeat=0, repeats=3),
        _result("b", True, repeat=1, repeats=3),
        _result("b", True, repeat=2, repeats=3),
        # c: all fail
        _result("c", False, repeat=0, repeats=3),
        _result("c", False, repeat=1, repeats=3),
        _result("c", False, repeat=2, repeats=3),
    )
    rates = report.case_pass_rates
    assert rates["a"] == 1 / 3
    assert rates["b"] == 1.0
    assert rates["c"] == 0.0
    assert report.total_cases == 3
    assert report.passed_cases == 1
    assert report.flaky_cases == 1
    assert report.failed_cases == 1


# ---------------------------------------------------------------------------
# aggregated markdown format
# ---------------------------------------------------------------------------
def test_aggregated_markdown_has_pass_rate_column_when_repeats_gt_one():
    report = _report(
        _result("a", True, repeat=0, repeats=2),
        _result("a", False, repeat=1, repeats=2),
    )
    md = report.to_markdown()
    assert "Pass rate" in md
    assert "Cases passed:" in md
    assert "Flaky cases:" in md
    # 50% pass rate surfaced as FLAKY verdict.
    assert "FLAKY" in md
    # Per-case section shows which repeats failed.
    assert "## FLAKY: a" in md
    assert "repeat 1: FAIL" in md


def test_aggregated_markdown_shows_pass_only_header_when_no_failures():
    report = _report(
        _result("a", True, repeat=0, repeats=2),
        _result("a", True, repeat=1, repeats=2),
    )
    md = report.to_markdown()
    assert "100%" in md
    assert "## FAIL" not in md
    assert "## FLAKY" not in md


def test_aggregated_summary_includes_pass_rates():
    report = _report(
        _result("a", True, repeat=0, repeats=2),
        _result("a", False, repeat=1, repeats=2),
    )
    data = report.to_summary()
    assert data["total_cases"] == 1
    assert data["flaky_cases"] == 1
    assert data["case_pass_rates"] == {"a": 0.5}
    # Per-run summary carries the repeat metadata too.
    assert all("repeats" in c for c in data["cases"])
