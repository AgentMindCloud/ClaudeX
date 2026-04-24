"""Declarative alignment-rules engine for Grok/Frok model calls.

Rules are pure functions that inspect a string (a prompt or a model output)
and emit zero or more `Finding`s. A `SafetyRuleSet` runs a batch of rules
and, depending on each finding's severity, either records, rewrites, or
blocks the text. The engine is deliberately simple: heuristic, deterministic,
auditable. It is not a replacement for a trained classifier — it is the
pre/post-flight guardrail that every `grok-client` call flows through.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Callable, Iterable


class Severity(enum.IntEnum):
    INFO = 10
    WARN = 20
    REWRITE = 30
    BLOCK = 40


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: Severity
    message: str
    span: tuple[int, int] | None = None
    replacement: str | None = None


@dataclass
class RuleResult:
    text: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(f.severity >= Severity.BLOCK for f in self.findings)

    @property
    def rewritten(self) -> bool:
        return any(f.severity == Severity.REWRITE for f in self.findings)

    def max_severity(self) -> Severity:
        if not self.findings:
            return Severity.INFO
        return max(f.severity for f in self.findings)


RuleFn = Callable[[str], Iterable[Finding]]


@dataclass(frozen=True)
class SafetyRule:
    name: str
    check: RuleFn
    description: str = ""


# ---------------------------------------------------------------------------
# Built-in rules
# ---------------------------------------------------------------------------

_SYCOPHANCY_PATTERNS = (
    r"\bas an ai (language )?model\b",
    r"\bgreat question\b",
    r"\bi (?:completely |totally )?agree\b",
    r"\byou('?re| are) absolutely right\b",
    r"\bwhat an excellent\b",
)
_SYCOPHANCY_RE = re.compile("|".join(_SYCOPHANCY_PATTERNS), re.IGNORECASE)


def _anti_sycophancy(text: str) -> Iterable[Finding]:
    for m in _SYCOPHANCY_RE.finditer(text):
        yield Finding(
            rule="anti-sycophancy",
            severity=Severity.REWRITE,
            message=f"Sycophantic phrasing: {m.group(0)!r}",
            span=(m.start(), m.end()),
            replacement="",
        )


_OVERCLAIM_PATTERNS = (
    r"\bi can guarantee\b",
    r"\b100% (?:accurate|certain|correct)\b",
    r"\bi (?:have|'ve) (?:just )?(?:browsed|accessed|queried) (?:the )?(?:internet|web|x\.com)\b",
    r"\bi am (?:self-?aware|conscious|sentient)\b",
)
_OVERCLAIM_RE = re.compile("|".join(_OVERCLAIM_PATTERNS), re.IGNORECASE)


def _no_overclaim(text: str) -> Iterable[Finding]:
    for m in _OVERCLAIM_RE.finditer(text):
        yield Finding(
            rule="no-overclaim",
            severity=Severity.BLOCK,
            message=f"Unverified capability claim: {m.group(0)!r}",
            span=(m.start(), m.end()),
        )


# Reasonable, conservative PII heuristics. Not a substitute for a real DLP
# system, but catches the obvious shapes before they hit an external API.
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def _pii_redaction(text: str) -> Iterable[Finding]:
    for label, pattern, token in (
        ("email", _EMAIL_RE, "[REDACTED_EMAIL]"),
        ("phone", _PHONE_RE, "[REDACTED_PHONE]"),
        ("ssn", _SSN_RE, "[REDACTED_SSN]"),
    ):
        for m in pattern.finditer(text):
            yield Finding(
                rule=f"pii-{label}",
                severity=Severity.REWRITE,
                message=f"Possible {label} in text",
                span=(m.start(), m.end()),
                replacement=token,
            )


_PROMPT_INJECTION_RE = re.compile(
    r"(?i)\b(?:ignore|disregard)\s+(?:all\s+)?(?:previous|prior|above)\s+"
    r"(?:instructions|prompts|rules)\b"
)


def _prompt_injection(text: str) -> Iterable[Finding]:
    for m in _PROMPT_INJECTION_RE.finditer(text):
        yield Finding(
            rule="prompt-injection",
            severity=Severity.WARN,
            message="Possible prompt-injection phrasing",
            span=(m.start(), m.end()),
        )


BUILTIN_RULES: tuple[SafetyRule, ...] = (
    SafetyRule(
        "anti-sycophancy",
        _anti_sycophancy,
        "Strip flattery that degrades truthfulness.",
    ),
    SafetyRule(
        "no-overclaim",
        _no_overclaim,
        "Block hallucinated capabilities and unverifiable certainty.",
    ),
    SafetyRule(
        "pii-redaction",
        _pii_redaction,
        "Redact obvious PII shapes before egress.",
    ),
    SafetyRule(
        "prompt-injection",
        _prompt_injection,
        "Flag likely prompt-injection on inbound text.",
    ),
)


# ---------------------------------------------------------------------------
# RuleSet runner
# ---------------------------------------------------------------------------


@dataclass
class SafetyRuleSet:
    rules: tuple[SafetyRule, ...] = BUILTIN_RULES

    def evaluate(self, text: str) -> RuleResult:
        findings: list[Finding] = []
        for rule in self.rules:
            findings.extend(rule.check(text))
        return RuleResult(text=text, findings=findings)

    def apply(self, text: str) -> RuleResult:
        """Run rules and apply rewrites. BLOCK findings leave text unchanged."""
        result = self.evaluate(text)
        if result.blocked:
            return result
        rewrites = [
            f for f in result.findings
            if f.severity == Severity.REWRITE and f.span is not None
        ]
        if not rewrites:
            return result
        # Apply non-overlapping rewrites right-to-left so spans stay valid.
        rewrites.sort(key=lambda f: f.span[0], reverse=True)  # type: ignore[index]
        out = text
        used: list[tuple[int, int]] = []
        for f in rewrites:
            assert f.span is not None
            s, e = f.span
            if any(not (e <= us or s >= ue) for us, ue in used):
                continue  # overlaps an earlier rewrite; skip
            out = out[:s] + (f.replacement or "") + out[e:]
            used.append((s, e))
        # Collapse any whitespace runs created by deletions.
        out = re.sub(r"[ \t]{2,}", " ", out).strip()
        result.text = out
        return result


def default_ruleset() -> SafetyRuleSet:
    return SafetyRuleSet()
