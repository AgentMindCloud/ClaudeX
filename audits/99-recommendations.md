# Recommendations — Phase 1A Ecosystem Audit

- **Scope**: distilled from 12 per-repo `§9 Top-5 high-impact improvements` tables (= **60 candidate recommendations**) and the cross-cutting concerns in `audits/00-ecosystem-overview.md` §9.
- **Snapshot**: 2026-04-23. Re-rank at each phase boundary.
- **Companion files**: `audits/00-ecosystem-overview.md` (cross-cut context), `audits/98-risk-register.md` (the risks these recommendations close).

## Purpose

Phase 1A produced a long tail of local nice-to-haves and a much shorter spine of changes that — if shipped — close multiple risks at once across the ecosystem. The job of this document is to surface that spine. It is **not** a complete merge of the 60 per-repo recommendations; it is the subset that earns its place by reach, not by polish. Per-repo recommendations that are valuable but local-only are catalogued in §3 (notable deferrals) with cross-links back to their source audit.

## Merging rubric

Each candidate was scored on three axes; the top-20 table in §2 carries those scores forward so they can be re-litigated.

| Axis | Definition | Scale |
|------|------------|:-:|
| **Cross-repo reach** | How many of the 12 audited repos materially benefit from the change. A change that closes one risk in one repo scores 1; a change that lands a shared module consumed by four implementations scores 5. | 1–5 |
| **Local leverage** | Within the affected repo(s), how much the change moves the headline-risk needle (severity reduction in `98-risk-register.md`, blocker removal, contract clarification). | 1–5 |
| **Effort** | Engineering cost to ship a credible v0.1 of the change, assuming a single contributor with repo write access. S = under a day; M = one to three days; L = a week or more, or requires coordination across maintainers. | S / M / L |

**Composite ranking** = `(cross-repo reach × local leverage) − effort-penalty`, where effort-penalty is 0 for S, 1 for M, 2 for L. Ties broken by cross-repo reach (we are explicitly weighting reach over local depth — this audit's central observation is that the ecosystem's leverage lives in its seams, not its individual repos).

A recommendation that scores high on local leverage but `1` on cross-repo reach belongs in §3, not §2 — no matter how appealing it looks in isolation.

## Mapping back to the risk register

Every recommendation in §2 cites at least one `98-risk-register.md` row ID (`SEC-N` / `SUP-N` / `GOV-N` / `VER-N` / `DOC-N` / `UNV-N`) so the closure relationship is explicit. A recommendation with no risk-register linkage is suspect and should be re-justified.

## How to read the source citations

`[→ NN §9 row M]` means *audit `NN-<repo>.md`, section 9 (Top-5 improvements), row M*. Where a recommendation is a direct lift of a per-repo top-5 row, the citation pins to that row; where it is a cross-cut merge of multiple per-repo rows, the citation lists each.

## 2. Top-20 ecosystem-wide recommendations

_(filled in unit 12 — table with columns: # · Recommendation · Effort · Cross-repo reach · Local leverage · Affected repos · Source audits · Blocked by)_

## 3. Notable deferrals

_(filled in unit 13 — per-repo recommendations that did not make the top-20 because their reach is local-only, with cross-links to their source audits)_

## 4. Sequencing notes

A handful of the §2 recommendations unblock others; the suggested sequencing will be derived from the `Blocked by` column once §2 is filled. Phase 1B will turn the §2 table into upstream issues / PRs; this document is the input to that triage, not its substitute.
