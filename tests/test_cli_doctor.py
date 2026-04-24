"""Tests for ``frok doctor``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main
from frok.cli.doctor import (
    FAIL,
    PASS,
    SKIP,
    Check,
    check_client_live,
    check_config,
    check_memory,
    check_multimodal,
    check_safety,
    check_telemetry,
    render_json,
    render_markdown,
)
from frok.config import load_config


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_doctor_shape():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "doctor",
            "-c",
            "/tmp/c.toml",
            "-p",
            "prod",
            "-o",
            "/tmp/r.md",
            "--json",
            "--no-live",
            "--fail-on-skip",
        ]
    )
    assert ns.command == "doctor"
    assert ns.config == Path("/tmp/c.toml")
    assert ns.profile == "prod"
    assert ns.output == Path("/tmp/r.md")
    assert ns.json is True
    assert ns.live is False
    assert ns.fail_on_skip is True


def test_parser_live_defaults_to_true():
    parser = build_parser()
    ns = parser.parse_args(["doctor"])
    assert ns.live is True
    assert ns.fail_on_skip is False


# ---------------------------------------------------------------------------
# library-level checks
# ---------------------------------------------------------------------------
async def test_check_config_reports_profile_and_source():
    cfg = load_config()
    c = await check_config(cfg, source="from env + defaults")
    assert c.status == PASS
    assert "'dev'" in c.detail
    assert "from env + defaults" in c.detail


async def test_check_safety_counts_active_rules():
    cfg = load_config()
    c = await check_safety(cfg)
    assert c.status == PASS
    assert "4 rules enabled" in c.detail  # BUILTIN_RULES has 4 entries


async def test_check_safety_reflects_disabled_rules():
    cfg = load_config(cli={"safety.disabled_rules": ("anti-sycophancy",)})
    c = await check_safety(cfg)
    assert c.status == PASS
    assert "anti-sycophancy" in c.detail


async def test_check_telemetry_null_sink_passes():
    cfg = load_config()
    c = await check_telemetry(cfg)
    assert c.status == PASS
    assert "'null'" in c.detail


async def test_check_telemetry_jsonl_missing_path_fails():
    cfg = load_config(cli={"telemetry.sink": "jsonl"})
    c = await check_telemetry(cfg)
    assert c.status == FAIL
    assert "path" in c.detail


async def test_check_telemetry_jsonl_opens_file(tmp_path):
    cfg = load_config(
        cli={
            "telemetry.sink": "jsonl",
            "telemetry.path": str(tmp_path / "t.jsonl"),
        }
    )
    c = await check_telemetry(cfg)
    assert c.status == PASS


async def test_check_memory_skipped_by_default():
    cfg = load_config()
    c = await check_memory(cfg)
    assert c.status == SKIP
    assert "disabled" in c.detail


async def test_check_memory_round_trip_when_enabled(tmp_path):
    cfg = load_config(
        cli={
            "memory.enabled": True,
            "memory.path": str(tmp_path / "m.db"),
            "memory.embedder_dim": 32,
        }
    )
    c = await check_memory(cfg)
    assert c.status == PASS
    assert "round-trip ok" in c.detail


async def test_check_memory_unsupported_embedder_fails():
    cfg = load_config(
        cli={"memory.enabled": True, "memory.embedder": "ghost"}
    )
    c = await check_memory(cfg)
    assert c.status == FAIL
    assert "unsupported" in c.detail


async def test_check_multimodal_reflects_config():
    cfg = load_config(
        cli={
            "multimodal.vision_enabled": True,
            "multimodal.voice_enabled": True,
        }
    )
    c = await check_multimodal(cfg)
    assert c.status == PASS
    assert "vision=on" in c.detail and "voice=on" in c.detail


# ---------------------------------------------------------------------------
# live client check with a stub transport
# ---------------------------------------------------------------------------
async def _stub_ok(*, method, url, headers, body, timeout):
    payload = {
        "model": "grok-4",
        "choices": [
            {"message": {"role": "assistant", "content": "pong"}, "finish_reason": "stop"}
        ],
        "usage": {"prompt_tokens": 3, "completion_tokens": 1},
    }
    return 200, {}, json.dumps(payload).encode("utf-8")


async def _stub_http_500(*, method, url, headers, body, timeout):
    return 500, {}, b'{"error": "bad"}'


async def test_client_live_skips_when_no_api_key():
    cfg = load_config()
    c = await check_client_live(cfg, live=True)
    assert c.status == SKIP
    assert "no client.api_key" in c.detail


async def test_client_live_skips_when_live_false():
    cfg = load_config(cli={"client.api_key": "sk-t"})
    c = await check_client_live(cfg, live=False, transport=_stub_ok)
    assert c.status == SKIP
    assert "--no-live" in c.detail


async def test_client_live_passes_with_stub_transport():
    cfg = load_config(cli={"client.api_key": "sk-t"})
    c = await check_client_live(cfg, live=True, transport=_stub_ok)
    assert c.status == PASS
    assert "tokens" in c.detail
    assert "grok-4" in c.detail


async def test_client_live_fails_on_http_error():
    cfg = load_config(
        cli={"client.api_key": "sk-t", "client.max_retries": 0}
    )
    c = await check_client_live(cfg, live=True, transport=_stub_http_500)
    assert c.status == FAIL
    assert "HTTPError" in c.detail or "HTTP 500" in c.detail


# ---------------------------------------------------------------------------
# renderers
# ---------------------------------------------------------------------------
def test_render_markdown_includes_all_checks_and_counts():
    checks = [
        Check("a", PASS, "ok"),
        Check("b", FAIL, "boom"),
        Check("c", SKIP, "later"),
    ]
    md = render_markdown(checks)
    assert "[PASS] a" in md
    assert "[FAIL] b" in md
    assert "[SKIP] c" in md
    assert "Total: 3 checks (1 PASS, 1 FAIL, 1 SKIP)" in md


def test_render_json_shape():
    checks = [Check("a", PASS, "ok"), Check("b", FAIL, "boom")]
    data = render_json(checks)
    assert data["total"] == 2
    assert data["counts"] == {PASS: 1, FAIL: 1, SKIP: 0}
    assert [c["name"] for c in data["checks"]] == ["a", "b"]
    # Round-trips through json.
    json.dumps(data)


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------
def test_cli_default_run_prints_markdown(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "# Frok Doctor" in out
    assert "[PASS] config" in out
    assert "[SKIP] client-live" in out
    assert "Total: 6 checks" in out


def test_cli_json_output_parseable(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    assert main(["doctor", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 6
    names = [c["name"] for c in data["checks"]]
    assert names == [
        "config",
        "safety",
        "telemetry",
        "memory",
        "multimodal",
        "client-live",
    ]


def test_cli_output_flag_writes_file(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    dest = tmp_path / "nested" / "doctor.md"
    assert main(["doctor", "-o", str(dest)]) == 0
    assert capsys.readouterr().out == ""
    assert "# Frok Doctor" in dest.read_text(encoding="utf-8")


def test_cli_fail_on_skip_returns_1(tmp_path, capsys, monkeypatch):
    # Default config has 2 SKIP (memory, client-live) — --fail-on-skip fires.
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    assert main(["doctor", "--fail-on-skip"]) == 1


def test_cli_fail_returns_1_on_failing_config(tmp_path, capsys, monkeypatch):
    # telemetry.sink=jsonl without a path → telemetry check FAILs.
    monkeypatch.setenv("FROK_TELEMETRY_SINK", "jsonl")
    monkeypatch.delenv("FROK_TELEMETRY_PATH", raising=False)
    assert main(["doctor"]) == 1
    out = capsys.readouterr().out
    assert "[FAIL] telemetry" in out


def test_cli_no_live_skips_client_check_even_with_api_key(monkeypatch, capsys):
    monkeypatch.setenv("FROK_CLIENT_API_KEY", "sk-fake")
    assert main(["doctor", "--no-live"]) == 0
    out = capsys.readouterr().out
    assert "[SKIP] client-live" in out
    assert "--no-live" in out


def test_cli_config_load_failure_surfaces_as_cli_error(tmp_path, capsys):
    code = main(["doctor", "-c", str(tmp_path / "missing.json")])
    assert code == 2
    assert "config load failed" in capsys.readouterr().err


def test_cli_honors_explicit_config_file(tmp_path, capsys, monkeypatch):
    # Strip any env so the file is the sole source of truth.
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    monkeypatch.delenv("FROK_PROFILE", raising=False)
    path = tmp_path / "c.json"
    path.write_text(
        json.dumps({"client": {"model": "grok-4-fast"}}),
        encoding="utf-8",
    )
    assert main(["doctor", "-c", str(path), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    config_check = next(c for c in data["checks"] if c["name"] == "config")
    assert f"from {path}" in config_check["detail"]
