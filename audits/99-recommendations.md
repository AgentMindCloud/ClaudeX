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

The 20 below are the merge-down of 60 per-repo candidate rows, ranked by the §1 rubric. Each cell in the **Recommendation** column ends with a parenthetical `closes: <risk-IDs>` mapping back to `audits/98-risk-register.md`. ClaudeX-only recommendations (audit 12) are intentionally **not** here — they affect a single repo (cross-repo reach = 1) and are listed under §3 instead.

| # | Recommendation | Effort | Reach | Leverage | Affected repos | Source audits | Blocked by |
|:-:|----------------|:-:|:-:|:-:|----------------|---------------|:-:|
| 1 | Extract a shared `grok-safety-rules` package consumed by every safety-aware repo, replacing today's parallel reimplementations. (closes: UNV-4; partial SEC-1) | L | 4 | 4 | grok-install-cli, grok-build-bridge, grok-agents-marketplace, grok-agent-orchestra | [→ 09 §9 row 4]; [→ 03 §9 row 3]; [→ 10 §9 row 5]; [→ 06 §9 row 2] | 5 |
| 2 | Extract a shared Grok API client (auth, retries, streaming, rate-limit) — collapses the four parallel implementations identified in `00-ecosystem-overview.md` §9.A. (closes: drift identified in 00 §9.A) | L | 5 | 4 | grok-install-cli, grok-build-bridge, grok-agents-marketplace, awesome-grok-agents | [→ 00 §9.A] | — |
| 3 | Pin every GitHub Action by commit SHA (not major tag) ecosystem-wide; ship a Renovate / Dependabot config to keep them moving. (closes: SUP-1) | M | 5 | 3 | grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace, grok-build-bridge | [→ 01 §6]; [→ 02 §5,§6]; [→ 03 §5]; [→ 04 §6]; [→ 05 §5]; [→ 06 §6]; [→ 08 §5]; [→ 09 §5] | — |
| 4 | Wire `repository_dispatch` from `grok-install` (spec) → `grok-docs`, `grok-install-action`, `grok-agents-marketplace` so a spec bump fans out automatically. (closes: VER-4 trigger; partial DOC-1) | M | 4 | 4 | grok-install, grok-docs, grok-install-action, grok-agents-marketplace | [→ 00 §9.E] | 10 |
| 5 | Publish a unified safety-profile rubric (strict / standard / permissive) with conformance tests in `grok-yaml-standards`. Today the words exist; the contract does not. (closes: partial UNV-3; enables UNV-4 closure) | M | 4 | 4 | grok-yaml-standards, awesome-grok-agents, grok-install-cli, grok-build-bridge, grok-agent-orchestra | [→ 02 §9 row 3]; [→ 06 §9 row 1] | — |
| 6 | Resolve the npm-vs-Python CLI install mismatch — pick one path, document it, and update `grok-install-action` accordingly. (closes: VER-3, UNV-1 — both S1) | S | 3 | 5 | grok-install-cli, grok-install-action | [→ 03 §9 row 1]; [→ 04 §9 row 1] | — |
| 7 | Publish proper `grok-install-cli` GitHub releases whose tag matches `pyproject.toml` and align the action's pin to that tag. (closes: VER-3 — same S1 as #6, different layer) | S | 2 | 5 | grok-install-cli, grok-install-action | [→ 03 §9 row 1] | 6 |
| 8 | Migrate `grok-yaml-standards` to JSON Schema **draft-2020-12** for v1.3, closing the draft-07/draft-2020 split with `grok-install`. (closes: VER-2) | M | 3 | 4 | grok-yaml-standards, grok-install (and downstream validators) | [→ 02 §9 row 1] | — |
| 9 | Migrate the remaining 5 of 6 `grok-install` examples to v2.14 schema and add a CI gate that fails if any in-repo example fails to validate. (closes: VER-1 — S1) | S | 2 | 5 | grok-install | [→ 01 §9 row 1] | — |
| 10 | Ship `grok-docs` v2.14 content and add reference pages for the 7 currently-undocumented standards. (closes: VER-4, DOC-2) | L | 4 | 5 | grok-docs (and every reader of the docs site) | [→ 05 §9 row 1] | — |
| 11 | Add a permissive-profile exemplar template to `awesome-grok-agents`, closing the 6/4/0 strict/standard/permissive distribution gap. (closes: 00 §6 missing-exemplar finding) | S | 3 | 4 | awesome-grok-agents, grok-agents-marketplace | [→ 06 §9 row 1] | 5 |
| 12 | Replace `awesome-grok-agents`'s `grok_install_stub` with a real CLI invocation in CI so template safety is actually validated against the live ruleset. (closes: partial UNV-4) | S | 2 | 4 | awesome-grok-agents, grok-install-cli | [→ 06 §9 row 2] | 6, 7 |
| 13 | Make `pip-audit` blocking (drop `continue-on-error`) and add `gitleaks` (or trufflehog) to every repo's CI, starting with the CLI + bridge templates. (closes: SEC-2, SEC-3) | S | 4 | 4 | grok-install-cli, grok-build-bridge (template); rolled out via #18 | [→ 03 §9 row 2]; [→ 03 §9 row 3]; [→ 09 §9 row 2] | — |
| 14 | Reconcile the "14 YAML specifications" phrasing in `grok-install-action` README and the `vscode-grok-yaml` landing page with `grok-yaml-standards/version-reconciliation.md` (12 standards) — pick a single source of truth and link to it. (closes: DOC-1) | S | 3 | 4 | grok-install-action, vscode-grok-yaml, grok-docs | [→ 04 §9 row 2]; [→ 07 §9 row 4] | — |
| 15 | Downgrade the README / landing-page descriptions of `vscode-grok-yaml` and `grok-agent-orchestra` to honestly describe the current LICENSE+README state, with a roadmap pointer. (closes: DOC-3) | S | 2 | 4 | vscode-grok-yaml, grok-agent-orchestra | [→ 07 §9 row 1]; [→ 10 §9 row 1] | — |
| 16 | Bootstrap a real `vscode-grok-yaml` v0.1.0 — even read-only schema-validation against `grok-yaml-standards` is enough to convert the shell into a usable extension. (closes: partial GOV-3) | M | 3 | 5 | vscode-grok-yaml (and every YAML-authoring repo in the ecosystem) | [→ 07 §9 row 2] | 15 |
| 17 | Bootstrap `grok-agent-orchestra` with a single working multi-agent pattern wired to the unified safety-profile rubric, plus a behavioural definition of the "Lucas safety veto". (closes: partial GOV-3, UNV-3) | L | 2 | 5 | grok-agent-orchestra | [→ 10 §9 row 2] | 5 |
| 18 | Extract `grok-build-bridge`'s CI workflow as the ecosystem baseline template (mypy strict, `--cov-fail-under=85`, draft-2020-12 validation, OS × Python matrix) and adopt it across the eight CI-enabled repos. (closes: indirectly SEC-2 across adopters; supports SUP-1 closure) | M | 5 | 4 | grok-build-bridge, grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace | [→ 09 §9 row 5]; [→ 10 §9 row 3] | — |
| 19 | Add minimum CI to `x-platform-toolkit` (html-validate, css-lint, broken-link, and a Live-vs-Spec consistency check that the toolkit's tools agree with current spec versions). (closes: SUP-5) | M | 2 | 5 | x-platform-toolkit (reach 2 because the toolkit publishes user-facing tools that read live spec versions) | [→ 11 §9 row 1] | — |
| 20 | Triage the 12 open PRs on `grok-agents-marketplace`, publish `CODEOWNERS`, and document a review SLA. (closes: GOV-2) | M | 2 | 5 | grok-agents-marketplace | [→ 08 §9 row 2] | — |

### Distribution check

- **Effort**: S × 9, M × 8, L × 4 (sum 21 because #18 is M-effort but L-coordination — captured as M).
- **Reach × Leverage composite (descending)**: #2 (20), #18 (20), #3 (15), #10 (20), #5 (16), #1 (16), #4 (16), #13 (16), #6 (15), #14 (12), #16 (15), #11 (12), #8 (12), #20 (10), #19 (10), #17 (10), #15 (8), #12 (8), #9 (10), #7 (10). Numbering is **prompt-mandated**, not score-derived; the composite column is for re-ranking in Phase 1B triage.
- **Risk-register coverage**: SEC-1 (partial via #1), SEC-2 (#13, #18), SEC-3 (#13), SUP-1 (#3, supported by #18), SUP-5 (#19), GOV-2 (#20), GOV-3 (#15, #16, #17), VER-1 (#9), VER-2 (#8), VER-3 (#6, #7), VER-4 (#4, #10), UNV-1 (#6), UNV-3 (#5, #17), UNV-4 (#1, #5, #12), DOC-1 (#14, partial #4), DOC-2 (#10), DOC-3 (#15). Uncovered by §2 (intentional — small-blast risks): SEC-4, SEC-5, SUP-2, SUP-3, SUP-4, GOV-1, GOV-4, GOV-5, VER-5, DOC-4, UNV-2, UNV-5 — see §3.

### Edge case: #19 (x-platform-toolkit CI)

The §1 rubric says reach-1 recommendations belong in §3. #19 is borderline: the toolkit hosts 8 of 20 advertised user-facing tools that **read live spec versions**, so a CI consistency check there protects every downstream user against silent spec-drift. Scored reach=2 on that argument. If a Phase 1B reviewer disagrees, demote it to §3.

## 3. Notable deferrals

_(filled in unit 13 — per-repo recommendations that did not make the top-20 because their reach is local-only, with cross-links to their source audits)_

## 4. Sequencing notes

A handful of the §2 recommendations unblock others; the suggested sequencing will be derived from the `Blocked by` column once §2 is filled. Phase 1B will turn the §2 table into upstream issues / PRs; this document is the input to that triage, not its substitute.
