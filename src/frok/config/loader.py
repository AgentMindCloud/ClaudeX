"""Layered config loader: defaults -> file -> env -> CLI overrides.

Precedence (earlier = lower, later wins):

  1. Dataclass defaults in `schema.py`
  2. File (``file=...``) — JSON or TOML, detected by extension.
     If the file declares top-level ``profile`` or nested
     ``[profiles.NAME]`` blocks, the selected profile's section is
     merged on top of the file's own base section.
  3. Environment variables (``env=os.environ``). Keys follow
     ``FROK_<SECTION>_<FIELD>`` (case-insensitive). ``FROK_PROFILE``
     picks the profile.
  4. CLI overrides (``cli=...``), either a nested dict or a flat
     dict keyed by ``"section.field"``.

The loader is deliberately deterministic and hermetic — it reads no
file and no env var unless the caller passes one. For the "just do the
right thing" path, see :func:`load_default_config`.
"""

from __future__ import annotations

import dataclasses
import json
import os
import sys
import types
import typing
from pathlib import Path
from typing import Any, Mapping, Union

from .schema import SECTIONS, FrokConfig


class ConfigError(RuntimeError):
    """Raised on malformed input: unknown sections, bad types, etc."""


# ---------------------------------------------------------------------------
# public entry points
# ---------------------------------------------------------------------------
def load_config(
    *,
    file: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    cli: Mapping[str, Any] | None = None,
    profile: str | None = None,
) -> FrokConfig:
    layers: list[dict[str, Any]] = []

    file_data: dict[str, Any] = {}
    if file is not None:
        file_data = _from_file(file)
        layers.append(_without_profiles(file_data))

    if env is not None:
        layers.append(_from_env(env))

    if cli:
        layers.append(_normalise_cli(cli))

    merged: dict[str, Any] = {}
    for layer in layers:
        _deep_update(merged, layer)

    # Pick the profile (arg > cli > env > merged > file > schema default).
    chosen = (
        profile
        or merged.get("profile")
        or (env.get("FROK_PROFILE") if env else None)
        or file_data.get("profile")
    )
    if chosen and file_data.get("profiles", {}).get(chosen):
        # Apply the profile section on top of everything else.
        _deep_update(merged, file_data["profiles"][chosen])
    if chosen:
        merged["profile"] = chosen

    _assert_known_sections(merged)
    return _from_dict(merged)


def load_default_config(**overrides: Any) -> FrokConfig:
    """Convenience: source env + optional ``FROK_CONFIG_FILE`` + explicit overrides."""
    file = overrides.pop("file", None) or os.environ.get("FROK_CONFIG_FILE")
    return load_config(file=file, env=os.environ, **overrides)


# ---------------------------------------------------------------------------
# file -> dict
# ---------------------------------------------------------------------------
def _from_file(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config file not found: {p}")
    suffix = p.suffix.lower()
    raw = p.read_text(encoding="utf-8")
    if suffix == ".json":
        return json.loads(raw) or {}
    if suffix in (".toml", ".tml"):
        if sys.version_info < (3, 11):  # pragma: no cover
            raise ConfigError("TOML config requires Python 3.11+ (tomllib)")
        import tomllib

        return tomllib.loads(raw) or {}
    raise ConfigError(f"unsupported config file extension: {p.suffix!r}")


def _without_profiles(data: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if k != "profiles"}


# ---------------------------------------------------------------------------
# env -> dict
# ---------------------------------------------------------------------------
def _from_env(env: Mapping[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "FROK_PROFILE" in env:
        out["profile"] = env["FROK_PROFILE"]
    for section_name, section_cls in SECTIONS.items():
        section_hints = typing.get_type_hints(section_cls)
        section_out: dict[str, Any] = {}
        for field in dataclasses.fields(section_cls):
            key = f"FROK_{section_name.upper()}_{field.name.upper()}"
            if key in env:
                section_out[field.name] = _coerce(
                    env[key], section_hints[field.name]
                )
        if section_out:
            out[section_name] = section_out
    return out


def _coerce(raw: str, type_hint: Any) -> Any:
    origin = typing.get_origin(type_hint)
    args = typing.get_args(type_hint)

    # Optional[T] / T | None
    if origin is Union or origin is types.UnionType:
        inner = [a for a in args if a is not type(None)]
        if not inner:
            return None
        if raw == "" and type(None) in args:
            return None
        return _coerce(raw, inner[0])

    # tuple[str, ...]
    if origin is tuple:
        if args and args[0] is str:
            return tuple(s.strip() for s in raw.split(",") if s.strip())

    if type_hint is bool:
        return raw.strip().lower() in ("1", "true", "yes", "on")
    if type_hint is int:
        return int(raw)
    if type_hint is float:
        return float(raw)
    if type_hint is str:
        return raw
    return raw


# ---------------------------------------------------------------------------
# CLI -> dict
# ---------------------------------------------------------------------------
def _normalise_cli(cli: Mapping[str, Any]) -> dict[str, Any]:
    """Accept either a nested dict or a flat one keyed by ``section.field``."""
    out: dict[str, Any] = {}
    for k, v in cli.items():
        if v is None:
            continue
        if isinstance(k, str) and "." in k:
            parts = k.split(".")
            cursor = out
            for p in parts[:-1]:
                cursor = cursor.setdefault(p, {})
            cursor[parts[-1]] = v
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# dict -> typed
# ---------------------------------------------------------------------------
def _assert_known_sections(merged: Mapping[str, Any]) -> None:
    known = set(SECTIONS) | {"profile"}
    extra = set(merged) - known
    if extra:
        raise ConfigError(f"unknown config section(s): {sorted(extra)}")


def _from_dict(merged: Mapping[str, Any]) -> FrokConfig:
    kwargs: dict[str, Any] = {}
    if "profile" in merged:
        kwargs["profile"] = merged["profile"]
    for section_name, section_cls in SECTIONS.items():
        section_data = merged.get(section_name)
        if not section_data:
            continue
        if not isinstance(section_data, Mapping):
            raise ConfigError(
                f"{section_name!r} must be a table, got {type(section_data).__name__}"
            )
        section_hints = typing.get_type_hints(section_cls)
        valid = {f.name for f in dataclasses.fields(section_cls)}
        unknown = set(section_data) - valid
        if unknown:
            raise ConfigError(
                f"unknown {section_name!r} field(s): {sorted(unknown)}"
            )
        coerced: dict[str, Any] = {}
        for k, v in section_data.items():
            # Env + CLI may have already coerced; be forgiving.
            if isinstance(v, str):
                coerced[k] = _coerce(v, section_hints[k])
            else:
                coerced[k] = v
        kwargs[section_name] = section_cls(**coerced)
    return FrokConfig(**kwargs)


# ---------------------------------------------------------------------------
# dict merge
# ---------------------------------------------------------------------------
def _deep_update(dst: dict[str, Any], src: Mapping[str, Any]) -> None:
    for k, v in src.items():
        if (
            k in dst
            and isinstance(dst[k], dict)
            and isinstance(v, Mapping)
        ):
            _deep_update(dst[k], v)
        else:
            dst[k] = v
