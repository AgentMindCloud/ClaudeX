"""Tests for ``frok retry show --limit N``.

Covers both the `format_retry_report` truncation + sort behaviour and
the CLI wiring.
"""

import json
from pathlib import Path

import pytest

from frok.cli import main
from frok.evals import format_retry_report
from frok.evals.retry_show import _worst_first_key


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


def _write(path: Path, entries: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cases": entries}), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# _worst_first_key unit: sort order
# ---------------------------------------------------------------------------
def test_sort_failing_before_passing():
    fail = _entry("a", attempts_list=[(False, "err", 0.0)])
    passing = _entry("b", attempts_list=[(False, "err", 0.0), (True, None, 0.0)])
    # Even though passing uses more attempts, failing sorts first.
    assert _worst_first_key(fail) < _worst_first_key(passing)


def test_sort_higher_ratio_first_among_same_passed():
    # Both pass after 2/5 and 2/3 attempts respectively — higher ratio wins.
    two_of_five = _entry(
        "a",
        attempts_list=[(False, "x", 0.0), (True, None, 0.0)],
        budget=5,
    )
    two_of_three = _entry(
        "b",
        attempts_list=[(False, "x", 0.0), (True, None, 0.0)],
        budget=3,
    )
    assert _worst_first_key(two_of_three) < _worst_first_key(two_of_five)


def test_sort_more_attempts_tiebreaks_equal_ratios():
    # Both 100% ratio (exhausted budget), different absolute attempts.
    small = _entry(
        "a",
        attempts_list=[(False, "x", 0.0)],
        budget=1,
    )
    big = _entry(
        "b",
        attempts_list=[(False, "x", 0.0)] * 5,
        budget=5,
    )
    # Same ratio (1.0); big has more raw attempts → sorted first.
    assert _worst_first_key(big) < _worst_first_key(small)


def test_sort_name_is_final_tiebreak():
    a = _entry("alpha", attempts_list=[(False, "x", 0.0)])
    b = _entry("beta", attempts_list=[(False, "x", 0.0)])
    # Identical by every metric except name; alpha sorts first.
    assert _worst_first_key(a) < _worst_first_key(b)


# ---------------------------------------------------------------------------
# format_retry_report with limit
# ---------------------------------------------------------------------------
def test_limit_less_than_total_shows_indicator():
    payload = _payload(
        _entry("a", attempts_list=[(False, "e", 0.0)]),
        _entry("b", attempts_list=[(False, "e", 0.0)]),
        _entry("c", attempts_list=[(False, "e", 0.0)]),
    )
    md = format_retry_report(payload, limit=2)
    assert "_Showing 2 of 3 retried/failing cases (worst-first)._" in md


def test_limit_equal_to_total_no_indicator():
    payload = _payload(
        _entry("a", attempts_list=[(False, "e", 0.0)]),
        _entry("b", attempts_list=[(False, "e", 0.0)]),
    )
    md = format_retry_report(payload, limit=2)
    assert "Showing" not in md


def test_limit_greater_than_total_no_indicator():
    payload = _payload(
        _entry("a", attempts_list=[(False, "e", 0.0)]),
    )
    md = format_retry_report(payload, limit=10)
    assert "Showing" not in md


def test_limit_zero_suppresses_all_detail_tables():
    payload = _payload(
        _entry("a", attempts_list=[(False, "e", 0.0)]),
        _entry("b", attempts_list=[(False, "e", 0.0)]),
    )
    md = format_retry_report(payload, limit=0)
    # Truncation indicator still shows, but no per-case tables.
    assert "Showing 0 of 2" in md
    assert "## FAIL:" not in md
    assert "## PASS:" not in md


def test_limit_doesnt_affect_clean_passes():
    payload = _payload(
        _entry("clean1", attempts_list=[(True, None, 0.0)]),
        _entry("clean2", attempts_list=[(True, None, 0.0)]),
        _entry("clean3", attempts_list=[(True, None, 0.0)]),
        _entry("flaky", attempts_list=[(False, "e", 0.0), (True, None, 0.0)]),
    )
    md = format_retry_report(payload, limit=0)
    # All clean passes still bulleted.
    assert "- clean1 (repeat 0)" in md
    assert "- clean2 (repeat 0)" in md
    assert "- clean3 (repeat 0)" in md


def test_limit_truncates_worst_first():
    # Build 3 retried cases: one failing, two passing with varying ratios.
    # With limit=1, the failing one should be the only detail section.
    payload = _payload(
        _entry(
            "passing_low_ratio",
            attempts_list=[(False, "e", 0.0), (True, None, 0.0)],
            budget=10,
        ),
        _entry(
            "failing",
            attempts_list=[(False, "e", 0.0), (False, "e", 0.0)],
            budget=2,
        ),
        _entry(
            "passing_high_ratio",
            attempts_list=[(False, "e", 0.0), (True, None, 0.0)],
            budget=2,
        ),
    )
    md = format_retry_report(payload, limit=1)
    assert "Showing 1 of 3" in md
    # Only the failing case gets a detail section.
    assert "## FAIL: failing" in md
    assert "## PASS: passing_high_ratio" not in md
    assert "## PASS: passing_low_ratio" not in md


def test_limit_with_compare_to_preserves_only_in_previous():
    # --compare-to adds an "Only in previous" section; --limit should not
    # affect it (it's already terse).
    prev = _payload(
        _entry("curr1", attempts_list=[(False, "e", 0.0), (True, None, 0.0)]),
        _entry("vanished", attempts_list=[(True, None, 0.0)]),
    )
    curr = _payload(
        _entry("curr1", attempts_list=[(False, "e", 0.0), (True, None, 0.0)]),
        _entry("curr2", attempts_list=[(False, "e", 0.0)]),
    )
    md = format_retry_report(curr, compare_to=prev, limit=1)
    assert "## Only in previous" in md
    assert "- vanished (repeat 0)" in md


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def test_cli_parser_limit_default_none(tmp_path):
    from frok.cli import build_parser

    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.limit is None


def test_cli_limit_applies_end_to_end(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("a", attempts_list=[(False, "e", 0.0)]),
            _entry("b", attempts_list=[(False, "e", 0.0)]),
            _entry("c", attempts_list=[(False, "e", 0.0)]),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--limit",
            "1",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "Showing 1 of 3" in md


def test_cli_negative_limit_is_cli_error(tmp_path, capsys):
    report = _write(
        tmp_path / "r.json",
        [_entry("a", attempts_list=[(True, None, 0.0)])],
    )
    code = main(
        ["retry", "show", str(report), "--limit", "-1"]
    )
    assert code == 2
    assert "--limit must be >= 0" in capsys.readouterr().err


def test_cli_limit_plus_json_still_passthrough(tmp_path):
    # --json ignores --limit (markdown-only feature).
    report = _write(
        tmp_path / "r.json",
        [
            _entry("a", attempts_list=[(False, "e", 0.0)]),
            _entry("b", attempts_list=[(False, "e", 0.0)]),
        ],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--limit",
            "1",
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Verbatim — both cases present.
    assert len(data["cases"]) == 2


def test_cli_limit_with_compare_to_end_to_end(tmp_path):
    prev = _write(
        tmp_path / "prev.json",
        [
            _entry("a", attempts_list=[(True, None, 0.0)]),
            _entry("b", attempts_list=[(True, None, 0.0)]),
        ],
    )
    curr = _write(
        tmp_path / "curr.json",
        [
            _entry(
                "a",
                attempts_list=[(False, "e", 0.0), (True, None, 0.0)],
                budget=3,
            ),
            _entry(
                "b",
                attempts_list=[(False, "e", 0.0), (True, None, 0.0)],
                budget=3,
            ),
            _entry("c", attempts_list=[(False, "e", 0.0)], budget=1),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(curr),
            "--compare-to",
            str(prev),
            "--limit",
            "1",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "Showing 1 of 3" in md
    # Failing case wins the top slot.
    assert "## FAIL: c" in md
    # Comparison section still present.
    assert "## Comparison" in md
