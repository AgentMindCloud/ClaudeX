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

### Changed
- Renamed `CLAUDE.me` → `CLAUDE.md` to match Claude Code's canonical filename.

### Open / deferred
- `CLAUDE.md` "Primary Repos & Focus Areas" (lines 8–15) remains a placeholder; needs real repo URLs from the user (tracked as `99 §3.3` row 2 and risk register `GOV-5`).
- Phase 1B first + second pass drafts (9 files total) await upstream filing by the user (MCP scope is `agentmindcloud/claudex`-only; the agent cannot file them). See `phase-1b/README.md §Filing workflow` and `phase-1b/ISSUES.md`.
- Phase 1B third-pass candidates (§2 #5, #8, #20) + post-filing follow-ups (§2 #7, #12, #4, #16, #1, #11, #17) await user go-ahead — see `PROGRESS.md` Phase-1B second-pass session "Next suggested action".
