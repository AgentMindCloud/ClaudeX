"""Tests for ``frok retry show --group-by-error``.

Covers the `format_retry_report(group_by_error=True)` rendering and
the CLI wiring.
"""

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
# format_retry_report(group_by_error=True) — rendering
# ---------------------------------------------------------------------------
def test_same_error_cases_group_together():
    payload = _payload(
        _entry("a", attempts_list=[(False, "429", 0.0)]),
        _entry("b", attempts_list=[(False, "429", 0.0)]),
        _entry("c", attempts_list=[(False, "429", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True)
    # One group "## Error: `429` — 3 case(s)"; no per-case "## FAIL:" headers.
    assert "## Error: `429` — 3 case(s)" in md
    assert "## FAIL: a" not in md
    # All three cases listed in the group's table.
    assert "| a | 0 | 1/1 | FAIL |" in md
    assert "| b | 0 | 1/1 | FAIL |" in md
    assert "| c | 0 | 1/1 | FAIL |" in md


def test_different_errors_split_into_distinct_groups():
    payload = _payload(
        _entry("a", attempts_list=[(False, "429", 0.0)]),
        _entry("b", attempts_list=[(False, "boom", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True)
    assert "## Error: `429` — 1 case(s)" in md
    assert "## Error: `boom` — 1 case(s)" in md


def test_scorer_only_failure_grouped_separately():
    # A case that passed at the transport level but failed the scorer
    # has observation.error = None; the last attempt's error is None too.
    payload = _payload(
        _entry("scorer-fail", attempts_list=[(False, None, 0.0)]),
        _entry("transport-fail", attempts_list=[(False, "429", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True)
    assert "## Error: `(no error — scorer failure or passing retry)`" in md
    assert "## Error: `429` — 1 case(s)" in md


def test_groups_sorted_by_size_desc():
    payload = _payload(
        _entry("a", attempts_list=[(False, "small-group", 0.0)]),
        _entry("b", attempts_list=[(False, "big-group", 0.0)]),
        _entry("c", attempts_list=[(False, "big-group", 0.0)]),
        _entry("d", attempts_list=[(False, "big-group", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True)
    # Big group comes first (3 cases) before small group (1 case).
    big_idx = md.index("## Error: `big-group`")
    small_idx = md.index("## Error: `small-group`")
    assert big_idx < small_idx


def test_groups_alpha_tiebreak_for_equal_sizes():
    payload = _payload(
        _entry("a", attempts_list=[(False, "zeta", 0.0)]),
        _entry("b", attempts_list=[(False, "alpha", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True)
    # Both groups have 1 case each → alpha order.
    alpha_idx = md.index("## Error: `alpha`")
    zeta_idx = md.index("## Error: `zeta`")
    assert alpha_idx < zeta_idx


def test_group_cases_sorted_worst_first_within_group():
    # Same error, different budget / verdict — worst-first sort applies
    # INSIDE each group.
    payload = _payload(
        _entry(
            "caught-late",
            attempts_list=[(False, "err", 0.0), (True, None, 0.0)],
            budget=5,
        ),
        _entry(
            "hard-fail",
            attempts_list=[(False, "err", 0.0)],
            budget=5,
        ),
        # NOTE: caught-late's LAST error is None (passing retry), so it
        # won't actually fall in the same group as hard-fail. Use a
        # different setup: two failing cases, different ratios.
    )
    # Redo with two cases in same group, both failing, different ratios.
    payload = _payload(
        _entry(
            "mid-ratio",
            attempts_list=[(False, "err", 0.0), (False, "err", 0.0)],
            budget=5,
        ),
        _entry(
            "high-ratio",
            attempts_list=[(False, "err", 0.0)] * 5,
            budget=5,
        ),
    )
    md = format_retry_report(payload, group_by_error=True)
    # Both in the same group; high-ratio sorts first.
    high_idx = md.index("| high-ratio | 0 | 5/5 | FAIL |")
    mid_idx = md.index("| mid-ratio | 0 | 2/5 | FAIL |")
    assert high_idx < mid_idx


def test_clean_passes_still_bucketed_in_grouped_mode():
    payload = _payload(
        _entry("clean", attempts_list=[(True, None, 0.0)]),
        _entry("failing", attempts_list=[(False, "err", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True)
    assert "## Clean passes" in md
    assert "- clean (repeat 0)" in md


def test_only_in_previous_still_surfaces_in_grouped_mode():
    prev = _payload(
        _entry("kept", attempts_list=[(False, "err", 0.0)]),
        _entry("vanished", attempts_list=[(True, None, 0.0)]),
    )
    curr = _payload(_entry("kept", attempts_list=[(False, "err", 0.0)]))
    md = format_retry_report(curr, compare_to=prev, group_by_error=True)
    assert "## Only in previous" in md
    assert "- vanished (repeat 0)" in md
    # The kept case still shows up under its error group.
    assert "## Error: `err`" in md


def test_no_group_by_error_preserves_per_case_tables():
    payload = _payload(
        _entry("a", attempts_list=[(False, "429", 0.0)]),
        _entry("b", attempts_list=[(False, "429", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=False)
    # Classic §25 layout: two "## FAIL:" sections, no "## Error:" groups.
    assert "## FAIL: a" in md
    assert "## FAIL: b" in md
    assert "## Error:" not in md


# ---------------------------------------------------------------------------
# --limit interaction
# ---------------------------------------------------------------------------
def test_limit_truncates_groups_not_cases_in_grouped_mode():
    payload = _payload(
        _entry("a", attempts_list=[(False, "err1", 0.0)]),
        _entry("b", attempts_list=[(False, "err1", 0.0)]),
        _entry("c", attempts_list=[(False, "err2", 0.0)]),
        _entry("d", attempts_list=[(False, "err3", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True, limit=2)
    # Indicator in group form.
    assert "_Showing 2 of 3 error groups (largest-first)._" in md
    # Two biggest groups shown (err1 with 2 cases, then one of err2/err3).
    assert "## Error: `err1` — 2 case(s)" in md
    # Total of 2 groups (not 3).
    assert md.count("## Error:") == 2


def test_limit_zero_in_grouped_mode_shows_indicator_no_groups():
    payload = _payload(
        _entry("a", attempts_list=[(False, "err", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True, limit=0)
    assert "_Showing 0 of 1 error groups (largest-first)._" in md
    assert "## Error:" not in md


def test_limit_equal_to_groups_no_indicator():
    payload = _payload(
        _entry("a", attempts_list=[(False, "err1", 0.0)]),
        _entry("b", attempts_list=[(False, "err2", 0.0)]),
    )
    md = format_retry_report(payload, group_by_error=True, limit=2)
    assert "Showing" not in md


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def test_cli_parser_group_by_error_default_false(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.group_by_error is False


def test_cli_parser_group_by_error_flag(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(
        ["retry", "show", str(tmp_path / "r.json"), "--group-by-error"]
    )
    assert ns.group_by_error is True


def test_cli_group_by_error_end_to_end(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("a", attempts_list=[(False, "429", 0.0)]),
            _entry("b", attempts_list=[(False, "429", 0.0)]),
            _entry("c", attempts_list=[(False, "boom", 0.0)]),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--group-by-error",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "## Error: `429` — 2 case(s)" in md
    assert "## Error: `boom` — 1 case(s)" in md


def test_cli_group_by_error_plus_limit(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("a", attempts_list=[(False, "err1", 0.0)]),
            _entry("b", attempts_list=[(False, "err1", 0.0)]),
            _entry("c", attempts_list=[(False, "err2", 0.0)]),
            _entry("d", attempts_list=[(False, "err3", 0.0)]),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--group-by-error",
            "--limit",
            "2",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "2 of 3 error groups" in md


def test_cli_group_by_error_plus_json_passthrough(tmp_path):
    # --json still passes raw payload through even with --group-by-error.
    report = _write(
        tmp_path / "r.json",
        [_entry("a", attempts_list=[(False, "429", 0.0)])],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--group-by-error",
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Verbatim — no grouped structure in JSON output.
    assert list(data.keys()) == ["cases"]
    assert "groups" not in data
