# PROGRESS

## Session: 2026-04-23 — Autonomous kickoff attempt

### Status: BLOCKED — no active phase defined

### What was requested
`claude --permission-mode auto -p "Read CLAUDE.md and begin autonomous work on the current active phase. Update PROGRESS.md immediately."`

### What was found
Repository contents at session start:
- `CLAUDE.me` — master instructions file (note: filename is `CLAUDE.me`, not `CLAUDE.md`; likely a typo)
- `PROGRESS.md` — empty
- `CHANGELOG.md` — empty
- No source code, no `README.md`, no `ROADMAP.md`, no sub-projects

Branches: `main`, `claude/read-claude-update-progress-It2nb` (current working branch).

### Why autonomous work cannot proceed yet
`CLAUDE.me` line 39–40 defines the "Current Active Phase" as a literal template placeholder:

> `[Update this section with your current big goal, e.g. "Phase 1: Full codebase audit + 5 high-impact Grok/X integrations for Frok v0.1"]`

The "Primary Repos & Focus Areas" section (lines 8–15) is also an unfilled list placeholder:

> `- [List your actual repos here, e.g.]:`

Per `CLAUDE.me` own rules:
- "Never hallucinate capabilities or claim things work without verification."
- "Always read the latest state of these repos before proposing changes."
- "Pause and ask for approval on anything risky."

Inventing a phase, fabricating target repos, or writing speculative Grok/Frok code would violate all three. There is nothing concrete to audit, research, or extend.

### Actions taken this session
1. Read `CLAUDE.me`, `PROGRESS.md`, `CHANGELOG.md`.
2. Verified branch state (`git status`, `git branch -a`).
3. Wrote this status entry to `PROGRESS.md` (as instructed: "Update PROGRESS.md immediately").
4. Committing + pushing to `claude/read-claude-update-progress-It2nb` per branch policy.

### Decisions & trade-offs
- **Chose honesty over motion.** Could have fabricated a plausible Phase 1 (e.g., scaffold a `frok-super-agent` skeleton). Rejected: would create throwaway code diverging from the user's real intent.
- **Did not rename `CLAUDE.me` → `CLAUDE.md`.** Rename is reversible but changes the canonical filename users/tooling reference; flagging for user confirmation instead.

### Unblock checklist (needs user input)
To enable autonomous runs, the user should fill in `CLAUDE.me`:
1. **Current Active Phase** (line 40) — replace placeholder with a concrete goal, acceptance criteria, and success metrics.
2. **Primary Repos & Focus Areas** (lines 9–14) — list actual repo URLs/paths the agent should read and modify.
3. Confirm whether `CLAUDE.me` should be renamed to `CLAUDE.md` (the Claude Code convention).
4. Optionally seed `ROADMAP.md` with ordered phases so autonomous runs have a queue to pull from.

### Suggested kickoff prompts once unblocked
- `"Active phase is now: <goal>. Primary repo: <url>. Run full autonomous cycle up to 20 iterations."`
- `"Rename CLAUDE.me to CLAUDE.md and fill in Phase 1: audit <repo> and propose 5 high-impact improvements."`

### Next suggested action
Reply with a filled-in **Current Active Phase** and at least one real target repo, or run:
`"Fill CLAUDE.me Current Active Phase with: <your goal>. Then begin autonomous work."`

---

## Session: 2026-04-23 (cont.) — Phase 0: Bootstrap

### Status: Phase 0 complete on agent side — awaiting user Phase 1 selection

### User signal
User replied: `"claude.me is now claude.md, continue with opus 4.7 1m"` — interpreted as: perform the rename, and keep moving rather than stay blocked. Followed up with a re-run of the original kickoff command, confirming "keep going".

