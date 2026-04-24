"""Tests for ``frok retry show --compare-to``.

Covers both the `format_retry_report` enrichment and the CLI wiring.
"""

import json
from pathlib import Path

import pytest

from frok.cli import main
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
# unit: format_retry_report with compare_to
# ---------------------------------------------------------------------------
def test_unit_header_suffix_shows_prev_attempts_and_verdict():
    prev = _payload(
        _entry(
            "flaky",
            attempts_list=[(False, "err", 0.0), (True, None, 100.0)],
            budget=4,
        )
    )
    curr = _payload(
        _entry(
            "flaky",
            attempts_list=[
                (False, "err", 0.0),
                (False, "err", 100.0),
                (True, None, 100.0),
            ],
            budget=4,
        )
    )
    md = format_retry_report(curr, compare_to=prev)
    # Current = 3/4 PASS; previous = 2/4 PASS.
    assert "## PASS: flaky (repeat 0) — 3/4 attempts (was 2/4, PASS)" in md


def test_unit_header_suffix_new_case_marked():
    prev = _payload()  # empty previous
    curr = _payload(_entry("fresh", attempts_list=[(False, "boom", 0.0)]))
    md = format_retry_report(curr, compare_to=prev)
    assert "## FAIL: fresh (repeat 0) — 1/1 attempts (NEW — not in previous)" in md


def test_unit_comparison_summary_section():
    prev = _payload(
        _entry("x", attempts_list=[(True, None, 0.0)]),
        _entry("removed", attempts_list=[(True, None, 0.0)]),
    )
    curr = _payload(
        _entry("x", attempts_list=[(False, "err", 0.0), (True, None, 100.0)], budget=3),
    )
    md = format_retry_report(curr, compare_to=prev)
    assert "## Comparison" in md
    assert "- Attempts grew on: 1 case(s)" in md
    assert "- Only in previous: 1" in md
    # "x" stayed a pass; no newly failing/passing.
    assert "- Newly failing: 0" in md
    assert "- Newly passing: 0" in md


def test_unit_only_in_previous_section_lists_vanished_cases():
    prev = _payload(
        _entry("kept", attempts_list=[(True, None, 0.0)]),
        _entry("vanished", attempts_list=[(False, "gone", 0.0)]),
    )
    curr = _payload(_entry("kept", attempts_list=[(True, None, 0.0)]))
    md = format_retry_report(curr, compare_to=prev)
    assert "## Only in previous" in md
    assert "- vanished (repeat 0): FAIL, 1/1 attempts" in md


def test_unit_compare_to_path_surfaces_in_summary():
    prev = _payload(_entry("a", attempts_list=[(True, None, 0.0)]))
    curr = _payload(_entry("a", attempts_list=[(True, None, 0.0)]))
    md = format_retry_report(
        curr,
        path="now.json",
        compare_to=prev,
        compare_to_path="prev.json",
    )
    assert "- Source: `now.json`" in md
    assert "- Compared to: `prev.json`" in md


def test_unit_no_compare_leaves_output_unchanged():
    payload = _payload(
        _entry(
            "x",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
            budget=3,
        )
    )
    md = format_retry_report(payload)
    assert "## Comparison" not in md
    assert "Compared to" not in md
    assert "was " not in md
    assert "Only in previous" not in md


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------
def test_cli_compare_to_renders_suffix(tmp_path):
    prev = _write(
        tmp_path / "prev.json",
        [
            _entry(
                "flaky",
                attempts_list=[(False, "err", 0.0), (True, None, 100.0)],
                budget=4,
            )
        ],
    )
    curr = _write(
        tmp_path / "curr.json",
        [
            _entry(
                "flaky",
                attempts_list=[
                    (False, "err", 0.0),
                    (False, "err", 100.0),
                    (True, None, 100.0),
                ],
                budget=4,
            )
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
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "Compared to:" in md
    assert "(was 2/4, PASS)" in md
    assert "## Comparison" in md


def test_cli_compare_to_missing_file_is_cli_error(tmp_path, capsys):
    curr = _write(
        tmp_path / "curr.json",
        [_entry("a", attempts_list=[(True, None, 0.0)])],
    )
    code = main(
        [
            "retry",
            "show",
            str(curr),
            "--compare-to",
            str(tmp_path / "missing.json"),
            "-o",
            str(tmp_path / "show.md"),
        ]
    )
    assert code == 2
    assert "retry report not found" in capsys.readouterr().err


def test_cli_compare_to_plus_json_passes_primary_through(tmp_path):
    # --json + --compare-to: the compare flag is markdown-only, so --json
    # should still just pass through the primary payload verbatim.
    prev = _write(
        tmp_path / "prev.json",
        [
            _entry(
                "flaky",
                attempts_list=[(False, "err", 0.0), (True, None, 100.0)],
                budget=4,
            )
        ],
    )
    curr = _write(
        tmp_path / "curr.json",
        [
            _entry(
                "flaky",
                attempts_list=[(True, None, 0.0)],
                budget=4,
            )
        ],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(curr),
            "--compare-to",
            str(prev),
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Verbatim primary payload — no comparison data in the JSON.
    assert list(data.keys()) == ["cases"]
    assert data["cases"][0]["case"] == "flaky"
    assert "diff" not in data
    assert "compare_to_path" not in data


def test_cli_compare_to_regression_does_not_affect_fail_on_failure(tmp_path):
    # --fail-on-failure gates on the PRIMARY report's failures, not on
    # regression vs previous. A primary all-pass run shouldn't exit 1
    # just because attempts grew compared to previous.
    prev = _write(
        tmp_path / "prev.json",
        [_entry("x", attempts_list=[(True, None, 0.0)], budget=3)],
    )
    curr = _write(
        tmp_path / "curr.json",
        [
            _entry(
                "x",
                attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
                budget=3,
            )
        ],
    )
    code = main(
        [
            "retry",
            "show",
            str(curr),
            "--compare-to",
            str(prev),
            "--fail-on-failure",
            "-o",
            str(tmp_path / "show.md"),
        ]
    )
    # Primary case passed — exit 0 despite attempts growing vs previous.
    assert code == 0
