"""Evaluation CLI — ``frok eval diff`` and ``frok eval summarize``.

Three complementary operations over `JsonlSink` captures:

* ``frok trace inspect <file>`` — summarise ONE capture.
* ``frok eval diff <a> <b>`` — symmetric A/B of two captures.
* ``frok eval summarize <dir>`` — aggregate rollup + cross-case
  leaders across every ``<slug>.jsonl`` in a baseline directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..evals import diff_event_streams, diff_to_markdown
from ..telemetry import (
    dir_summary_to_json,
    dir_summary_to_markdown,
    read_jsonl,
    summarize_directory,
)
from .common import CliError


def _read_capture(path: Path) -> list:
    if not path.exists():
        raise CliError(f"capture file not found: {path}")
    try:
        events = list(read_jsonl(path))
    except Exception as exc:
        raise CliError(f"cannot read capture {path}: {exc}") from exc
    if not events:
        raise CliError(f"capture file is empty: {path}")
    return events


async def diff_cmd(args: argparse.Namespace) -> int:
    a_events = _read_capture(args.a)
    b_events = _read_capture(args.b)

    diff = diff_event_streams(a_events, b_events, a_label="a", b_label="b")

    if args.json:
        # Surface paths alongside the diff for downstream tooling.
        payload = dict(diff)
        payload["a_path"] = str(args.a)
        payload["b_path"] = str(args.b)
        out = json.dumps(payload, indent=2, default=str)
    else:
        out = diff_to_markdown(
            diff, a_label="a", b_label="b", a_path=args.a, b_path=args.b
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    if args.fail_on_regression and diff["regressed"]:
        return 1
    return 0


async def summarize_cmd(args: argparse.Namespace) -> int:
    directory: Path = args.directory
    if not directory.exists():
        raise CliError(f"directory not found: {directory}")
    if not directory.is_dir():
        raise CliError(f"not a directory: {directory}")

    try:
        summary = summarize_directory(directory)
    except Exception as exc:
        raise CliError(f"cannot summarize {directory}: {exc}") from exc

    if not summary.cases:
        raise CliError(f"no .jsonl captures found in {directory}")

    if args.json:
        out = json.dumps(
            dir_summary_to_json(summary, top=args.top), indent=2, default=str
        )
    else:
        out = dir_summary_to_markdown(summary, top=args.top)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    if args.fail_on_errors and summary.total_errors > 0:
        return 1
    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    eval_ = sub.add_parser(
        "eval",
        help="Evaluation utilities.",
        description="Post-hoc operations across eval captures.",
    )
    eval_sub = eval_.add_subparsers(dest="eval_command", required=True)

    diff = eval_sub.add_parser(
        "diff",
        help="Diff two JsonlSink captures (A vs B).",
        description=(
            "Compare two capture files and print a compact diff of tool "
            "ordering, token totals, error counts, and span counts. Use "
            "for A/B testing prompt / model / config changes."
        ),
    )
    diff.add_argument(
        "a", type=Path, help="reference capture (treated as the 'before' side)"
    )
    diff.add_argument(
        "b", type=Path, help="candidate capture (treated as the 'after' side)"
    )
    diff.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write diff to this file instead of stdout",
    )
    diff.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of Markdown",
    )
    diff.add_argument(
        "--fail-on-regression",
        action="store_true",
        help=(
            "exit non-zero when the diff is regressed (tool-order "
            "divergence or new errors in b)"
        ),
    )
    diff.set_defaults(fn=diff_cmd)

    summ = eval_sub.add_parser(
        "summarize",
        help="Aggregate stats + leaders across a directory of captures.",
        description=(
            "Walk <DIR>/*.jsonl, summarize each capture, and print a "
            "per-case rollup plus cross-case leaders (slowest, heaviest "
            "tokens, most errors, errored tools, top tools)."
        ),
    )
    summ.add_argument(
        "directory",
        type=Path,
        help="directory of JsonlSink captures (e.g. from --capture-baseline)",
    )
    summ.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write report to this file instead of stdout",
    )
    summ.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of Markdown",
    )
    summ.add_argument(
        "--top",
        type=int,
        default=5,
        help="limit leader tables to this many rows (default 5)",
    )
    summ.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="exit non-zero when any capture contains an errored span",
    )
    summ.set_defaults(fn=summarize_cmd)
