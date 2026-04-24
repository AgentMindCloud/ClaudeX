"""End-to-end tests for ``frok retry diff A B``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


def _write_report(path: Path, entries: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"cases": entries}, indent=2), encoding="utf-8"
    )
    return path


def _entry(case, *, repeat=0, attempts_list, passed=None):
    attempts = [
        {
            "attempt": i + 1,
            "passed": ok,
            "error": err,
            "sleep_before_ms": 0.0,
        }
        for i, (ok, err) in enumerate(attempts_list)
    ]
    if passed is None:
        passed = bool(attempts_list) and bool(attempts_list[-1][0])
    return {
        "case": case,
        "repeat": repeat,
        "attempts": attempts,
        "retry_budget": max(len(attempts_list), 1),
        "passed": passed,
    }


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_registers_retry_diff(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(
        [
            "retry",
            "diff",
            str(tmp_path / "a.json"),
            str(tmp_path / "b.json"),
        ]
    )
    assert ns.command == "retry"
    assert ns.retry_command == "diff"
    assert ns.a == tmp_path / "a.json"
    assert ns.b == tmp_path / "b.json"
    assert ns.fail_on_regression is False
    assert ns.json is False


# ---------------------------------------------------------------------------
# clean diff of identical reports
# ---------------------------------------------------------------------------
def test_identical_reports_exit_zero(tmp_path):
    a = _write_report(
        tmp_path / "a.json", [_entry("x", attempts_list=[(True, None)])]
    )
    b = _write_report(
        tmp_path / "b.json", [_entry("x", attempts_list=[(True, None)])]
    )
    out = tmp_path / "diff.md"
    code = main(
        ["retry", "diff", str(a), str(b), "-o", str(out)]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "Matched cases: 1" in md
    assert "Regressed: no" in md


# ---------------------------------------------------------------------------
# attempts grew → --fail-on-regression returns 1
# ---------------------------------------------------------------------------
def test_attempts_grew_fail_on_regression(tmp_path):
    a = _write_report(
        tmp_path / "a.json",
        [_entry("x", attempts_list=[(False, "err"), (True, None)])],
    )
    b = _write_report(
        tmp_path / "b.json",
        [
            _entry(
                "x",
                attempts_list=[
                    (False, "err"),
                    (False, "err"),
                    (True, None),
                ],
            )
        ],
    )
    code = main(
        [
            "retry",
            "diff",
            str(a),
            str(b),
            "--fail-on-regression",
            "-o",
            str(tmp_path / "diff.md"),
        ]
    )
    assert code == 1


# ---------------------------------------------------------------------------
# --json emits structured output
# ---------------------------------------------------------------------------
def test_json_output_structured(tmp_path):
    a = _write_report(
        tmp_path / "a.json", [_entry("x", attempts_list=[(True, None)])]
    )
    b = _write_report(
        tmp_path / "b.json", [_entry("x", attempts_list=[(False, "boom")])]
    )
    out = tmp_path / "diff.json"
    code = main(
        [
            "retry",
            "diff",
            str(a),
            str(b),
            "--json",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["a_path"] == str(a)
    assert data["b_path"] == str(b)
    assert data["regressed"] is True
    assert len(data["newly_failing"]) == 1


# ---------------------------------------------------------------------------
# missing report file → CliError
# ---------------------------------------------------------------------------
def test_missing_report_is_cli_error(tmp_path, capsys):
    a = tmp_path / "missing.json"
    b = _write_report(
        tmp_path / "b.json", [_entry("x", attempts_list=[(True, None)])]
    )
    code = main(["retry", "diff", str(a), str(b)])
    assert code == 2
    assert "retry report not found" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# malformed report → CliError
# ---------------------------------------------------------------------------
def test_malformed_report_is_cli_error(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("not-valid-json{", encoding="utf-8")
    good = _write_report(
        tmp_path / "good.json", [_entry("x", attempts_list=[(True, None)])]
    )
    code = main(["retry", "diff", str(bad), str(good)])
    assert code == 2
    assert "retry report is not valid JSON" in capsys.readouterr().err


def test_report_missing_cases_key_is_cli_error(tmp_path, capsys):
    bad = tmp_path / "noroot.json"
    bad.write_text(json.dumps({"other": []}), encoding="utf-8")
    good = _write_report(
        tmp_path / "good.json", [_entry("x", attempts_list=[(True, None)])]
    )
    code = main(["retry", "diff", str(bad), str(good)])
    assert code == 2
    assert "missing 'cases' list" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# custom labels surface in markdown
# ---------------------------------------------------------------------------
def test_labels_surface_in_markdown(tmp_path):
    a = _write_report(
        tmp_path / "a.json", [_entry("x", attempts_list=[(True, None)])]
    )
    b = _write_report(
        tmp_path / "b.json", [_entry("x", attempts_list=[(True, None)])]
    )
    out = tmp_path / "diff.md"
    code = main(
        [
            "retry",
            "diff",
            str(a),
            str(b),
            "--a-label",
            "monday",
            "--b-label",
            "today",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "- monday:" in md
    assert "- today:" in md
