"""``frok version`` — print frok / Python / platform versions.

Small but essential for bug reports: the first thing any triage asks
is "what version?". Defaults to a single line that's pipe-friendly
and eye-friendly; ``--short`` emits just the frok version (handy in
shell scripts), ``--json`` emits all three fields for tooling.
"""

from __future__ import annotations

import argparse
import json
import platform as _platform
from dataclasses import asdict, dataclass

from .. import __version__


@dataclass(frozen=True)
class VersionInfo:
    frok: str
    python: str
    platform: str


def collect_version_info() -> VersionInfo:
    return VersionInfo(
        frok=__version__,
        python=_platform.python_version(),
        platform=_platform.platform(aliased=True),
    )


async def version_cmd(args: argparse.Namespace) -> int:
    info = collect_version_info()
    if args.short:
        # `--short` wins over `--json` — it's the most specific request.
        print(info.frok)
        return 0
    if args.json:
        print(json.dumps(asdict(info), indent=2))
        return 0
    print(f"frok {info.frok} (Python {info.python}, {info.platform})")
    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    v = sub.add_parser(
        "version",
        help="Print frok, Python, and platform versions.",
        description=(
            "Print the installed frok version, the Python runtime it's "
            "running on, and the platform. Defaults to a one-line "
            "summary; use --short for just the frok version or --json "
            "for all three fields as a JSON object."
        ),
    )
    v.add_argument(
        "--short",
        action="store_true",
        help="print only the frok version (shell-friendly)",
    )
    v.add_argument(
        "--json",
        action="store_true",
        help="emit a JSON object with frok / python / platform fields",
    )
    v.set_defaults(fn=version_cmd)
