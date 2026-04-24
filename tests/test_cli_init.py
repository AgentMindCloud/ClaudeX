"""Tests for ``frok init [PATH]``."""

import json
import sys
import tomllib
from pathlib import Path

import pytest

from frok.cli import build_parser, main
from frok.cli.init import TEMPLATES
from frok.config import load_config


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_init_shape():
    parser = build_parser()
    ns = parser.parse_args(["init", "my-project", "--force"])
    assert ns.command == "init"
    assert ns.path == Path("my-project")
    assert ns.force is True


def test_parser_init_path_defaults_to_dot():
    parser = build_parser()
    ns = parser.parse_args(["init"])
    assert ns.path == Path(".")
    assert ns.force is False


# ---------------------------------------------------------------------------
# scaffolding
# ---------------------------------------------------------------------------
def test_init_writes_every_template_file(tmp_path, capsys):
    target = tmp_path / "fresh"
    code = main(["init", str(target)])
    assert code == 0

    for rel in TEMPLATES:
        assert (target / rel).is_file()
        assert (target / rel).read_text(encoding="utf-8").strip() != ""

    out = capsys.readouterr().out
    for rel in TEMPLATES:
        assert rel in out
    assert "Next steps" in out


def test_init_creates_nested_path_if_missing(tmp_path):
    target = tmp_path / "a" / "b" / "c"
    assert main(["init", str(target)]) == 0
    assert (target / "frok.toml").is_file()
    assert (target / ".github/workflows/frok.yml").is_file()


def test_init_existing_files_abort_without_force(tmp_path, capsys):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# custom", encoding="utf-8")

    assert main(["init", str(target)]) == 2
    err = capsys.readouterr().err
    assert "already exist" in err
    assert "CLAUDE.md" in err
    # Original contents preserved.
    assert (target / "CLAUDE.md").read_text(encoding="utf-8") == "# custom"


def test_init_force_overwrites_existing(tmp_path):
    target = tmp_path / "force"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# old", encoding="utf-8")
    assert main(["init", str(target), "--force"]) == 0
    content = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert content != "# old"
    assert "Frok" in content


# ---------------------------------------------------------------------------
# generated files are well-formed + self-consistent
# ---------------------------------------------------------------------------
def test_generated_frok_toml_loads_via_load_config(tmp_path):
    target = tmp_path / "proj"
    main(["init", str(target)])
    # Load config from the generated file — no env lookup.
    cfg = load_config(file=target / "frok.toml")
    assert cfg.profile == "dev"
    assert cfg.client.model == "grok-4"
    assert cfg.safety.enabled is True
    assert cfg.telemetry.sink == "null"
    assert cfg.memory.enabled is False


def test_generated_frok_toml_profile_override_applies(tmp_path):
    target = tmp_path / "proj"
    main(["init", str(target)])
    cfg = load_config(file=target / "frok.toml", profile="prod")
    assert cfg.profile == "prod"
    assert cfg.telemetry.sink == "jsonl"
    assert cfg.telemetry.path == "/var/log/frok.jsonl"


def test_generated_frok_toml_is_valid_toml(tmp_path):
    target = tmp_path / "proj"
    main(["init", str(target)])
    text = (target / "frok.toml").read_text(encoding="utf-8")
    # tomllib parses it without raising.
    tomllib.loads(text)


def test_generated_smoke_case_runs_green(tmp_path, capsys):
    target = tmp_path / "proj"
    assert main(["init", str(target)]) == 0
    capsys.readouterr()  # drop init output

    report_md = tmp_path / "report.md"
    summary = tmp_path / "summary.json"
    code = main(
        [
            "run",
            str(target / "cases/smoke.py"),
            "-o",
            str(report_md),
            "--summary-json",
            str(summary),
            "--fail-on-regression",
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    assert data["failed"] == 0
    assert data["cases"][0]["case"] == "smoke-greeting"


def test_generated_smoke_case_listable(tmp_path, capsys):
    target = tmp_path / "proj"
    main(["init", str(target)])
    capsys.readouterr()
    assert main(["run", str(target / "cases/smoke.py"), "--list"]) == 0
    out = capsys.readouterr().out
    assert "smoke-greeting" in out


def test_generated_claude_md_mentions_frok_usage(tmp_path):
    target = tmp_path / "proj"
    main(["init", str(target)])
    content = (target / "CLAUDE.md").read_text(encoding="utf-8")
    assert "frok run" in content
    assert "capture-baseline" in content
    assert "fail-on-regression" in content


def test_generated_workflow_references_frok_commands(tmp_path):
    target = tmp_path / "proj"
    main(["init", str(target)])
    content = (target / ".github/workflows/frok.yml").read_text(encoding="utf-8")
    assert "frok run cases/smoke.py" in content
    assert "--fail-on-regression" in content
    assert "FROK_CLIENT_API_KEY" in content


# ---------------------------------------------------------------------------
# all-or-nothing semantics
# ---------------------------------------------------------------------------
def test_init_abort_does_not_touch_other_files(tmp_path, capsys):
    target = tmp_path / "proj"
    target.mkdir()
    (target / "frok.toml").write_text("already-here", encoding="utf-8")

    assert main(["init", str(target)]) == 2
    # CLAUDE.md should NOT have been written because the existence check
    # aborted before any file was touched.
    assert not (target / "CLAUDE.md").exists()
    assert not (target / "cases/smoke.py").exists()
    # The existing frok.toml is untouched.
    assert (target / "frok.toml").read_text(encoding="utf-8") == "already-here"
