"""Tests for ``frok retry show --sort-by KEY``."""

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
    """Return the case names in the order their detail headers appear."""
    pattern = re.compile(
        r"^## (?:PASS|FAIL): (?P<name>\S+)", re.MULTILINE
    )
    return [m.group("name") for m in pattern.finditer(md)]


# ---------------------------------------------------------------------------
# default 'worst' preserves existing behaviour
# ---------------------------------------------------------------------------
def test_sort_by_worst_default_unchanged_no_limit():
    payload = _payload(
        _entry("alpha", attempts_list=[(False, "x", 0.0)]),
        _entry("beta", attempts_list=[(False, "x", 0.0)]),
    )
    md_default = format_retry_report(payload)
    md_worst = format_retry_report(payload, sort_by="worst")
    # Without --limit, 'worst' (default) preserves payload order — outputs
    # are byte-identical.
    assert md_default == md_worst


def test_sort_by_worst_with_limit_uses_worst_first():
    payload = _payload(
        # All failing, different ratios; 'worst' picks highest ratio first.
        _entry("low-ratio", attempts_list=[(False, "x", 0.0)], budget=10),
        _entry("high-ratio", attempts_list=[(False, "x", 0.0)] * 3, budget=3),
    )
    md = format_retry_report(payload, sort_by="worst", limit=1)
    assert "## FAIL: high-ratio" in md
    assert "low-ratio" not in md


# ---------------------------------------------------------------------------
# --sort-by name
# ---------------------------------------------------------------------------
def test_sort_by_name_alphabetical():
    payload = _payload(
        _entry("zebra", attempts_list=[(False, "x", 0.0)]),
        _entry("alpha", attempts_list=[(False, "x", 0.0)]),
        _entry("mango", attempts_list=[(False, "x", 0.0)]),
    )
    md = format_retry_report(payload, sort_by="name")
    assert _section_order(md) == ["alpha", "mango", "zebra"]


# ---------------------------------------------------------------------------
# --sort-by attempts
# ---------------------------------------------------------------------------
def test_sort_by_attempts_most_first():
    payload = _payload(
        _entry("two", attempts_list=[(False, "x", 0.0)] * 2),
        _entry("five", attempts_list=[(False, "x", 0.0)] * 5),
        _entry("one", attempts_list=[(False, "x", 0.0)]),
    )
    md = format_retry_report(payload, sort_by="attempts")
    assert _section_order(md) == ["five", "two", "one"]


# ---------------------------------------------------------------------------
# --sort-by ratio
# ---------------------------------------------------------------------------
def test_sort_by_ratio_highest_first():
    payload = _payload(
        # 1/10 = 0.1
        _entry("low", attempts_list=[(False, "x", 0.0)], budget=10),
        # 5/5 = 1.0
        _entry("max", attempts_list=[(False, "x", 0.0)] * 5, budget=5),
        # 3/6 = 0.5
        _entry("mid", attempts_list=[(False, "x", 0.0)] * 3, budget=6),
    )
    md = format_retry_report(payload, sort_by="ratio")
    assert _section_order(md) == ["max", "mid", "low"]


# ---------------------------------------------------------------------------
# --sort-by error
# ---------------------------------------------------------------------------
def test_sort_by_error_alpha_with_no_error_last():
    payload = _payload(
        _entry("c", attempts_list=[(False, "zeta-error", 0.0)]),
        _entry("a", attempts_list=[(False, None, 0.0)]),  # no obs error
        _entry("b", attempts_list=[(False, "alpha-error", 0.0)]),
    )
    md = format_retry_report(payload, sort_by="error")
    # alpha-error → zeta-error → no-error case last.
    assert _section_order(md) == ["b", "c", "a"]


# ---------------------------------------------------------------------------
# --sort-by sleep
# ---------------------------------------------------------------------------
def test_sort_by_sleep_highest_total_first():
    payload = _payload(
        _entry(
            "low-sleep",
            attempts_list=[(False, "x", 0.0), (False, "x", 100.0)],
        ),
        _entry(
            "high-sleep",
            attempts_list=[
                (False, "x", 0.0),
                (False, "x", 500.0),
                (False, "x", 500.0),
            ],
        ),
        _entry(
            "mid-sleep",
            attempts_list=[(False, "x", 0.0), (False, "x", 250.0)],
        ),
    )
    md = format_retry_report(payload, sort_by="sleep")
    assert _section_order(md) == ["high-sleep", "mid-sleep", "low-sleep"]


# ---------------------------------------------------------------------------
# composition: --sort-by + --limit (sort then truncate)
# ---------------------------------------------------------------------------
def test_sort_then_truncate():
    payload = _payload(
        _entry("a", attempts_list=[(False, "x", 0.0)] * 3),
        _entry("b", attempts_list=[(False, "x", 0.0)] * 5),
        _entry("c", attempts_list=[(False, "x", 0.0)] * 1),
    )
    md = format_retry_report(payload, sort_by="attempts", limit=2)
    # Sort by attempts desc → b (5), a (3), c (1). Limit 2 → b + a.
    assert _section_order(md) == ["b", "a"]
    assert "Showing 2 of 3" in md


# ---------------------------------------------------------------------------
# composition: --sort-by + --group-by-error (sort within groups)
# ---------------------------------------------------------------------------
def test_sort_within_group_by_error():
    payload = _payload(
        _entry("z", attempts_list=[(False, "shared", 0.0)] * 1),
        _entry("a", attempts_list=[(False, "shared", 0.0)] * 5),
        _entry("m", attempts_list=[(False, "shared", 0.0)] * 3),
    )
    md = format_retry_report(payload, sort_by="name", group_by_error=True)
    # Inside the single group, cases ordered alphabetically: a, m, z.
    rows_pattern = re.compile(
        r"^\| (?P<name>\S+) \| 0 \| ", re.MULTILINE
    )
    rows = [m.group("name") for m in rows_pattern.finditer(md)]
    assert rows == ["a", "m", "z"]


# ---------------------------------------------------------------------------
# unknown sort key raises
# ---------------------------------------------------------------------------
def test_unknown_sort_key_raises():
    with pytest.raises(ValueError):
        format_retry_report({"cases": []}, sort_by="bogus")


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------
def test_parser_sort_by_default_worst(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.sort_by == "worst"


def test_parser_sort_by_accepts_choices(tmp_path):
    parser = build_parser()
    for key in ["attempts", "ratio", "name", "error", "sleep"]:
        ns = parser.parse_args(
            ["retry", "show", str(tmp_path / "r.json"), "--sort-by", key]
        )
        assert ns.sort_by == key


def test_parser_sort_by_rejects_unknown_key(tmp_path, capsys):
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(
            ["retry", "show", str(tmp_path / "r.json"), "--sort-by", "bogus"]
        )


def test_cli_sort_by_end_to_end(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("zebra", attempts_list=[(False, "x", 0.0)]),
            _entry("alpha", attempts_list=[(False, "x", 0.0)]),
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
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert _section_order(md) == ["alpha", "zebra"]


def test_cli_sort_by_plus_json_passthrough(tmp_path):
    # --json passes raw payload through; --sort-by is markdown-only.
    report = _write(
        tmp_path / "r.json",
        [
            _entry("zebra", attempts_list=[(False, "x", 0.0)]),
            _entry("alpha", attempts_list=[(False, "x", 0.0)]),
        ],
    )
    out = tmp_path / "show.json"
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--sort-by",
            "name",
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # Raw payload preserves submission order — zebra first.
    assert [c["case"] for c in data["cases"]] == ["zebra", "alpha"]
