"""Single retry-report triage renderer.

Complements the ``frok retry`` toolkit:

* §22 ``frok run --retry-report PATH`` — *produces* the JSON.
* §23 ``frok retry diff A B`` — *compares* two reports.
* §24 ``frok retry summarize DIR`` — series trend across many.
* §25 ``frok retry show PATH`` — *this* — single-report triage.

Pretty-prints a report as markdown: a summary bloc (cases, pass/fail,
total attempts / budget, retried count), detailed attempt tables for
every retried or failing case, and a "clean passes" bulleted list for
cases that passed on the first try (keeps the output scannable when
most of the suite is passing).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def format_retry_report(
    payload: dict[str, Any], *, path: Path | str | None = None
) -> str:
    cases = payload.get("cases", [])
    total_attempts = sum(len(c.get("attempts") or []) for c in cases)
    total_budget = sum(int(c.get("retry_budget", 1) or 1) for c in cases)
    passed = sum(1 for c in cases if c.get("passed"))
    failed = len(cases) - passed
    retried = sum(1 for c in cases if len(c.get("attempts") or []) > 1)

    lines: list[str] = ["# Frok Retry Report", ""]
    if path is not None:
        lines.append(f"- Source: `{path}`")
    lines.extend(
        [
            f"- Cases: {len(cases)}",
            f"- Passed: {passed}",
            f"- Failed: {failed}",
            f"- Retried cases: {retried}",
            f"- Attempts / Budget: {total_attempts} / {total_budget}",
            "",
        ]
    )

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
        lines.append(
            f"## {verdict}: {name} (repeat {repeat}) — "
            f"{len(attempts)}/{budget} attempts"
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

    return "\n".join(lines)
