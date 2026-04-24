"""``frok config show`` — render the resolved FrokConfig.

Loads config exactly like ``frok run`` does (env + optional file +
profile merging via `load_default_config`), then prints the final
object back out as TOML (default), JSON, or dotenv-style env lines so
operators can sanity-check which settings actually got applied before
running anything.

Sensitive fields (``client.api_key`` today) are masked by default —
last four characters preserved, everything else replaced with ``****``.
Pass ``--reveal`` to print plain.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ..config import load_default_config, to_env, to_json, to_toml
from .common import CliError


_RENDERERS = {
    "toml": to_toml,
    "json": to_json,
    "env": to_env,
}


async def show_cmd(args: argparse.Namespace) -> int:
    try:
        config = load_default_config(file=args.config, profile=args.profile)
    except Exception as exc:
        raise CliError(f"config load failed: {exc}") from exc

    fmt = args.format
    renderer = _RENDERERS.get(fmt)
    if renderer is None:  # argparse choices=... should already guard this
        raise CliError(f"unknown format: {fmt!r}")
    out = renderer(config, reveal=args.reveal)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        # Renderers already terminate with a newline; print() would double it.
        import sys as _sys

        _sys.stdout.write(out)
        if not out.endswith("\n"):
            _sys.stdout.write("\n")

    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    config = sub.add_parser(
        "config",
        help="Config utilities.",
        description="Inspect resolved configuration.",
    )
    config_sub = config.add_subparsers(dest="config_command", required=True)

    show = config_sub.add_parser(
        "show",
        help="Render the resolved FrokConfig as TOML / JSON / env lines.",
        description=(
            "Load config the same way `frok run` does (env + optional "
            "file + profile merging) and print the final object. "
            "Sensitive fields (client.api_key) are masked by default."
        ),
    )
    show.add_argument(
        "--format",
        choices=sorted(_RENDERERS.keys()),
        default="toml",
        help="output format (default: toml)",
    )
    show.add_argument(
        "-c",
        "--config",
        type=Path,
        help="explicit config file path (overrides FROK_CONFIG_FILE)",
    )
    show.add_argument("-p", "--profile", help="profile name to select")
    show.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write rendered config to this file instead of stdout",
    )
    show.add_argument(
        "--reveal",
        action="store_true",
        help="show sensitive values (e.g. api_key) in plain text",
    )
    show.set_defaults(fn=show_cmd)
