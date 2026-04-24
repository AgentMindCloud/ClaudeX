"""``frok doctor`` — preflight health check.

Loads the resolved `FrokConfig` and runs one check per major Phase-2
subsystem. Each check returns a `Check(name, status, detail)` where
`status` is ``PASS`` / ``FAIL`` / ``SKIP``. Output is a Markdown
report (default) or JSON (``--json``); the exit code reflects
whether any check failed (or was skipped under ``--fail-on-skip``).

Designed for "does my setup actually work?" — safe to run before the
first real eval, cheap when nothing's configured yet (everything skips
gracefully), and honest about what it couldn't verify.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..clients.grok import GrokMessage, Transport
from ..clients.transports import urllib_transport
from ..config import (
    FrokConfig,
    build_client,
    build_memory_store,
    build_safety_ruleset,
    build_telemetry_sink,
    load_default_config,
)
from .common import CliError


# ---------------------------------------------------------------------------
# result shape
# ---------------------------------------------------------------------------
PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str = ""


def _fmt_exc(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# per-subsystem checks
# ---------------------------------------------------------------------------
async def check_config(config: FrokConfig, *, source: str) -> Check:
    return Check("config", PASS, f"profile={config.profile!r} ({source})")


async def check_safety(config: FrokConfig) -> Check:
    try:
        rs = build_safety_ruleset(config)
    except Exception as exc:  # pragma: no cover — logic paths above
        return Check("safety", FAIL, _fmt_exc(exc))
    disabled = list(config.safety.disabled_rules)
    return Check(
        "safety",
        PASS,
        f"{len(rs.rules)} rules enabled (disabled={disabled})",
    )


async def check_telemetry(config: FrokConfig) -> Check:
    try:
        sink = build_telemetry_sink(config)
    except Exception as exc:
        return Check("telemetry", FAIL, _fmt_exc(exc))
    close = getattr(sink, "close", None)
    if callable(close):
        try:
            close()
        except Exception:  # pragma: no cover — sink close is best-effort
            pass
    return Check("telemetry", PASS, f"sink={config.telemetry.sink!r}")


async def check_memory(config: FrokConfig) -> Check:
    if not config.memory.enabled:
        return Check("memory", SKIP, "disabled in config")
    try:
        store = build_memory_store(config)
        if store is None:  # pragma: no cover — defensive
            return Check("memory", SKIP, "builder returned None")
        rec = await store.remember("frok-doctor-ping", kind="doctor")
        hits = await store.recall("frok-doctor-ping", k=1, kind="doctor")
        await store.forget(rec.id)
        store.close()
    except Exception as exc:
        return Check("memory", FAIL, _fmt_exc(exc))
    if not hits:
        return Check("memory", FAIL, "round-trip lost the test memory")
    return Check("memory", PASS, f"round-trip ok (path={config.memory.path!r})")


async def check_multimodal(config: FrokConfig) -> Check:
    mm = config.multimodal
    return Check(
        "multimodal",
        PASS,
        f"vision={'on' if mm.vision_enabled else 'off'}, "
        f"voice={'on' if mm.voice_enabled else 'off'}",
    )


async def check_client_live(
    config: FrokConfig,
    *,
    live: bool = True,
    transport: Transport | None = None,
) -> Check:
    if not live:
        return Check("client-live", SKIP, "--no-live set")
    if not config.client.api_key:
        return Check(
            "client-live",
            SKIP,
            "no client.api_key (set FROK_CLIENT_API_KEY to enable)",
        )
    try:
        client = build_client(config, transport=transport or urllib_transport)
        resp = await client.chat([GrokMessage("user", "ping")])
    except Exception as exc:
        return Check("client-live", FAIL, _fmt_exc(exc))
    return Check(
        "client-live",
        PASS,
        f"{resp.total_tokens} tokens, model={resp.model!r}",
    )


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------
def render_markdown(checks: list[Check]) -> str:
    lines = ["# Frok Doctor", ""]
    for c in checks:
        lines.append(f"- [{c.status}] {c.name} — {c.detail}")
    counts = _counts(checks)
    lines += [
        "",
        f"Total: {len(checks)} checks "
        f"({counts[PASS]} PASS, {counts[FAIL]} FAIL, {counts[SKIP]} SKIP)",
    ]
    return "\n".join(lines) + "\n"


def render_json(checks: list[Check]) -> dict[str, Any]:
    counts = _counts(checks)
    return {
        "checks": [asdict(c) for c in checks],
        "counts": {k: counts[k] for k in (PASS, FAIL, SKIP)},
        "total": len(checks),
    }


def _counts(checks: list[Check]) -> dict[str, int]:
    out = {PASS: 0, FAIL: 0, SKIP: 0}
    for c in checks:
        out[c.status] = out.get(c.status, 0) + 1
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
async def _collect_checks(
    config: FrokConfig,
    *,
    source: str,
    live: bool,
    transport: Transport | None = None,
) -> list[Check]:
    return [
        await check_config(config, source=source),
        await check_safety(config),
        await check_telemetry(config),
        await check_memory(config),
        await check_multimodal(config),
        await check_client_live(config, live=live, transport=transport),
    ]


async def doctor_cmd(args: argparse.Namespace) -> int:
    try:
        config = load_default_config(file=args.config, profile=args.profile)
    except Exception as exc:
        raise CliError(f"config load failed: {exc}") from exc

    source = f"from {args.config}" if args.config else "from env + defaults"
    checks = await _collect_checks(config, source=source, live=args.live)

    if args.json:
        out = json.dumps(render_json(checks), indent=2, default=str)
    else:
        out = render_markdown(checks)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    counts = _counts(checks)
    if counts[FAIL] > 0:
        return 1
    if args.fail_on_skip and counts[SKIP] > 0:
        return 1
    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    doctor = sub.add_parser(
        "doctor",
        help="Preflight health check: config, safety, telemetry, memory, client.",
        description=(
            "Run a preflight check against the resolved FrokConfig and "
            "report PASS / FAIL / SKIP for each major subsystem. A live "
            "`client.chat` ping runs if client.api_key is set; pass "
            "--no-live to skip it."
        ),
    )
    doctor.add_argument("-c", "--config", type=Path, help="explicit config file path")
    doctor.add_argument("-p", "--profile", help="profile name to select")
    doctor.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write the doctor report to this file instead of stdout",
    )
    doctor.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of Markdown",
    )
    doctor.add_argument(
        "--no-live",
        dest="live",
        action="store_false",
        default=True,
        help="skip the live `client.chat` ping even if client.api_key is set",
    )
    doctor.add_argument(
        "--fail-on-skip",
        action="store_true",
        help="treat SKIP as failure for exit-code purposes (strict CI mode)",
    )
    doctor.set_defaults(fn=doctor_cmd)
