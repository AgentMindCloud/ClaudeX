"""``frok eval diff <a.jsonl> <b.jsonl>`` — A/B two JsonlSink captures.

Complements:
  * ``frok trace inspect`` (summarise ONE capture)
  * ``frok run --use-baseline`` (per-case diff against a recorded
    baseline, one case at a time)
with a symmetric two-file comparison that the operator can run
outside of a live eval — e.g. to A/B a prompt change, a model
version bump, or a config tweak against captures collected from
earlier ``frok run --capture-baseline`` invocations.

The ``a`` side is treated as the reference ("before"); ``b`` is the
candidate ("after"). A diff carrying ``regressed=True`` — tool
order diverged or a new error appeared — turns the exit code red
under ``--fail-on-regression``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..evals import diff_event_streams, diff_to_markdown
from ..telemetry import read_jsonl
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
