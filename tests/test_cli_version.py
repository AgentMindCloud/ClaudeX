"""Tests for ``frok version``."""

import json
import platform
import re

import pytest

import frok
from frok.cli import build_parser, main
from frok.cli.version import VersionInfo, collect_version_info


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_version_defaults():
    parser = build_parser()
    ns = parser.parse_args(["version"])
    assert ns.command == "version"
    assert ns.short is False
    assert ns.json is False


def test_parser_version_flags():
    parser = build_parser()
    ns = parser.parse_args(["version", "--short", "--json"])
    assert ns.short is True
    assert ns.json is True


# ---------------------------------------------------------------------------
# collect_version_info
# ---------------------------------------------------------------------------
def test_collect_version_info_matches_runtime():
    info = collect_version_info()
    assert isinstance(info, VersionInfo)
    assert info.frok == frok.__version__
    assert info.python == platform.python_version()
    assert info.platform  # non-empty platform string


# ---------------------------------------------------------------------------
# CLI output
# ---------------------------------------------------------------------------
def test_cli_default_prints_single_line_summary(capsys):
    assert main(["version"]) == 0
    out = capsys.readouterr().out.strip()
    # Exactly one line, shape: "frok X.Y.Z (Python X.Y.Z, <platform>)"
    assert "\n" not in out
    assert out.startswith(f"frok {frok.__version__} (Python ")
    assert out.endswith(")")
    assert re.search(r"Python \d+\.\d+\.\d+", out)


def test_cli_short_prints_only_frok_version(capsys):
    assert main(["version", "--short"]) == 0
    assert capsys.readouterr().out.strip() == frok.__version__


def test_cli_json_is_parseable_and_complete(capsys):
    assert main(["version", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == {
        "frok": frok.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(aliased=True),
    }


def test_cli_short_wins_over_json(capsys):
    # If both flags are set, --short is the more specific request.
    assert main(["version", "--short", "--json"]) == 0
    out = capsys.readouterr().out.strip()
    assert out == frok.__version__
    # Not JSON.
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_cli_version_returns_zero():
    assert main(["version"]) == 0
    assert main(["version", "--short"]) == 0
    assert main(["version", "--json"]) == 0
