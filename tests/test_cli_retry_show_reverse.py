"""Tests for ``frok retry show --reverse``."""

import json
import re
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


def _section_order(md: str) -> list[str]:
    pattern = re.compile(r"^## (?:PASS|FAIL): (?P<name>\S+)", re.MULTILINE)
    return [m.group("name") for m in pattern.finditer(md)]


# ---------------------------------------------------------------------------
# default False preserves §31
# ---------------------------------------------------------------------------
def test_reverse_false_byte_identical_to_no_flag():
    payload = _payload(
        _entry("alpha", attempts_list=[(False, "x", 0.0)]),
        _entry("beta", attempts_list=[(False, "x", 0.0)]),
    )
    assert format_retry_report(payload, reverse=False) == format_retry_report(payload)


# ---------------------------------------------------------------------------
# --reverse flips an explicit sort key
# ---------------------------------------------------------------------------
def test_reverse_flips_name_sort():
    payload = _payload(
        _entry("alpha", attempts_list=[(False, "x", 0.0)]),
        _entry("beta", attempts_list=[(False, "x", 0.0)]),
        _entry("gamma", attempts_list=[(False, "x", 0.0)]),
    )
    md = format_retry_report(payload, sort_by="name", reverse=True)
    assert _section_order(md) == ["gamma", "beta", "alpha"]


def test_reverse_flips_attempts_sort():
    payload = _payload(
        _entry("one", attempts_list=[(False, "x", 0.0)]),
        _entry("five", attempts_list=[(False, "x", 0.0)] * 5),
        _entry("three", attempts_list=[(False, "x", 0.0)] * 3),
    )
    # --sort-by attempts: five (5), three (3), one (1). Reversed: one, three, five.
    md = format_retry_report(payload, sort_by="attempts", reverse=True)
    assert _section_order(md) == ["one", "three", "five"]


# ---------------------------------------------------------------------------
# --reverse with default 'worst' forces the sort (usually payload order)
# ---------------------------------------------------------------------------
def test_reverse_with_default_worst_applies_sort_then_flips():
    # All failing, different ratios → worst-first is high-ratio → low-ratio.
    # Reversed: low-ratio first.
    payload = _payload(
        _entry("high", attempts_list=[(False, "x", 0.0)] * 5, budget=5),
        _entry("low", attempts_list=[(False, "x", 0.0)], budget=10),
        _entry("mid", attempts_list=[(False, "x", 0.0)] * 3, budget=6),
    )
    md = format_retry_report(payload, reverse=True)  # sort_by defaults to worst
    # Worst-first: high (1.0) → mid (0.5) → low (0.1). Reversed: low, mid, high.
    assert _section_order(md) == ["low", "mid", "high"]


# ---------------------------------------------------------------------------
# --reverse + --limit: truncation applies AFTER reverse
# ---------------------------------------------------------------------------
def test_reverse_plus_limit_picks_least_worst():
    payload = _payload(
        _entry("low", attempts_list=[(False, "x", 0.0)], budget=10),
        _entry("mid", attempts_list=[(False, "x", 0.0)] * 3, budget=6),
        _entry("high", attempts_list=[(False, "x", 0.0)] * 5, budget=5),
    )
    # Worst-first: high, mid, low. Reverse: low, mid, high. Limit 1: low.
    md = format_retry_report(payload, reverse=True, limit=1)
    assert _section_order(md) == ["low"]
    assert "Showing 1 of 3" in md


# ---------------------------------------------------------------------------
# --reverse within --group-by-error groups; group ORDER untouched
# ---------------------------------------------------------------------------
def test_reverse_within_group_but_group_order_preserved():
    payload = _payload(
        # big group (err1) — 3 cases
        _entry("a", attempts_list=[(False, "err1", 0.0)]),
        _entry("b", attempts_list=[(False, "err1", 0.0)]),
        _entry("c", attempts_list=[(False, "err1", 0.0)]),
        # small group (err2) — 1 case
        _entry("z", attempts_list=[(False, "err2", 0.0)]),
    )
    md = format_retry_report(
        payload, group_by_error=True, sort_by="name", reverse=True
    )
    # Group order: err1 (size 3) then err2 (size 1). Within err1: reversed alpha.
    big_idx = md.index("## Error: `err1`")
    small_idx = md.index("## Error: `err2`")
    assert big_idx < small_idx  # group size order preserved
    # Within err1: c, b, a (reversed alpha).
    rows_pattern = re.compile(r"^\| (?P<name>\S+) \| 0 \| ", re.MULTILINE)
    # Slice the markdown between the two group headers to isolate err1's rows.
    err1_section = md[big_idx:small_idx]
    err1_rows = [m.group("name") for m in rows_pattern.finditer(err1_section)]
    assert err1_rows == ["c", "b", "a"]


# ---------------------------------------------------------------------------
# --reverse + --only-errors: only failing cases remain, reversed
# ---------------------------------------------------------------------------
def test_reverse_composes_with_only_errors():
    payload = _payload(
        _entry("passing", attempts_list=[(True, None, 0.0)]),
        _entry("fail-a", attempts_list=[(False, "x", 0.0)]),
        _entry("fail-z", attempts_list=[(False, "x", 0.0)]),
    )
    md = format_retry_report(
        payload, only_errors=True, sort_by="name", reverse=True
    )
    assert _section_order(md) == ["fail-z", "fail-a"]
    assert "passing" not in md.replace("passed", "").replace("Passed", "")


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def test_parser_reverse_default_false(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.reverse is False


def test_parser_reverse_sets_true(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(
        ["retry", "show", str(tmp_path / "r.json"), "--reverse"]
    )
    assert ns.reverse is True


def test_cli_reverse_end_to_end(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("alpha", attempts_list=[(False, "x", 0.0)]),
            _entry("beta", attempts_list=[(False, "x", 0.0)]),
        ],
    )
    out = tmp_path / "show.md"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--sort-by",
            "name",
            "--reverse",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert _section_order(md) == ["beta", "alpha"]


def test_cli_reverse_plus_json_passthrough(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("alpha", attempts_list=[(False, "x", 0.0)]),
            _entry("beta", attempts_list=[(False, "x", 0.0)]),
        ],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--reverse",
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Raw payload — submission order preserved, unaffected by --reverse.
    assert [c["case"] for c in data["cases"]] == ["alpha", "beta"]
