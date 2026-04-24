"""Tests for ``frok init --transport {stub,real}``."""

import ast
import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_transport_default_is_stub():
    parser = build_parser()
    ns = parser.parse_args(["init"])
    assert ns.transport == "stub"


def test_parser_accepts_real_transport():
    parser = build_parser()
    ns = parser.parse_args(["init", "--transport", "real"])
    assert ns.transport == "real"


def test_parser_rejects_unknown_transport(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["init", "--transport", "bogus"])
    assert "invalid choice" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# stub (default) keeps existing behavior
# ---------------------------------------------------------------------------
def test_stub_default_scaffolds_stub_smoke_case(tmp_path):
    target = tmp_path / "p"
    assert main(["init", str(target)]) == 0
    smoke = (target / "cases" / "smoke.py").read_text(encoding="utf-8")
    # Stub-path markers:
    assert "_StubTransport" in smoke
    assert "def make_client" in smoke
    assert "api_key=\"stub\"" in smoke


def test_stub_next_steps_mentions_no_api_key_required(tmp_path, capsys):
    target = tmp_path / "p"
    main(["init", str(target)])
    out = capsys.readouterr().out
    assert "no API key is required yet" in out
    assert "FROK_CLIENT_API_KEY" not in out


# ---------------------------------------------------------------------------
# real: swaps the smoke case
# ---------------------------------------------------------------------------
def test_real_transport_scaffolds_live_case(tmp_path):
    target = tmp_path / "p"
    assert main(["init", str(target), "--transport", "real"]) == 0
    smoke = (target / "cases" / "smoke.py").read_text(encoding="utf-8")
    # No stub transport, no make_client override.
    assert "_StubTransport" not in smoke
    assert "def make_client" not in smoke
    # But it IS a valid Python module with CASES + the live-transport hint.
    assert "FROK_CLIENT_API_KEY" in smoke
    assert "CASES" in smoke
    # And it parses — the runner can import it.
    ast.parse(smoke)


def test_real_transport_next_steps_mentions_api_key(tmp_path, capsys):
    target = tmp_path / "p"
    main(["init", str(target), "--transport", "real"])
    out = capsys.readouterr().out
    assert "FROK_CLIENT_API_KEY" in out
    assert "`frok doctor`" in out
    assert "no API key is required" not in out


def test_real_smoke_case_has_expected_scorers(tmp_path):
    target = tmp_path / "p"
    main(["init", str(target), "--transport", "real"])
    smoke = (target / "cases" / "smoke.py").read_text(encoding="utf-8")
    # Loose scorers chosen so a real-model swap doesn't fail on first run.
    assert "AnswerMatches" in smoke
    assert "NoErrors" in smoke


# ---------------------------------------------------------------------------
# real + run: without api_key → ConfigError exit 2
# ---------------------------------------------------------------------------
def test_real_case_errors_without_api_key(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    target = tmp_path / "p"
    main(["init", str(target), "--transport", "real"])
    capsys.readouterr()  # drop init output

    code = main(["run", str(target / "cases" / "smoke.py")])
    assert code == 2
    err = capsys.readouterr().err
    assert "api_key" in err


# ---------------------------------------------------------------------------
# real + run: with a stubbed urllib_transport + api_key set → green
# ---------------------------------------------------------------------------
def test_real_case_runs_green_with_stubbed_urllib_transport(
    tmp_path, monkeypatch, capsys
):
    target = tmp_path / "p"
    main(["init", str(target), "--transport", "real"])
    capsys.readouterr()

    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-test")

    async def _stub_transport(*, method, url, headers, body, timeout):
        payload = {
            "model": "grok-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "Hello there."},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        }
        return 200, {}, json.dumps(payload).encode("utf-8")

    # Default factory imports urllib_transport into frok.cli.run's namespace;
    # patch it there so the factory picks up the stub.
    monkeypatch.setattr("frok.cli.run.urllib_transport", _stub_transport)

    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(target / "cases" / "smoke.py"),
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
            "--fail-on-regression",
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    assert data["failed"] == 0
    assert data["cases"][0]["case"] == "smoke-greeting"


# ---------------------------------------------------------------------------
# real + --example still works (base smoke swapped, examples unchanged)
# ---------------------------------------------------------------------------
def test_real_transport_composes_with_examples(tmp_path):
    target = tmp_path / "p"
    code = main(
        [
            "init",
            str(target),
            "--transport",
            "real",
            "--example",
            "tools",
        ]
    )
    assert code == 0
    # Smoke swapped to live version.
    smoke = (target / "cases" / "smoke.py").read_text(encoding="utf-8")
    assert "_StubTransport" not in smoke
    # Examples still use their stub transport (they run out of the box).
    tools = (target / "cases" / "tools.py").read_text(encoding="utf-8")
    assert "_StubTransport" in tools
