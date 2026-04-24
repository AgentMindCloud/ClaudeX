"""Tests for ``frok retry show --min-attempts N``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main
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


def _write(path: Path, entries: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cases": entries}), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# format_retry_report(min_attempts=N) — filter behaviour
# ---------------------------------------------------------------------------
def test_min_attempts_two_drops_single_attempt_cases():
    payload = _payload(
        _entry("single-pass", attempts_list=[(True, None, 0.0)]),
        _entry(
            "retried-pass",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
        _entry("single-fail", attempts_list=[(False, "err", 0.0)]),
    )
    md = format_retry_report(payload, min_attempts=2)
    # Only retried-pass (2 attempts) should be detailed.
    assert "## PASS: retried-pass" in md
    assert "single-fail" not in md  # 1 attempt → filtered
    # Clean passes bucket: single-pass is 1 attempt → filtered too.
    assert "single-pass" not in md
    # Indicator shows.
    assert "_Filtered to cases with >= 2 attempts._" in md


def test_min_attempts_one_is_noop():
    payload = _payload(
        _entry("single-pass", attempts_list=[(True, None, 0.0)]),
        _entry("single-fail", attempts_list=[(False, "err", 0.0)]),
    )
    md_noop = format_retry_report(payload, min_attempts=1)
    md_default = format_retry_report(payload)
    # No indicator when N=1.
    assert "Filtered to cases" not in md_noop
    # Outputs are identical.
    assert md_noop == md_default


def test_min_attempts_drops_clean_passes_below_threshold():
    payload = _payload(
        _entry("clean1", attempts_list=[(True, None, 0.0)]),
        _entry("clean2", attempts_list=[(True, None, 0.0)]),
        _entry(
            "retried-pass",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
    )
    md = format_retry_report(payload, min_attempts=2)
    assert "## Clean passes" not in md
    assert "clean1" not in md
    assert "clean2" not in md
    # retried-pass still detailed (2 attempts).
    assert "## PASS: retried-pass" in md


def test_min_attempts_high_threshold_empties_detail():
    payload = _payload(
        _entry("a", attempts_list=[(False, "err", 0.0), (True, None, 0.0)]),
    )
    md = format_retry_report(payload, min_attempts=5)
    # No case meets >= 5; detail sections all empty.
    assert "## PASS:" not in md
    assert "## FAIL:" not in md
    # Summary bloc still renders.
    assert "- Cases: 1" in md


# ---------------------------------------------------------------------------
# composition: min_attempts + group_by_error
# ---------------------------------------------------------------------------
def test_min_attempts_before_grouping():
    payload = _payload(
        # 1 attempt, "429" — should be filtered out before grouping.
        _entry("a", attempts_list=[(False, "429", 0.0)]),
        # 3 attempts (retried), "429" — survives.
        _entry(
            "b",
            attempts_list=[
                (False, "429", 0.0),
                (False, "429", 100.0),
                (False, "429", 100.0),
            ],
        ),
        _entry(
            "c",
            attempts_list=[
                (False, "429", 0.0),
                (False, "429", 100.0),
            ],
        ),
    )
    md = format_retry_report(payload, min_attempts=2, group_by_error=True)
    # Group '429' should show only b and c (2 cases), not a.
    assert "## Error: `429` — 2 case(s)" in md
    assert "| b |" in md
    assert "| c |" in md
    assert "| a |" not in md


# ---------------------------------------------------------------------------
# composition: min_attempts + limit
# ---------------------------------------------------------------------------
def test_min_attempts_before_limit():
    payload = _payload(
        _entry("single", attempts_list=[(False, "err", 0.0)]),
        _entry(
            "two",
            attempts_list=[(False, "err", 0.0), (False, "err", 0.0)],
        ),
        _entry(
            "three",
            attempts_list=[(False, "err", 0.0)] * 3,
        ),
    )
    md = format_retry_report(payload, min_attempts=2, limit=1)
    # After filter: two + three. After limit=1: one of them.
    assert "Showing 1 of 2 retried/failing cases" in md
    assert "single" not in md


# ---------------------------------------------------------------------------
# composition: min_attempts + compare_to — Only-in-previous untouched
# ---------------------------------------------------------------------------
def test_min_attempts_leaves_only_in_previous_untouched():
    # Previous has a single-attempt case "vanished"; current-run filter
    # should NOT touch the Only-in-previous bucket even though vanished
    # has < min_attempts.
    prev = _payload(
        _entry("vanished", attempts_list=[(True, None, 0.0)]),
        _entry(
            "kept",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
    )
    curr = _payload(
        _entry(
            "kept",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
    )
    md = format_retry_report(curr, compare_to=prev, min_attempts=2)
    # vanished still surfaces in Only-in-previous.
    assert "## Only in previous" in md
    assert "- vanished (repeat 0)" in md


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def test_parser_min_attempts_default_none(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.min_attempts is None


def test_cli_min_attempts_end_to_end(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("single", attempts_list=[(False, "err", 0.0)]),
            _entry(
                "retried",
                attempts_list=[
                    (False, "err", 0.0),
                    (False, "err", 0.0),
                ],
            ),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--min-attempts",
            "2",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "_Filtered to cases with >= 2 attempts._" in md
    assert "## FAIL: retried" in md
    assert "single" not in md


def test_cli_min_attempts_negative_or_zero_is_cli_error(tmp_path, capsys):
    report = _write(
        tmp_path / "r.json",
        [_entry("a", attempts_list=[(True, None, 0.0)])],
    )
    code = main(
        ["retry", "show", str(report), "--min-attempts", "0"]
    )
    assert code == 2
    assert "--min-attempts must be >= 1" in capsys.readouterr().err


def test_cli_min_attempts_plus_json_passthrough(tmp_path):
    # --json still passes raw payload verbatim even with --min-attempts.
    report = _write(
        tmp_path / "r.json",
        [
            _entry("single", attempts_list=[(True, None, 0.0)]),
            _entry(
                "retried",
                attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
            ),
        ],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--min-attempts",
            "2",
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Both cases still in the raw payload — filter is markdown-only.
    assert len(data["cases"]) == 2
