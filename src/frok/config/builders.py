"""Factories turning a `FrokConfig` into live component instances.

These are the one place where configuration values are validated and
mapped onto concrete defaults. Everything downstream keeps taking the
narrow component types (``GrokClient``, ``Tracer``, …) — nothing else
needs to know about ``FrokConfig``.
"""

from __future__ import annotations

from ..clients.grok import DEFAULT_BASE_URL, GrokClient, StreamingTransport, Transport
from ..memory.embedder import HashEmbedder
from ..memory.store import MemoryStore
from ..multimodal.adapter import AdapterConfig, MultimodalAdapter
from ..safety.rules import BUILTIN_RULES, SafetyRule, SafetyRuleSet
from ..telemetry import (
    InMemorySink,
    JsonlSink,
    NullSink,
    TelemetrySink,
    Tracer,
)
from .loader import ConfigError
from .schema import FrokConfig


def build_safety_ruleset(config: FrokConfig) -> SafetyRuleSet:
    if not config.safety.enabled:
        return SafetyRuleSet(rules=())
    disabled = set(config.safety.disabled_rules)
    active: tuple[SafetyRule, ...] = tuple(
        r for r in BUILTIN_RULES if r.name not in disabled
    )
    unknown = disabled - {r.name for r in BUILTIN_RULES}
    if unknown:
        raise ConfigError(f"unknown safety rule(s) disabled: {sorted(unknown)}")
    return SafetyRuleSet(rules=active)


def build_telemetry_sink(config: FrokConfig) -> TelemetrySink:
    kind = config.telemetry.sink
    if kind == "null":
        return NullSink()
    if kind == "memory":
        return InMemorySink()
    if kind == "jsonl":
        if not config.telemetry.path:
            raise ConfigError("telemetry.path is required when sink='jsonl'")
        return JsonlSink(config.telemetry.path)
    raise ConfigError(f"unknown telemetry.sink: {kind!r}")


def build_tracer(config: FrokConfig) -> Tracer:
    return Tracer(sink=build_telemetry_sink(config))


def build_client(
    config: FrokConfig,
    *,
    transport: Transport | None = None,
    streaming_transport: StreamingTransport | None = None,
    tracer: Tracer | None = None,
) -> GrokClient:
    c = config.client
    if not c.api_key:
        raise ConfigError(
            "client.api_key is not configured (set FROK_CLIENT_API_KEY or pass via file/cli)"
        )
    return GrokClient(
        api_key=c.api_key,
        model=c.model,
        base_url=c.base_url or DEFAULT_BASE_URL,
        timeout_s=c.timeout_s,
        max_retries=c.max_retries,
        transport=transport,
        streaming_transport=streaming_transport,
        tool_choice=c.tool_choice,
        safety=build_safety_ruleset(config),
        tracer=tracer or build_tracer(config),
    )


def build_memory_store(
    config: FrokConfig,
    *,
    tracer: Tracer | None = None,
) -> MemoryStore | None:
    if not config.memory.enabled:
        return None
    if config.memory.embedder == "hash":
        embedder = HashEmbedder(dim=config.memory.embedder_dim)
    else:
        raise ConfigError(
            f"unsupported memory.embedder: {config.memory.embedder!r} "
            f"(only 'hash' is wired today)"
        )
    return MemoryStore(config.memory.path, embedder, tracer=tracer)


def build_multimodal_adapter(
    client: GrokClient, config: FrokConfig
) -> MultimodalAdapter:
    mm = config.multimodal
    return MultimodalAdapter(
        client=client,
        config=AdapterConfig(
            vision_enabled=mm.vision_enabled,
            voice_enabled=mm.voice_enabled,
            audio_transcribe_path=mm.audio_transcribe_path,
            voice_model=mm.voice_model,
        ),
    )
