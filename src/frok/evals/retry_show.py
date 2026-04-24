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


def _worst_first_key(case: dict[str, Any]) -> tuple[bool, float, int, str]:
    """Sort key putting the most-attention-worthy cases first.

    Order: failing before passing → highest attempts/budget ratio →
    most raw attempts → case name (deterministic tiebreak).
    """
    attempts = len(case.get("attempts") or [])
    budget = max(int(case.get("retry_budget", 1) or 1), 1)
    ratio = attempts / budget
    passed = bool(case.get("passed"))
    return (passed, -ratio, -attempts, case.get("case", ""))


def _last_attempt_error(case: dict[str, Any]) -> str | None:
    attempts = case.get("attempts") or []
    if not attempts:
        return None
    return attempts[-1].get("error")


# Sentinel label for cases whose last attempt had no observation error
# (typically scorer-only failures). Kept explicit rather than `None` in
# the markdown so operators see the bucket at a glance.
_NO_ERROR_LABEL = "(no error — scorer failure or passing retry)"


def format_retry_report(
    payload: dict[str, Any],
    *,
    path: Path | str | None = None,
    compare_to: dict[str, Any] | None = None,
    compare_to_path: Path | str | None = None,
    limit: int | None = None,
    group_by_error: bool = False,
    min_attempts: int | None = None,
    only_errors: bool = False,
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

    # `--only-errors` — drops every passing case (both Clean passes
    # and retried-but-passed) so the detail surface contains only the
    # current run's failures. Applies BEFORE `--min-attempts`,
    # `--group-by-error`, and `--limit` so downstream filters /
    # clustering / truncation see only the failing subset. Same scope
    # rule as `--min-attempts`: "Only in previous" is untouched.
    if only_errors:
        retried_or_failed = [
            c for c in retried_or_failed if not c.get("passed")
        ]
        clean_passes = []
        lines.append("_Showing failing cases only._")
        lines.append("")

    # `--min-attempts N` filter — drops any case whose attempt count is
    # below N from both detail buckets. Applies BEFORE grouping and
    # BEFORE `--limit` so the clustering / truncation logic sees only
    # the still-interesting cases. "Only in previous" is untouched —
    # it's a diff-derived view where the per-case attempt count is
    # from a *different run* and filtering on it would be misleading.
    filter_active = min_attempts is not None and min_attempts > 1
    if filter_active:
        retried_or_failed = [
            c
            for c in retried_or_failed
            if len(c.get("attempts") or []) >= min_attempts
        ]
        clean_passes = [
            c
            for c in clean_passes
            if len(c.get("attempts") or []) >= min_attempts
        ]
        lines.append(
            f"_Filtered to cases with >= {min_attempts} attempts._"
        )
        lines.append("")

    # `--limit N` meaning depends on --group-by-error:
    #   * plain mode: truncate to the N most-attention-worthy cases
    #     (failing first → highest attempts/budget ratio → most raw
    #     attempts → name).
    #   * grouped mode: truncate to the N biggest error clusters
    #     (most cases in the group). Cases within a group stay whole.
    # Clean passes and "Only in previous" are NOT truncated in either
    # mode — both terse; operators may want the full picture there.
    if group_by_error:
        # Group by last-attempt error string; None → _NO_ERROR_LABEL.
        by_error: dict[str, list[dict[str, Any]]] = {}
        for c in retried_or_failed:
            err = _last_attempt_error(c)
            label = err if err else _NO_ERROR_LABEL
            by_error.setdefault(label, []).append(c)
        # Order groups by size desc, then label alpha for determinism.
        ordered_groups = sorted(
            by_error.items(),
            key=lambda kv: (-len(kv[1]), kv[0]),
        )
        total_groups = len(ordered_groups)
        truncated_groups = False
        if limit is not None and limit < total_groups:
            ordered_groups = ordered_groups[: max(limit, 0)]
            truncated_groups = True
        if truncated_groups:
            lines.append(
                f"_Showing {len(ordered_groups)} of {total_groups} "
                f"error groups (largest-first)._"
            )
            lines.append("")
        for err_label, group_cases in ordered_groups:
            sorted_cases = sorted(group_cases, key=_worst_first_key)
            lines.append(
                f"## Error: `{err_label}` — {len(group_cases)} case(s)"
            )
            lines.append("")
            lines.append(
                "| Case | Repeat | Attempts/Budget | Verdict |"
            )
            lines.append(
                "|------|-------:|-----------------|---------|"
            )
            for c in sorted_cases:
                name = c.get("case", "?")
                repeat = c.get("repeat", 0)
                attempts_n = len(c.get("attempts") or [])
                budget = int(c.get("retry_budget", 1) or 1)
                verdict = "PASS" if c.get("passed") else "FAIL"
                lines.append(
                    f"| {name} | {repeat} | {attempts_n}/{budget} | "
                    f"{verdict} |"
                )
            lines.append("")
    else:
        total_detailed = len(retried_or_failed)
        truncated = False
        if limit is not None and limit < total_detailed:
            retried_or_failed = sorted(retried_or_failed, key=_worst_first_key)[
                : max(limit, 0)
            ]
            truncated = True

        if truncated:
            lines.append(
                f"_Showing {len(retried_or_failed)} of {total_detailed} "
                f"retried/failing cases (worst-first)._"
            )
            lines.append("")

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
