"""End-to-end tests for ``frok retry summarize DIR``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


def _entry(case: str, *, repeat: int = 0, attempts: int = 1, passed: bool = True):
    return {
        "case": case,
        "repeat": repeat,
        "attempts": [
            {
                "attempt": i + 1,
                "passed": (i == attempts - 1 and passed),
                "error": None,
                "sleep_before_ms": 0.0,
            }
            for i in range(attempts)
        ],
        "retry_budget": max(attempts, 1),
        "passed": passed,
    }


def _write(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"cases": entries}), encoding="utf-8")


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_registers_retry_summarize(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["retry", "summarize", str(tmp_path)])
    assert ns.command == "retry"
    assert ns.retry_command == "summarize"
    assert ns.directory == tmp_path
    assert ns.fail_on_growing is False
    assert ns.json is False


# ---------------------------------------------------------------------------
# happy path
# ---------------------------------------------------------------------------
def test_summarize_writes_markdown(tmp_path):
    _write(tmp_path / "2026-04-20.json", [_entry("x", attempts=1)])
    _write(tmp_path / "2026-04-21.json", [_entry("x", attempts=3)])
    out = tmp_path / "summary.md"
    code = main(["retry", "summarize", str(tmp_path), "-o", str(out)])
    assert code == 0
    md = out.read_text(encoding="utf-8")
    assert "Reports: 2" in md
    assert "Growing: 1" in md


def test_summarize_json_output(tmp_path):
    _write(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write(tmp_path / "b.json", [_entry("x", attempts=2)])
    out = tmp_path / "summary.json"
    code = main(
        ["retry", "summarize", str(tmp_path), "--json", "-o", str(out)]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["trend_counts"]["growing"] == 1
    assert len(data["cases"]) == 1
    assert data["cases"][0]["attempts_by_report"] == [1, 2]


# ---------------------------------------------------------------------------
# --fail-on-growing interop
# ---------------------------------------------------------------------------
def test_fail_on_growing_returns_1_when_growing(tmp_path):
    _write(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write(tmp_path / "b.json", [_entry("x", attempts=2)])
    code = main(
        [
            "retry",
            "summarize",
            str(tmp_path),
            "--fail-on-growing",
            "-o",
            str(tmp_path / "s.md"),
        ]
    )
    assert code == 1


def test_fail_on_growing_returns_0_when_no_growing(tmp_path):
    # Mixed, not growing.
    _write(tmp_path / "a.json", [_entry("x", attempts=1)])
    _write(tmp_path / "b.json", [_entry("x", attempts=3)])
    _write(tmp_path / "c.json", [_entry("x", attempts=2)])
    code = main(
        [
            "retry",
            "summarize",
            str(tmp_path),
            "--fail-on-growing",
            "-o",
            str(tmp_path / "s.md"),
        ]
    )
    # "mixed" trend, not "growing" — flag only catches monotonic growth.
    assert code == 0


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_missing_directory_is_cli_error(tmp_path, capsys):
    code = main(["retry", "summarize", str(tmp_path / "nope")])
    assert code == 2
    assert "directory not found" in capsys.readouterr().err


def test_empty_directory_is_cli_error(tmp_path, capsys):
    code = main(["retry", "summarize", str(tmp_path)])
    assert code == 2
    assert "no *.json retry reports" in capsys.readouterr().err


def test_malformed_report_is_cli_error(tmp_path, capsys):
    (tmp_path / "bad.json").write_text("not-json{", encoding="utf-8")
    code = main(["retry", "summarize", str(tmp_path)])
    assert code == 2
    assert "not valid JSON" in capsys.readouterr().err


def test_not_a_directory_is_cli_error(tmp_path, capsys):
    f = tmp_path / "file.json"
    f.write_text("{}", encoding="utf-8")
    code = main(["retry", "summarize", str(f)])
    assert code == 2
    assert "not a directory" in capsys.readouterr().err
