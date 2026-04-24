"""Typed config schema.

The whole Frok stack reads exactly one object — `FrokConfig` — assembled
from defaults, a file, environment variables, and explicit CLI overrides
(in that order of precedence). Sub-dataclasses group settings per
component so builders can take one section each without knowing the
whole config.

Keep this module narrow: no logic, no side effects. If a validation
check or default value is non-trivial, push it into the builder that
uses it.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ClientConfig:
    api_key: str | None = None
    model: str = "grok-4"
    base_url: str = "https://api.x.ai/v1"
    timeout_s: float = 60.0
    max_retries: int = 4


@dataclass
class SafetyConfig:
    enabled: bool = True
    # Rule names from `frok.safety.rules.BUILTIN_RULES` to disable.
    disabled_rules: tuple[str, ...] = ()


@dataclass
class TelemetryConfig:
    sink: str = "null"  # "null" | "memory" | "jsonl"
    path: str | None = None  # required when sink == "jsonl"


@dataclass
class MemoryConfig:
    enabled: bool = False  # off by default — callers opt in
    path: str = "./frok-memory.db"
    embedder: str = "hash"  # "hash" is the only built-in today
    embedder_dim: int = 128


@dataclass
class MultimodalConfig:
    vision_enabled: bool = True
    voice_enabled: bool = False
    audio_transcribe_path: str = "/audio/transcriptions"
    voice_model: str | None = None


@dataclass
class FrokConfig:
    profile: str = "dev"
    client: ClientConfig = field(default_factory=ClientConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    multimodal: MultimodalConfig = field(default_factory=MultimodalConfig)


# Ordered map used by the loader for env-var flattening + CLI merging.
SECTIONS: dict[str, type] = {
    "client": ClientConfig,
    "safety": SafetyConfig,
    "telemetry": TelemetryConfig,
    "memory": MemoryConfig,
    "multimodal": MultimodalConfig,
}
