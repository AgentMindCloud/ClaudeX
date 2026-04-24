"""Diff two ``--retry-report`` JSON dumps.

A retry-report (produced by ``frok run --retry-report PATH``) carries
one entry per (case, repeat) unit:

    {
      "cases": [
        {
          "case": "<name>",
          "repeat": <int>,
          "attempts": [{"attempt", "passed", "error", "sleep_before_ms"}],
          "retry_budget": <int>,
          "passed": <bool>
        }, ...
      ]
    }

``diff_retry_reports(a, b)`` matches `(case, repeat)` pairs across two
such reports and surfaces:

* ``matched`` — per-pair record with attempt deltas and error drift
* ``only_in_a`` / ``only_in_b`` — entries missing from one side
* ``attempts_grew`` / ``attempts_shrank`` — subsets of ``matched``
* ``error_changed`` — last-attempt error drift (either direction)
* ``newly_failing`` / ``newly_passing`` — terminal verdict flipped
* ``regressed`` — True iff attempts grew, a new failure appeared in
  B, or a previously-matching error shape changed to a new string
  (a new failure mode surfaced)

The "regressed" heuristic is deliberately conservative: attempt
shrinkage and pass-flipping (a→b going from fail→pass) are not
regressions; both are improvements. Error drift between two non-null
strings IS regressed because it signals the failure shape moved.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _last_error(entry: dict[str, Any]) -> str | None:
    attempts = entry.get("attempts") or []
    if not attempts:
        return None
    return attempts[-1].get("error")


def _num_attempts(entry: dict[str, Any]) -> int:
    return len(entry.get("attempts") or [])


def _key(entry: dict[str, Any]) -> tuple[str, int]:
    return (entry["case"], int(entry.get("repeat", 0)))


def diff_retry_reports(
    a: dict[str, Any], b: dict[str, Any]
) -> dict[str, Any]:
    """Symmetric diff of two retry-report payloads."""
    a_by_key = {_key(e): e for e in a.get("cases", [])}
    b_by_key = {_key(e): e for e in b.get("cases", [])}

    matched: list[dict[str, Any]] = []
    attempts_grew: list[dict[str, Any]] = []
    attempts_shrank: list[dict[str, Any]] = []
    error_changed: list[dict[str, Any]] = []
    newly_failing: list[dict[str, Any]] = []
    newly_passing: list[dict[str, Any]] = []

    for key in sorted(set(a_by_key) & set(b_by_key)):
        a_entry = a_by_key[key]
        b_entry = b_by_key[key]
        a_attempts = _num_attempts(a_entry)
        b_attempts = _num_attempts(b_entry)
        a_error = _last_error(a_entry)
        b_error = _last_error(b_entry)
        a_passed = bool(a_entry.get("passed", False))
        b_passed = bool(b_entry.get("passed", False))

        record = {
            "case": key[0],
            "repeat": key[1],
            "a_attempts": a_attempts,
            "b_attempts": b_attempts,
            "attempts_delta": b_attempts - a_attempts,
            "a_passed": a_passed,
            "b_passed": b_passed,
            "a_error": a_error,
            "b_error": b_error,
            "error_changed": a_error != b_error,
        }
        matched.append(record)

        if b_attempts > a_attempts:
            attempts_grew.append(record)
        elif b_attempts < a_attempts:
            attempts_shrank.append(record)

        if a_error != b_error:
            error_changed.append(record)

        if a_passed and not b_passed:
            newly_failing.append(record)
        elif not a_passed and b_passed:
            newly_passing.append(record)

    only_in_a = [
        a_by_key[k] for k in sorted(set(a_by_key) - set(b_by_key))
    ]
    only_in_b = [
        b_by_key[k] for k in sorted(set(b_by_key) - set(a_by_key))
    ]

    # Conservative regression heuristic. Errors drifting from null →
    # non-null is caught by newly_failing already; non-null → null is
    # an improvement (error resolved); non-null → different non-null
    # is a shape change we flag.
    error_drift_regressed = [
        r
        for r in error_changed
        if r["a_error"] is not None and r["b_error"] is not None
    ]
    new_failures_in_b_only = [
        e for e in only_in_b if not bool(e.get("passed", False))
    ]
    regressed = bool(
        attempts_grew
        or newly_failing
        or error_drift_regressed
        or new_failures_in_b_only
    )

    return {
        "matched": matched,
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "attempts_grew": attempts_grew,
        "attempts_shrank": attempts_shrank,
        "error_changed": error_changed,
        "newly_failing": newly_failing,
        "newly_passing": newly_passing,
        "regressed": regressed,
    }


def retry_diff_to_markdown(
    diff: dict[str, Any],
    *,
    a_label: str = "a",
    b_label: str = "b",
    a_path: Path | str | None = None,
    b_path: Path | str | None = None,
) -> str:
    lines: list[str] = ["# Frok Retry-Report Diff", ""]
    if a_path is not None or b_path is not None:
        lines.append(f"- {a_label}: `{a_path or '-'}`")
        lines.append(f"- {b_label}: `{b_path or '-'}`")
    lines.extend(
        [
            f"- Matched cases: {len(diff['matched'])}",
            f"- Attempts grew: {len(diff['attempts_grew'])}",
            f"- Attempts shrank: {len(diff['attempts_shrank'])}",
            f"- Error changed: {len(diff['error_changed'])}",
            f"- Newly failing: {len(diff['newly_failing'])}",
            f"- Newly passing: {len(diff['newly_passing'])}",
            f"- Only in {a_label}: {len(diff['only_in_a'])}",
            f"- Only in {b_label}: {len(diff['only_in_b'])}",
            f"- Regressed: {'yes' if diff['regressed'] else 'no'}",
            "",
        ]
    )

    def _section(title: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        lines.append(f"## {title}")
        lines.append("")
        lines.append(
            f"| Case | Repeat | {a_label} attempts | {b_label} attempts "
            f"| Δ | {a_label} error | {b_label} error |"
        )
        lines.append(
            "|------|-------:|------------------:|------------------:|"
            "--:|----------|----------|"
        )
        for r in rows:
            lines.append(
                f"| {r['case']} | {r['repeat']} | {r['a_attempts']} | "
                f"{r['b_attempts']} | {r['attempts_delta']:+d} | "
                f"`{r['a_error'] or '-'}` | `{r['b_error'] or '-'}` |"
            )
        lines.append("")

    _section("Attempts grew", diff["attempts_grew"])
    _section("Error changed", diff["error_changed"])
    _section("Newly failing", diff["newly_failing"])
    _section("Attempts shrank", diff["attempts_shrank"])
    _section("Newly passing", diff["newly_passing"])

    def _only_section(title: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        lines.append(f"## {title}")
        lines.append("")
        lines.append(
            "| Case | Repeat | Attempts | Passed | Last error |"
        )
        lines.append(
            "|------|-------:|---------:|--------|------------|"
        )
        for entry in rows:
            lines.append(
                f"| {entry['case']} | {entry.get('repeat', 0)} | "
                f"{_num_attempts(entry)} | "
                f"{'yes' if entry.get('passed') else 'no'} | "
                f"`{_last_error(entry) or '-'}` |"
            )
        lines.append("")

    _only_section(f"Only in {a_label}", diff["only_in_a"])
    _only_section(f"Only in {b_label}", diff["only_in_b"])

    return "\n".join(lines)
