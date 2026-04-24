"""Unit tests for ``format_retry_report``."""

from frok.evals import format_retry_report


def _entry(case, *, repeat=0, attempts_list, passed=None, budget=None):
    attempts = [
        {
            "attempt": i + 1,
            "passed": ok,
            "error": err,
            "sleep_before_ms": ms,
        }
        for i, (ok, err, ms) in enumerate(attempts_list)
    ]
    if passed is None:
        passed = bool(attempts_list) and bool(attempts_list[-1][0])
    if budget is None:
        budget = len(attempts_list) or 1
    return {
        "case": case,
        "repeat": repeat,
        "attempts": attempts,
        "retry_budget": budget,
        "passed": passed,
    }


def _payload(*entries):
    return {"cases": list(entries)}


# ---------------------------------------------------------------------------
# summary bloc
# ---------------------------------------------------------------------------
def test_summary_bloc_counts_everything():
    payload = _payload(
        _entry("a", attempts_list=[(True, None, 0.0)], budget=4),
        _entry(
            "b",
            attempts_list=[(False, "err", 0.0), (True, None, 100.0)],
            budget=4,
        ),
        _entry(
            "c",
            attempts_list=[(False, "err", 0.0)],
            budget=4,
        ),
    )
    md = format_retry_report(payload, path="x.json")
    assert "- Source: `x.json`" in md
    assert "- Cases: 3" in md
    assert "- Passed: 2" in md
    assert "- Failed: 1" in md
    assert "- Retried cases: 1" in md  # only case b had more than one attempt
    assert "- Attempts / Budget: 4 / 12" in md


def test_summary_bloc_no_path_omits_source_line():
    payload = _payload(_entry("a", attempts_list=[(True, None, 0.0)]))
    md = format_retry_report(payload)
    assert "Source" not in md


# ---------------------------------------------------------------------------
# clean passes bucket
# ---------------------------------------------------------------------------
def test_clean_passes_bucketed_list_not_full_table():
    payload = _payload(
        _entry("a", attempts_list=[(True, None, 0.0)]),
        _entry("b", attempts_list=[(True, None, 0.0)]),
    )
    md = format_retry_report(payload)
    # No per-case "## PASS" tables for single-attempt passes.
    assert "## PASS:" not in md
    # Clean passes listed in a single section.
    assert "## Clean passes" in md
    assert "- a (repeat 0)" in md
    assert "- b (repeat 0)" in md


# ---------------------------------------------------------------------------
# retried or failing cases get full tables
# ---------------------------------------------------------------------------
def test_retried_case_shows_attempt_table():
    payload = _payload(
        _entry(
            "flaky",
            attempts_list=[
                (False, "429", 0.0),
                (False, "429", 250.0),
                (True, None, 250.0),
            ],
            budget=4,
        )
    )
    md = format_retry_report(payload)
    assert "## PASS: flaky (repeat 0) — 3/4 attempts" in md
    assert "| Attempt | Passed | Error | Sleep before (ms) |" in md
    # Error cells backticked; empty error cells as "-".
    assert "| 1 | no | `429` | 0.0 |" in md
    assert "| 2 | no | `429` | 250.0 |" in md
    assert "| 3 | yes | - | 250.0 |" in md


def test_failing_case_shows_full_table_and_FAIL_header():
    payload = _payload(
        _entry(
            "dead",
            attempts_list=[(False, "boom", 0.0)],
            budget=1,
        )
    )
    md = format_retry_report(payload)
    assert "## FAIL: dead (repeat 0) — 1/1 attempts" in md
    assert "| 1 | no | `boom` | 0.0 |" in md


# ---------------------------------------------------------------------------
# empty report
# ---------------------------------------------------------------------------
def test_empty_cases_list_renders_cleanly():
    md = format_retry_report({"cases": []}, path="empty.json")
    assert "- Cases: 0" in md
    assert "- Passed: 0" in md
    assert "- Failed: 0" in md
    assert "Clean passes" not in md  # no pass section
    assert "## PASS:" not in md
    assert "## FAIL:" not in md


# ---------------------------------------------------------------------------
# mixed report: clean passes + retried case + failure
# ---------------------------------------------------------------------------
def test_mixed_report_surfaces_everything():
    payload = _payload(
        _entry("clean", attempts_list=[(True, None, 0.0)]),
        _entry(
            "flaky",
            attempts_list=[
                (False, "err", 0.0),
                (True, None, 100.0),
            ],
            budget=3,
        ),
        _entry(
            "dead",
            attempts_list=[(False, "boom", 0.0)],
            budget=2,
        ),
    )
    md = format_retry_report(payload)
    # Summary counts.
    assert "- Cases: 3" in md
    assert "- Retried cases: 1" in md  # only "flaky" had multiple attempts
    # Detailed sections for flaky (retried) and dead (failed).
    assert "## PASS: flaky (repeat 0) — 2/3 attempts" in md
    assert "## FAIL: dead (repeat 0) — 1/2 attempts" in md
    # Clean pass bucketed.
    assert "## Clean passes" in md
    assert "- clean (repeat 0)" in md
