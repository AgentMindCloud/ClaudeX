"""Unit tests for ``diff_retry_reports`` and markdown rendering."""

import json
from pathlib import Path

import pytest

from frok.evals import diff_retry_reports, retry_diff_to_markdown


def _entry(case, *, repeat=0, attempts_list, passed=None, budget=None):
    """Build a retry-report entry from a list of (passed, error) tuples."""
    attempts = [
        {
            "attempt": i + 1,
            "passed": bool(ok),
            "error": err,
            "sleep_before_ms": 0.0,
        }
        for i, (ok, err) in enumerate(attempts_list)
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


def _report(*entries):
    return {"cases": list(entries)}


# ---------------------------------------------------------------------------
# identical reports → no regression, no drift
# ---------------------------------------------------------------------------
def test_identical_reports_clean():
    a = _report(_entry("x", attempts_list=[(True, None)]))
    b = _report(_entry("x", attempts_list=[(True, None)]))
    diff = diff_retry_reports(a, b)
    assert diff["matched"] and len(diff["matched"]) == 1
    assert diff["only_in_a"] == []
    assert diff["only_in_b"] == []
    assert diff["attempts_grew"] == []
    assert diff["attempts_shrank"] == []
    assert diff["error_changed"] == []
    assert diff["newly_failing"] == []
    assert diff["newly_passing"] == []
    assert diff["regressed"] is False


# ---------------------------------------------------------------------------
# attempts grew → regressed, attempts_grew populated
# ---------------------------------------------------------------------------
def test_attempts_grew_is_regressed():
    a = _report(
        _entry("x", attempts_list=[(False, "err"), (True, None)])
    )
    b = _report(
        _entry(
            "x",
            attempts_list=[
                (False, "err"),
                (False, "err"),
                (True, None),
            ],
        )
    )
    diff = diff_retry_reports(a, b)
    assert len(diff["attempts_grew"]) == 1
    grown = diff["attempts_grew"][0]
    assert grown["a_attempts"] == 2
    assert grown["b_attempts"] == 3
    assert grown["attempts_delta"] == 1
    assert diff["regressed"] is True


# ---------------------------------------------------------------------------
# attempts shrank → NOT regressed, attempts_shrank populated
# ---------------------------------------------------------------------------
def test_attempts_shrank_not_regressed():
    a = _report(
        _entry("x", attempts_list=[(False, "err"), (False, "err"), (True, None)])
    )
    b = _report(_entry("x", attempts_list=[(True, None)]))
    diff = diff_retry_reports(a, b)
    assert len(diff["attempts_shrank"]) == 1
    assert diff["attempts_grew"] == []
    assert diff["regressed"] is False


# ---------------------------------------------------------------------------
# error shape drift between two non-null strings → regressed
# ---------------------------------------------------------------------------
def test_error_drift_between_two_non_null_is_regressed():
    a = _report(_entry("x", attempts_list=[(False, "RuntimeError: 429")]))
    b = _report(_entry("x", attempts_list=[(False, "RuntimeError: 503")]))
    diff = diff_retry_reports(a, b)
    assert len(diff["error_changed"]) == 1
    assert diff["regressed"] is True


# ---------------------------------------------------------------------------
# error resolved (non-null → null) → NOT regressed, IS newly_passing
# ---------------------------------------------------------------------------
def test_error_resolved_newly_passing_not_regressed():
    a = _report(_entry("x", attempts_list=[(False, "RuntimeError: 429")]))
    b = _report(_entry("x", attempts_list=[(True, None)]))
    diff = diff_retry_reports(a, b)
    assert len(diff["error_changed"]) == 1
    assert len(diff["newly_passing"]) == 1
    assert diff["regressed"] is False


# ---------------------------------------------------------------------------
# newly-failing case → regressed
# ---------------------------------------------------------------------------
def test_newly_failing_case_is_regressed():
    a = _report(_entry("x", attempts_list=[(True, None)]))
    b = _report(_entry("x", attempts_list=[(False, "boom")]))
    diff = diff_retry_reports(a, b)
    assert len(diff["newly_failing"]) == 1
    assert diff["regressed"] is True


# ---------------------------------------------------------------------------
# only in A (case removed) — not regressed on its own
# ---------------------------------------------------------------------------
def test_only_in_a_not_regressed():
    a = _report(_entry("x", attempts_list=[(True, None)]))
    b = _report()
    diff = diff_retry_reports(a, b)
    assert len(diff["only_in_a"]) == 1
    assert diff["matched"] == []
    assert diff["regressed"] is False


# ---------------------------------------------------------------------------
# only in B (new case) passing → not regressed
# only in B failing → regressed
# ---------------------------------------------------------------------------
def test_only_in_b_pass_not_regressed():
    a = _report()
    b = _report(_entry("new", attempts_list=[(True, None)]))
    diff = diff_retry_reports(a, b)
    assert len(diff["only_in_b"]) == 1
    assert diff["regressed"] is False


def test_only_in_b_failing_is_regressed():
    a = _report()
    b = _report(_entry("new", attempts_list=[(False, "boom")]))
    diff = diff_retry_reports(a, b)
    assert len(diff["only_in_b"]) == 1
    assert diff["regressed"] is True


# ---------------------------------------------------------------------------
# matching by (case, repeat) — same case, different repeat are distinct keys
# ---------------------------------------------------------------------------
def test_matching_by_case_repeat_tuple():
    a = _report(
        _entry("x", repeat=0, attempts_list=[(True, None)]),
        _entry("x", repeat=1, attempts_list=[(True, None)]),
    )
    b = _report(
        _entry("x", repeat=0, attempts_list=[(True, None)]),
        # repeat 1 shrank — still matches, not regressed
    )
    diff = diff_retry_reports(a, b)
    assert len(diff["matched"]) == 1
    assert len(diff["only_in_a"]) == 1
    assert diff["only_in_a"][0]["repeat"] == 1


# ---------------------------------------------------------------------------
# markdown rendering
# ---------------------------------------------------------------------------
def test_markdown_includes_summary_and_sections():
    a = _report(
        _entry("x", attempts_list=[(False, "err"), (True, None)]),
        _entry("y", attempts_list=[(True, None)]),
    )
    b = _report(
        _entry(
            "x",
            attempts_list=[
                (False, "err"),
                (False, "err"),
                (True, None),
            ],
        ),
        # y removed from B
        _entry("z", attempts_list=[(False, "new-err")]),  # new failing
    )
    diff = diff_retry_reports(a, b)
    md = retry_diff_to_markdown(diff, a_label="ref", b_label="cand")
    assert "# Frok Retry-Report Diff" in md
    assert "Matched cases: 1" in md
    assert "Attempts grew: 1" in md
    assert "Only in ref: 1" in md
    assert "Only in cand: 1" in md
    assert "Regressed: yes" in md
    assert "## Attempts grew" in md
    assert "## Only in ref" in md
    assert "## Only in cand" in md
