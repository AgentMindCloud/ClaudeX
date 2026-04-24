"""Tests for ``frok retry show --only-errors``."""

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
# format_retry_report(only_errors=True) — filter behaviour
# ---------------------------------------------------------------------------
def test_only_errors_drops_clean_passes_and_retried_passes():
    payload = _payload(
        _entry("clean-pass", attempts_list=[(True, None, 0.0)]),
        _entry(
            "retried-pass",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
        _entry("hard-fail", attempts_list=[(False, "boom", 0.0)]),
        _entry(
            "retried-fail",
            attempts_list=[
                (False, "err", 0.0),
                (False, "err", 0.0),
            ],
        ),
    )
    md = format_retry_report(payload, only_errors=True)
    # Only failing cases survive.
    assert "## FAIL: hard-fail" in md
    assert "## FAIL: retried-fail" in md
    assert "## PASS: retried-pass" not in md
    assert "## Clean passes" not in md
    assert "clean-pass" not in md
    assert "_Showing failing cases only._" in md


def test_only_errors_false_default_unchanged():
    payload = _payload(
        _entry("clean-pass", attempts_list=[(True, None, 0.0)]),
        _entry(
            "retried-pass",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
    )
    md = format_retry_report(payload, only_errors=False)
    md_default = format_retry_report(payload)
    assert md == md_default
    assert "Showing failing cases only" not in md


def test_only_errors_indicator_fires_even_with_zero_failures():
    # Suite is all-green; --only-errors should still surface the
    # indicator so operators know the filter applied (no failures
    # ≠ filter wasn't requested).
    payload = _payload(
        _entry("clean-pass", attempts_list=[(True, None, 0.0)]),
        _entry(
            "retried-pass",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
    )
    md = format_retry_report(payload, only_errors=True)
    assert "_Showing failing cases only._" in md
    # No detail tables.
    assert "## PASS:" not in md
    assert "## FAIL:" not in md
    # Summary still reflects the full run.
    assert "- Cases: 2" in md
    assert "- Passed: 2" in md


# ---------------------------------------------------------------------------
# composition
# ---------------------------------------------------------------------------
def test_only_errors_before_grouping():
    payload = _payload(
        _entry(
            "passing",
            attempts_list=[(False, "429", 0.0), (True, None, 0.0)],
        ),
        _entry("failing-a", attempts_list=[(False, "429", 0.0)]),
        _entry("failing-b", attempts_list=[(False, "429", 0.0)]),
    )
    md = format_retry_report(payload, only_errors=True, group_by_error=True)
    # Only the two failing cases get clustered; passing-case excluded.
    assert "## Error: `429` — 2 case(s)" in md
    assert "passing" not in md.replace("Failing", "")  # only as substring


def test_only_errors_before_limit():
    payload = _payload(
        _entry(
            "passing",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
        ),
        _entry("fail-1", attempts_list=[(False, "err", 0.0)]),
        _entry("fail-2", attempts_list=[(False, "err", 0.0)]),
        _entry("fail-3", attempts_list=[(False, "err", 0.0)]),
    )
    md = format_retry_report(payload, only_errors=True, limit=2)
    # After only_errors: 3 failing cases. After limit=2: 2 detailed.
    assert "Showing 2 of 3 retried/failing cases" in md


def test_only_errors_before_min_attempts():
    payload = _payload(
        _entry(
            "passing-retried",
            attempts_list=[
                (False, "err", 0.0),
                (False, "err", 0.0),
                (True, None, 0.0),
            ],
        ),
        _entry("failing-1-attempt", attempts_list=[(False, "err", 0.0)]),
        _entry(
            "failing-3-attempts",
            attempts_list=[(False, "err", 0.0)] * 3,
        ),
    )
    md = format_retry_report(payload, only_errors=True, min_attempts=2)
    # only_errors first → keeps failing-1 + failing-3 (drops passing-retried).
    # min_attempts=2 then → drops failing-1 (1 attempt).
    assert "## FAIL: failing-3-attempts" in md
    assert "failing-1-attempt" not in md
    assert "passing-retried" not in md
    # Both indicators surface.
    assert "_Showing failing cases only._" in md
    assert "_Filtered to cases with >= 2 attempts._" in md


def test_only_errors_leaves_only_in_previous_untouched():
    prev = _payload(
        _entry("vanished-pass", attempts_list=[(True, None, 0.0)]),
        _entry("vanished-fail", attempts_list=[(False, "err", 0.0)]),
        _entry("kept", attempts_list=[(False, "err", 0.0)]),
    )
    curr = _payload(_entry("kept", attempts_list=[(False, "err", 0.0)]))
    md = format_retry_report(curr, compare_to=prev, only_errors=True)
    # Both vanished cases (pass + fail) still surface — not filtered.
    assert "## Only in previous" in md
    assert "- vanished-pass (repeat 0)" in md
    assert "- vanished-fail (repeat 0)" in md


def test_only_errors_summary_unchanged():
    # Summary bloc reflects FULL run, not filtered subset.
    payload = _payload(
        _entry("pass", attempts_list=[(True, None, 0.0)]),
        _entry("fail", attempts_list=[(False, "err", 0.0)]),
    )
    md = format_retry_report(payload, only_errors=True)
    assert "- Cases: 2" in md
    assert "- Passed: 1" in md
    assert "- Failed: 1" in md


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def test_parser_only_errors_default_false(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.only_errors is False


def test_parser_only_errors_flag(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(
        ["retry", "show", str(tmp_path / "r.json"), "--only-errors"]
    )
    assert ns.only_errors is True


def test_cli_only_errors_end_to_end(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("pass", attempts_list=[(True, None, 0.0)]),
            _entry("fail", attempts_list=[(False, "boom", 0.0)]),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--only-errors",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "_Showing failing cases only._" in md
    assert "## FAIL: fail" in md
    assert "pass" not in md.replace("Passed", "").replace("passed", "")


def test_cli_only_errors_plus_json_passthrough(tmp_path):
    # --json passes raw payload through; --only-errors is markdown-only.
    report = _write(
        tmp_path / "r.json",
        [
            _entry("pass", attempts_list=[(True, None, 0.0)]),
            _entry("fail", attempts_list=[(False, "boom", 0.0)]),
        ],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--only-errors",
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["cases"]) == 2  # both still in raw payload
