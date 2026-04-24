import json

import pytest

from frok.config import ConfigError, FrokConfig, load_config


# ---------------------------------------------------------------------------
# defaults
# ---------------------------------------------------------------------------
def test_defaults_are_hermetic_with_no_inputs():
    cfg = load_config()
    assert isinstance(cfg, FrokConfig)
    assert cfg.profile == "dev"
    assert cfg.client.model == "grok-4"
    assert cfg.client.base_url == "https://api.x.ai/v1"
    assert cfg.client.api_key is None
    assert cfg.safety.enabled is True
    assert cfg.safety.disabled_rules == ()
    assert cfg.telemetry.sink == "null"
    assert cfg.memory.enabled is False
    assert cfg.multimodal.vision_enabled is True
    assert cfg.multimodal.voice_enabled is False


def test_env_none_means_dont_read_environ():
    # Even if the real os.environ had FROK_* vars set, passing env=None leaves
    # them untouched; defaults win.
    cfg = load_config(env=None)
    assert cfg.client.api_key is None


# ---------------------------------------------------------------------------
# env
# ---------------------------------------------------------------------------
def test_env_populates_all_types():
    env = {
        "FROK_PROFILE": "prod",
        "FROK_CLIENT_API_KEY": "sk-test",
        "FROK_CLIENT_MODEL": "grok-4-fast",
        "FROK_CLIENT_TIMEOUT_S": "12.5",
        "FROK_CLIENT_MAX_RETRIES": "6",
        "FROK_SAFETY_ENABLED": "false",
        "FROK_SAFETY_DISABLED_RULES": "anti-sycophancy, prompt-injection",
        "FROK_TELEMETRY_SINK": "memory",
        "FROK_MEMORY_ENABLED": "1",
        "FROK_MEMORY_EMBEDDER_DIM": "256",
        "FROK_MULTIMODAL_VOICE_ENABLED": "yes",
        "FROK_MULTIMODAL_VOICE_MODEL": "grok-voice",
    }
    cfg = load_config(env=env)
    assert cfg.profile == "prod"
    assert cfg.client.api_key == "sk-test"
    assert cfg.client.model == "grok-4-fast"
    assert cfg.client.timeout_s == 12.5
    assert cfg.client.max_retries == 6
    assert cfg.safety.enabled is False
    assert cfg.safety.disabled_rules == ("anti-sycophancy", "prompt-injection")
    assert cfg.telemetry.sink == "memory"
    assert cfg.memory.enabled is True
    assert cfg.memory.embedder_dim == 256
    assert cfg.multimodal.voice_enabled is True
    assert cfg.multimodal.voice_model == "grok-voice"


def test_env_ignores_unrelated_vars():
    env = {"PATH": "/usr/bin", "HOME": "/root", "FROK_CLIENT_MODEL": "only-this"}
    cfg = load_config(env=env)
    assert cfg.client.model == "only-this"


# ---------------------------------------------------------------------------
# file (json + toml)
# ---------------------------------------------------------------------------
def test_json_file_loads_sections(tmp_path):
    path = tmp_path / "conf.json"
    path.write_text(
        json.dumps(
            {
                "client": {"api_key": "from-file", "model": "grok-4-alpha"},
                "memory": {"enabled": True, "path": "./f.db"},
            }
        ),
        encoding="utf-8",
    )
    cfg = load_config(file=path)
    assert cfg.client.api_key == "from-file"
    assert cfg.memory.enabled is True
    assert cfg.memory.path == "./f.db"


def test_toml_file_loads_sections(tmp_path):
    path = tmp_path / "conf.toml"
    path.write_text(
        """
        profile = "staging"
        [client]
        api_key = "sk-toml"
        timeout_s = 30.0
        [telemetry]
        sink = "jsonl"
        path = "./trace.jsonl"
        """,
        encoding="utf-8",
    )
    cfg = load_config(file=path)
    assert cfg.profile == "staging"
    assert cfg.client.api_key == "sk-toml"
    assert cfg.client.timeout_s == 30.0
    assert cfg.telemetry.sink == "jsonl"


def test_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(file=tmp_path / "missing.json")


def test_unsupported_extension_raises(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("a: b", encoding="utf-8")
    with pytest.raises(ConfigError, match="unsupported"):
        load_config(file=p)


# ---------------------------------------------------------------------------
# CLI overrides: nested + flat-dotted
# ---------------------------------------------------------------------------
def test_cli_nested_dict_wins_over_env():
    env = {"FROK_CLIENT_MODEL": "env-model"}
    cfg = load_config(env=env, cli={"client": {"model": "cli-model"}})
    assert cfg.client.model == "cli-model"


def test_cli_flat_dotted_keys_are_nested():
    cfg = load_config(cli={"client.api_key": "dotted", "memory.enabled": True})
    assert cfg.client.api_key == "dotted"
    assert cfg.memory.enabled is True


def test_cli_none_values_are_ignored():
    # Makes it trivial to forward argparse.Namespace() vars() dicts.
    env = {"FROK_CLIENT_MODEL": "from-env"}
    cfg = load_config(env=env, cli={"client.model": None, "client.api_key": "k"})
    assert cfg.client.model == "from-env"  # not overridden by None
    assert cfg.client.api_key == "k"


# ---------------------------------------------------------------------------
# precedence: file < env < cli
# ---------------------------------------------------------------------------
def test_precedence_file_env_cli(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(
        json.dumps(
            {"client": {"api_key": "file-key", "model": "file-model"}}
        ),
        encoding="utf-8",
    )
    env = {"FROK_CLIENT_MODEL": "env-model"}
    cli = {"client.model": "cli-model"}
    cfg = load_config(file=path, env=env, cli=cli)
    assert cfg.client.api_key == "file-key"  # only file set it
    assert cfg.client.model == "cli-model"  # CLI wins


# ---------------------------------------------------------------------------
# profiles
# ---------------------------------------------------------------------------
def test_profile_section_merges_on_top(tmp_path):
    path = tmp_path / "p.json"
    path.write_text(
        json.dumps(
            {
                "client": {"model": "base-model"},
                "telemetry": {"sink": "null"},
                "profiles": {
                    "prod": {
                        "client": {"model": "prod-model"},
                        "telemetry": {"sink": "jsonl", "path": "/tmp/t.jsonl"},
                    },
                    "dev": {"client": {"model": "dev-model"}},
                },
            }
        ),
        encoding="utf-8",
    )
    prod = load_config(file=path, profile="prod")
    assert prod.profile == "prod"
    assert prod.client.model == "prod-model"
    assert prod.telemetry.sink == "jsonl"
    assert prod.telemetry.path == "/tmp/t.jsonl"

    dev = load_config(file=path, profile="dev")
    assert dev.client.model == "dev-model"
    assert dev.telemetry.sink == "null"  # not touched by dev profile


def test_profile_can_be_set_via_env(tmp_path):
    path = tmp_path / "p.json"
    path.write_text(
        json.dumps(
            {
                "client": {"model": "base"},
                "profiles": {"prod": {"client": {"model": "prod"}}},
            }
        ),
        encoding="utf-8",
    )
    cfg = load_config(file=path, env={"FROK_PROFILE": "prod"})
    assert cfg.profile == "prod"
    assert cfg.client.model == "prod"


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_unknown_section_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"ghost": {"x": 1}}), encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown config section"):
        load_config(file=path)


def test_unknown_field_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"client": {"bogus": 1}}), encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown 'client' field"):
        load_config(file=path)


def test_non_mapping_section_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"client": "not-a-table"}), encoding="utf-8")
    with pytest.raises(ConfigError, match="must be a table"):
        load_config(file=path)
