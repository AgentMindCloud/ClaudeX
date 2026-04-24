"""Render a resolved `FrokConfig` back out as TOML / JSON / env lines.

Used by ``frok config show`` so operators can sanity-check which values
actually got applied after file + env + CLI + profile merging. All three
formats serialise the same dict; only the surface syntax differs.

Sensitive fields (currently just ``client.api_key``) are masked by
default — the last four characters survive, everything else is replaced
with ``****``. Pass ``reveal=True`` to print plain.
"""

from __future__ import annotations

import dataclasses
import json
from typing import Any

from .schema import SECTIONS, FrokConfig

# Fields that should be masked unless reveal=True. Keep narrow and explicit.
SENSITIVE_FIELDS: set[tuple[str, str]] = {("client", "api_key")}


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "****"
    return "****" + value[-4:]


def _as_plain_dict(config: FrokConfig, *, reveal: bool = False) -> dict[str, Any]:
    out: dict[str, Any] = {"profile": config.profile}
    for name, section_cls in SECTIONS.items():
        section = getattr(config, name)
        fields = {}
        for field in dataclasses.fields(section_cls):
            value = getattr(section, field.name)
            if (
                (name, field.name) in SENSITIVE_FIELDS
                and isinstance(value, str)
                and not reveal
            ):
                value = _mask(value)
            fields[field.name] = value
        out[name] = fields
    return out


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------
def to_json(config: FrokConfig, *, reveal: bool = False) -> str:
    return json.dumps(
        _as_plain_dict(config, reveal=reveal),
        indent=2,
        default=str,
        sort_keys=False,
    )


# ---------------------------------------------------------------------------
# TOML (minimal emitter — we only ever write our own shape)
# ---------------------------------------------------------------------------
def _toml_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_toml_literal(x) for x in value) + "]"
    return f'"{str(value)}"'


def to_toml(config: FrokConfig, *, reveal: bool = False) -> str:
    d = _as_plain_dict(config, reveal=reveal)
    lines: list[str] = [f"profile = {_toml_literal(d['profile'])}", ""]
    for name, section_cls in SECTIONS.items():
        lines.append(f"[{name}]")
        for field in dataclasses.fields(section_cls):
            value = d[name][field.name]
            if value is None:
                # TOML has no null; mark the key as unset so reader sees the shape.
                lines.append(f"# {field.name}  (unset)")
            else:
                lines.append(f"{field.name} = {_toml_literal(value)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# env (dotenv-ish lines matching the loader's FROK_<SECTION>_<FIELD> shape)
# ---------------------------------------------------------------------------
def _env_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ",".join(str(x) for x in value)
    return str(value)


def to_env(config: FrokConfig, *, reveal: bool = False) -> str:
    d = _as_plain_dict(config, reveal=reveal)
    lines: list[str] = [f"FROK_PROFILE={d['profile']}"]
    for name, section_cls in SECTIONS.items():
        for field in dataclasses.fields(section_cls):
            value = d[name][field.name]
            key = f"FROK_{name.upper()}_{field.name.upper()}"
            if value is None:
                lines.append(f"# {key}=")
            else:
                lines.append(f"{key}={_env_literal(value)}")
    return "\n".join(lines) + "\n"
