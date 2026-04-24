"""End-to-end tests for ``frok retry show PATH``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


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


def _write(path: Path, entries: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cases": entries}), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_registers_retry_show(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "show", str(tmp_path / "r.json")])
    assert ns.command == "retry"
    assert ns.retry_command == "show"
    assert ns.path == tmp_path / "r.json"
    assert ns.fail_on_failure is False
    assert ns.json is False


# ---------------------------------------------------------------------------
# happy path: clean pass renders markdown, exit 0
# ---------------------------------------------------------------------------
def test_clean_pass_renders_markdown(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [_entry("a", attempts_list=[(True, None, 0.0)])],
    )
    out = tmp_path / "show.md"
    code = main(["retry", "show", str(report), "-o", str(out)])
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "# Frok Retry Report" in md
    assert "- Cases: 1" in md
    assert "## Clean passes" in md


# ---------------------------------------------------------------------------
# --json passes through the payload
# ---------------------------------------------------------------------------
def test_json_output_passes_through(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [_entry("a", attempts_list=[(True, None, 0.0)])],
    )
    out = tmp_path / "show.json"
    code = main(
        ["retry", "show", str(report), "--json", "-o", str(out)]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    # The payload is preserved verbatim.
    assert data["cases"][0]["case"] == "a"
    assert data["cases"][0]["passed"] is True


# ---------------------------------------------------------------------------
# retried case shows attempt table with error + sleep
# ---------------------------------------------------------------------------
def test_retried_case_table(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry(
                "flaky",
                attempts_list=[
                    (False, "429", 0.0),
                    (False, "429", 250.0),
                    (True, None, 250.0),
                ],
                budget=4,
            )
        ],
    )
    out = tmp_path / "show.md"
    code = main(["retry", "show", str(report), "-o", str(out)])
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "## PASS: flaky (repeat 0) — 3/4 attempts" in md
    assert "| 1 | no | `429` | 0.0 |" in md
    assert "| 3 | yes | - | 250.0 |" in md


# ---------------------------------------------------------------------------
# --fail-on-failure gate
# ---------------------------------------------------------------------------
def test_fail_on_failure_returns_1_when_any_case_failed(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [
            _entry("a", attempts_list=[(True, None, 0.0)]),
            _entry("b", attempts_list=[(False, "boom", 0.0)]),
        ],
    )
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--fail-on-failure",
            "-o",
            str(tmp_path / "show.md"),
        ]
    )
    assert code == 1


def test_fail_on_failure_returns_0_when_all_pass(tmp_path):
    report = _write(
        tmp_path / "r.json",
        [_entry("a", attempts_list=[(True, None, 0.0)])],
    )
    code = main(
        [
            "retry",
            "show",
            str(report),
            "--fail-on-failure",
            "-o",
            str(tmp_path / "show.md"),
        ]
    )
    assert code == 0


# ---------------------------------------------------------------------------
# error paths (reuse retry diff's loader, so same error shapes)
# ---------------------------------------------------------------------------
def test_missing_file_is_cli_error(tmp_path, capsys):
    code = main(["retry", "show", str(tmp_path / "nope.json")])
    assert code == 2
    assert "retry report not found" in capsys.readouterr().err


def test_malformed_json_is_cli_error(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("not-json{", encoding="utf-8")
    code = main(["retry", "show", str(bad)])
    assert code == 2
    assert "retry report is not valid JSON" in capsys.readouterr().err


def test_missing_cases_key_is_cli_error(tmp_path, capsys):
    bad = tmp_path / "noroot.json"
    bad.write_text(json.dumps({"other": []}), encoding="utf-8")
    code = main(["retry", "show", str(bad)])
    assert code == 2
    assert "missing 'cases' list" in capsys.readouterr().err
