"""Retry-report CLI — ``frok retry diff A B``.

Loads two retry-report JSONs produced by ``frok run --retry-report
PATH`` and surfaces attempts drift, error-shape changes, and
newly-failing / newly-passing cases. Pairs with the summary JSON's
coarse "attempts / budget" rollup: the diff catches creeping flake
patterns the budget-relative view would miss.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..evals import (
    diff_retry_reports,
    format_retry_report,
    retry_diff_to_markdown,
    retry_summary_to_markdown,
    summarize_retry_reports,
)
from .common import CliError


def _load_report(path: Path) -> dict:
    if not path.exists():
        raise CliError(f"retry report not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"retry report is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict) or "cases" not in payload:
        raise CliError(
            f"retry report is missing 'cases' list: {path}"
        )
    return payload


async def diff_cmd(args: argparse.Namespace) -> int:
    a_payload = _load_report(args.a)
    b_payload = _load_report(args.b)

    diff = diff_retry_reports(a_payload, b_payload)

    if args.json:
        out = json.dumps(
            {
                "a_path": str(args.a),
                "b_path": str(args.b),
                **diff,
            },
            indent=2,
            default=str,
        )
    else:
        out = retry_diff_to_markdown(
            diff,
            a_label=args.a_label or "a",
            b_label=args.b_label or "b",
            a_path=args.a,
            b_path=args.b,
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    if args.fail_on_regression and diff["regressed"]:
        return 1
    return 0


async def show_cmd(args: argparse.Namespace) -> int:
    payload = _load_report(args.path)

    compare_payload = None
    if args.compare_to is not None:
        compare_payload = _load_report(args.compare_to)

    if args.json:
        # Passthrough of the primary payload. --compare-to is a
        # markdown-only enrichment; operators wanting structured pair
        # diff should use `frok retry diff` instead.
        out = json.dumps(payload, indent=2, default=str)
    else:
        out = format_retry_report(
            payload,
            path=args.path,
            compare_to=compare_payload,
            compare_to_path=args.compare_to,
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    cases = payload.get("cases", [])
    failed = sum(1 for c in cases if not c.get("passed"))
    if args.fail_on_failure and failed > 0:
        return 1
    return 0


async def summarize_cmd(args: argparse.Namespace) -> int:
    try:
        summary = summarize_retry_reports(args.directory)
    except FileNotFoundError as exc:
        raise CliError(str(exc)) from exc
    except ValueError as exc:
        raise CliError(str(exc)) from exc

    if args.json:
        out = json.dumps(summary, indent=2, default=str)
    else:
        out = retry_summary_to_markdown(summary)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)

    if args.fail_on_growing and summary["trend_counts"]["growing"] > 0:
        return 1
    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    retry = sub.add_parser(
        "retry",
        help="Retry-report utilities.",
        description="Operations over --retry-report JSON dumps.",
    )
    retry_sub = retry.add_subparsers(dest="retry_command", required=True)

    diff = retry_sub.add_parser(
        "diff",
        help="Diff two retry-report JSON files (A vs B).",
        description=(
            "Compare two retry-report JSON dumps from "
            "`frok run --retry-report PATH`. Surfaces attempts drift, "
            "error-shape changes, newly-failing / newly-passing cases, "
            "and slugs only in one side. Catches creeping flake that "
            "the budget-relative summary would miss."
        ),
    )
    diff.add_argument(
        "a", type=Path, help="reference retry report (before / baseline)"
    )
    diff.add_argument(
        "b", type=Path, help="candidate retry report (after / today)"
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
        "--a-label",
        default=None,
        metavar="LABEL",
        help="label for side A in the markdown (default 'a')",
    )
    diff.add_argument(
        "--b-label",
        default=None,
        metavar="LABEL",
        help="label for side B in the markdown (default 'b')",
    )
    diff.add_argument(
        "--fail-on-regression",
        action="store_true",
        help=(
            "exit non-zero when attempts grew, a case newly failed, the "
            "last-attempt error shape drifted between two non-null "
            "strings, or a new failing case appeared in B"
        ),
    )
    diff.set_defaults(fn=diff_cmd)

    summ = retry_sub.add_parser(
        "summarize",
        help="Walk a directory of retry-report JSONs and print a trend view.",
        description=(
            "Walk DIR/*.json (retry-reports; one per run, typically "
            "YYYY-MM-DD.json), match (case, repeat) entries across "
            "every report, and classify each case's attempt trend as "
            "flat / growing / shrinking / mixed. Catches slow creeping "
            "flake that pairwise diffs would miss — attempts going 1 "
            "→ 1 → 2 → 3 → 4 over two weeks is only visible in the "
            "full series."
        ),
    )
    summ.add_argument(
        "directory",
        type=Path,
        help=(
            "directory of retry-report JSONs (lexicographic filename "
            "ordering)"
        ),
    )
    summ.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write summary to this file instead of stdout",
    )
    summ.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of Markdown",
    )
    summ.add_argument(
        "--fail-on-growing",
        action="store_true",
        help=(
            "exit non-zero when any case's attempt trend is 'growing' "
            "across the series (monotonic non-decreasing with at least "
            "one increase). Ignores 'mixed' — those are flake, which "
            "the pairwise `retry diff` already flags as regressions."
        ),
    )
    summ.set_defaults(fn=summarize_cmd)

    show = retry_sub.add_parser(
        "show",
        help="Pretty-print a single retry-report JSON as markdown.",
        description=(
            "Render one retry-report JSON (from `frok run "
            "--retry-report PATH`) as markdown: a summary bloc plus "
            "per-case attempt tables for retried or failing cases. "
            "Single-attempt passes collapse to a bulleted list so the "
            "output stays scannable. Complements `retry diff` (two "
            "reports) and `retry summarize` (series) with the single-"
            "report triage view."
        ),
    )
    show.add_argument(
        "path",
        type=Path,
        help="retry-report JSON file",
    )
    show.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write rendered view to this file instead of stdout",
    )
    show.add_argument(
        "--json",
        action="store_true",
        help=(
            "pass through the raw JSON payload (re-serialised "
            "indented) instead of rendering markdown"
        ),
    )
    show.add_argument(
        "--fail-on-failure",
        action="store_true",
        help=(
            "exit non-zero when any case's terminal verdict is failed. "
            "Useful when the retry-report is the only CI artifact "
            "and the producer didn't pass --fail-on-regression."
        ),
    )
    show.add_argument(
        "--compare-to",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "path to a second retry-report JSON (typically the "
            "previous run's report). When set, per-case headers gain "
            "a '(was N/M, PASS/FAIL)' suffix, the summary grows "
            "pairwise diff counters, and a 'Only in previous' "
            "section lists cases that vanished. Markdown-only — "
            "`--json` still passes through the primary payload "
            "verbatim; use `frok retry diff` for structured diff data."
        ),
    )
    show.set_defaults(fn=show_cmd)
