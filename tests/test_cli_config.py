"""Tests for ``frok config show``."""

import json
from pathlib import Path

from frok.cli import build_parser, main


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_config_show_shape():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "config",
            "show",
            "--format=json",
            "-p",
            "prod",
            "-o",
            "/tmp/out",
            "--reveal",
        ]
    )
    assert ns.command == "config"
    assert ns.config_command == "show"
    assert ns.format == "json"
    assert ns.profile == "prod"
    assert ns.output == Path("/tmp/out")
    assert ns.reveal is True


# ---------------------------------------------------------------------------
# default format is TOML; api_key masked unless --reveal
# ---------------------------------------------------------------------------
def test_show_default_toml_masks_api_key(monkeypatch, capsys):
    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-abcdefgh1234")
    assert main(["config", "show"]) == 0
    out = capsys.readouterr().out
    assert 'api_key = "****1234"' in out
    assert "sk-abcdefgh1234" not in out
    assert 'profile = "dev"' in out


def test_show_reveal_emits_plain_api_key(monkeypatch, capsys):
    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-abcdefgh1234")
    assert main(["config", "show", "--reveal"]) == 0
    out = capsys.readouterr().out
    assert "sk-abcdefgh1234" in out


# ---------------------------------------------------------------------------
# --format=json / env
# ---------------------------------------------------------------------------
def test_show_json_format_is_parsable(monkeypatch, capsys):
    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-abcdefgh1234")
    monkeypatch.setenv("FROK_MEMORY_ENABLED", "true")
    assert main(["config", "show", "--format=json"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["client"]["api_key"] == "****1234"
    assert data["memory"]["enabled"] is True


def test_show_env_format_matches_loader_keys(monkeypatch, capsys):
    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-abcd1234")
    assert main(["config", "show", "--format=env"]) == 0
    out = capsys.readouterr().out
    assert "FROK_PROFILE=dev" in out
    assert "FROK_CLIENT_API_KEY=****1234" in out
    assert "FROK_CLIENT_MODEL=grok-4" in out


# ---------------------------------------------------------------------------
# --config / --profile honoured the same way `run` does
# ---------------------------------------------------------------------------
def test_show_reads_explicit_config_file_and_profile(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    monkeypatch.delenv("FROK_PROFILE", raising=False)
    path = tmp_path / "c.json"
    path.write_text(
        json.dumps(
            {
                "client": {"model": "base-model"},
                "profiles": {
                    "prod": {"client": {"model": "prod-model", "api_key": "sk-prod1234"}}
                },
            }
        ),
        encoding="utf-8",
    )
    assert main(
        [
            "config",
            "show",
            "--format=json",
            "-c",
            str(path),
            "-p",
            "prod",
        ]
    ) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["profile"] == "prod"
    assert data["client"]["model"] == "prod-model"
    assert data["client"]["api_key"] == "****1234"


# ---------------------------------------------------------------------------
# --output writes file + suppresses stdout
# ---------------------------------------------------------------------------
def test_show_output_writes_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-abcd1234")
    dest = tmp_path / "nested" / "config.toml"
    assert main(["config", "show", "-o", str(dest)]) == 0
    assert capsys.readouterr().out == ""
    text = dest.read_text(encoding="utf-8")
    assert 'api_key = "****1234"' in text


# ---------------------------------------------------------------------------
# config load failure surfaces as CliError / exit 2
# ---------------------------------------------------------------------------
def test_show_with_missing_config_file_is_cli_error(tmp_path, capsys):
    code = main(
        ["config", "show", "-c", str(tmp_path / "does-not-exist.json")]
    )
    assert code == 2
    assert "config load failed" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# config subparser without 'show' still fails with exit 2
# ---------------------------------------------------------------------------
def test_config_subcommand_required():
    import pytest

    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["config"])
