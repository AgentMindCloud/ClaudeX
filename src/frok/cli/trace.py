"""``frok trace inspect <jsonl>`` — post-hoc trace triage.

Reads a `JsonlSink` capture, reconstructs the trace tree, and prints a
compact summary (per-span durations, error hot-spots, top tool
invocations). Closes the telemetry <-> eval loop: after a
``frok run --summary-json`` + ``telemetry.sink=jsonl`` capture, the
operator can ``frok trace inspect trace.jsonl`` and see where time and
errors went, without rebuilding the whole agent stack.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..telemetry import (
    build_tree,
    read_jsonl,
    summarize,
    summary_to_json,
    summary_to_markdown,
)
from .common import CliError


async def inspect_cmd(args: argparse.Namespace) -> int:
    path: Path = args.jsonl_path
    if not path.exists():
        raise CliError(f"trace file not found: {path}")
    try:
        events = list(read_jsonl(path))
    except Exception as exc:
        raise CliError(f"cannot read trace file {path}: {exc}") from exc
    if not events:
        raise CliError(f"trace file is empty: {path}")

    summary = summarize(events)

    if args.json:
        out = json.dumps(summary_to_json(summary, top=args.top), indent=2, default=str)
    else:
        roots = build_tree(events) if args.tree else None
        out = summary_to_markdown(
            summary,
            top=args.top,
            include_tree=args.tree,
            roots=roots,
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    trace = sub.add_parser(
        "trace",
        help="Telemetry trace utilities.",
        description="Post-hoc operations on JsonlSink captures.",
    )
    trace_sub = trace.add_subparsers(dest="trace_command", required=True)

    inspect = trace_sub.add_parser(
        "inspect",
        help="Summarize a JsonlSink capture.",
        description=(
            "Load a JsonlSink file, reconstruct the trace tree, and "
            "print a summary of span durations, errors, and top tool "
            "invocations."
        ),
    )
    inspect.add_argument(
        "jsonl_path",
        type=Path,
        help="path to a JsonlSink capture (newline-delimited Event JSON)",
    )
    inspect.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write report to this file instead of stdout",
    )
    inspect.add_argument(
        "--tree",
        action="store_true",
        help="also append the trace tree (one line per span)",
    )
    inspect.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of Markdown",
    )
    inspect.add_argument(
        "--top",
        type=int,
        default=20,
        help="limit tool / error tables to this many rows (default 20)",
    )
    inspect.set_defaults(fn=inspect_cmd)
