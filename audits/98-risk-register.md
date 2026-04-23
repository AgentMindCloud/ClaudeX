# Risk Register — Phase 1A Ecosystem Audit

- **Scope**: risks harvested from each per-repo audit's §6 (Security & safety signals), §10 (Open questions), and headline-findings (§1). Cross-referenced as `[→ NN, §s]`.
- **Snapshot**: 2026-04-23. Re-assess at each phase boundary.
- **Severity scale**: S1 (critical — blocks reproducible use / introduces security exposure), S2 (high — causes drift or silent degradation), S3 (medium — hygiene / credibility), S4 (low — future-facing or cosmetic).
- **Likelihood scale**: L-high / L-med / L-low.
- **Status legend**: `open` · `mitigated-partial` · `deferred` · `needs-info`.

Companion files: `audits/00-ecosystem-overview.md` (for the cross-cutting context), `audits/99-recommendations.md` (for the fix pipeline).

Risks are grouped into six categories. Row counts (filled in unit 10):

| § | Category | Why this grouping | Row count |
|---|----------|-------------------|:-:|
| 1 | Security & runtime safety | Static-scan gaps, LLM-audit fragility, secret-handling surfaces. | — |
| 2 | Supply chain & dependency hygiene | Pinning discipline, action-tag pinning, lockfile presence. | — |
| 3 | Governance & single-points-of-failure | Solo-maintainer channels, missing disclosure policies, unreviewed PR queues. | — |
| 4 | Version & schema coherence | Spec / CLI / schema-draft drifts; multi-version tolerance. | — |
| 5 | Documentation drift | Count mismatches, version-number lag, shell-repo descriptions. | — |
| 6 | Unverifiable or deferred claims | Capability claims that the audit couldn't confirm without clone / org MCP / maintainer input. | — |

## 1. Security & runtime safety

_(filled in unit 10)_

## 2. Supply chain & dependency hygiene

_(filled in unit 10)_

## 3. Governance & single-points-of-failure

_(filled in unit 10)_

## 4. Version & schema coherence

_(filled in unit 10)_

## 5. Documentation drift

_(filled in unit 10)_

## 6. Unverifiable or deferred claims

_(filled in unit 10)_
