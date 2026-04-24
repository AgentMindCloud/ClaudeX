"""Longitudinal trend across a directory of ``--retry-report`` JSONs.

§23's ``frok retry diff A B`` is a point-in-time pair diff. This module
complements it with the series view: walk a directory of reports (one
per run, typically named ``YYYY-MM-DD.json``), match `(case, repeat)`
entries across every report, and classify each case's attempt trend:

* ``flat`` — every report has the same attempt count
* ``growing`` — monotonic non-decreasing with at least one increase
* ``shrinking`` — monotonic non-increasing with at least one decrease
* ``mixed`` — some ups, some downs (real flake signal)

Reports are ordered by filename (lexicographic), so operators using
``YYYY-MM-DD.json`` names get chronological order automatically.
Missing entries (case didn't exist in an earlier report) are recorded
as ``None``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_report(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"retry report is not valid JSON: {path}: {exc}"
        ) from exc
    if not isinstance(payload, dict) or "cases" not in payload:
        raise ValueError(
            f"retry report is missing 'cases' list: {path}"
        )
    return payload


def _classify_trend(attempts: list[int | None]) -> str:
    """Label the attempt series. Missing entries (None) are ignored."""
    real = [a for a in attempts if a is not None]
    if len(real) < 2:
        return "flat"
    grew = any(b > a for a, b in zip(real, real[1:]))
    shrank = any(b < a for a, b in zip(real, real[1:]))
    if grew and shrank:
        return "mixed"
    if grew:
        return "growing"
    if shrank:
        return "shrinking"
    return "flat"


def summarize_retry_reports(directory: Path) -> dict[str, Any]:
    """Walk ``directory/*.json`` and return a cross-report trend summary.

    Raises ``FileNotFoundError`` if the directory doesn't exist or is
    empty; ``ValueError`` on malformed reports.
    """
    if not directory.exists():
        raise FileNotFoundError(f"directory not found: {directory}")
    if not directory.is_dir():
        raise FileNotFoundError(f"not a directory: {directory}")

    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise FileNotFoundError(
            f"no *.json retry reports found in: {directory}"
        )

    reports: list[dict[str, Any]] = []
    per_report_entries: list[dict[tuple[str, int], dict[str, Any]]] = []
    for p in paths:
        payload = _load_report(p)
        reports.append({"path": str(p), "label": p.stem})
        by_key: dict[tuple[str, int], dict[str, Any]] = {}
        for entry in payload.get("cases", []):
            key = (entry["case"], int(entry.get("repeat", 0)))
            by_key[key] = entry
        per_report_entries.append(by_key)

    all_keys = sorted({k for m in per_report_entries for k in m})

    cases: list[dict[str, Any]] = []
    trend_counts = {"flat": 0, "growing": 0, "shrinking": 0, "mixed": 0}
    for key in all_keys:
        attempts_by_report: list[int | None] = []
        passed_by_report: list[bool | None] = []
        for m in per_report_entries:
            entry = m.get(key)
            if entry is None:
                attempts_by_report.append(None)
                passed_by_report.append(None)
            else:
                attempts_by_report.append(len(entry.get("attempts") or []))
                passed_by_report.append(bool(entry.get("passed", False)))
        trend = _classify_trend(attempts_by_report)
        trend_counts[trend] += 1
        cases.append(
            {
                "case": key[0],
                "repeat": key[1],
                "attempts_by_report": attempts_by_report,
                "passed_by_report": passed_by_report,
                "trend": trend,
            }
        )

    return {
        "reports": reports,
        "cases": cases,
        "trend_counts": trend_counts,
    }


def retry_summary_to_markdown(summary: dict[str, Any]) -> str:
    reports = summary["reports"]
    labels = [r["label"] for r in reports]
    cases = summary["cases"]
    counts = summary["trend_counts"]

    lines: list[str] = [
        "# Frok Retry-Report Trend",
        "",
        f"- Reports: {len(reports)}",
        f"- Cases tracked: {len(cases)}",
        f"- Growing: {counts['growing']}",
        f"- Shrinking: {counts['shrinking']}",
        f"- Mixed: {counts['mixed']}",
        f"- Flat: {counts['flat']}",
        "",
    ]

    if reports:
        lines.append("## Reports")
        lines.append("")
        for r in reports:
            lines.append(f"- `{r['label']}` — `{r['path']}`")
        lines.append("")

    # Full attempts matrix.
    if cases and labels:
        header = "| Case | Repeat | Trend | " + " | ".join(labels) + " |"
        sep = (
            "|------|-------:|-------|"
            + "|".join(["----:"] * len(labels))
            + "|"
        )
        lines.append(header)
        lines.append(sep)
        for c in cases:
            row = (
                f"| {c['case']} | {c['repeat']} | {c['trend']} | "
                + " | ".join(
                    str(a) if a is not None else "-"
                    for a in c["attempts_by_report"]
                )
                + " |"
            )
            lines.append(row)
        lines.append("")

    # Per-trend breakouts — spotlight the ones that need operator eyes.
    for label, trend in [("Growing", "growing"), ("Mixed", "mixed")]:
        rows = [c for c in cases if c["trend"] == trend]
        if not rows:
            continue
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| Case | Repeat | Attempts timeline |")
        lines.append("|------|-------:|-------------------|")
        for c in rows:
            series = " → ".join(
                str(a) if a is not None else "-"
                for a in c["attempts_by_report"]
            )
            lines.append(f"| {c['case']} | {c['repeat']} | {series} |")
        lines.append("")

    return "\n".join(lines)
