"""Single retry-report triage renderer.

Complements the ``frok retry`` toolkit:

* §22 ``frok run --retry-report PATH`` — *produces* the JSON.
* §23 ``frok retry diff A B`` — *compares* two reports.
* §24 ``frok retry summarize DIR`` — series trend across many.
* §25 ``frok retry show PATH`` — *this* — single-report triage.
* §26 ``frok retry show --compare-to PATH2`` — show + inline pair diff.

Pretty-prints a report as markdown: a summary bloc (cases, pass/fail,
total attempts / budget, retried count), detailed attempt tables for
every retried or failing case, and a "clean passes" bulleted list for
cases that passed on the first try (keeps the output scannable when
most of the suite is passing).

When ``compare_to`` is provided, per-case headers gain a "(was N/M,
PASS/FAIL)" suffix, the summary bloc grows pairwise diff counts, and
a "## Only in <previous>" section lists cases that vanished.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .retry_diff import diff_retry_reports


def _key_lookup(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (c["case"], int(c.get("repeat", 0))): c
        for c in payload.get("cases", [])
    }


def format_retry_report(
    payload: dict[str, Any],
    *,
    path: Path | str | None = None,
    compare_to: dict[str, Any] | None = None,
    compare_to_path: Path | str | None = None,
) -> str:
    cases = payload.get("cases", [])
    total_attempts = sum(len(c.get("attempts") or []) for c in cases)
    total_budget = sum(int(c.get("retry_budget", 1) or 1) for c in cases)
    passed = sum(1 for c in cases if c.get("passed"))
    failed = len(cases) - passed
    retried = sum(1 for c in cases if len(c.get("attempts") or []) > 1)

    # Compute the diff once; downstream uses are read-only.
    diff: dict[str, Any] | None = None
    prev_lookup: dict[tuple[str, int], dict[str, Any]] = {}
    if compare_to is not None:
        diff = diff_retry_reports(compare_to, payload)
        prev_lookup = _key_lookup(compare_to)

    lines: list[str] = ["# Frok Retry Report", ""]
    if path is not None:
        lines.append(f"- Source: `{path}`")
    if compare_to is not None and compare_to_path is not None:
        lines.append(f"- Compared to: `{compare_to_path}`")
    lines.extend(
        [
            f"- Cases: {len(cases)}",
            f"- Passed: {passed}",
            f"- Failed: {failed}",
            f"- Retried cases: {retried}",
            f"- Attempts / Budget: {total_attempts} / {total_budget}",
        ]
    )
    if diff is not None:
        lines.extend(
            [
                "",
                "## Comparison",
                "",
                f"- Attempts grew on: {len(diff['attempts_grew'])} case(s)",
                f"- Attempts shrank on: {len(diff['attempts_shrank'])} case(s)",
                f"- Newly failing: {len(diff['newly_failing'])}",
                f"- Newly passing: {len(diff['newly_passing'])}",
                f"- Error changed: {len(diff['error_changed'])}",
                f"- Only in previous: {len(diff['only_in_a'])}",
                f"- Only in current: {len(diff['only_in_b'])}",
                f"- Regressed: {'yes' if diff['regressed'] else 'no'}",
            ]
        )
    lines.append("")

    # Per-case detail: only for retried OR failing cases.
    # Single-attempt passes go into a terse bulleted list below so the
    # markdown stays scannable when most of the suite is green.
    retried_or_failed = [
        c
        for c in cases
        if len(c.get("attempts") or []) > 1 or not c.get("passed")
    ]
    clean_passes = [
        c
        for c in cases
        if len(c.get("attempts") or []) == 1 and c.get("passed")
    ]

    for c in retried_or_failed:
        verdict = "PASS" if c.get("passed") else "FAIL"
        name = c.get("case", "?")
        repeat = c.get("repeat", 0)
        attempts = c.get("attempts") or []
        budget = int(c.get("retry_budget", 1) or 1)
        suffix = ""
        if compare_to is not None:
            prev = prev_lookup.get((name, int(repeat)))
            if prev is not None:
                prev_attempts = len(prev.get("attempts") or [])
                prev_budget = int(prev.get("retry_budget", 1) or 1)
                prev_verdict = "PASS" if prev.get("passed") else "FAIL"
                suffix = (
                    f" (was {prev_attempts}/{prev_budget}, {prev_verdict})"
                )
            else:
                suffix = " (NEW — not in previous)"
        lines.append(
            f"## {verdict}: {name} (repeat {repeat}) — "
            f"{len(attempts)}/{budget} attempts{suffix}"
        )
        lines.append("")
        lines.append(
            "| Attempt | Passed | Error | Sleep before (ms) |"
        )
        lines.append(
            "|--------:|--------|-------|------------------:|"
        )
        for a in attempts:
            err = a.get("error")
            err_cell = f"`{err}`" if err else "-"
            sleep = a.get("sleep_before_ms")
            sleep_cell = (
                f"{float(sleep):.1f}" if sleep is not None else "-"
            )
            passed_cell = "yes" if a.get("passed") else "no"
            lines.append(
                f"| {a.get('attempt', '?')} | {passed_cell} | "
                f"{err_cell} | {sleep_cell} |"
            )
        lines.append("")

    if clean_passes:
        lines.append("## Clean passes")
        lines.append("")
        for c in clean_passes:
            lines.append(
                f"- {c.get('case', '?')} (repeat {c.get('repeat', 0)})"
            )
        lines.append("")

    if diff is not None and diff["only_in_a"]:
        lines.append("## Only in previous")
        lines.append("")
        for entry in diff["only_in_a"]:
            verdict = "PASS" if entry.get("passed") else "FAIL"
            attempts_n = len(entry.get("attempts") or [])
            budget = int(entry.get("retry_budget", 1) or 1)
            lines.append(
                f"- {entry.get('case', '?')} (repeat "
                f"{entry.get('repeat', 0)}): {verdict}, "
                f"{attempts_n}/{budget} attempts"
            )
        lines.append("")

    return "\n".join(lines)
