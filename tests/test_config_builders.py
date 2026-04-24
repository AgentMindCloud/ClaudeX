import pytest

from frok.clients.grok import GrokClient
from frok.config import (
    ConfigError,
    FrokConfig,
    build_client,
    build_memory_store,
    build_multimodal_adapter,
    build_safety_ruleset,
    build_telemetry_sink,
    build_tracer,
    load_config,
)
from frok.memory import HashEmbedder, MemoryStore
from frok.multimodal import MultimodalAdapter
from frok.telemetry import InMemorySink, JsonlSink, NullSink


# ---------------------------------------------------------------------------
# safety
# ---------------------------------------------------------------------------
def test_safety_disabled_returns_empty_ruleset():
    cfg = load_config(cli={"safety.enabled": False})
    rs = build_safety_ruleset(cfg)
    assert rs.rules == ()


def test_safety_excludes_disabled_rules_but_keeps_others():
    cfg = load_config(cli={"safety.disabled_rules": ("anti-sycophancy",)})
    rs = build_safety_ruleset(cfg)
    names = {r.name for r in rs.rules}
    assert "anti-sycophancy" not in names
    assert "no-overclaim" in names


def test_safety_unknown_disabled_rule_raises():
    cfg = load_config(cli={"safety.disabled_rules": ("ghost-rule",)})
    with pytest.raises(ConfigError, match="unknown safety rule"):
        build_safety_ruleset(cfg)


# ---------------------------------------------------------------------------
# telemetry
# ---------------------------------------------------------------------------
def test_telemetry_sink_null_by_default():
    assert isinstance(build_telemetry_sink(load_config()), NullSink)


def test_telemetry_sink_memory():
    cfg = load_config(cli={"telemetry.sink": "memory"})
    assert isinstance(build_telemetry_sink(cfg), InMemorySink)


def test_telemetry_sink_jsonl_requires_path(tmp_path):
    cfg_no_path = load_config(cli={"telemetry.sink": "jsonl"})
    with pytest.raises(ConfigError, match="path is required"):
        build_telemetry_sink(cfg_no_path)
    cfg_ok = load_config(
        cli={
            "telemetry.sink": "jsonl",
            "telemetry.path": str(tmp_path / "t.jsonl"),
        }
    )
    sink = build_telemetry_sink(cfg_ok)
    try:
        assert isinstance(sink, JsonlSink)
    finally:
        sink.close()


def test_telemetry_sink_unknown_raises():
    cfg = load_config(cli={"telemetry.sink": "carrier-pigeon"})
    with pytest.raises(ConfigError, match="unknown telemetry.sink"):
        build_telemetry_sink(cfg)


def test_build_tracer_wires_sink_from_config():
    cfg = load_config(cli={"telemetry.sink": "memory"})
    t = build_tracer(cfg)
    assert isinstance(t.sink, InMemorySink)


# ---------------------------------------------------------------------------
# client
# ---------------------------------------------------------------------------
def test_build_client_requires_api_key():
    with pytest.raises(ConfigError, match="api_key is not configured"):
        build_client(load_config())


def test_build_client_wires_fields():
    cfg = load_config(
        cli={
            "client.api_key": "sk-x",
            "client.model": "grok-4-mini",
            "client.base_url": "https://api.example/v2",
            "client.timeout_s": 3.0,
            "client.max_retries": 2,
            "safety.disabled_rules": ("anti-sycophancy",),
            "telemetry.sink": "memory",
        }
    )
    client = build_client(cfg)
    assert isinstance(client, GrokClient)
    assert client.api_key == "sk-x"
    assert client.model == "grok-4-mini"
    assert client.base_url == "https://api.example/v2"
    assert client.timeout_s == 3.0
    assert client.max_retries == 2
    # Safety ruleset honours disabled list.
    names = {r.name for r in client.safety.rules}
    assert "anti-sycophancy" not in names
    # Tracer wired from config.
    assert isinstance(client.tracer.sink, InMemorySink)


def test_build_client_accepts_explicit_tracer_override():
    from frok.telemetry import Tracer
    explicit = Tracer(sink=InMemorySink())
    cfg = load_config(cli={"client.api_key": "k", "telemetry.sink": "jsonl"})
    client = build_client(cfg, tracer=explicit)
    assert client.tracer is explicit  # config sink ignored


# ---------------------------------------------------------------------------
# memory
# ---------------------------------------------------------------------------
def test_build_memory_store_returns_none_when_disabled():
    cfg = load_config()
    assert build_memory_store(cfg) is None


def test_build_memory_store_enabled(tmp_path):
    cfg = load_config(
        cli={
            "memory.enabled": True,
            "memory.path": str(tmp_path / "m.db"),
            "memory.embedder_dim": 64,
        }
    )
    store = build_memory_store(cfg)
    assert isinstance(store, MemoryStore)
    try:
        assert isinstance(store.embedder, HashEmbedder)
        assert store.embedder.dim == 64
    finally:
        store.close()


def test_build_memory_store_unknown_embedder_raises():
    cfg = load_config(cli={"memory.enabled": True, "memory.embedder": "magic"})
    with pytest.raises(ConfigError, match="unsupported memory.embedder"):
        build_memory_store(cfg)


# ---------------------------------------------------------------------------
# multimodal
# ---------------------------------------------------------------------------
def test_build_multimodal_adapter_wires_config():
    cfg = load_config(
        cli={
            "client.api_key": "k",
            "multimodal.vision_enabled": False,
            "multimodal.voice_enabled": True,
            "multimodal.voice_model": "grok-voice",
            "multimodal.audio_transcribe_path": "/v1/transcribe",
        }
    )
    client = build_client(cfg)
    adapter = build_multimodal_adapter(client, cfg)
    assert isinstance(adapter, MultimodalAdapter)
    assert adapter.client is client
    assert adapter.config.vision_enabled is False
    assert adapter.config.voice_enabled is True
    assert adapter.config.voice_model == "grok-voice"
    assert adapter.config.audio_transcribe_path == "/v1/transcribe"


# ---------------------------------------------------------------------------
# end-to-end wiring from a single config
# ---------------------------------------------------------------------------
def test_end_to_end_single_config_builds_full_stack(tmp_path):
    cfg = load_config(
        cli={
            "client.api_key": "sk-e2e",
            "telemetry.sink": "memory",
            "memory.enabled": True,
            "memory.path": str(tmp_path / "e2e.db"),
        }
    )
    tracer = build_tracer(cfg)
    client = build_client(cfg, tracer=tracer)
    store = build_memory_store(cfg, tracer=tracer)
    adapter = build_multimodal_adapter(client, cfg)
    assert client.tracer is tracer
    assert store is not None
    try:
        assert store.tracer is tracer
        assert adapter.client is client
    finally:
        store.close()