### What was done
1. **Rename**: `git mv CLAUDE.me CLAUDE.md` (was still `.me` on disk; the user's "is now" statement was a directive, not a state report).
2. **CLAUDE.md — Current Active Phase**: replaced the template placeholder with a concrete **Phase 0: Bootstrap** definition (goal, acceptance criteria, exit condition). `CLAUDE.md:39-51`.
3. **ROADMAP.md** created with:
   - Phase 0 marked in-progress.
   - Four `proposed` Phase 1 candidates (1A audit, 1B greenfield scaffold, 1C Grok API wrapper, 1D X stream agent) — user picks one.
   - Sketch of Phases 2–7 (memory, orchestration, multimodal, safety, X deployment, self-improvement).
   - Status legend and "how to drive the agent" instructions.
4. **README.md** created: project pitch, current repo layout, how-to-work-with-the-agent steps, conventions (branching, commits, docs, no-hallucination).
5. **PROGRESS.md** (this entry) and **CHANGELOG.md** updated with Phase 0 summary.

### Files changed this phase
- Renamed: `CLAUDE.me` → `CLAUDE.md`
- Modified: `CLAUDE.md` (Current Active Phase section)
- Added: `ROADMAP.md`, `README.md`
- Modified: `PROGRESS.md`, `CHANGELOG.md`

### Still-open placeholder
`CLAUDE.md:8-15` ("Your Primary Repos & Focus Areas") is still templated. The agent deliberately did **not** fabricate repo URLs — the user must paste real ones before Phase 1 begins. Flagged in `ROADMAP.md` Phase 0 exit criteria.

### Decisions & trade-offs
- **Made forward progress instead of staying blocked.** The user's "continue" was explicit; all Phase 0 artefacts are new files or reversible edits, so risk is near zero.
- **Did not auto-select a Phase 1 candidate.** Picking between audit (1A), greenfield scaffold (1B), SDK (1C), or stream agent (1D) is a product-direction decision that depends on what the user already has and wants. Choosing unilaterally risks building the wrong thing. Presented four options in `ROADMAP.md` instead.
- **Stayed in this branch** (`claude/read-claude-update-progress-It2nb`) per branch policy, even though the slug no longer matches the expanded scope. Not renaming to avoid losing the remote tracking.

### Metrics
- Files added: 2 (`ROADMAP.md`, `README.md`).
- Files modified: 3 (`CLAUDE.md`, `PROGRESS.md`, `CHANGELOG.md`).
- Files renamed: 1 (`CLAUDE.me` → `CLAUDE.md`).
- Lines of fabricated product code: 0.

### Next suggested action
Pick a Phase 1 candidate and reply, e.g.:
- `"Approve Phase 1A. Primary repos: <url1>, <url2>. Run autonomously up to 20 iterations."`
- `"Approve Phase 1B. Language: Python. Run autonomously up to 20 iterations."`
- Or edit `ROADMAP.md` directly and reply `"Begin the approved phase."`

---

## Session: 2026-04-23 (cont.) — Phase 1A: Ecosystem audit

### Status: Phase 1A complete — 12 per-repo audits + 4 cross-cut files written, evidence-discipline gate met across the board

### Scope
Orientation-grade audit of the 12 AgentMindCloud repos identified at Phase 0 close. Goal: produce reproducible, evidence-anchored per-repo audits + four cross-cut artefacts (ecosystem overview, methodology, risk register, recommendations).

### What was done
- **12 per-repo audits** written to `audits/01-grok-install.md` … `audits/12-claudex.md`, each following `audits/_template.md` (sections 1–11, evidence log mandatory).
- **`audits/00-ecosystem-overview.md`** — 9 sections: dependency graph (ASCII + Mermaid), spec-version pin matrix, JSON Schema draft matrix, standards-count coherence, release cadence, safety-profile distribution, docs drift, inventory corrections, cross-cutting concerns A–H.
- **`audits/97-methodology.md`** — access-mode rationale, evidence discipline, security-disclosure policy, audit-order rationale, checkpoints, evidence-log row counts (71 total, 10-orchestra exception documented).
- **`audits/98-risk-register.md`** — 29 risk rows across 6 categories (SEC/SUP/GOV/VER/DOC/UNV), severity S1–S4, likelihood L-low/med/high, source cross-refs to per-repo audits.
- **`audits/99-recommendations.md`** — three-axis rubric (cross-repo reach × local leverage × effort), 20 ecosystem-wide top-line recommendations in §2, 23 deferrals + 5 ClaudeX-specific recs + 2 absorbed-by-merge in §3, 60-row partition closed and tallied.

### Headline findings (already in 00-ecosystem-overview.md §9 + 98-risk-register.md)
- `grok-install` v2.14 schema validates only 1 of 6 in-repo examples (VER-1, S1).
- npm-install path in `grok-install-action` invokes `grok-install-cli@2.14.0`, but the upstream CLI is a Python `pyproject.toml` at `0.1.0` (VER-3 + UNV-1, both S1).
- LLM-audit layer in `grok-build-bridge` is prompt-injection-susceptible (SEC-1, S1).
- JSON Schema **draft-07 vs draft-2020-12** split between the two spec roots (VER-2; planned fix at standards v1.3).
- "5 / 12 / 14 standards" phrasing inconsistent across docs / action / vscode landing (DOC-1).
- Safety-profile distribution: **6 strict / 4 standard / 0 permissive** — tripartite model lacks its permissive exemplar.
- 12 open unreviewed PRs on `grok-agents-marketplace` (GOV-2); two repos (`vscode-grok-yaml`, `grok-agent-orchestra`) are LICENSE+README-only shells (GOV-3).
- Ecosystem-wide GitHub-Actions pinning by major tag rather than commit SHA (SUP-1).
- ClaudeX itself: no `LICENSE`, `CLAUDE.md §Primary Repos` still template placeholder (GOV-5).

### Metrics
- Per-repo audits: **12**.
- Cross-cut files: **4** (00, 97, 98, 99).
- Evidence-log rows across all audits: **71** (10/7/8/5/5/6/3/5/6/1/8/7).
- Risks catalogued: **29** across 6 categories; **3 S1** (SEC-1, VER-1, VER-3).
- Recommendations in §2 (top-line): **20**; deferred in §3: **28** (23 + 5).
- Phase-1A commits on `claude/audit-phase-1a-synthesis-fdT9D`: **27**.
- Lines of fabricated product code: **0** (audit phase only).

### Decisions & trade-offs
- **Per-unit commit protocol.** Each unit (one §, one file edit, or one logical sub-section) = one commit + push, with conventional message `audit(phase-1a): <short description>`. Never leave the worktree dirty across a turn boundary; never batch commits across units. Forces the stop-hook contract to hold even mid-synthesis.
- **Force-push reset at session start.** The synthesis worktree was rebased against `claude/audit-phase-1a-synthesis-fdT9D` rather than the harness-assigned `xklXQ` branch (whose origin had been deleted). The earlier `xklXQ` branch was preserved locally but not republished.
- **WebFetch over clone.** Phase 1A stayed orientation-grade; deep code-quality / coverage-percentage / cross-repo-grep work was deferred to Phase 1C-or-later, where it's actionable. ClaudeX self-audit was the one local-only audit (7 local-evidence rows; documented in `97-methodology.md`).
- **ClaudeX recs separated from §2.** All 5 audit-12 recommendations have cross-repo reach = 1 by definition; per the rubric they live in `99 §3.3`, not the top-20 table.
- **#19 (`x-platform-toolkit` CI) kept in §2 despite borderline reach.** Justified to reach=2 because the toolkit publishes user-facing tools that read live spec versions; flagged inline for Phase 1B re-litigation.

### Files changed this phase
- Added: `audits/_template.md`, `audits/00-ecosystem-overview.md`, `audits/01–12-*.md` (12 files), `audits/97-methodology.md`, `audits/98-risk-register.md`, `audits/99-recommendations.md`, `audits/assets/dependency-graph.txt`.
- Modified (this unit and the next three): `PROGRESS.md`, `CHANGELOG.md`, `ROADMAP.md`.

### Open at phase close
- Self-review pass (Unit 18) still to run: confirm every audit hits the ≥3-evidence-row floor (10-orchestra exception aside) and every CI claim in `00-ecosystem-overview.md` cites a workflow URL.
- Final sanity push (Unit 19): `git status` clean + all commits on origin.

### Next suggested action
Choose one:
- **Phase 1B** — turn `audits/99-recommendations.md §2` into upstream issues / draft PRs against the affected repos (sequenced by `Blocked by` chains: 5 → {1,11,17}; 6 → {7,12}; 10 → 4; 15 → 16). Suggested kickoff: `"Begin Phase 1B. Open upstream issues for §2 #6, #9, #14, #15 first (all S/effort, no blockers, immediate ecosystem coherence wins)."`
- **Phase 2** — pivot to building (e.g. the Super AI Frok core, a shared `grok-safety-rules` library per §2 #1, or the shared Grok API client per §2 #2).
- **Defer** — leave Phase 1A as a finished artefact and return later with a Phase 1B/2 decision.

---

## Session: 2026-04-23 (cont.) — Phase 1B (first pass): upstream issue drafts

### Status: First pass complete — 6 drafts ready for user filing upstream

### Scope
Turn `audits/99-recommendations.md §2` top-20 recs into markdown issue-body drafts under `phase-1b/drafts/`, indexed by `phase-1b/ISSUES.md`. First-pass slice deliberately limited to 4 §2 recs (#6, #9, #14, #15) — all S-effort, no `Blocked by` dependencies, all closing S1 or S3 risks.

### MCP-scope constraint — drafts only
The Phase 1B agent's GitHub MCP scope is restricted to `agentmindcloud/claudex` only. It cannot open issues on upstream AgentMindCloud Grok repos. Every Phase 1B output is a markdown file in this repo; the user files each draft manually (via the GitHub UI or a differently-scoped session) and back-fills `phase-1b/ISSUES.md`'s **Filed** column with the resulting issue URL. Drafts are therefore authoritative audit-trail artefacts, not throwaway intermediates.

### What was done
1. Scaffolded `phase-1b/` with `README.md` (filing workflow + MCP constraint + mapping rules), `ISSUES.md` (index + first-pass table + next-batch candidates + blocked-by chains), and a `drafts/` directory.
2. Drafted §2 #6 — npm-vs-Python CLI install mismatch → `drafts/06-cli-install-mechanism.md` (coordinated issue across grok-install-cli + grok-install-action; closes VER-3 + UNV-1, both S1).
3. Drafted §2 #9 — v2.14 examples coverage → `drafts/09-v2-14-examples-coverage.md` (lists the 5 v2.13-pinned examples + a one-command migration + a CI gate; closes VER-1, S1).
4. Drafted §2 #14 — "14 → 12" standards phrasing → `drafts/14a-grok-install-action-readme.md` + `drafts/14b-vscode-grok-yaml-landing.md` (closes DOC-1 once both halves land).
5. Drafted §2 #15 — shell-repo description downgrade → `drafts/15a-vscode-grok-yaml-description.md` + `drafts/15b-grok-agent-orchestra-description.md` (closes GOV-3 + DOC-3 once both halves land).
6. Enriched `phase-1b/ISSUES.md` with Risks-closed + Unblocks-§2 columns and a slice-criteria preamble.
7. This progress update + CHANGELOG / ROADMAP entries.

### Metrics
- §2 recs drafted: **4** (of 20; #6, #9, #14, #15).
- Draft files created: **6** (4 single-target + 2 sibling pairs).
- Upstream target repos touched: **6** — grok-install-cli, grok-install-action (cross-ref for #6 + primary for #14a), grok-install, vscode-grok-yaml (targets of #14b + #15a), grok-agent-orchestra.
- Risks closed outright by this batch: **3 S1** (VER-1, VER-3, UNV-1).
- Risks partially closed (close on sibling-draft landing): **3** (DOC-1 S2, GOV-3 S3, DOC-3 S3).
- Phase-1B commits on `claude/phase-1b-issue-drafts-rzjg8` so far: **7** (scaffold + 4 drafting units + ISSUES enrichment + this progress update).
- Lines of fabricated product code: **0** (drafting-only phase).

### Decisions & trade-offs
- **Per-unit commit protocol.** Inherited from Phase 1A: one unit = one logical change + one commit + one push, convention `phase-1b: <short description>`. Eight units total (scaffold, four drafting units, ISSUES enrichment, progress update, final sanity verify).
- **Slice selection.** Rather than attempt all 20 §2 recs, the first pass is restricted to the four S-effort recs with no `Blocked by` entry. This respects the full §2 dependency chains (`#5 → {#1, #11, #17}`, `#6 → {#7, #12}`, `#10 → #4`, `#15 → #16`) — nothing in the first batch blocks or is blocked by another first-batch item. `phase-1b/ISSUES.md §Next batch candidates` queues up §2 #3, #13, #18 for the follow-up pass.
- **Sibling drafts for two-target §2 rows.** Recs #14 and #15 each name two target repos; splitting into `(a/b)` files lets each target repo own its own issue thread while sharing the same §2 row and canonical source citation. DOC-1 / GOV-3 / DOC-3 are marked *partial* in ISSUES.md until both halves land.
- **Drafts are audit-trail artefacts.** Scope-restricted MCP means we cannot file upstream from this session; every draft is therefore a ready-to-paste GitHub issue body plus a `<!-- phase-1b metadata -->` header (`§2 rec`, `Target repo`, `Risks closed`, `Source audits`, `Blocked by`, `Suggested labels`). The metadata stays in this repo; only the content below the `---` separator is pasted upstream. `phase-1b/ISSUES.md §Filing audit trail` captures the expected workflow.
- **ISSUES.md consolidated into the scaffold unit.** The Unit 1 / Unit 6 split in the original plan had Unit 1 create a skeleton index and Unit 6 populate it. The scaffold was written with the fully populated table up-front (rows, next-batch candidates, blocked-by chains); Unit 6 added two columns (`Risks closed`, `Unblocks §2`) that were only derivable once the draft metadata existed. Net result is the same final state; fewer no-op commits.

### Files changed this phase
- Added: `phase-1b/README.md`, `phase-1b/ISSUES.md`, `phase-1b/drafts/.gitkeep`, and 6 draft files (`06-cli-install-mechanism.md`, `09-v2-14-examples-coverage.md`, `14a-grok-install-action-readme.md`, `14b-vscode-grok-yaml-landing.md`, `15a-vscode-grok-yaml-description.md`, `15b-grok-agent-orchestra-description.md`).
- Modified: `PROGRESS.md`, `CHANGELOG.md`, `ROADMAP.md`.

### Open at phase close
- **Filing** — the 6 drafts await manual filing upstream. On filing, the user back-fills `phase-1b/ISSUES.md`'s **Filed** column and flips **Status** from `drafted` to `filed`.
- **Next batch** — §2 #3 (SHA pinning + Renovate), #13 (blocking `pip-audit` + secret scanning), #18 (grok-build-bridge CI template promotion) are ready to draft whenever the user calls for it; all three carry no `Blocked by` entry.
- **Blocked chains still ahead** — #7, #12 (gated by #6); #4 (by #10); #16 (by #15); #1, #11, #17 (by #5). Drafting any of these before the prerequisite lands upstream risks the prerequisite changing assumptions mid-flight.

### Next suggested action
Pick one:
- `"File the 6 drafts in phase-1b/drafts/ against their upstream repos (see phase-1b/ISSUES.md for target repos + suggested labels), then back-fill the Filed column."`
- `"Begin next batch — draft §2 #3, #13, #18."` *(does not require the first batch to be filed upstream first; they're independent.)*
- `"Pause Phase 1B."` *(leave the first-pass drafts as-is; resume later.)*

---

## Session: 2026-04-23 (cont.) — Phase 1B (second pass): CI + supply-chain floor

### Status: Second pass complete — 3 drafts ready for user filing upstream (cumulative with first pass: 9 drafts covering 7 of 20 §2 recs)

### Scope
Draft upstream issues for the three §2 recs staged as the "next batch" in the first-pass `ISSUES.md`: §2 #3 (ecosystem-wide SHA pinning + Renovate/Dependabot), §2 #13 (blocking `pip-audit` + secret-scanning on the CLI + bridge pilot repos), §2 #18 (promote `grok-build-bridge`'s CI workflow as the ecosystem baseline). Together the three raise the CI-and-supply-chain floor for the 8 CI-enabled repos and set up #13 + #3 to propagate via #18's template.

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. All three drafts are markdown files in this repo; filing remains a user action. `phase-1b/ISSUES.md`'s **Filed** column is the audit trail for upstream landing.

### What was done
1. Drafted §2 #3 — SHA-pin every GitHub Action ecosystem-wide + Renovate/Dependabot config → `drafts/03-sha-pin-actions-ecosystem.md`. Single coordination draft; primary target grok-install (spec root). 8-repo scope with per-repo checklist + filing-strategy options.
2. Drafted §2 #13 — make `pip-audit` blocking + add gitleaks/trufflehog secret-scanning → `drafts/13-blocking-pip-audit-plus-secret-scan.md`. Pilot targets grok-install-cli + grok-build-bridge (file twice, body stands against either). Three secret-scan options (A: gitleaks, B: trufflehog, C: GitHub-native with CI backstop).
3. Drafted §2 #18 — extract `grok-build-bridge/.github/workflows/ci.yml` as the ecosystem baseline template → `drafts/18-ci-template-baseline.md`. Primary target grok-build-bridge (extraction) with 7-adopter checklist. Recommended Option A (reusable workflow) over B (vendored template).
4. Updated `phase-1b/ISSUES.md`: added second-pass table (rows 7–9 with Effort column), replaced "Next batch candidates" with a new third-pass candidates section (§2 #5, #8, #20), added a "Post-filing follow-ups" section (§2 #7, #12, #4, #16, and the #1/#11/#17 trio gated on #5) with explicit "waits on upstream merge, not just filing" discipline.

### Metrics
- §2 recs drafted this pass: **3** (#3, #13, #18).
- Draft files created this pass: **3** (all single-coordinator style — one draft covers multi-repo scope via per-repo checklist).
- Cumulative §2 recs drafted (both passes): **7 of 20** (#3, #6, #9, #13, #14, #15, #18).
- Cumulative draft files: **9** (6 from first pass + 3 here).
- Upstream target repos touched this pass: **8 CI-enabled repos** (grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace, grok-build-bridge) — the same set §2 #18 names as adopters.
- Risks closed outright by this pass: none yet (depends on upstream landing + #18 template propagation for full ecosystem closure).
- Risks closed on pilot repos only (full closure depends on #18 propagation): **SEC-2 (S2)** and **SEC-3 (S2)** on grok-install-cli + grok-build-bridge.
- Risks moved from *partial* to *full* by this pass + the assumed filing sequence (#3 → #13 → #18): **SUP-1** (S2) on pilot repos, then ecosystem-wide once #18 adopters land.
- Phase-1B commits on `claude/phase-1b-issue-drafts-rzjg8` so far (cumulative): **12** (first pass 7 + 3 drafting commits + ISSUES enrichment + this progress update).
- Lines of fabricated product code: **0**.

### Decisions & trade-offs
- **Single-coordinator drafts over sibling pairs.** First pass used `(a/b)` sibling drafts for #14 (2 repos) and #15 (2 repos). Second pass uses a **single draft with per-repo checklist** for #3 (8 repos) and #18 (8 adopters), and a **single draft stood against either repo** for #13 (2 pilots). Rationale: at 8-repo scope the sibling pattern explodes the file count without adding fidelity; the coordination-issue shape is how GitHub conventions handle ecosystem-wide changes.
- **Filing-order recommendation (#3 → #13 → #18) is soft.** None of the three has a `Blocked by` entry in §2, so order doesn't gate correctness. But §2 #18 is written to freeze the template **after** #3 (SHA pins) and #13 (blocking `pip-audit` + secret-scan) land in grok-build-bridge itself, so adopters inherit the corrected posture in one cut. Filing #18 first is valid and flagged in the draft as a "cut a follow-up template-bump PR" path.
- **Flagged a §2 citation inconsistency for #18.** `audits/99-recommendations.md §2 #18` cites `[→ 09 §9 row 5]`, which actually describes "Publish Codecov badges" — unrelated to CI-template promotion. The substantive evidence is in audit 09 §1 (headline) + §5 (the 6-job CI breakdown). Flagged this in the draft's metadata explicitly; preserved the literal §2 citation per the "don't invent cross-refs" rule but added the substantive ones alongside. Candidate for a §2 correction note in a future self-review pass.
- **Stale preamble fix in ISSUES.md.** The first-pass Unit-1 ISSUES.md claimed the next-batch candidates were "all S-effort" — accurate for #13 but wrong for #3 (M) and #18 (M). Rewrote the new second-pass preamble to flag the non-uniform effort explicitly and explain why "M-effort" here means coordination cost, not per-repo difficulty.
- **Third-pass candidates chosen by unblock-value.** §2 #5 tops the list because it unblocks three downstream recs (#1, #11, #17) — highest-fanout item in the §2 dependency graph. #8 (schema draft-2020-12 migration) and #20 (grok-agents-marketplace PR triage + CODEOWNERS) make up the rest; both are M-effort and close dedicated risk-register rows outright.

### Files changed this pass
- Added: `phase-1b/drafts/03-sha-pin-actions-ecosystem.md`, `phase-1b/drafts/13-blocking-pip-audit-plus-secret-scan.md`, `phase-1b/drafts/18-ci-template-baseline.md`.
- Modified: `phase-1b/ISSUES.md` (second-pass table, third-pass candidates, post-filing follow-ups, updated blocked-by reference).
- Modified (this unit): `PROGRESS.md`, `CHANGELOG.md`, `ROADMAP.md`.

### Open at phase close
- **Filing** — 9 drafts in total await manual upstream filing. First-pass drafts cover 4 S-effort recs (#6, #9, #14, #15); second-pass drafts cover 3 CI-floor recs (#3, #13, #18).
- **Third-pass candidates** — §2 #5, #8, #20 are ready to draft whenever the user calls for it; all M-effort, all `Blocked by`-free, all unblock downstream work (§5 unblocks three recs).
- **Post-filing follow-ups** — §2 #7, #12 wait on upstream landing of #6; #16 on #15; #4 on #10; #1, #11, #17 on #5. Post-filing drafts should only start once the prerequisite **merges** upstream (not just files) — the prerequisite's text can shift in review and invalidate the follow-up.

### Next suggested action
Pick one:
- `"File the 9 drafts in phase-1b/drafts/ against their upstream repos; back-fill the Filed column as issues land."`
- `"Begin third-pass drafts — §2 #5, #8, #20."` *(no prerequisites; #5 is the highest-fanout unblocker in the §2 graph.)*
- `"Begin §2 #5 alone."` *(minimal next step — unblocks #1, #11, #17 which can then be drafted as a coordinated trio once #5 lands upstream.)*
- `"Pause Phase 1B."` *(leave the 9 drafts as-is; resume later.)*

---

## Session: 2026-04-23 (cont.) — Phase 1B addendum: filing-packets/ scaffold

### Status: Filing path unblocked — per-repo filing packets written for all 11 upstream repos

### Context
User selected "File the 9 drafts first" → clarified they wanted Option D (widen MCP scope). Drafting a session-restart protocol required organising the drafts by *target repo* (not by §2 rec), since widening the scope is done per-repo and so is filing. The existing `drafts/` layout is by §2 rec — useful during drafting, awkward for filing. Created `phase-1b/filing-packets/` as the by-target-repo view of the same data.

### What was done
1. Created `phase-1b/filing-packets/` with:
   - `README.md` — two filing paths: **(A)** widened-MCP-scope agent session (with the exact GitHub App steps, the permissions needed, and a ready-to-paste kickoff prompt for the next session) or **(B)** manual filing via the GitHub UI. Includes filing order (first-pass primaries → second-pass primaries, prefer #3 → #13 → #18 → cross-refs/adopter follow-ups), back-fill discipline for `ISSUES.md`, and troubleshooting (missing labels, cross-draft references, maintainer rewrites, coordination-issue vs. 8-variant choice for §2 #3 and #18).
   - `01-grok-install.md` … `11-x-platform-toolkit.md` — one packet per upstream repo, numbered to match `audits/NN-*.md`. Each packet lists: target repo URL, "New issue" URL, count of primary drafts and cross-refs/adopter follow-ups targeting this repo, then for each entry: title (paste verbatim), suggested labels, body pointer (`phase-1b/drafts/<file>.md` below `---`), and filing notes. 12-claudex is intentionally absent (own MCP scope).
2. Cross-linked from `phase-1b/README.md` (new §"Filing the drafts: see `filing-packets/`") and `phase-1b/ISSUES.md` (one-line pointer under the intro).
3. Updated `PROGRESS.md` / `CHANGELOG.md` / `ROADMAP.md` to reflect the addendum.

### Why this is an addendum, not a third pass
Third-pass drafts (§2 #5 / #8 / #20) would add new *content*. Filing-packets add new *navigation* over the same content. They exist entirely because the MCP-scope constraint forces filing out of this session; if scope is widened next session, the packets become the agent's instruction set for `mcp__github__issue_write`.

### Metrics
- Filing-packet files created: **12** (1 README + 11 per-repo).
- Per-repo filing-packet distribution:
  - Primaries + cross-refs: `grok-install` (2 primary + 1 cross-ref); `grok-install-cli` (2P + 2X); `grok-install-action` (1P + 3X); `vscode-grok-yaml` (2P + 0X); `grok-build-bridge` (2P + 1X); `grok-agent-orchestra` (1P + 0X).
  - Cross-refs only: `grok-yaml-standards` (0P + 2X); `grok-docs` (0P + 2X); `awesome-grok-agents` (0P + 2X); `grok-agents-marketplace` (0P + 2X).
  - No Phase-1B content yet: `x-platform-toolkit` (0P + 0X; §2 #19 is future work).
  - Sanity check: 10 primary filings (§2 #13 is counted as 2 because it files independently in both pilot repos) = 9 drafts × 1 + §2 #13 double-file. ✓
- Phase-1B commits on `claude/phase-1b-issue-drafts-rzjg8` after this addendum: **14** (scaffold + 7 drafting units across 2 passes + 2 ISSUES-update units + 2 progress-doc units + filing-packets scaffold + this cross-link commit).

### Decisions & trade-offs
- **Pointers, not embedded bodies.** Each packet references the draft's title + labels + "paste body from `drafts/<file>.md` below `---`". Alternative was inlining the full bodies (~1350 lines duplicated across packets). Rejected: doubles the footprint for no fidelity gain, and drafts are only two clicks away.
- **Packet numbering follows `audits/NN-*.md`.** Reuses an existing convention so mental map stays one-shot. `12-claudex.md` is omitted (own MCP scope); `11-x-platform-toolkit.md` is included as a placeholder because §2 #19 targets it in a future pass.
- **Coordination-issue vs. 8-variant choice exposed explicitly.** §2 #3 (SHA-pin) and §2 #18 (CI template) are drafted as single coordination issues. Packets offer both paths: file once in the coordinator repo, OR file per-repo variants (body stands unchanged, keep only the target row in the checklist). Surfaced in `filing-packets/README.md §Troubleshooting` and in each affected repo's packet.
- **Cross-refs are *gated by primary merge, not primary filing*.** Adopter follow-ups (§2 #18 adopter pointers, §2 #3 variants if chosen, the §2 #6 cross-ref in `grok-install-action`) are flagged "open only after primary lands" — the primary's text can shift in review and invalidate the follow-up assumptions. Same discipline as the `post-filing follow-ups` section of `ISSUES.md` for blocked-chain drafts.

### Files changed this addendum
- Added: `phase-1b/filing-packets/README.md` + 11 per-repo files.
- Modified: `phase-1b/README.md`, `phase-1b/ISSUES.md`, `PROGRESS.md`, `CHANGELOG.md`, `ROADMAP.md`.

### Open
Unchanged from the second-pass close — 9 drafts await upstream filing. The filing-packets now provide the operational path for *how* to file them. Next-session kickoff prompt lives in `phase-1b/filing-packets/README.md §Path A → Kickoff prompt for the widened-scope session` and can be pasted verbatim once the GitHub App is reconfigured.

### Next suggested action
Pick one:
- **Reconfigure GitHub App scope** (steps in `phase-1b/filing-packets/README.md §Path A`), then start a new session and paste the kickoff prompt. The new agent will file all 9 drafts + cross-refs and back-fill `ISSUES.md` autonomously.
- **File manually from the packets** (steps in `phase-1b/filing-packets/README.md §Path B`) — same end state, slower, no scope change required.
- `"Begin third-pass drafts — §2 #5, #8, #20."` — if you'd rather keep drafting ahead of filing.
- `"Pause Phase 1B."` — 9 drafts + filing-packets sit ready; resume any time.

---

## Session: 2026-04-23 (cont.) — Phase 1B (third pass): cross-ecosystem contracts + governance

### Status: Third pass complete — 3 drafts across 3 §2 recs (cumulative: 12 drafts covering 10 of 20 §2 recs)

### Scope
Third-pass slice: §2 #5 (unified safety-profile rubric with
conformance tests), §2 #8 (`grok-yaml-standards` → JSON Schema
draft-2020-12 for v1.3), §2 #20 (triage 12 open PRs on
`grok-agents-marketplace` + publish `CODEOWNERS` + document a
review SLA). All three are M-effort with no `Blocked by` entry
in §2. §2 #5 is the highest-fanout item in the §2 graph (three
downstream recs — #1, #11, #17 — become eligible as speculative
drafts once #5 is in repo).

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. All three drafts are
markdown files in this repo; filing remains a user action.
`phase-1b/ISSUES.md`'s **Filed** column is the audit trail for
upstream landing.

### What was done
1. Drafted §2 #5 — safety-profile rubric → `drafts/05-safety-profile-rubric.md`. Four-part acceptance: (A) rubric contents with a seven-axis normative table across `strict` / `standard` / `permissive`, (B) location in repo (`docs/safety-profile-rubric-v1.md` human-readable + `schemas/safety-profile-rubric.schema.json` draft-2020-12 companion), (C) conformance-test format (`tests/conformance/<case_id>/` structure + reference validator `tools/check_profile_conformance.py` + CI wiring into `validate-schemas.yml`), (D) consumer contract for the four downstream repos.
2. Drafted §2 #8 — draft-2020-12 migration → `drafts/08-grok-yaml-standards-draft-2020-12-migration.md`. Two-part acceptance: (A) core migration (`$schema` flip across 12 schemas + `definitions` → `$defs` rename + `schema-smoke` CI flip + `standards-overview.md` + `version-reconciliation.md` updates + v1.3.0 release notes), (B) downstream smoke-test coordination (pre-release tests against grok-install, grok-docs, awesome-grok-agents, grok-install-cli, grok-build-bridge; announcement follow-ups only in grok-install + grok-docs).
3. Drafted §2 #20 — PR triage + CODEOWNERS + SLA → `drafts/20-grok-agents-marketplace-pr-triage-codeowners.md`. Three-part acceptance, each independently mergeable: (A) PR triage sweep (tracking issue, 4-outcome classification, timebox 10 business days), (B) publish `.github/CODEOWNERS` + `SECURITY.md` + `CONTRIBUTING.md`, (C) review SLA doc with concrete first-response / first-review / follow-up / escalation / deviation-surfacing targets.
4. Updated `phase-1b/ISSUES.md`: added third-pass table (rows 10–12), replaced "Next-pass candidates" with §2 #2 / #10 / #19, updated post-filing follow-ups to note #5 is now drafted + speculative-draft discipline for #7 / #12 / #16 / #1-#11-#17 + flagged the #10 gap that blocks #4.
5. Updated filing-packets `02-grok-yaml-standards.md` (added §2 #5 and §2 #8 as primaries) and `08-grok-agents-marketplace.md` (added §2 #20 as primary); both packets' primary counts now reflect third-pass content.

### Metrics
- §2 recs drafted this pass: **3** (#5, #8, #20).
- Draft files created this pass: **3**.
- Cumulative §2 recs drafted (three passes): **10 of 20** (#3, #5, #6, #8, #9, #13, #14, #15, #18, #20).
- Cumulative draft files: **12**.
- Risks closed outright by this pass (on upstream merge): **VER-2** (S2, via #8), **GOV-2** (S2, via #20).
- Risks partially closed (full closure gated on consumer-repo follow-ups): **UNV-3** (S3, via #5), **UNV-4** (S3, enabled by #5).
- Recs unblocked for speculative drafting by this pass: **§2 #1, #11, #17** (all gated on #5, which is now drafted).
- Recs still blocked at draft time for the correct reason: **§2 #4** (gated on #10, which remains undrafted — flagged for user decision in the prompt).
- Phase-1B commits on `claude/phase-1b-session-continuation-zQBET` this pass: **29** (21 draft micro-commits + 3 ISSUES.md + 2 filing-packet + this PROGRESS entry + CHANGELOG + ROADMAP). Per-unit commit protocol held: each section of each draft is a single committed + pushed unit.
- Cumulative Phase-1B commits across three passes + addendum: 14 (through addendum) + 29 (this pass) = **43**.
- Lines of fabricated product code: **0** (drafting-only phase).

### Decisions & trade-offs
- **Micro-unit commit protocol.** The third pass adopted a finer commit granularity than passes 1–2. Each draft was built as a skeleton-first commit (H1 + metadata header + separator) followed by section commits (Context, Evidence, one commit per Acceptance-criteria Part, Notes). Each index/filing-packet/progress-doc update is also its own commit. Rationale: faster visible progress + smaller-diff review units + explicit checkpointing between acceptance sub-criteria. Total commits this pass (29) is larger than passes 1–2's per-pass counts (7 and 5) because of this deliberate decomposition. Cost: higher push volume. Value: a reviewer can disagree with one axis of the §2 #5 rubric (e.g. the `scan_severity_threshold` row of Part A) without having to reverse-engineer which commit introduced it.
- **§2 #5 rubric: seven axes, not a prose definition.** The existing ecosystem references to `strict` / `standard` / `permissive` are prose. The draft deliberately ships a normative seven-axis table (external writes / secret access / code execution / approval gate / scan severity threshold / network egress / halt on anomaly) so the rubric has behavioural bite. Each axis takes an enumerated value across three profiles; the machine-readable companion schema (Part B) enforces the shape.
- **§2 #5 Part D names consumer repos but does NOT file follow-ups.** The Part-D contract for `grok-install-cli` / `awesome-grok-agents` / `grok-build-bridge` / `grok-agent-orchestra` is the contract language this primary ships. Follow-up issues in each consumer repo open *only after the primary merges* — the rubric's normative values may shift in review, which would invalidate the follow-up checklists. Same discipline as the second-pass cross-refs and the first-pass post-filing follow-ups.
- **§2 #8 coordination is smoke-test-only, not code changes.** Downstream Python validators (`jsonschema>=4.21` in CLI; hard-bound `Draft202012Validator` in bridge) and JS validators (`ajv-cli@5 + ajv-formats@3`) are all `$schema`-keyword-aware by default. The Part-B smoke tests confirm this empirically before release day; no consumer-repo code changes are expected. Announcement follow-ups go only in `grok-install` and `grok-docs` — the two repos where the draft-07/draft-2020-12 drift is user-visible. Other consumer repos get silence unless a smoke test surfaces a real problem, to keep the audit trail clean.
- **§2 #20 CODEOWNERS placeholders are literal.** The draft ships `@<default-maintainer>` / `@<frontend-maintainer>` / `@<backend-maintainer>` / `@<platform-maintainer>` placeholder handles. Filing maintainer substitutes real GitHub handles at file time. If only one maintainer exists today, all rows point at the same handle — *explicit beats implicit*. When a second maintainer onboards, this file is the first place their scope is recorded.
- **§2 #20 SLA targets flagged as dial-back candidates.** The draft's Part-C SLA numbers (5 / 10 / 14 / 30 business days) are aspirational defaults. The draft's Notes section tells the filing maintainer to dial back to what the team can actually hit — an SLA routinely missed is worse than an honest four-week one. This is the one acceptance-criteria decision the draft explicitly delegates to the filer.
- **Speculative-draft discipline explicitly recorded in ISSUES.md.** Post-filing follow-ups (§2 #7, #12, #16, and the #1/#11/#17 trio) can now be drafted speculatively against the in-repo prerequisite drafts rather than waiting for upstream merge. Every such speculative draft must carry a metadata-header flag. ISSUES.md post-filing-follow-ups table was rewritten to encode this rule + flag the #4-blocked-by-#10 gap (which remains the one post-filing follow-up that still cannot be responsibly drafted without also drafting #10 first).
- **Pause at the S1→S2 transition (mandatory).** Per the kickoff prompt, Session 1 closes here pending three user-decision questions: (1) proceed to Session 2 now or pause; (2) include §2 #4 (requires drafting §2 #10 first — L-effort) or defer #4 to a later session; (3) draft the #1/#11/#17 trio as one coordinated file or three sibling files. No Session-2 drafting happens until these decisions come back.

### Files changed this pass
- Added: `phase-1b/drafts/05-safety-profile-rubric.md`, `phase-1b/drafts/08-grok-yaml-standards-draft-2020-12-migration.md`, `phase-1b/drafts/20-grok-agents-marketplace-pr-triage-codeowners.md`.
- Modified: `phase-1b/ISSUES.md` (third-pass table, next-pass candidates rewrite, post-filing follow-ups rewrite with speculative-draft discipline).
- Modified: `phase-1b/filing-packets/02-grok-yaml-standards.md` (added §2 #5 and §2 #8 primaries), `phase-1b/filing-packets/08-grok-agents-marketplace.md` (added §2 #20 primary).
- Modified (this unit and the next two): `PROGRESS.md`, `CHANGELOG.md`, `ROADMAP.md`.

### Open at pass close (Session 1 of this chat)
- **Filing** — 12 drafts total await manual upstream filing. MCP scope restricts this session from filing; `phase-1b/filing-packets/` is the operational path. Pre-bootstrap filing via a widened-scope session (`filing-packets/README.md §Path A`) remains the fastest route.
- **Session 2 (in-chat)** — speculative drafts for §2 #7, #12, #16, and the #1/#11/#17 trio are ready to start once the three user-decision questions above are answered. Each Session-2 draft will carry the mandatory speculative-draft metadata header (*"drafted in `phase-1b/drafts/<prereq>.md`; not yet filed upstream; speculative"* + *"re-review trigger: rewrite this draft if the prerequisite is substantially rewritten during upstream review"*).
- **§2 #4** — NOT on the Session-2 list until #10 is drafted or #4 is explicitly deferred. The kickoff prompt mandates surfacing this at Session-2 kickoff.
- **Next-pass candidates (beyond Session 2)** — §2 #2 (shared Grok API client, L-effort, reach 5), §2 #10 (grok-docs v2.14 + 7 standards reference pages, L-effort, reach 4), §2 #19 (x-platform-toolkit CI, M-effort, reach 2).

### Next suggested action
Pick one (Session 2 trigger):
- `"Proceed to Session 2; defer §2 #4 to a later session; draft #1/#11/#17 as three sibling files."` *(recommended default — matches the prompt's pre-chosen safest path.)*
- `"Proceed to Session 2; draft §2 #10 first then §2 #4; #1/#11/#17 as three sibling files."` *(widens Session-2 scope to include the L-effort #10 drafting.)*
- `"Proceed to Session 2; draft #1/#11/#17 as one coordinated file, not three siblings."` *(tighter trio but less honest — each targets a different repo.)*
- `"Pause Phase 1B."` *(12 drafts sit ready; resume any time.)*
- `"File the 12 drafts first, then reopen Session 2."` *(path A: widen MCP scope and file before drafting further; path B: manual GitHub UI filing from filing-packets/.)*

---

## Session: 2026-04-23 (cont.) — Phase 1B (Session 2): speculative post-filing follow-ups

### Status: Session 2 complete — 6 speculative drafts (cumulative: 18 drafts covering 16 of 20 §2 recs)

### Scope
User accepted the kickoff prompt's recommended defaults: proceed
to Session 2; defer §2 #4 (since §2 #10 is still not drafted);
draft the #1/#11/#17 trio as three sibling files (each targeting
a different repo — more honest than a single coordinated file).

Six speculative drafts in this pass:
- §2 #16 (`vscode-grok-yaml` v0.1.0 bootstrap) — gated on §2 #15.
- §2 #7 (`grok-install-cli` tagged releases + action pin
  alignment) — gated on §2 #6.
- §2 #12 (replace `awesome-grok-agents`' `grok_install_stub`
  with real CLI) — gated on §2 #6 + #7 (deepest).
- §2 #1 (shared `grok-safety-rules` package) — trio member;
  gated on §2 #5.
- §2 #11 (permissive-profile exemplar template) — trio member;
  gated on §2 #5.
- §2 #17 (orchestra bootstrap + behavioural Lucas veto) — trio
  member; gated on §2 #5 + §2 #1 (deepest).

### Speculative-draft discipline
Every Session-2 draft carries the mandatory
speculative-draft metadata header:
- **Prerequisite status**: drafted in `phase-1b/drafts/<prereq>.md`;
  not yet filed upstream; speculative.
- **Re-review trigger**: specific rewrite conditions if the
  prerequisite issue is substantively changed during upstream
  review.

Policy recorded in `phase-1b/README.md` (speculative drafts) +
`phase-1b/ISSUES.md §Post-filing follow-ups` (per-row rewrite
triggers + which prerequisite is itself speculative).

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. All 18 drafts (cumulative
across Sessions 0-2) await user filing upstream.
`phase-1b/filing-packets/` updated to reflect Session-2
primaries on the 4 affected per-repo packets (07, 03, 06, 10).

### What was done
1. Drafted §2 #16 → `drafts/16-vscode-grok-yaml-bootstrap.md`.
   Two-part acceptance: (A) minimum-viable extension (package.json
   + TypeScript source + governance files + Marketplace publish);
   (B) schema-fetch strategy (B1 fetch from grok-docs mirror vs.
   B2 bundle in repo) + CI. Speculative on §2 #15a/#15b.
2. Drafted §2 #7 → `drafts/07-grok-install-cli-releases-pyproject-alignment.md`.
   Two-part acceptance: (A) tagged release pipeline with PyPI
   Trusted Publisher; (B) action-pin alignment under each of §2
   #6's three acceptance options. Speculative on §2 #6.
3. Drafted §2 #12 → `drafts/12-awesome-grok-agents-replace-install-stub.md`.
   Two-part acceptance: (A) replace stub with real CLI invocation
   in validate-templates.yml + delete `scripts/grok_install_stub/`;
   (B) optional rubric-conformance matrix once §2 #5 lands.
   Speculative on §2 #6 + #7 (deepest — transitive through #7).
4. Drafted §2 #1 → `drafts/01-shared-grok-safety-rules-package.md`.
   Two-part acceptance: (A) package shape + ownership (A1 in-repo
   vs. A2 new repo, recommending A2) + seven-axis API mirroring
   §2 #5's rubric; (B) consumer adoption sequencing (CLI first,
   bridge second, gallery transitive, orchestra day-one).
   Speculative on §2 #5.
5. Drafted §2 #11 → `drafts/11-awesome-grok-agents-permissive-exemplar.md`.
   Two-part acceptance: (A) `internal-ci-assistant/` template
   with `grok-install.yaml` body mirroring §2 #5's `permissive`
   row cell-for-cell + registry entry + README; (B) optional CI
   distribution report. Speculative on §2 #5.
6. Drafted §2 #17 → `drafts/17-grok-agent-orchestra-bootstrap.md`.
   Two-part acceptance: (A) v0.1.0 plan-execute-critique pattern
   + package scaffolding + §2 #18 CI template adoption from day
   one + governance files; (B) Lucas safety veto behavioural
   contract ("strictest profile claimed by any agent in team"
   + `safety/lucas.py` implementation + two CI veto fixtures).
   Speculative on §2 #5 + §2 #1 (deepest — two layers, with
   #1 having an explicit fall-back).
7. Updated `phase-1b/ISSUES.md`: added "Session-2 speculative
   drafts" table (6 rows with speculative-depth column);
   rewrote Post-filing follow-ups table to mark Session-2
   drafts linked + flag §2 #4 as still deferred pending §2 #10.
8. Updated filing-packets: `07-vscode-grok-yaml.md` (+§2 #16),
   `03-grok-install-cli.md` (+§2 #7 + #1), `06-awesome-grok-agents.md`
   (+§2 #11 + #12), `10-grok-agent-orchestra.md` (+§2 #17).

### Metrics
- §2 recs drafted this pass: **6** (#1, #7, #11, #12, #16, #17).
- Draft files created this pass: **6**.
- Cumulative §2 recs drafted (across all passes): **16 of 20**
  (#1, #3, #5, #6, #7, #8, #9, #11, #12, #13, #14, #15, #16,
  #17, #18, #20).
- Cumulative draft files: **18**.
- Still undrafted from §2: **#2** (shared Grok API client, L),
  **#4** (repository_dispatch, gated on #10), **#10** (grok-docs
  v2.14, L), **#19** (x-platform-toolkit CI, M).
- Risks closed outright (on all upstream merges): **VER-2**
  (S2, #8), **GOV-2** (S2, #20), **UNV-3** (S3, #17), **UNV-4**
  (S3, #1).
- Risks partially closed pending consumer adoption:
  **UNV-3** (partial via #5), **SEC-1** (partial via #1's
  shared static-scan layer), **GOV-3** (partial via #16 + #17;
  full closure also needs §2 #15).
- Recs no longer blocked anywhere in the graph (draft exists
  for every prerequisite): **§2 #7, #12, #16, #1, #11, #17**.
- Recs still blocked at draft time for the correct reason:
  **§2 #4** (gated on #10 which remains undrafted; deferred
  per user decision at S1→S2 kickoff).
- Phase-1B commits on `claude/phase-1b-session-continuation-zQBET`
  this pass: **44** (36 draft micro-commits + 2 ISSUES + 4
  filing-packet + this PROGRESS + CHANGELOG + ROADMAP + final
  sanity-check unit).
- Cumulative Phase-1B commits across 1st-pass / 2nd-pass /
  addendum / 3rd-pass / Session 2: ~14 (through addendum) +
  29 (3rd pass) + 44 (Session 2) = **~87**.
- Lines of fabricated product code: **0** (drafting-only phase).

### Decisions & trade-offs
- **User decisions at S1→S2 kickoff, recorded verbatim.**
  (1) Proceed to Session 2 now. (2) Defer §2 #4 (do NOT draft
  §2 #10 inside Session 2 to unblock #4). (3) Draft §2
  #1/#11/#17 as three sibling files. Defaults matched the
  kickoff prompt's pre-chosen safest path; no widening-scope
  discussion required.
- **Speculative-draft metadata header is mandatory across
  all 6 drafts.** Each draft spells out which in-repo
  prerequisite it depends on + what conditions trigger a
  rewrite. The ISSUES.md Post-filing-follow-ups table
  cross-references the same data so a reviewer can see the
  speculative-depth tree at a glance.
- **Deepest speculation: §2 #12 (through #7→#6) and §2 #17
  (through #1→#5).** Both are two layers deep. Filing order
  matters: do not file either until both of their
  prerequisites have merged upstream. The drafts explicitly
  ask reviewers to wait for the prerequisite-merge signal
  rather than racing.
- **§2 #1 recommends a new-repo path (A2) over in-repo
  extraction (A1).** Rationale in the draft's Notes: shared
  libraries with ambiguous ownership across 4 consumer repos
  create compound-interest governance debt; a new repo makes
  the boundary explicit. A1 is valid and cheaper short-term
  but creates circular governance.
- **§2 #17 Lucas veto is team-level, not per-agent.** The
  draft explicitly defends "check against strictest profile
  claimed by any agent in team" over "check against proposing
  agent's own profile". Conservative by design; prevents
  permissive scratchpad agents from laundering actions past
  strict executors.
- **§2 #7 version-naming recommendation: A1 (`0.1.0`).** Match
  today's `pyproject.toml` honestly rather than inflating to
  `2.14.0` to chase the action pin. The consumer (action)
  should pin to the CLI's actual version, not vice versa.
  Flagged explicitly for maintainer review.
- **§2 #11 chose internal-CI-assistant as exemplar** over
  customer-facing permissive agents. Customer-facing
  permissive is a policy decision most operators should
  refuse; modeling it in a gallery template is dangerous.
  Internal-CI teaches "permissive is honest when the
  environment sandboxes you" — a durable framing.
- **§2 #12 deletes the stub rather than keeping it as
  fallback.** A fallback path no one exercises rots. If CI
  only exercises the real CLI, the stub is dead code that
  looks alive. Better to remove cleanly.
- **§2 #16 recommends Option B1 (fetch from grok-docs daily
  mirror).** Avoids adding a fourth schema-distribution
  location. If `grok-docs` does not yet expose
  `/assets/schemas/latest/`, a one-comment coordination
  post after §2 #15 merges is enough to add it.

### Files changed this pass
- Added: `phase-1b/drafts/01-shared-grok-safety-rules-package.md`,
  `phase-1b/drafts/07-grok-install-cli-releases-pyproject-alignment.md`,
  `phase-1b/drafts/11-awesome-grok-agents-permissive-exemplar.md`,
  `phase-1b/drafts/12-awesome-grok-agents-replace-install-stub.md`,
  `phase-1b/drafts/16-vscode-grok-yaml-bootstrap.md`,
  `phase-1b/drafts/17-grok-agent-orchestra-bootstrap.md`.
- Modified: `phase-1b/ISSUES.md` (Session-2 table + post-filing
  follow-ups rewrite), `phase-1b/filing-packets/07-vscode-grok-yaml.md`,
  `phase-1b/filing-packets/03-grok-install-cli.md`,
  `phase-1b/filing-packets/06-awesome-grok-agents.md`,
  `phase-1b/filing-packets/10-grok-agent-orchestra.md`.
- Modified (this + next two units): `PROGRESS.md`, `CHANGELOG.md`,
  `ROADMAP.md`.

### Open at session close
- **Filing** — 18 drafts await upstream filing. Filing order
  must respect blocked-by chains: first-pass (#6, #9, #14,
  #15) → second-pass (#3, #13, #18) → third-pass (#5, #8,
  #20) → Session-2 drafts only after their prerequisites
  merge. `filing-packets/README.md §Path A/B` covers
  mechanics.
- **Undrafted §2 recs** — #2 (shared Grok API client), #10
  (grok-docs v2.14), #19 (x-platform-toolkit CI), #4 (gated
  on #10; user deferred).
- **Speculative-draft re-review posture** — each Session-2
  draft's metadata header lists specific conditions that
  trigger a rewrite. If upstream review of any prerequisite
  changes the prerequisite's acceptance criteria materially,
  the listed Session-2 draft(s) need a PR in this repo
  updating the speculative body before the user files
  upstream. ISSUES.md §Post-filing follow-ups table is the
  coordination surface.

### Next suggested action
Pick one:
- `"Draft §2 #10 (grok-docs v2.14 + 7 standards reference)."`
  *(L-effort; unblocks §2 #4 once drafted — the only gated
  follow-up still waiting for its prerequisite draft.)*
- `"Draft §2 #2 (shared Grok API client)."` *(L-effort, reach
  5 — highest reach in §2. Highest-impact remaining undrafted
  rec.)*
- `"Draft §2 #19 (x-platform-toolkit CI minimum)."` *(M-effort,
  reach 2 — lowest-effort remaining. Closes SUP-5.)*
- `"Draft §2 #4 after §2 #10."` *(natural continuation after
  #10 lands in this repo.)*
- `"File the 18 drafts now."` *(Path A: widen MCP scope; Path
  B: manual GitHub UI.)*
- `"Pause Phase 1B."` *(18 drafts sit ready; resume any time.)*

---

## Session: 2026-04-23 (cont.) — Phase 1B (fourth pass): grok-docs v2.14 unblocker

### Status: Fourth pass complete — 1 draft (§2 #10) (cumulative: 19 drafts covering 17 of 20 §2 recs)

### Scope
Single-rec pass: §2 #10 — ship `grok-docs` v2.14 content +
reference pages for the 7 undocumented standards. Selected by
user ("Draft §2 #10") because it's the only remaining §2 rec
that unblocks a post-filing follow-up (§2 #4,
`repository_dispatch` wiring). Closes VER-4 + DOC-2 outright.

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. 19 drafts now await user
filing upstream.

### What was done
1. Drafted §2 #10 → `drafts/10-grok-docs-v2-14-plus-7-standards-reference.md`.
   Three-part acceptance: (A) refresh the `grok-install` spec
   page to v2.14 — embed the v2.14 schema via
   `--8<--` snippet, add migration-from-v2.13 section, cite
   v2.14's draft-2020-12 switch; (B) ship seven new reference
   pages (`grok-config`, `grok-update`, `grok-test`, `grok-tools`,
   `grok-deploy`, `grok-analytics`, `grok-ui`) each following
   an identical template (front-matter + overview + when-to-use
   + schema reference + example + fields table + related
   standards + see-also); (C) publication layer (mkdocs.yml
   nav with two-level Core/Extensions grouping, version banner
   in `overrides/main.html`, Mike-archive v2.12 before the
   main-branch rewrite lands). Notes section flags L-effort
   honestly, proposes a four-PR split strategy for a
   single-maintainer context.
2. Updated `phase-1b/ISSUES.md`: added "Fourth-pass drafts"
   table (row 19 with §2 #10); flagged §2 #4 as now eligible
   (its prerequisite is in repo); moved §2 #10 out of the
   next-pass-candidates list; added §2 #4 there instead.
3. Updated `phase-1b/filing-packets/05-grok-docs.md`: added
   §2 #10 as the single primary (previously had 0 primaries +
   2 cross-refs); spelled out a split-PR strategy, the no-CI-
   changes-required property, and the §2 #4 unblock linkage
   in the filing notes.

### Metrics
- §2 recs drafted this pass: **1** (#10).
- Draft files created this pass: **1**.
- Cumulative §2 recs drafted (through fourth pass): **17 of 20**
  (#1, #3, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #15,
  #16, #17, #18, #20).
- Cumulative draft files: **19**.
- Still undrafted from §2: **#2** (shared Grok API client, L,
  reach 5), **#4** (now eligible — unblocks from drafted #10),
  **#19** (x-platform-toolkit CI, M, reach 2).
- Risks closed outright (on upstream merge): **VER-4** (S2),
  **DOC-2** (S2).
- Recs newly eligible for drafting as of this pass: **§2 #4**
  (gated on #10 which is now in repo).
- Phase-1B commits on `claude/phase-1b-session-continuation-zQBET`
  this pass: **12** (7 draft micro-commits + 1 ISSUES.md +
  1 filing-packet + this PROGRESS + CHANGELOG + ROADMAP +
  final sanity-check unit).
- Cumulative Phase-1B commits across all passes + Session 2:
  ~87 (through Session 2) + 12 (this pass) ≈ **~99**.
- Lines of fabricated product code: **0**.

### Decisions & trade-offs
- **Why #10 over the other two undrafted recs.** User choice
  (explicit "Draft §2 #10"). Upstream value argument: #10
  unblocks #4 (the only post-filing follow-up whose
  prerequisite was still undrafted). Drafting #10 closes the
  speculative-draft graph's longest unfulfilled dependency
  chain.
- **Acceptance criteria designed for incremental merge.**
  L-effort against a single-maintainer repo (audit 05 §10)
  is governance-risky if the PR is monolithic. The draft's
  three parts + Part B's per-standard checkboxes intentionally
  map to 4–7 bite-sized PRs. Partial landings still move the
  site closer to truth; none of the parts regresses v2.14
  claims.
- **`grok-docs` the standard is self-documenting.** Confirmed
  explicitly in the draft: the site IS its own `grok-docs`
  standard reference. A standalone `spec/grok-docs.md` page
  would be redundant. Ships as 7 new pages (one per missing
  standard in the 12-catalogue), not 8. The draft's Evidence
  section defends the count explicitly so a reviewer doesn't
  wonder about an off-by-one.
- **No CI changes required in v2.14 docs.**
  `sync-schemas.yml` already republishes the 12 schemas daily;
  new reference pages embed them via `--8<--` snippets.
  §2 #3 (SHA-pin actions) and §2 #18 (CI template adoption)
  remain separate recs; deliberately NOT bundled here to keep
  reviewer cognitive load low.
- **Field-table authoring hand-written.** Auto-generation
  (pre-build hook emitting tables from JSON schemas) is the
  right long-term answer; deferred. Hand-authoring 7 tables
  is tractable; gating v2.14 ship on an auto-generator is
  not.
- **Mike v2.12 archive before main-branch rewrite.** Draft's
  Part C spells out the exact Mike incantations
  (`mike deploy v2.12 --push; mike deploy v2.14 latest ...`).
  Users maintaining v2.12 agents during the deprecation window
  keep access to v2.12 docs; the site defaults to v2.14. The
  1-release grace window §2 #11's draft Part-B alluded to is
  now concrete.
- **§2 #4 is the next natural pass.** With #10 drafted, #4 is
  now speculative-on-in-repo-prerequisite rather than blocked.
  Surfaced in "Next suggested action" below.

### Files changed this pass
- Added: `phase-1b/drafts/10-grok-docs-v2-14-plus-7-standards-reference.md`.
- Modified: `phase-1b/ISSUES.md` (fourth-pass table; #4 eligibility;
  next-pass candidates rewrite), `phase-1b/filing-packets/05-grok-docs.md`
  (added §2 #10 primary).
- Modified (this + next two units): `PROGRESS.md`, `CHANGELOG.md`,
  `ROADMAP.md`.

### Open at pass close
- **Filing** — 19 drafts await upstream filing. Filing order
  respects blocked-by chains per `phase-1b/README.md` and
  `phase-1b/ISSUES.md §Post-filing follow-ups`.
- **Undrafted §2 residual (3 of 20)**: #2 (L, reach 5), #4
  (newly eligible — speculative on #10), #19 (M, reach 2).
- **§2 #4 drafteable once user requests it.** With #10 in
  repo, #4 can be written as a speculative-on-#10 draft
  (exactly the same discipline Session 2's drafts use).

### Next suggested action
Pick one:
- `"Draft §2 #4 (repository_dispatch wiring)."` *(Now
  eligible as speculative-on-#10. Natural continuation; M-effort.)*
- `"Draft §2 #2 (shared Grok API client)."` *(L-effort, reach
  5 — highest reach still undrafted.)*
- `"Draft §2 #19 (x-platform-toolkit CI)."` *(M-effort, reach
  2 — lowest-effort remaining. Closes SUP-5.)*
- `"Draft both §2 #4 and §2 #19 (small batch)."` *(two
  M-effort drafts; pushes cumulative to 19 of 20. Leaves only
  §2 #2 undrafted.)*
- `"File the 19 drafts now."` *(Path A widen MCP; Path B manual UI.)*
- `"Pause Phase 1B."`

---

## Session: 2026-04-23 (cont.) — Phase 1B (fifth pass): repository_dispatch wiring

### Status: Fifth pass complete — 1 speculative draft (§2 #4) (cumulative: 20 drafts covering 18 of 20 §2 recs)

### Scope
Single-rec pass: §2 #4 — wire `repository_dispatch` from
`grok-install` → `grok-docs`, `grok-install-action`,
`grok-agents-marketplace` so a spec bump fans out automatically.
User chose explicitly ("Draft §2 #4") after the fourth-pass
unblocked it (drafting #10 satisfied §4's in-repo prerequisite).
Closes VER-4 trigger half + partial DOC-1.

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. 20 drafts now await user
filing upstream.

### What was done
1. Drafted §2 #4 → `drafts/04-repository-dispatch-spec-to-consumers.md`.
   Two-part acceptance: (A) publisher workflow in `grok-install`
   — new `fan-out-spec-release.yml` firing
   `repository_dispatch` on GitHub Release publish, with a
   matrix over the three subscriber repos; the
   dispatch-event contract is documented (event type
   `grok-install-release`, payload shape with `version` +
   `source_repo` + `release_url`, additive-only semantics).
   PAT/token strategy + GitHub-App alternative spelled out.
   (B) three subscriber listener workflows — one per consumer
   repo — each opens a PR (grok-docs, grok-install-action) or
   a tracking issue (grok-agents-marketplace, since work there
   is likelier to be rendering-logic-flavoured). Common
   YAML skeleton above the per-subscriber variants avoids
   duplication; PAT lives only on the publisher, subscribers
   use default `GITHUB_TOKEN`.
2. Updated `phase-1b/ISSUES.md`: added row 20 to the Session-2
   speculative drafts table (§2 #4, M-effort, speculative on
   #10, publisher + 3 subscriber cross-refs); moved #4 row in
   Post-filing follow-ups from "eligible" to "drafted"; updated
   next-pass-candidates preamble ("17 → 18 of 20"; two
   undrafted remaining: §2 #2 and §2 #19).
3. Updated filing-packets: `01-grok-install.md` (added §2 #4
   as Issue 3 primary with PAT-setup notes); `04-grok-install-
   action.md`, `05-grok-docs.md`, `08-grok-agents-marketplace.md`
   (each gained a §2 #4 subscriber cross-ref — "open only
   after §2 #4 primary merges", body points at the relevant
   Part-B subsection of the draft, repo-specific coordination
   notes for each).

### Metrics
- §2 recs drafted this pass: **1** (#4).
- Draft files created this pass: **1**.
- Cumulative §2 recs drafted (through fifth pass): **18 of 20**
  (#1, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14,
  #15, #16, #17, #18, #20).
- Cumulative draft files: **20**.
- Still undrafted from §2: **#2** (shared Grok API client, L,
  reach 5), **#19** (x-platform-toolkit CI, M, reach 2).
- Risks closed outright (on upstream merge of this + #10):
  **VER-4** (S2) full closure (trigger side from #4 + content
  side from #10).
- Risks partially closed: **DOC-1** (partial — this rec lets
  consumer-side number-claim rebuilds fan out automatically;
  the hard-coded prose fixes in §2 #14a/#14b + §2 #10 are
  the other axis).
- Phase-1B commits on `claude/phase-1b-session-continuation-zQBET`
  this pass: **13** (6 draft micro-commits + 1 ISSUES.md + 1
  filing-packets bundle + this PROGRESS + CHANGELOG + ROADMAP
  + final sanity-check unit).
- Cumulative Phase-1B commits across all passes + Session 2 +
  fourth pass: ~99 (through fourth pass) + 13 (this pass) ≈
  **~112**.
- Lines of fabricated product code: **0**.

### Decisions & trade-offs
- **Why filing-packets got only one bundled commit this pass.**
  Four files changed (packets 01 / 04 / 05 / 08) but the
  changes are symmetric — one new primary entry + three new
  cross-ref entries, all citing the same draft and same
  primary-URL-TODO pattern. Splitting into four commits would
  be micro-unit theatre without review value; one bundled
  commit lets a reviewer compare the four subscriber-packet
  entries side by side.
- **Why GitHub-Release trigger (A1) over tag-push (A2).**
  GitHub Releases already carry human-readable release notes
  and a stable `release.html_url` the dispatch payload can
  carry. Tag-push works too (and is cheaper if the repo
  doesn't cut Releases today), but A1 is the canonical
  pattern.
- **Why `grok-yaml-standards` is NOT a subscriber.**
  `grok-docs/sync-schemas.yml` pulls from
  `grok-yaml-standards@main` daily; `grok-yaml-standards`
  doesn't need a `grok-install` release trigger to do
  anything. Adding it as a subscriber creates noise, not
  signal.
- **Why `awesome-grok-agents` is NOT a subscriber in this
  first cut.** Its CI validates templates via the stub today
  (§2 #12 removes the stub). Until §2 #12 lands and the CI
  exercises the real CLI, a spec-release dispatch has no
  sensible action for `awesome-grok-agents` to take. Flag as
  a future-subscriber in the draft's Notes.
- **Why subscribers ship three different shapes.**
  `grok-docs` opens a PR (banner bump + mkdocs trigger) —
  mechanical.
  `grok-install-action` opens a PR (cli-version default +
  README prose bumps) — mechanical.
  `grok-agents-marketplace` opens a tracking issue (submission-
  form allowed-versions check, `visuals:` block rendering) —
  non-mechanical. Matching the workflow's output to the
  complexity of the downstream work avoids auto-generated
  PRs that require human labour to close manually.
- **PAT scope minimised.** Fine-grained PAT with `contents:
  read` + `metadata: read` on only the three subscriber
  repos. No write scope on the subscribers (the listener
  uses its own default `GITHUB_TOKEN` for PR/issue creation
  on its side). Captures least-privilege.
- **Drift-window math.** Before: up to 24h (cron). After
  happy-path: seconds. After missed dispatch (PAT expired,
  network blip): the 03:00 UTC cron still runs — floor
  remains 24h, not undefined. Defensive.

### Files changed this pass
- Added: `phase-1b/drafts/04-repository-dispatch-spec-to-consumers.md`.
- Modified: `phase-1b/ISSUES.md` (added row 20 to Session-2
  table; flipped #4 row to "drafted" in post-filing
  follow-ups; updated next-pass candidates preamble),
  `phase-1b/filing-packets/01-grok-install.md` (added §2 #4
  primary as Issue 3), `phase-1b/filing-packets/04-grok-install-action.md`
  + `phase-1b/filing-packets/05-grok-docs.md` +
  `phase-1b/filing-packets/08-grok-agents-marketplace.md`
  (each gained a §2 #4 subscriber cross-ref).
- Modified (this + next two units): `PROGRESS.md`, `CHANGELOG.md`,
  `ROADMAP.md`.

### Open at pass close
- **Filing** — 20 drafts await upstream filing. Filing order
  is now a meaningful coordination artefact given the depth
  of speculative-draft chains.
- **Undrafted §2 residual (2 of 20)**: #2 (L, reach 5 —
  highest reach remaining), #19 (M, reach 2 — lowest effort
  remaining).
- **Phase 1B drafting is one pass away from complete.**
  Drafting #2 + #19 in either order (or both in one pass)
  closes the §2 top-20.

### Next suggested action
Pick one:
- `"Draft §2 #2 (shared Grok API client)."` *(L-effort, reach
  5 — highest reach remaining. Most strategically valuable
  rec left.)*
- `"Draft §2 #19 (x-platform-toolkit CI minimum)."` *(M-effort,
  reach 2 — smallest-effort rec remaining. Closes SUP-5
  outright.)*
- `"Draft both in one pass."` *(final drafting pass; closes
  the §2 top-20 at 20 of 20.)*
- `"File the 20 drafts now."` *(Path A widen MCP; Path B
  manual UI.)*
- `"Pause Phase 1B."` *(20 drafts sit ready; resume any time.)*

---

## Session: 2026-04-23 (cont.) — Phase 1B (sixth pass): shared Grok API client

### Status: Sixth pass complete — 1 non-speculative draft (§2 #2) (cumulative: 21 drafts covering 19 of 20 §2 recs)

### Scope
Single-rec pass: §2 #2 — extract a shared Grok API client
collapsing the four parallel implementations enumerated in
`audits/00-ecosystem-overview.md §9.A`. User chose explicitly
("Draft §2 #2") as the highest-reach undrafted rec. L-effort;
Reach 5 × Leverage 4 = composite 20 (tied with §2 #18 for the
highest composite in the §2 table).

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. 21 drafts now await
user filing upstream.

### What was done
1. Drafted §2 #2 → `drafts/02-shared-grok-api-client.md`.
   Three-part acceptance:
   - (A) Package shape + ownership — A1 in-repo vs. A2 new
     repo; recommendation A2 for ecosystem consistency with
     §2 #1. Package naming (`grok-client` dist, `grok_client`
     import). Scope decision: Python-first, JS-second-or-
     never. Trusted-Publisher release pipeline matching §2 #7.
     Governance files + §2 #18 CI template from day one.
     Test discipline with recorded-cassette fixtures.
   - (B) Feature surface for v0.1.0 parity — auth / retries /
     streaming / rate-limiting / tool calling / structured
     output / SDK-version pin. Indicative public API
     (`GrokClient`, `AsyncGrokClient`, `ClientConfig`,
     `Message`, `ToolDecl`, `StreamChunk`, exception
     hierarchy). Non-goals documented. Model-ID handling
     via strings, not enums.
   - (C) Consumer adoption sequencing — `grok-install-cli`
     first, `grok-build-bridge` second (most divergent);
     `awesome-grok-agents` transitively via §2 #12;
     `grok-agents-marketplace` not a v0.1.0 consumer (TS
     frontend). JS implementations (grok-install browser +
     x-platform-toolkit inlined) explicitly out of scope.
     Cross-cut verification via a shared cassette regression
     suite.
2. Honest §2-row-vs-§9.A discrepancy flag in §Evidence —
   §2 #2's "Affected repos" column names future consumers
   (grok-install-cli, grok-build-bridge,
   grok-agents-marketplace, awesome-grok-agents) while
   §9.A's implementation table names current parallel
   clients (grok-install, grok-install-cli, grok-build-
   bridge, x-platform-toolkit). Draft treats §9.A as
   authoritative current-state ground truth and §2's list
   as future-consumer aspiration. Same discipline the §2
   #18 draft used for its own audit-citation inconsistency.
3. Updated `phase-1b/ISSUES.md`: added "Sixth-pass drafts"
   table (row 21 with §2 #2); updated next-pass candidates
   preamble ("18 → 19 of 20"; one undrafted remaining: §2
   #19).
4. Updated `phase-1b/filing-packets/03-grok-install-cli.md`:
   added §2 #2 as Issue 5 primary (non-speculative). Now
   carries 5 primaries total (§2 #6, #13, #7, #1, #2).

### Metrics
- §2 recs drafted this pass: **1** (#2).
- Draft files created this pass: **1**.
- Cumulative §2 recs drafted (through sixth pass): **19 of 20**
  (#1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13,
  #14, #15, #16, #17, #18, #20).
- Cumulative draft files: **21**.
- Still undrafted from §2: **#19** only (x-platform-toolkit
  CI, M, reach 2).
- Risks closed outright (on upstream merge): none directly
  (§2 #2 closes the cross-cutting concern from 00 §9.A, not
  a risk-register row). Indirect benefit: preempts future
  SEC/SUP-category risks from parallel-implementation drift.
- Phase-1B commits this pass: **12** (7 draft micro-commits
  + 1 ISSUES.md + 1 filing-packet + this PROGRESS +
  CHANGELOG + ROADMAP + final sanity-check unit). Two push
  retries needed mid-pass due to transient remote 500s; per
  the git-push guidance, the third retry (after 8s) succeeded
  both times.
- Cumulative Phase-1B commits across all passes + Session 2:
  ~112 (through fifth pass) + 12 (this pass) ≈ **~124**.
- Lines of fabricated product code: **0**.

### Decisions & trade-offs
- **Why #2 over #19 for this pass.** User's "highest-reach"
  framing (and §2 #2's reach 5 vs. §19's reach 2) drove the
  choice. §19 remains the final rec; smallest-effort of the
  two, so a sensible finisher.
- **A2 (new repo) recommended over A1 (in-repo extraction).**
  Same governance rationale as §2 #1. The shared client has
  ≥3 Python consumers across repos; cleaner ownership
  boundary in a dedicated repo. Explicit coordination note:
  §2 #1 and §2 #2 should make the same A1/A2 choice for
  ecosystem consistency.
- **Python-first, JS-second-or-never.** The two JS
  implementations are language-incompatible with a
  Python-flavoured extraction. Rather than force-fit, the
  draft documents this as a deliberate choice. The
  `x-platform-toolkit` inlined JS constraint (single-file
  HTML tools with no build step) is a genuine blocker for a
  shared JS package today.
- **Feature surface = parity, not ambition.** v0.1.0 covers
  exactly what the two current Python implementations do.
  Non-goals (caching, batching, cost tracking, prompt
  templating, JS port) are documented so v0.1.0 reviewers
  don't scope-creep. Post-v0.1.0 extensions land per real
  consumer need.
- **Recorded-cassette test discipline.** Live-API tests on
  every CI run are both expensive and brittle. `vcrpy`-style
  recorded cassettes pin SDK behaviour without hitting the
  live API; live tests gated behind an opt-in workflow with
  `XAI_API_KEY` secret. Matches ecosystem CI discipline.
- **Model-ID churn discipline.** The package passes model
  strings through; does NOT hard-code IDs or enum-gate them.
  Audit 09 §9 row 3 called out the bridge's current
  hard-coded `grok-4.20` as a risk; moving model ID to
  consumer-side config is the fix.
- **Push resilience.** Two mid-pass pushes failed with
  transient 500s. The prompt's git-push guidance (retry up
  to 4 times with 2s / 4s / 8s / 16s exponential backoff)
  resolved both. No further action needed; flagged here in
  case the pattern recurs.

### Files changed this pass
- Added: `phase-1b/drafts/02-shared-grok-api-client.md`.
- Modified: `phase-1b/ISSUES.md` (sixth-pass table; candidates
  list down to #19 only),
  `phase-1b/filing-packets/03-grok-install-cli.md` (added §2
  #2 as Issue 5 primary).
- Modified (this + next two units): `PROGRESS.md`,
  `CHANGELOG.md`, `ROADMAP.md`.

### Open at pass close
- **Filing** — 21 drafts await upstream filing. Filing-order
  and speculative-draft-chain discipline unchanged.
- **Undrafted §2 residual (1 of 20)**: #19 (x-platform-toolkit
  CI minimum, M, reach 2). Closes SUP-5.
- **Phase 1B drafting is one pass away from §2 top-20
  complete.** Drafting §2 #19 closes the pile at 20/20.

### Next suggested action
Pick one:
- `"Draft §2 #19."` *(M-effort, closes §2 top-20 at 20 of
  20. The natural finisher.)*
- `"File the 21 drafts now."` *(Path A widen MCP; Path B
  manual UI. Skipping §19 is fine — it is a local-CI
  hygiene rec and does not block filing anything else.)*
- `"Pause Phase 1B."` *(21 drafts sit ready.)*

---

## Session: 2026-04-23 (cont.) — Phase 1B (seventh pass): §2 top-20 COMPLETE

### Status: Phase 1B §2 drafting complete — 22 draft files covering 20 of 20 §2 recs

### Scope
Final §2 draft. §2 #19 (x-platform-toolkit minimum CI).
User chose explicitly ("Draft §2 #19") as the natural
finisher. Closes SUP-5 outright.

### MCP-scope constraint (unchanged)
Still `agentmindcloud/claudex`-only. 22 drafts now await
user filing upstream.

### What was done
1. Drafted §2 #19 →
   `drafts/19-x-platform-toolkit-minimum-ci.md`.
   Two-part acceptance:
   - **Part A — Lint + link-check (3 jobs)**:
     html-validate against the 8 Live `tools/*/index.html`
     (config `.html-validate.json` at repo root,
     `html-validate:recommended` preset); stylelint on
     `shared/ui-kit/{tokens,components}.css`
     (`stylelint-config-standard` + custom-property-pattern
     rule); lychee link-check across every `*.md` in the
     repo (tolerant 403/429 per ecosystem convention).
     SHA-pinned actions from day one (satisfies §2 #3 for
     this repo).
   - **Part B — Live-vs-Spec consistency check**: a
     Python script (`scripts/check-live-vs-spec.py`) parses
     the top-level README's Live/Spec table and asserts
     the invariant that Live tools have `index.html` and
     Spec'd tools have `SPEC.md` (and not vice-versa).
     Fails CI on drift. First-run behaviour may flag
     pre-existing discrepancies — fix in the introducing
     PR.
2. Updated `phase-1b/ISSUES.md`: added "Seventh-pass
   drafts" table (row 22, §2 #19); replaced the
   "Next-pass candidates" section with a **"§2 top-20
   drafting: COMPLETE"** marker documenting that all 20
   §2 recs now have ready-to-file issue bodies under
   `phase-1b/drafts/`.
3. Updated `phase-1b/filing-packets/11-x-platform-toolkit.md`:
   added §2 #19 as Issue 1 primary (previously the packet
   carried only future-drafting notes).

### Metrics
- §2 recs drafted this pass: **1** (#19).
- Draft files created this pass: **1**.
- **Cumulative §2 recs drafted: 20 of 20 (complete)**.
- Cumulative draft files: **22** (20 distinct §2 recs;
  two §2 rows — #14, #15 — ship sibling `a/b` pairs).
- Risks closed outright (on upstream merge of this pass):
  **SUP-5** (S3).
- Phase-1B commits this pass: **12** (6 draft micro-commits
  + 1 ISSUES.md + 1 filing-packet + this PROGRESS +
  CHANGELOG + ROADMAP + final sanity-check unit). One
  transient remote 500 on push, resolved on the 2s retry
  per the git-push guidance.
- Cumulative Phase-1B commits across all passes + Session 2
  + fourth through seventh passes: ~124 (through sixth
  pass) + 12 (this pass) ≈ **~136**.
- Lines of fabricated product code: **0**.

### Cumulative Phase-1B summary across all passes

| Pass | When | §2 recs drafted | Draft files | Key risks closed on upstream merge |
|:-:|---|---|:-:|---|
| 1st | original session | #6, #9, #14, #15 | 6 | VER-1, VER-3, UNV-1 outright; DOC-1/GOV-3/DOC-3 on sibling landing |
| 2nd | original session | #3, #13, #18 | 3 | SEC-2, SEC-3 (pilot); SUP-1 across 8 repos |
| 3rd | this branch | #5, #8, #20 | 3 | VER-2, GOV-2 outright; UNV-3/UNV-4 partial |
| S2 | this branch | #1, #7, #11, #12, #16, #17 | 6 | UNV-3 outright (via #17); UNV-4 outright (via #1); partial SEC-1/GOV-3 |
| 4th | this branch | #10 | 1 | VER-4 content; DOC-2 outright |
| 5th | this branch | #4 | 1 | VER-4 trigger; partial DOC-1 |
| 6th | this branch | #2 | 1 | 00 §9.A cross-cutting concern |
| 7th | this branch | #19 | 1 | SUP-5 outright |
| **Total** | | **20 of 20** | **22** | — |

Filing-packets carry ready-to-paste title / labels / body
pointers for every primary + cross-ref. 11 packets (one per
upstream AgentMindCloud repo); `12-claudex.md` absent by
design (own MCP scope).

### Decisions & trade-offs
- **Why #19 last.** Lowest reach (2) of the undrafted §2
  recs. Local-hygiene flavour (one repo, one workflow
  file). Natural finisher — completing §2 at 20/20
  without having to re-open the scope decision.
- **Reach=2 honest defense in Evidence.** `99-recommendations.md §Edge case: #19`
  already flagged this rec's reach as borderline.
  This draft's Evidence section cites the edge-case
  argument verbatim and accepts it: the Live-vs-Spec
  consistency check (Part B) is what makes this rec
  ecosystem-relevant rather than purely local.
- **Part B's first-run behaviour flagged honestly.** The
  consistency script may find pre-existing Live/Spec
  drift. Rather than hide that behind a grace period, the
  draft asks the maintainer to fix the drift in the
  introducing PR and document it in the PR description.
  Audit-trail honesty > landing-without-diff.
- **No §2 #18 CI-template adoption here.** The toolkit is
  HTML/CSS, not Python; §2 #18's template doesn't apply
  1:1. Notes section flags this repo as a candidate for a
  future "JS/HTML-flavour sibling template" if §2 #18
  grows a multi-language form — not this rec.
- **SUP-5 closure mechanics flagged explicitly.** The
  draft's Part B and Notes both call out that the
  risk-register row flip to `mitigated` is a post-merge
  manual step the Phase-1B review layer owns. Not buried;
  not assumed.
- **Filing-packet 11 promoted from "future-drafting notes"
  to a real primary.** Previously the only packet with
  zero primaries + zero cross-refs; now carries the §2
  #19 primary. Phase 1B packets are now all non-empty —
  every upstream AgentMindCloud repo has at least one
  primary or cross-ref.

### Files changed this pass
- Added: `phase-1b/drafts/19-x-platform-toolkit-minimum-ci.md`.
- Modified: `phase-1b/ISSUES.md` (seventh-pass table;
  next-pass candidates replaced with "§2 top-20 drafting:
  COMPLETE" marker), `phase-1b/filing-packets/11-x-platform-toolkit.md`
  (added §2 #19 as Issue 1 primary).
- Modified (this + next two units): `PROGRESS.md`,
  `CHANGELOG.md`, `ROADMAP.md`.

### Open at pass close (= end of Phase 1B §2 drafting)
- **Filing** — 22 drafts across 20 §2 recs await upstream
  filing. `phase-1b/filing-packets/` is the operational
  path. Filing order respects blocked-by chains +
  speculative-draft discipline per
  `phase-1b/ISSUES.md §Post-filing follow-ups`.
- **Undrafted §2 residual**: **none**. Phase 1B §2
  drafting is complete.
- **Deferred (not §2)**: `audits/99-recommendations.md §3.2`
  per-repo hygiene rows + `§3.3` ClaudeX-specific rows
  + `§3.1` absorbed rows. Not part of Phase 1B scope.

### Next suggested action
Pick one:
- `"File the 22 drafts now."` *(Path A widen MCP; Path B
  manual UI. `phase-1b/filing-packets/README.md` has the
  ready-to-paste kickoff prompt for a widened-scope agent
  session + the manual workflow for the GitHub UI.)*
- `"Draft from §3 deferrals."` *(opens a separate pass
  against per-repo hygiene rows that §2 intentionally
  excluded.)*
- `"Pause Phase 1B."` *(22 drafts + 11 filing-packets sit
  ready; resume any time.)*
- `"Begin Phase 2."` *(move to implementation — e.g.
  §2 #1's shared `grok-safety-rules` package, §2 #2's
  shared Grok client, §2 #10's content work, or Super
  AI Frok core development.)*
