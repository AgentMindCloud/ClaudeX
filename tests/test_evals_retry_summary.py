"""Unit tests for ``summarize_retry_reports`` + markdown renderer."""

import json
from pathlib import Path

import pytest

from frok.evals import (
    retry_summary_to_markdown,
    summarize_retry_reports,
)
from frok.evals.retry_summary import _classify_trend


# ---------------------------------------------------------------------------
# trend classifier
# ---------------------------------------------------------------------------
def test_classify_flat_all_equal():
    assert _classify_trend([2, 2, 2]) == "flat"


def test_classify_flat_single_value():
    assert _classify_trend([3]) == "flat"


def test_classify_growing_monotonic():
    assert _classify_trend([1, 2, 3, 4]) == "growing"


def test_classify_growing_with_plateaus():
    assert _classify_trend([1, 1, 2, 2, 3]) == "growing"


def test_classify_shrinking_monotonic():
    assert _classify_trend([5, 4, 3, 2]) == "shrinking"


def test_classify_mixed_up_then_down():
    assert _classify_trend([1, 3, 2]) == "mixed"


def test_classify_nones_ignored():
    # None entries are skipped; the remaining [2, 3] classifies as growing.
    assert _classify_trend([None, 2, None, 3]) == "growing"


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------
def _entry(case: str, *, repeat: int = 0, attempts: int = 1, passed: bool = True):
    # Minimal entry with the fields the summarizer reads.
    return {
        "case": case,
        "repeat": repeat,
        "attempts": [
            {"attempt": i + 1, "passed": (i == attempts - 1 and passed), "error": None, "sleep_before_ms": 0.0}
            for i in range(attempts)
        ],
        "retry_budget": max(attempts, 1),
        "passed": passed,
    }


def _write_report(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"cases": entries}, indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# summarize_retry_reports
# ---------------------------------------------------------------------------
def test_summarize_three_reports_growing(tmp_path):
    _write_report(tmp_path / "2026-04-20.json", [_entry("x", attempts=1)])
    _write_report(tmp_path / "2026-04-21.json", [_entry("x", attempts=2)])
    _write_report(tmp_path / "2026-04-22.json", [_entry("x", attempts=3)])

    summary = summarize_retry_reports(tmp_path)
    assert [r["label"] for r in summary["reports"]] == [
        "2026-04-20",
        "2026-04-21",
        "2026-04-22",
    ]
    assert len(summary["cases"]) == 1
    case = summary["cases"][0]
    assert case["case"] == "x"
    assert case["attempts_by_report"] == [1, 2, 3]
    assert case["trend"] == "growing"
    assert summary["trend_counts"] == {
        "flat": 0,
        "growing": 1,
        "shrinking": 0,
        "mixed": 0,
    }


def test_summarize_flat_case_across_reports(tmp_path):
    _write_report(tmp_path / "a.json", [_entry("x", attempts=2)])
    _write_report(tmp_path / "b.json", [_entry("x", attempts=2)])
    summary = summarize_retry_reports(tmp_path)
    assert summary["cases"][0]["trend"] == "flat"
    assert summary["trend_counts"]["flat"] == 1


def test_summarize_mixed_up_and_down(tmp_path):
    _write_report(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write_report(tmp_path / "b.json", [_entry("x", attempts=3)])
    _write_report(tmp_path / "c.json", [_entry("x", attempts=2)])
    summary = summarize_retry_reports(tmp_path)
    assert summary["cases"][0]["trend"] == "mixed"


def test_summarize_case_late_arrival_records_none(tmp_path):
    # Case "y" only appears in the second report.
    _write_report(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write_report(
        tmp_path / "b.json",
        [_entry("x", attempts=1), _entry("y", attempts=2)],
    )
    summary = summarize_retry_reports(tmp_path)
    y = next(c for c in summary["cases"] if c["case"] == "y")
    assert y["attempts_by_report"] == [None, 2]
    assert y["passed_by_report"] == [None, True]
    # Single real value → flat.
    assert y["trend"] == "flat"


def test_summarize_case_repeat_distinct_keys(tmp_path):
    _write_report(
        tmp_path / "a.json",
        [
            _entry("x", repeat=0, attempts=1),
            _entry("x", repeat=1, attempts=3),
        ],
    )
    _write_report(
        tmp_path / "b.json",
        [
            _entry("x", repeat=0, attempts=2),
            _entry("x", repeat=1, attempts=3),
        ],
    )
    summary = summarize_retry_reports(tmp_path)
    assert len(summary["cases"]) == 2
    by_rep = {c["repeat"]: c for c in summary["cases"]}
    assert by_rep[0]["trend"] == "growing"
    assert by_rep[1]["trend"] == "flat"


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        summarize_retry_reports(tmp_path / "nope")


def test_not_a_directory_raises(tmp_path):
    f = tmp_path / "file.json"
    f.write_text("{}", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        summarize_retry_reports(f)


def test_empty_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        summarize_retry_reports(tmp_path)


def test_malformed_report_raises(tmp_path):
    (tmp_path / "bad.json").write_text("not-json{", encoding="utf-8")
    with pytest.raises(ValueError):
        summarize_retry_reports(tmp_path)


def test_missing_cases_key_raises(tmp_path):
    (tmp_path / "noroot.json").write_text(
        json.dumps({"other": []}), encoding="utf-8"
    )
    with pytest.raises(ValueError):
        summarize_retry_reports(tmp_path)


# ---------------------------------------------------------------------------
# markdown rendering
# ---------------------------------------------------------------------------
def test_markdown_surfaces_summary_and_matrix(tmp_path):
    _write_report(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write_report(tmp_path / "b.json", [_entry("x", attempts=3)])
    summary = summarize_retry_reports(tmp_path)
    md = retry_summary_to_markdown(summary)
    assert "# Frok Retry-Report Trend" in md
    assert "Reports: 2" in md
    assert "Growing: 1" in md
    assert "## Reports" in md
    assert "## Growing" in md
    # The timeline arrow shows the progression.
    assert "1 → 3" in md


def test_markdown_spotlights_mixed_section(tmp_path):
    _write_report(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write_report(tmp_path / "b.json", [_entry("x", attempts=3)])
    _write_report(tmp_path / "c.json", [_entry("x", attempts=2)])
    summary = summarize_retry_reports(tmp_path)
    md = retry_summary_to_markdown(summary)
    assert "## Mixed" in md
    assert "1 → 3 → 2" in md


def test_markdown_flat_case_has_no_spotlight_section(tmp_path):
    _write_report(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write_report(tmp_path / "b.json", [_entry("x", attempts=1)])
    summary = summarize_retry_reports(tmp_path)
    md = retry_summary_to_markdown(summary)
    assert "## Growing" not in md
    assert "## Mixed" not in md
