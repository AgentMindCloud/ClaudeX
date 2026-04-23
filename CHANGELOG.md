# Changelog

All notable changes to this repository are logged here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); dates are ISO 8601.

## [Unreleased]

### Added
- `README.md` — project pitch, repo layout, how to work with the agent, conventions.
- `ROADMAP.md` — living roadmap with Phase 0 in-progress and four proposed Phase 1 candidates (codebase audit, greenfield Frok scaffold, Grok API wrapper, X stream agent).
- `PROGRESS.md` — structured per-session log (session 1: blocked-kickoff; session 2: Phase 0 bootstrap; session 3: Phase 1A close).
- `CLAUDE.md` "Current Active Phase" now populated with **Phase 0: Bootstrap** (goal, acceptance criteria, exit condition).
- `audits/_template.md` — per-repo audit template (sections 1–11, evidence-log mandatory).
- `audits/01-grok-install.md` … `audits/12-claudex.md` — 12 per-repo Phase-1A audits.
- `audits/00-ecosystem-overview.md` — 9-section cross-cut synthesis (dependency graph, spec-version pin matrix, JSON Schema draft matrix, standards-count coherence, release cadence, safety-profile distribution, docs drift, inventory corrections, cross-cutting concerns A–H).
- `audits/97-methodology.md` — access-mode rationale, evidence discipline, security-disclosure policy, audit-order rationale, checkpoints, evidence-log row counts (71 across 12 audits; 10-orchestra exception documented).
- `audits/98-risk-register.md` — 29 risk rows across 6 categories (Security, Supply chain, Governance, Version coherence, Documentation drift, Unverifiable claims); 3 S1, severity / likelihood / source / status per row.
- `audits/99-recommendations.md` — three-axis rubric (cross-repo reach × local leverage × effort), 20 ecosystem-wide recommendations in §2 with risk-register linkage, 28 deferrals in §3 (23 per-repo + 5 ClaudeX), 60-row partition closed.
- `audits/assets/dependency-graph.txt` — ASCII dependency graph used as source for `00 §1`.
- `phase-1b/README.md` — Phase 1B scope, MCP-scope (drafts-only) constraint, draft → §2 rec → risk-register → upstream target-repo mapping rules, filing workflow for the user.
- `phase-1b/ISSUES.md` — authoritative tracker: first-pass table (6 drafts across 4 §2 recs with `Risks closed` + `Unblocks §2` columns), second-pass table (3 drafts across 3 §2 recs with `Effort` + `Risks closed` + `Unblocks §2`), third-pass candidates (§2 #5, #8, #20), post-filing follow-ups (gated drafts), blocked-by chains, filing audit trail.
- `phase-1b/drafts/06-cli-install-mechanism.md` — upstream issue draft for §2 #6 (npm-vs-Python CLI install mismatch; closes VER-3 + UNV-1 S1).
- `phase-1b/drafts/09-v2-14-examples-coverage.md` — upstream issue draft for §2 #9 (migrate 5 remaining examples to v2.14 + CI gate; closes VER-1 S1).
- `phase-1b/drafts/14a-grok-install-action-readme.md` — upstream issue draft for §2 #14 in `grok-install-action` (14→12 standards phrasing).
- `phase-1b/drafts/14b-vscode-grok-yaml-landing.md` — upstream issue draft for §2 #14 in `vscode-grok-yaml` (14→12 standards phrasing). Sibling pair with 14a closes DOC-1.
- `phase-1b/drafts/15a-vscode-grok-yaml-description.md` — upstream issue draft for §2 #15 in `vscode-grok-yaml` (downgrade landing description; unblocks §2 #16).
- `phase-1b/drafts/15b-grok-agent-orchestra-description.md` — upstream issue draft for §2 #15 in `grok-agent-orchestra` (downgrade landing description). Sibling pair with 15a closes GOV-3 + DOC-3.
- `phase-1b/drafts/03-sha-pin-actions-ecosystem.md` — upstream issue draft for §2 #3 (ecosystem-wide SHA-pin of GitHub Actions + Renovate/Dependabot config; closes SUP-1 S2 across 8 CI-enabled repos; single coordination draft with 8-row per-repo checklist).
- `phase-1b/drafts/13-blocking-pip-audit-plus-secret-scan.md` — upstream issue draft for §2 #13 (drop `continue-on-error` on `pip-audit` + add gitleaks/trufflehog secret-scan; pilot on grok-install-cli + grok-build-bridge; closes SEC-2 + SEC-3 S2 on pilot repos).
- `phase-1b/drafts/18-ci-template-baseline.md` — upstream issue draft for §2 #18 (promote `grok-build-bridge`'s CI workflow as ecosystem baseline; primary target grok-build-bridge + 7-adopter checklist; delivers SEC-2 / SUP-1 closure across adopters once the posture fixes from #3 + #13 land at the source).
- `phase-1b/filing-packets/README.md` — two filing paths (widened-MCP-scope agent session vs. manual GitHub UI), ready-to-paste kickoff prompt for the next session, filing order, back-fill discipline for `ISSUES.md`, and troubleshooting notes.
- `phase-1b/filing-packets/01-grok-install.md` … `11-x-platform-toolkit.md` — 11 per-repo filing packets carrying title / suggested labels / body pointer (to `phase-1b/drafts/<file>.md`) for each Phase-1B primary and cross-ref targeting that repo. Numbering matches `audits/NN-*.md`; `12-claudex.md` is intentionally absent (own MCP scope).
- `phase-1b/drafts/05-safety-profile-rubric.md` — upstream issue draft for §2 #5 (unified safety-profile rubric with conformance tests; target `grok-yaml-standards`; four-part acceptance covering rubric contents, location, conformance-test format, and consumer contract for grok-install-cli / awesome-grok-agents / grok-build-bridge / grok-agent-orchestra; closes partial UNV-3 S3 and enables UNV-4 S3 closure).
- `phase-1b/drafts/08-grok-yaml-standards-draft-2020-12-migration.md` — upstream issue draft for §2 #8 (migrate `grok-yaml-standards` schemas to JSON Schema draft-2020-12 for v1.3; two-part acceptance covering core migration + downstream smoke-test coordination; closes VER-2 S2 outright).
- `phase-1b/drafts/20-grok-agents-marketplace-pr-triage-codeowners.md` — upstream issue draft for §2 #20 (triage the 12 open PRs + publish `.github/CODEOWNERS` + `SECURITY.md` + `CONTRIBUTING.md` + document a review SLA; three-part acceptance, each independently mergeable; closes GOV-2 S2 outright).
- `phase-1b/drafts/16-vscode-grok-yaml-bootstrap.md` — upstream issue draft for §2 #16 (bootstrap v0.1.0 with read-only schema validation against `grok-yaml-standards`; two-part acceptance covering minimum-viable extension + schema-fetch strategy options; speculative on §2 #15a/#15b; closes partial GOV-3).
- `phase-1b/drafts/07-grok-install-cli-releases-pyproject-alignment.md` — upstream issue draft for §2 #7 (publish tagged GitHub releases + align `grok-install-action`'s pin; two-part acceptance covering release pipeline in CLI + pin alignment under each of §2 #6's three options; speculative on §2 #6; closes VER-3 at the pin layer).
- `phase-1b/drafts/12-awesome-grok-agents-replace-install-stub.md` — upstream issue draft for §2 #12 (replace `grok_install_stub` with real `grok-install-cli` invocation in `validate-templates.yml`; two-part acceptance including optional rubric-conformance matrix; speculative on §2 #6 + #7 — deepest speculation; closes partial UNV-4).
- `phase-1b/drafts/01-shared-grok-safety-rules-package.md` — upstream issue draft for §2 #1 (extract shared `grok-safety-rules` package consumed by CLI + bridge + orchestra + gallery; two-part acceptance covering package shape / ownership options + consumer-adoption sequencing; speculative on §2 #5; closes UNV-4 S3 outright + partial SEC-1).
- `phase-1b/drafts/11-awesome-grok-agents-permissive-exemplar.md` — upstream issue draft for §2 #11 (add `internal-ci-assistant` permissive-exemplar template + optional CI distribution report; speculative on §2 #5; closes the 6/4/0 "missing-exemplar" finding in `00-ecosystem-overview.md §6.2`).
- `phase-1b/drafts/17-grok-agent-orchestra-bootstrap.md` — upstream issue draft for §2 #17 (bootstrap v0.1.0 with a plan-execute-critique pattern + a behavioural Lucas safety veto; two-part acceptance; speculative on §2 #5 + #1 — deepest speculation with explicit fall-back if #1 not shipped; closes UNV-3 S3 outright + partial GOV-3).
- `phase-1b/drafts/10-grok-docs-v2-14-plus-7-standards-reference.md` — upstream issue draft for §2 #10 (ship `grok-docs` v2.14 content + reference pages for the 7 undocumented standards; three-part acceptance covering spec-page refresh + 7 new reference pages + publication layer; L-effort content-writing; closes VER-4 + DOC-2 outright; unblocks §2 #4 for drafting).
- `phase-1b/drafts/04-repository-dispatch-spec-to-consumers.md` — upstream issue draft for §2 #4 (wire `repository_dispatch` from `grok-install` → `grok-docs` + `grok-install-action` + `grok-agents-marketplace`; two-part acceptance covering publisher workflow + three subscriber listeners; speculative on §2 #10; closes VER-4 trigger + partial DOC-1).

### Changed
- Renamed `CLAUDE.me` → `CLAUDE.md` to match Claude Code's canonical filename.

### Open / deferred
- `CLAUDE.md` "Primary Repos & Focus Areas" (lines 8–15) remains a placeholder; needs real repo URLs from the user (tracked as `99 §3.3` row 2 and risk register `GOV-5`).
- Phase 1B first + second pass drafts (9 files total) await upstream filing by the user (MCP scope is `agentmindcloud/claudex`-only; the agent cannot file them). See `phase-1b/README.md §Filing workflow` and `phase-1b/ISSUES.md`.
- Phase 1B fifth-pass draft (§2 #4 — 1 file) shipped 2026-04-23; cumulative **20 drafts across 18 of 20 §2 recs** still await upstream filing.
- Session-2 + fourth-pass + fifth-pass drafts all carry the mandatory speculative-draft metadata header (prerequisite status + re-review trigger). Filing order respects the prerequisite tree.
- Undrafted from §2 (2 of 20 remaining): **#2** (shared Grok API client, L, reach 5), **#19** (x-platform-toolkit CI, M, reach 2). See `PROGRESS.md` Phase-1B fifth-pass "Next suggested action".
