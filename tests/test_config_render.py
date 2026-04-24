import json
import sys

import pytest

from frok.config import load_config, to_env, to_json, to_toml


def _cfg(**cli):
    return load_config(cli=cli)


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------
def test_to_json_round_trips_structure():
    cfg = _cfg(**{"client.api_key": "sk-abcdefgh1234", "memory.enabled": True})
    data = json.loads(to_json(cfg))
    assert data["profile"] == "dev"
    assert data["client"]["api_key"] == "****1234"
    assert data["client"]["model"] == "grok-4"
    assert data["memory"]["enabled"] is True
    # Unset fields serialise to null.
    assert data["multimodal"]["voice_model"] is None


def test_to_json_reveal_shows_api_key_plain():
    cfg = _cfg(**{"client.api_key": "sk-abcdefgh1234"})
    data = json.loads(to_json(cfg, reveal=True))
    assert data["client"]["api_key"] == "sk-abcdefgh1234"


def test_short_api_keys_are_fully_masked():
    cfg = _cfg(**{"client.api_key": "abcd"})
    data = json.loads(to_json(cfg))
    assert data["client"]["api_key"] == "****"


# ---------------------------------------------------------------------------
# to_toml
# ---------------------------------------------------------------------------
def test_to_toml_round_trips_through_tomllib():
    cfg = _cfg(
        **{
            "client.api_key": "sk-abcdefgh1234",
            "memory.enabled": True,
            "safety.disabled_rules": ("anti-sycophancy", "prompt-injection"),
            "telemetry.sink": "jsonl",
            "telemetry.path": "/tmp/frok.jsonl",
        }
    )
    text = to_toml(cfg)
    if sys.version_info >= (3, 11):
        import tomllib

        parsed = tomllib.loads(text)
        assert parsed["profile"] == "dev"
        assert parsed["client"]["model"] == "grok-4"
        assert parsed["client"]["api_key"] == "****1234"
        assert parsed["safety"]["disabled_rules"] == [
            "anti-sycophancy",
            "prompt-injection",
        ]
        assert parsed["telemetry"]["path"] == "/tmp/frok.jsonl"
        # Unset values should be absent (commented out).
        assert "voice_model" not in parsed["multimodal"]


def test_to_toml_comments_unset_fields():
    cfg = _cfg()
    text = to_toml(cfg)
    # Default config has voice_model = None and api_key = None.
    assert "# api_key  (unset)" in text
    assert "# voice_model  (unset)" in text


def test_to_toml_escapes_special_chars_in_strings():
    cfg = _cfg(**{"client.base_url": 'https://x.ai/"has quote"'})
    text = to_toml(cfg)
    assert 'base_url = "https://x.ai/\\"has quote\\""' in text


# ---------------------------------------------------------------------------
# to_env
# ---------------------------------------------------------------------------
def test_to_env_uses_loader_keys():
    cfg = _cfg(
        **{
            "client.api_key": "sk-abcdefgh1234",
            "memory.enabled": True,
            "safety.disabled_rules": ("anti-sycophancy",),
        }
    )
    text = to_env(cfg)
    lines = text.splitlines()
    assert "FROK_PROFILE=dev" in lines
    assert "FROK_CLIENT_API_KEY=****1234" in lines
    assert "FROK_CLIENT_MODEL=grok-4" in lines
    assert "FROK_SAFETY_ENABLED=true" in lines
    assert "FROK_MEMORY_ENABLED=true" in lines
    assert "FROK_SAFETY_DISABLED_RULES=anti-sycophancy" in lines
    # Unset fields get commented out.
    assert "# FROK_CLIENT_API_KEY=" not in lines  # api_key IS set
    assert "# FROK_MULTIMODAL_VOICE_MODEL=" in lines


def test_to_env_booleans_and_lists():
    cfg = _cfg(
        **{
            "multimodal.voice_enabled": True,
            "safety.disabled_rules": ("a", "b", "c"),
        }
    )
    text = to_env(cfg)
    assert "FROK_MULTIMODAL_VOICE_ENABLED=true" in text
    assert "FROK_SAFETY_DISABLED_RULES=a,b,c" in text


def test_to_env_reveal_shows_plain():
    cfg = _cfg(**{"client.api_key": "sk-abcdefgh1234"})
    assert "FROK_CLIENT_API_KEY=sk-abcdefgh1234" in to_env(cfg, reveal=True)
