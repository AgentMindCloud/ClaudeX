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
---

# Super AI Frok — implementation log

Living log of what shipped and why (Frok Python package). Most recent entries first.

## 2026-04-24 — Phase 5 §32: retry-show-reverse

**Shipped** ``frok retry show --reverse`` — flips the
chosen sort order so operators can surface the OPPOSITE
end of any ranking. With `--sort-by attempts --reverse`,
the "which case has the fewest attempts" question becomes
a one-command answer; with `--sort-by sleep --reverse`,
"which case uses the least backoff". Combined with
`--limit N`, the N LEAST-interesting cases surface — useful
for debugging "why isn't this case getting any retry
budget?"

* **API extension** — `format_retry_report(...,
  reverse=False)`. When True: sort is applied
  unconditionally (even with default `sort_by='worst'`,
  which is normally a conditional sort), then the sorted
  list is reversed, then `--limit` truncates. Defaults
  preserve §31 byte-for-byte.
* **Plain mode** — restructured the sort / truncate
  path so the three operations compose cleanly:
  `sort → reverse → truncate`. Truncation happens AFTER
  reverse so `--reverse --limit N` yields the N tail
  cases of the natural order, not the top N displayed
  in flipped order.
* **Grouped mode** — `--reverse` reverses within each
  group; the group ORDER (size desc) stays unchanged.
  Different dimensions: group order is "which cluster
  is biggest"; within-group order is "operator's chosen
  lens into that cluster". Composing them produces a
  natural "biggest cluster, scanned bottom-up" view.
* **CLI** — `--reverse` boolean, no validation. Passes
  through to `format_retry_report`. `--json` still
  passes the raw payload (markdown-only feature, same as
  every other display flag since §26).
* **Default False preserves §31** — locked in by a
  byte-identical comparison test.

**Verification.** `python3 -m pytest -q` → 873 passed in 3.25s
(11 new). Unit tests cover: default False byte-identical
to no-flag, --reverse flips name sort, --reverse flips
attempts sort, --reverse with default `worst` sorts then
flips (least-worst first), `--reverse --limit 1` picks
the least-worst case, within-group reverse preserves
group order, composes with `--only-errors`. CLI: parser
default False, flag sets True, end-to-end with
`--sort-by name --reverse`, --json passthrough.

**Decisions / trade-offs.**
* Truncate AFTER reverse, not before. `--reverse
  --limit 5` means "5 least-worst cases", which is the
  tail of the natural sort. Truncating first would give
  "top 5 worst, flipped for display" — same cases, just
  different order, which is a different (and usually
  wrong) answer.
* `--reverse` without explicit `--sort-by` forces the
  default worst-first sort (normally conditional).
  Nothing to reverse without a sorted base; making the
  flag imply the sort matches operator intent ("flip my
  output") better than silently no-op'ing.
* Group order (size desc) stays untouched. Reversing it
  would say "smallest cluster first", which serves no
  common operator question. Group order is a separate
  dimension; keeping it orthogonal to within-group sort
  maximises composition flexibility.
* Boolean flag, not a KEY value. Operators don't need
  fine control over "reverse just the within-group
  order but not the group order"; either dimension has
  one sensible reverse, not a matrix of choices.

**This closes the retry-show display toolkit** at 8
composable flags (§25-§32). Further extensions should
pivot to different surfaces; the current flag set covers
the common triage, diff, cluster, and ranking needs.

## 2026-04-24 — Phase 5 §31: retry-show-sort-by

**Shipped** ``frok retry show --sort-by KEY`` — five
new sort keys alongside the default `worst`, letting
operators investigate retry behaviour through whichever
lens fits the question they're asking. The default
preserves §27's worst-first ordering exactly; any other
key triggers an unconditional sort.

* **Sort keys** (`SORT_KEYS` registry in
  `retry_show.py`):
  * `worst` — default; existing `_worst_first_key`
    (failing → ratio → attempts → name).
  * `attempts` — most raw attempts first; "what
    retried hardest".
  * `ratio` — highest attempts/budget ratio first;
    "who's against the wall budget-wise".
  * `name` — alphabetical; predictable scan / diff-
    friendly listing.
  * `error` — alpha by last-attempt error string,
    no-error cases collected at the end; "show me
    similar failure modes adjacent".
  * `sleep` — highest total `sleep_before_ms` first;
    "which cases are eating my wall-clock budget on
    backoff alone".
* **API extension** — `format_retry_report(...,
  sort_by="worst")`. Default preserves §27 (sort only
  when `--limit` truncates); non-default triggers
  unconditional sort in plain mode AND inside
  `--group-by-error` groups. Unknown keys raise
  `ValueError` so library callers see the bad-input
  early.
* **CLI flag** — `--sort-by KEY` with `argparse.
  choices` validation. Unknown keys produce the
  standard argparse error (exit 2) — no custom
  CliError needed because the choices list is
  authoritative.
* **Composition** —
  * With `--limit N`: sort then truncate (the chosen
    sort decides which cases survive).
  * With `--group-by-error`: chosen sort applies
    INSIDE each group; the GROUPS themselves still
    order by size desc (group order is a different
    dimension).
  * With `--only-errors` / `--min-attempts`: filters
    run first, sort applies to the surviving cases.
* **Backward compatibility** — every existing test
  passed without modification. The "default `worst`
  preserves §27" invariant is locked in by an
  explicit byte-identical comparison test.

**Verification.** `python3 -m pytest -q` → 862 passed in 3.04s
(15 new). Unit tests cover: default `worst` byte-
identical to no-flag, `worst` + `--limit` picks worst-
first, `name` alphabetical, `attempts` most-first,
`ratio` highest-first, `error` alpha with no-error
last, `sleep` highest-total-first, sort-then-truncate
under `--limit`, sort-within-group under `--group-by-
error`, unknown key raises ValueError. CLI: parser
default `worst`, accepts each valid choice, rejects
unknown via argparse SystemExit, end-to-end alpha
sort, --json passthrough preserves submission order.

**Decisions / trade-offs.**
* Default `worst` is conditional sort (only under
  `--limit`); non-default keys are unconditional. The
  asymmetry serves backward compatibility: §27's
  behaviour was "no sort unless truncating", and
  changing that for `--sort-by=worst` callers would
  surprise. Operators who want unconditional worst-
  first ordering can still pass `--sort-by worst
  --limit 999999` to force the sort without
  truncating.
* `argparse choices` rather than runtime CliError
  validation. The choices list is the spec; argparse
  surfaces the available options in the error message
  for free, which is better UX than a custom
  "invalid sort key" message.
* `error` sort puts no-error cases LAST, not first.
  Operators sorting by error are looking for patterns
  in errored cases; scorer-only failures (no
  observation error) are the "weird" bucket and
  cluster more naturally at the end of the list.
* `sleep` uses TOTAL across attempts, not max. The
  question operators ask is "which case cost me the
  most cumulative backoff"; max sleep would surface
  the case with the longest single sleep, which is a
  different (and less common) signal.
* All sort keys end with `(case_name, repeat)` as
  the deterministic tiebreak. Two runs with identical
  data produce byte-identical markdown — text-diff
  / snapshot-test friendly across every sort key.
* `name` sort breaks the case-name → repeat
  hierarchy: same-name cases with different repeats
  end up adjacent. That's the desired behaviour
  ("show me everything for case X together").
* Sort applies WITHIN groups under `--group-by-
  error`, not BETWEEN them. Group order (size desc)
  is a different signal than within-group order
  (operator's chosen lens); collapsing them would
  reduce flexibility. Operators wanting size-sorted
  groups + named-sorted within use
  `--group-by-error --sort-by name`.

**Next suggested action:** `Extend Phase 5 §32 with a
\`frok retry show --reverse\` flag that flips the
chosen sort order. Useful when operators want "the
cases with the LEAST attempts" or "least sleep" —
debugging "why isn't this case getting any retry
budget?" Composes with --sort-by (reverses any chosen
key) and --limit (truncates after reverse). Default
unset preserves the natural sort order from §31.
Markdown-only.`

## 2026-04-24 — Phase 5 §30: retry-show-only-errors

**Shipped** ``frok retry show --only-errors`` — the
"what's broken right now" triage view. Drops every
passing case (both Clean passes AND retried-but-passed)
from the detail surface, leaving only the current run's
failures. The shortest path from "the suite ran" to
"here are the cases that need attention".

* **API extension** — `format_retry_report(...,
  only_errors=False)`. When True, `retried_or_failed` is
  filtered to `passed=False` cases only and
  `clean_passes` is forced to empty. Defaults preserve
  §29 behaviour exactly.
* **Filter precedence** — `only_errors` runs FIRST in
  the filter chain, before `min_attempts`, before
  grouping, before limit truncation. Operators chaining
  flags get a coherent pipeline: failures → ≥N attempts
  → cluster → truncate.
* **Indicator always fires** — `_Showing failing cases
  only._` appears whenever the flag is set, even on
  suites with zero failures. Same rationale as §29's
  `--min-attempts` indicator: filter operators looking
  at filtered output need to know the filter applied
  even when the data happens to be all-pass.
* **Summary unchanged** — top-level totals (Cases,
  Passed, Failed, Retried cases, Attempts/Budget)
  still reflect the FULL run. Display filters never
  rewrite the truth bloc.
* **"Only in previous" untouched** — same scope rule
  as `--min-attempts` (§29). Vanished cases' verdicts
  belong to a different run; filtering them by current-
  run intent would cross-contaminate the diff signal.
* **CLI** — single `--only-errors` boolean (no value,
  no validation). `--json` ignores it (markdown-only,
  same as the other display flags).
* **Composition note** — combined with
  `--group-by-error`, every group contains only
  failing cases (clean clusters); combined with
  `--limit`, the N truncation operates over the
  filtered failure set; combined with
  `--min-attempts N`, the filter chain is
  `only_errors → min_attempts`, so "show only failing
  cases that took ≥ 3 attempts" is one invocation.

**Verification.** `python3 -m pytest -q` → 847 passed in 3.07s
(12 new). Unit tests cover: only_errors drops Clean
passes + retried-but-passed (keeps both single-attempt
fail and retried-fail), default False is byte-identical
to no-flag, indicator fires even with zero failures,
composition with group_by_error (clusters only failing),
composition with limit (truncates failing-only), filter
chain ordering with min_attempts (only_errors first),
Only-in-previous untouched under compare_to, summary
reflects full run. CLI: parser default False, flag sets
True, end-to-end markdown, --json passthrough.

**Decisions / trade-offs.**
* Strict interpretation of "only errors" — drops
  retried-but-passed too, not just Clean passes. The
  flag name promises "errors only"; keeping retried-
  passes would have been more like "no-clean-passes".
  Operators wanting context for cases that retried
  successfully use `--min-attempts 2` instead.
* Filter chain order: `only_errors → min_attempts →
  group → limit`. Each filter narrows the surface;
  later filters see the already-narrowed view. Running
  in this order makes "only failing cases that
  retried, grouped by error, top 3 clusters" a one-
  liner with predictable behaviour.
* No special CLI validation. The flag is a boolean —
  argparse handles parsing. No "requires --retry > 0"
  check because the filter is meaningful even on
  zero-retry runs (showing only failing cases is
  always a valid request).
* Indicator regardless of whether anything got
  dropped. Same reasoning as §29's `--min-attempts`:
  silent no-op behaviour would let filtered views
  masquerade as unfiltered, confusing operators
  reading saved markdown reports without context.
* Doesn't touch summary bloc. The flag's intent is
  "give me a focused view"; the summary's intent is
  "tell me the run's truth". Two cleanly-separated
  contracts that compose without conflict.
* "Only in previous" stays unfiltered. Vanished cases
  carry signal regardless of their previous-run
  verdict (a vanished pass might mean a test was
  removed; a vanished fail might mean a fix landed).
  Filtering by "current-run failure" would lose both
  signals.

**Next suggested action:** `Extend Phase 5 §31 with a
\`frok retry show --sort-by KEY\` flag that overrides
the default worst-first sort with operator-chosen
keys: \`attempts\`, \`ratio\`, \`name\`, \`error\`,
\`sleep\`. Useful when operators investigating a
specific signal (e.g. "show me cases sorted by total
backoff sleep — the ones costing me wall-clock time")
want a different lens. Composes with --limit (sort
THEN truncate) and --group-by-error (sort applies
within groups). Default 'worst' preserves §27.
Markdown-only.`

## 2026-04-24 — Phase 5 §29: retry-show-min-attempts

**Shipped** ``frok retry show --min-attempts N`` — an
attempt-count filter that drops cases below the
threshold from the detail sections. Closes a specific
signal/noise problem: when operators allocate a generous
retry budget (e.g. `--retry 10`) but only a handful of
cases actually use it, the Clean passes list balloons
with "passed first try, budget irrelevant" entries that
dilute the interesting retry activity.

* **API extension** — `format_retry_report(...,
  min_attempts=N)`. When set and > 1, drops any case
  (from both `retried_or_failed` and `clean_passes`)
  whose attempt count is below N, then proceeds to
  grouping / limiting with the filtered lists. N=1 is
  explicitly a no-op (matches "no filter") to make
  the flag idempotent against the default.
* **Indicator line** — when the filter is active
  (`min_attempts > 1`), an italicised
  `_Filtered to cases with >= N attempts._` line sits
  between the summary bloc and the first detail
  section. Unlike the `--limit` indicator (which only
  fires when truncation actually drops content), the
  filter indicator always fires when set — operators
  need to know the filter applied, even on runs where
  every case happened to survive.
* **Precedence** — filter runs BEFORE grouping and
  BEFORE limiting. A group count from `--group-by-
  error --min-attempts 3` reflects "clusters of cases
  that actually retried", which is what operators
  want; running the filter after would mean the group
  sizes include cases that aren't even displayed.
* **"Only in previous" untouched** — the diff-derived
  section's per-case attempt counts come from a
  DIFFERENT run (the comparison side). Filtering them
  by the current-run threshold would cross-contaminate
  two different run shapes. Keeping that section
  unfiltered is the right move; operators who want to
  filter the previous run can run `retry show` on it
  directly with the same flag.
* **Summary bloc unchanged** — totals (Cases, Passed,
  Failed, Retried cases, Attempts/Budget) still
  reflect the FULL run, not the filtered subset. The
  filter is a display concern; the summary is a run-
  state truth. Operators see "50 cases, 48 passed"
  even if only 5 are detailed.
* **CLI validation** — `--min-attempts < 1` →
  `CliError` ("must be >= 1"). N=0 would be a no-op
  (every case has at least 1 attempt if it has an
  entry) but operators typing `0` almost always meant
  `1`; hard-erroring catches the confusion.

**Verification.** `python3 -m pytest -q` → 835 passed in 3.16s
(11 new). Unit tests cover: N=2 drops 1-attempt cases
from both retried_or_failed and clean_passes, N=1 is
byte-identical to default, N=5 empties detail but
preserves summary, filter-before-grouping (group sizes
reflect filtered cases), filter-before-limit ("X of Y"
indicator matches filtered total), Only-in-previous
untouched under --compare-to. CLI: parser default
None, end-to-end filtered markdown, N=0 rejected,
--json passthrough preserves raw payload.

**Decisions / trade-offs.**
* Filter applies to Clean passes too. An operator
  running `--min-attempts 3` is saying "don't show me
  anything with < 3 attempts"; keeping Clean passes
  (which are always 1-attempt) visible would
  undermine the flag's intent.
* `--min-attempts 1` is a no-op rather than an error.
  1 is the default-like value; treating it as a bug
  would surprise operators who pass it explicitly
  (e.g. from a script that always sets the flag).
* Summary reflects the full run, not filtered totals.
  The report's top bloc is a truth-claim about what
  happened; filtering is a view concern. Two
  different lenses on the same data.
* Indicator fires always-when-active, not just when
  cases got dropped. Operators looking at a filtered
  report need to know the filter applied even when
  the data happened to all pass through —
  silently-no-op behaviour would let filtered views
  masquerade as unfiltered.
* N=0 is a hard error. Every case has >= 1 attempt
  (otherwise it wouldn't be in the report), so N=0
  is identical to N=1 in effect. The ambiguity
  isn't worth allowing; operators who typed 0 almost
  always meant 1 and the error catches the fat-finger.
* Filter precedence is filter → group → limit. The
  clustering / truncation logic should see a coherent
  view of the filtered data; running filter AFTER
  grouping would mean group sizes mismatch the
  displayed rows, which is confusing.

**Next suggested action:** `Extend Phase 5 §30 with a
\`frok retry show --only-errors\` flag (shorthand for
\`--min-attempts 2\` restricted to failing-or-retried
cases only — drops Clean passes regardless of attempt
count). Useful when operators just want the
"what's broken right now" view without the bulleted
pass list noise. Composes with --group-by-error
(groups only the failing-or-retried subset), --limit
(truncates the still-interesting cases), and
--compare-to (per-case suffixes still apply).
Markdown-only.`

## 2026-04-24 — Phase 5 §28: retry-show-group-by-error

**Shipped** ``frok retry show --group-by-error`` — a
clustering knob that collapses retried/failing cases
sharing the same last-attempt error into a single
section. Closes the "40 identical tables" problem that
§27's `--limit` only partially solved: on large-suite
outages, operators want to see "`RuntimeError: 429`
affected 40 cases" as one section, not scroll through
40 single-row tables.

* **API extension** — `format_retry_report(...,
  group_by_error=False)`. When True, retried-or-failed
  cases are bucketed by `_last_attempt_error(case)`.
  Scorer-only failures (no observation.error on the
  last attempt) land in a dedicated bucket labelled
  `(no error — scorer failure or passing retry)` — the
  explicit label keeps "why is this case here?"
  answered at a glance.
* **Group sort** — largest group first, alpha tiebreak
  on the error string for determinism. Within each
  group, cases use §27's `_worst_first_key` so the
  intra-group ordering matches the plain-mode ordering.
* **Per-group table** — four columns: Case, Repeat,
  Attempts/Budget, Verdict. Narrower than the per-
  attempt table because the interesting signal is
  "which cases are in this cluster", not the specific
  sleep / attempt-by-attempt timeline (which is still
  in the raw JSON for operators who need it).
* **`--limit` semantic pivots under grouped mode** —
  plain mode truncates cases; grouped mode truncates
  groups. The indicator changes to "`N of M error
  groups (largest-first)`" so operators always know
  what dimension got cut. Cases within a group stay
  whole — truncating both would hide the clustering
  signal the flag exists to surface.
* **Clean passes + Only-in-previous unchanged** — both
  sections still surface independent of
  `--group-by-error`. Clean passes aren't "cases with
  errors" (there's no error to group by); Only-in-
  previous is a diff-derived section that doesn't
  interact with current-run error shapes.

**Verification.** `python3 -m pytest -q` → 824 passed in 3.09s
(17 new). Unit tests cover: same-error cases group
together, different errors split, scorer-only failures
in dedicated bucket, groups sorted by size desc, alpha
tiebreak for equal-size groups, worst-first ordering
within group, Clean passes still bucketed, Only-in-
previous still surfaces, no-flag preserves per-case
tables. `--limit` interaction: truncates groups not
cases, limit=0 shows indicator + no groups, limit ==
total no indicator. CLI: parser default False, flag
sets True, end-to-end rendering, `--limit` composition,
`--json` still passthrough.

**Decisions / trade-offs.**
* Group by last-attempt error, not first or
  intermediate. The final error is the one that made
  the retry loop give up (or the only error on a
  single-attempt case); earlier errors are noise in a
  clustering view. Operators who want the full
  attempt-by-attempt view can drop `--group-by-error`.
* Explicit sentinel label for no-error cases, not
  `None` in markdown. A `(no error)` bucket visible in
  the section list is much clearer than a missing
  entry or a `null` string. Scorer failures are a real
  cluster shape and deserve their own named bucket.
* `--limit` pivots semantics under grouped mode rather
  than applying to cases. The flag's value to operators
  is "don't show me everything"; under grouping, the
  things getting "everything" counted are groups, not
  cases. A flag that truncates one dimension under one
  flag and the other dimension under a different flag
  would be surprising.
* Per-group table is four columns, not the full five-
  column per-attempt table. Grouping is a summary
  mode; showing sleep_before_ms per attempt inside
  each group would balloon the output and defeat the
  purpose. The raw JSON still carries the full data.
* Alpha tiebreak on error string for same-size groups.
  Determinism matters for text diffs between runs; the
  alternative (dict-insertion order) would produce
  run-dependent output, which breaks snapshot tests.
* Sort cases within each group using `_worst_first_key`
  from §27 rather than a different ordering (e.g.
  alpha). The sort key is the tool's canonical "most
  interesting case" ordering — using it everywhere
  (plain mode detail, grouped mode within-group,
  future per-report ranking) keeps operators'
  expectations aligned.

**Next suggested action:** `Extend Phase 5 §29 with a
\`frok retry show --min-attempts N\` filter that drops
any case whose attempt count is below N from the detail
sections. Useful to hide the "passed first try but
budget > 1" noise when operators have allocated a
generous retry budget and want to focus only on cases
that actually used it. Composes with --group-by-error
(filters before grouping) and --limit (filters before
truncating). Markdown-only.`

## 2026-04-24 — Phase 5 §27: retry-show-limit

**Shipped** ``frok retry show --limit N`` — a truncation
knob for the single-report triage view. Closes the "wall
of text" problem on large suites: when a transient
outage makes 40 cases fail with the same `429`
`RuntimeError`, operators want to see the 5 worst and
decide, not scroll through 40 nearly-identical tables.

* **Sort key** — `_worst_first_key(case)` returns
  `(passed, -ratio, -attempts, name)`. Failing cases
  come first (False < True in Python), then highest
  attempts/budget ratio (most retry pressure), then
  most raw attempts (tiebreaks identical ratios —
  5/5 outranks 1/1), then case name (deterministic
  across runs, stable ordering for diff-friendliness).
* **API extension** — `format_retry_report(..., limit=N)`.
  When `limit < total_detailed`, sorts retried-or-
  failed cases and truncates to the top N. Single-
  attempt passes ("Clean passes" list) and "Only in
  previous" are untouched — both are already terse and
  operators may want the full picture there.
* **Truncation indicator** — a single italicised line
  `_Showing N of M retried/failing cases (worst-first)._`
  sits between the summary bloc and the first detail
  section when truncation fires. Operators immediately
  know the detail list isn't complete.
* **`--limit 0`** is allowed (surfaces just the summary
  + indicator, no detail tables). Useful for a "quick
  glance" invocation where operators want the counts
  but not the tables. Negative values are rejected as
  `CliError`, matching the §16/§18 validation shape.
* **CLI flag** — `--limit N` on `show`. `--json` passes
  through verbatim (markdown-only feature, same as
  `--compare-to`). Composes cleanly with `--compare-to`:
  the sort key works on the primary report's attempts,
  so "worst 5 since yesterday" shows the 5 cases most
  in need of attention right now, independent of the
  previous run's shape.

**Verification.** `python3 -m pytest -q` → 807 passed in 2.92s
(16 new). Unit tests cover: sort key failing-before-
passing, higher-ratio-first-among-same-passed, more-
attempts-tiebreaks-equal-ratios, name-is-final-
tiebreak, limit<total shows indicator, limit==total
/ limit>total no indicator, limit=0 suppresses detail
tables but keeps summary + clean passes, truncation
picks the worst case (failing) when limit=1 over
retried passes, limit+compare-to preserves Only-in-
previous. CLI tests cover: parser default None,
end-to-end truncation indicator, negative CliError,
--json + --limit passes through primary verbatim,
--limit + --compare-to composition.

**Decisions / trade-offs.**
* Failing cases always first, regardless of ratio. A
  failing 1/1 is more important than a passing 5/5 —
  the terminal verdict wins. Ratio-only sort would
  have buried the actual failures under caught-late
  retries.
* Attempts/budget ratio over raw attempts as the
  primary tiebreaker. A case using 5/5 of its budget
  is in more trouble than a case using 5/10 even if
  the absolute numbers match — ratio normalises
  against the budget operators actually allocated.
* Raw attempts as secondary tiebreaker. When two
  cases hit 100% (exhausted budget), the one with the
  bigger budget tried harder and is more diagnostic.
* Name as final tiebreaker, not undefined order.
  Deterministic ordering means two runs with the
  same data produce byte-identical markdown — useful
  for text diffs and snapshot tests.
* Clean passes NOT truncated. Operators scanning a
  green suite may still want to confirm every case
  ran; the bulleted list is already terse enough that
  40 bullets isn't a problem (compared to 40 full
  tables).
* "Only in previous" NOT truncated. The vanished-case
  list is diagnostic gold ("wait, which case did we
  delete?"); truncating it would hide data operators
  rarely see and always care about.
* `--limit 0` is valid. Symmetric with `--retry 0`,
  `--timeout-s 0`, `--jobs 0`-adjacent flags
  throughout Phase 5. Negatives are always bugs.
* Markdown-only. `--json` is passthrough of the raw
  payload; operators wanting truncated structured
  data should post-process the full JSON (every row
  is already tagged with the data the sort key needs).

**Next suggested action:** `Extend Phase 5 §28 with a
\`frok retry show --group-by-error\` flag that
collapses retried/failing cases sharing the same last-
attempt error string into a single "## Error: <error>"
section listing the affected cases. Mainly for large-
suite outages where 40 cases fail with the same
"RuntimeError: 429 Too Many Requests" — right now
each gets its own table; grouped, the operator sees
"429 affected 40 cases" as one line + the case names.
Composes with --limit: "show me the 3 biggest error
clusters."`

## 2026-04-24 — Phase 5 §26: retry-show-compare

**Shipped** ``frok retry show --compare-to PATH2`` — the
single-report triage view (§25) enriched with inline
pairwise comparison. Operators investigating a regression
used to need two commands (`retry show` for the detailed
view + `retry diff` for the regression signal); now one
command carries both.

* **API extension** — `format_retry_report` grows two
  keyword-only params: `compare_to` (second retry-report
  payload) and `compare_to_path` (surfacing in the
  summary bloc). Defaults `None` keep every existing
  call site byte-compatible; the §25 `retry show`
  behaviour is preserved when the flag isn't passed.
* **Header suffix** — per-case sections gain a
  "(was N/M, PASS/FAIL)" suffix when the case existed
  in the previous report (matched by `(case, repeat)`),
  or "(NEW — not in previous)" when it's brand new.
  Readers see both current and historical state on one
  line without scrolling to a separate diff.
* **Comparison summary section** — between the top-
  level summary bloc and the per-case detail, a
  `## Comparison` block summarises the pair diff:
  attempts grew/shrank counts, newly failing/passing,
  error-changed, only-in-previous/current, and the
  `regressed` boolean. Reuses §23's `diff_retry_reports`
  verbatim — no logic duplication.
* **"Only in previous" section** — cases present in the
  previous report but missing from the current one get
  a dedicated bulleted list at the bottom, with each
  entry's verdict + attempt ratio so operators can tell
  whether the vanished case was important (an
  operationally-critical failure) or benign (a removed
  passing test).
* **CLI flag** (`src/frok/cli/retry.py`) —
  `--compare-to PATH` on the `show` subcommand. Reuses
  the `_load_report` helper for the second file so
  error messages stay uniform across the retry
  subcommand group.
* **`--json` passthrough preserved** — when both
  `--json` and `--compare-to` are set, the output is
  still just the primary payload verbatim. The
  comparison is a markdown enrichment; operators
  needing structured diff data should use
  `frok retry diff`. This keeps the two subcommands'
  contracts cleanly separated.
* **`--fail-on-failure` unchanged** — still gates on
  the PRIMARY report's failures. Attempts growing vs
  previous with the current run still passing shouldn't
  fail CI; that's `retry diff --fail-on-regression`'s
  job if the operator wants it.

**Verification.** `python3 -m pytest -q` → 791 passed in 2.94s
(10 new). Unit tests cover: header suffix shows previous
attempts + verdict, new case marked "(NEW — not in
previous)" when previous is empty, comparison summary
counts grew/only-in-previous, "Only in previous" lists
vanished cases with verdict + ratio, source + compared-
to paths both appear in summary, no-compare leaves
output byte-identical to §25. CLI tests cover: end-to-
end suffix rendering, missing comparison file is
CliError, `--json` + `--compare-to` still passes through
primary verbatim (no `diff` or `compare_to_path` keys
added), `--fail-on-failure` gates on primary not on
regression.

**Decisions / trade-offs.**
* Reuse `diff_retry_reports` rather than re-implementing
  the pair diff. Keeps the two commands' semantics in
  lockstep; any future change to what "regressed"
  means flows to both through one code path.
* Header-suffix format `(was N/M, PASS/FAIL)` matches
  the header's own `N/M attempts PASS/FAIL` shape.
  Readers parse "new ratio, old ratio" left-to-right
  without context switching.
* "NEW — not in previous" for unmatched-in-previous
  cases. Leaving no suffix would look like an omission;
  explicit marking makes "this case is brand new" a
  positive signal rather than a missing-data question.
* `--json` + `--compare-to` doesn't merge the diff into
  the output. Two cleanly-separated contracts
  (`retry show --json` = raw payload; `retry diff
  --json` = structured diff) compose better than one
  fused contract with conditional fields.
* Reused `_load_report` on `args.compare_to` instead of
  adding a new loader. Error messages stay consistent —
  "`retry report not found`" reads the same whether the
  missing file is the primary or the comparison.
* Keep "Only in current" cases inline in the regular
  per-case sections (tagged "NEW") rather than a
  dedicated section. Operators scanning the report want
  new cases interleaved with the rest; vanished cases
  need a dedicated section because they CAN'T be
  interleaved (no current entry to slot them near).

**Next suggested action:** `Extend Phase 5 §27 with a
\`frok retry show --limit N\` flag that truncates the
per-case detail sections to the N worst cases (highest
attempts/budget ratio, or failing cases first). For
large suites where most failures share the same
transient error, the current output can sprawl; a
truncation flag lets operators scan the top-N worst
without piping through head/grep. Pairs with --compare-
to: "show me the 5 cases that got worst since
yesterday."`

## 2026-04-24 — Phase 5 §25: retry-show

**Shipped** ``frok retry show PATH`` — the single-report
triage view that completes the retry-report toolkit. The
four subcommands now cover every operator need:

* `frok run --retry-report PATH` — produces (§22)
* `frok retry diff A B` — compares two (§23)
* `frok retry summarize DIR` — series trend across many (§24)
* `frok retry show PATH` — pretty-prints one (§25, this)

* **Module** (`src/frok/evals/retry_show.py`) — one
  function: `format_retry_report(payload, *, path=None)`
  returning markdown. Top-level summary bloc (cases,
  passed, failed, retried cases, attempts/budget), per-
  case sections for retried OR failing cases with full
  attempt tables (attempt, passed, error, sleep_before_
  ms), and a terse "Clean passes" bulleted list for
  single-attempt passes so the output stays scannable on
  mostly-green suites.
* **CLI subcommand** (`src/frok/cli/retry.py`) — added
  `show` alongside `diff` and `summarize`:
  `frok retry show PATH [-o OUT] [--json]
  [--fail-on-failure]`. Reuses the §23 `_load_report`
  helper so error messages stay consistent across the
  subcommand group (missing file, malformed JSON, missing
  `cases` key all surface the same way).
* **`--json` passthrough** — unlike `retry diff --json`
  and `retry summarize --json` which emit STRUCTURED
  diff/summary data, `retry show --json` re-serialises
  the raw payload. The operator's intent with `show` is
  "what's in this file?" — passthrough matches it.
  (The raw and structured views are already distinct
  artifacts; no translation needed.)
* **`--fail-on-failure`** — exits 1 when any case's
  terminal verdict is failed. Useful when the retry-
  report is the only CI artifact and the producer didn't
  pass `--fail-on-regression`. Complements §24's
  `--fail-on-growing` and §23's `--fail-on-regression`.

**Verification.** `python3 -m pytest -q` → 781 passed in 2.98s
(16 new: 7 module + 9 CLI). Module tests cover: summary
bloc with/without source path, clean-passes bucketed list
(no full tables for single-attempt passes), retried case
gets full attempt table + sleep column, failing case has
`FAIL` header, empty cases list renders cleanly, mixed
report surfaces everything. CLI tests cover: parser
registration, clean-pass markdown, `--json` passthrough,
retried case end-to-end, `--fail-on-failure` returns 1
on any failure + 0 on all-pass, missing / malformed /
missing-cases CliError paths.

**Decisions / trade-offs.**
* Two buckets: retried-or-failed (full tables) and
  clean-passes (bulleted). A third "shrank" bucket
  doesn't exist because single-report view has nothing
  to compare against — shrinkage is a diff/summarize
  concept. Two buckets cover every single-report story:
  "something interesting happened" vs "nothing did."
* Clean-passes collapse to bullets, not tables. A
  1-row table with a single "yes" cell is pure noise
  for operators scanning a 50-case suite for problems.
  Bullets keep the happy path out of the way so the
  signal (retries, failures) dominates the screen.
* `--json` passes through verbatim, not a re-rendered
  summary. The single-report case doesn't need a
  summarised JSON — that's `retry summarize`'s job.
  Passthrough lets operators use `show --json` as a
  "validate this file parses" step in CI pipelines.
* Reuse `_load_report` from §23. Duplicating the
  loader would have diverged the error messages; one
  shared helper keeps the subcommand group's error
  surface uniform.
* Header format: `## PASS/FAIL: <case> (repeat R) —
  N/M attempts`. The ratio in the header surfaces
  budget utilisation at a glance without requiring the
  operator to read the table. `(repeat R)` makes multi-
  repeat suites unambiguous.
* Budget = 1 cases still show `N/M` (e.g. `1/1`) in
  the header. Keeps the header format consistent across
  all sections; operators never have to special-case
  reading the ratio.

**Next suggested action:** `Extend Phase 5 §26 with a
\`frok retry show --compare-to PATH2\` flag that renders
a single report WITH an inline "vs previous run" column
on each attempt table (e.g. "was 2/3 on 2026-04-22,
now 3/3"). One command gives the single-report triage
view + the pairwise regression signal; operators stop
needing to run \`retry show\` and \`retry diff\` in two
separate invocations for day-to-day investigation.`

## 2026-04-24 — Phase 5 §24: retry-summarize

**Shipped** ``frok retry summarize DIR`` — a longitudinal
trend view across a directory of retry-reports. §23's
pairwise diff catches point-in-time regressions; §24
catches the slow creep that pairwise diffs miss —
"attempts went 1 → 1 → 2 → 3 → 4 over two weeks" only
becomes visible when you look at the whole series.

* **Module** (`src/frok/evals/retry_summary.py`) — two
  functions: `summarize_retry_reports(directory)` and
  `retry_summary_to_markdown(summary)`. Directory walk
  uses lexicographic filename ordering, so the
  convention `YYYY-MM-DD.json` sorts chronologically for
  free without operators having to pass `--sort-by`.
* **Trend classifier** — per case, across the attempt
  series: `flat` (all equal), `growing` (monotonic non-
  decreasing with at least one rise), `shrinking`
  (monotonic non-increasing with at least one drop),
  `mixed` (some ups, some downs — the real flake signal).
  `None` entries (case didn't exist in that report) are
  skipped during classification so late-arriving cases
  aren't penalised by short histories.
* **Markdown output** — summary counts, ordered report
  list, full attempts matrix (case × report), plus
  spotlight sections for `Growing` and `Mixed` cases
  only. Flat and shrinking cases aren't broken out
  separately — operators scanning for regressions want
  the creep / flake rows front and centre.
* **CLI** (`src/frok/cli/retry.py`) — new `summarize`
  sub-subcommand under `retry`:
  `frok retry summarize DIR [-o OUT] [--json]
  [--fail-on-growing]`. The gate flag only catches
  `growing` (not `mixed`) because `mixed` trend is
  already flagged as a regression by §23's pairwise
  diff; a CI that gates on both flags gets clean
  layering: diff flags real-time flake, summarize flags
  slow creep.
* **Error handling** — missing directory, non-directory,
  empty directory, malformed report, or payload
  missing `cases` all surface as `CliError`. Matches
  the §23 behaviour so operators see consistent
  failure messages across the retry subcommand group.

**Verification.** `python3 -m pytest -q` → 765 passed in 2.89s
(29 new: 17 module + 12 CLI). Module tests cover: trend
classifier for flat/growing/shrinking/mixed/single-value/
nones-ignored, three-report growing, flat, mixed, case
late arrival (None slots), `(case, repeat)` tuple
matching (repeats tracked independently), missing dir /
non-dir / empty dir / malformed report / missing-cases
errors, markdown matrix + spotlight sections. CLI tests
cover: parser registration, markdown write, `--json`
structured output, `--fail-on-growing` returns 1 on
growing and 0 on mixed (correct gating), missing/empty/
malformed/non-dir CliError paths.

**Decisions / trade-offs.**
* Lexicographic filename ordering, not modification
  time. Operators producing retry-reports at predictable
  cadences (daily CI) get YYYY-MM-DD naming for free;
  mtime is unreliable under copies/restores. When
  operators want a different order they can rename; the
  rule is simple and discoverable.
* `--fail-on-growing`, not `--fail-on-mixed`. Mixed
  trends are real flake that §23's pairwise diff
  already flags (any repeat that regressed is caught).
  Growing is the creep signal that ONLY the series view
  catches — hence the dedicated gate. Stacking both
  flags in CI (`retry diff --fail-on-regression` +
  `retry summarize --fail-on-growing`) gives full
  coverage without overlap.
* Missing entries recorded as `None`, not skipped. The
  row-per-case layout needs alignment across reports so
  operators can eyeball "case X was added on Tuesday".
  Skipping would collapse columns and make the matrix
  hard to read.
* Markdown spotlights only `Growing` and `Mixed`. A
  dedicated "Shrinking" section would celebrate
  improvements but operators scanning for problems
  don't need them called out — the trend column already
  flags them. Less noise, more signal.
* `.json` glob, not `**/*.json`. Nested retry-report
  directories are a future concern (§25+: compare
  CI-run series across branches). For now the flat
  directory matches every existing operator workflow
  (one dir per environment, day-stamped files).

**Next suggested action:** `Extend Phase 5 §25 with a
\`frok retry show PATH\` subcommand that pretty-prints a
single retry-report JSON as markdown: per-case attempt
tables with sleep timings, terminal verdicts, and
retry-budget utilisation. Complements --retry-report
(produces the JSON), retry diff (compares two), and
retry summarize (series trend) with a single-report
triage view — "what did this specific run do?".`

## 2026-04-24 — Phase 5 §23: retry-diff

**Shipped** ``frok retry diff A B`` — a new CLI subcommand
that diffs two retry-report JSONs and surfaces the
creeping-flake signals the budget-relative summary would
miss. Closes the loop opened by §22: the per-attempt
timeline is diff-able now, not just introspectable.

* **Differ** (`src/frok/evals/retry_diff.py`) — two
  functions: `diff_retry_reports(a, b)` and
  `retry_diff_to_markdown(diff)`. Matches entries by
  `(case, repeat)` tuple so `--repeat` runs diff coherently
  without collapsing independent repeats. Returns a dict
  with `matched`, `only_in_a`, `only_in_b`, plus four
  subset lists (`attempts_grew`, `attempts_shrank`,
  `error_changed`, `newly_failing`, `newly_passing`) and a
  `regressed` bool.
* **Regression heuristic** — `regressed = True` iff any
  of: attempts grew, a case newly failed, the last-attempt
  error drifted between two non-null strings (new failure
  shape), or a new failing case appeared in B. Explicitly
  NOT regressed: attempts shrank, pass-flipped from fail
  to pass, error resolved from non-null to null, or a new
  passing case appeared. These are all improvements or
  neutral changes.
* **CLI subcommand** (`src/frok/cli/retry.py`) — follows
  the `frok eval diff`/`frok eval summarize` pattern:
  `frok retry diff A B [-o OUT] [--json]
  [--a-label LABEL] [--b-label LABEL]
  [--fail-on-regression]`. Subcommand group (`retry`) with
  sub-subcommand (`diff`) so future retry CLI operations
  (summarize, report-show) slot in naturally.
* **Epilog entry** — root parser's help epilog now lists
  `frok retry diff A B` alongside the other everyday-
  operations commands (eval diff, eval summarize, trace
  inspect).
* **Error handling** — missing report file → `CliError`
  ("`retry report not found`"); malformed JSON → `CliError`
  ("`retry report is not valid JSON`"); payload without a
  `cases` key → `CliError` ("`missing 'cases' list`").
  Each gives the file path inline so operators can re-run
  the producer.

**Verification.** `python3 -m pytest -q` → 736 passed in 2.86s
(19 new: 10 differ + 9 CLI). Differ tests cover: identical
clean, attempts grew/shrank, error drift between two non-
null strings, error resolved (non-null → null), newly
failing, only-in-A, only-in-B pass vs fail, (case, repeat)
tuple matching, markdown summary + section rendering. CLI
tests cover: parser registration, clean identical exits 0,
attempts-grew under `--fail-on-regression` exits 1, `--json`
emits structured payload, missing file + malformed JSON +
missing-`cases` all hard-error, custom labels surface in
markdown.

**Decisions / trade-offs.**
* Match by `(case, repeat)` tuple rather than collapsing
  repeats. Under `--repeat N`, repeat 0 and repeat 2
  legitimately have different attempt counts and error
  shapes; collapsing would hide that. Operators who want a
  case-level rollup can post-process the matched list.
* Error-drift regression only when both sides are non-null.
  `null → "RuntimeError"` is already caught by
  `newly_failing`; `"RuntimeError" → null` is an
  improvement. Only two non-null strings differing is a
  true shape drift — same failure mode → different failure
  mode signals that the problem moved, which is a
  regression worth surfacing.
* New subcommand group (`retry`) rather than
  `frok eval retry-diff`. `eval` holds capture-based
  operations (summarize, diff of JsonlSink directories);
  retry reports are a different object with different
  shape. Keeping `retry` separate leaves room to grow
  (`frok retry summarize`, `frok retry show`) without
  cramming unrelated noun-verbs under `eval`.
* CLI reads JSON directly rather than going through a
  `RetryReport` dataclass. The report is a pure JSON dump;
  introducing a dataclass would add a schema-validation
  layer with no callers — the differ already treats the
  input as `dict[str, Any]` and fails cleanly on missing
  keys.
* Kept the three filter lists (`attempts_grew`,
  `error_changed`, `newly_failing`) as separate markdown
  sections instead of one mega-table. Each tells a
  different story, and a single cramped table makes the
  "what's the actual problem" harder to scan.
* `--a-label` / `--b-label` default to "a" / "b" rather
  than inferring from paths. Path-based labels are
  distracting when paths are long; explicit labels keep
  the markdown scannable ("monday vs today" vs the full
  `reports/2026-04-22/retry.json` path).

**Next suggested action:** `Extend Phase 5 §24 with a
\`frok retry summarize DIR\` subcommand that walks a
directory of retry-report JSONs (one per run, typically
named by date) and produces a trend table: per-case, the
attempts timeline across every report. Catches slow creep
that pairwise diffs would miss — "case X attempts went 1
→ 1 → 2 → 3 → 4 over two weeks" is only visible when
you look at the whole series. Complements §23's point-in-
time diff with a longitudinal view.`

## 2026-04-24 — Phase 5 §22: retry-report

**Shipped** ``frok run --retry-report PATH`` — a sibling
JSON dump to `--summary-json` carrying the full per-case
per-attempt retry timeline. Closes the remaining
diagnostic gap in the retry stack: the markdown report and
summary JSON both aggregate to "attempts / budget" per
case, which misses creeping flake patterns like "the suite
still passes but Tuesday needed 2 attempts per case,
today's needs 5 across three cases — same 5/5 budget, but
the shape is eroding." The timeline makes those shifts
diffable across runs.

* **CLI flag** — `--retry-report PATH`. Default `None`
  means no file written; setting it always writes,
  regardless of `--retry` value (so operators see the
  single-attempt baseline too, which helps when comparing
  before/after adding `--retry`).
* **Data shape** — top-level `{"cases": [...]}` with one
  object per `(case, repeat)` unit. Each carries `case`,
  `repeat`, `attempts`, `retry_budget`, `passed` (the
  terminal verdict). Each attempt is `{"attempt",
  "passed", "error", "sleep_before_ms"}`. `attempt` is
  1-based; `error` is the raw `observation.error` string
  or `null`; `sleep_before_ms` is the actual backoff
  slept *before* this attempt (0.0 for attempt #1, and
  jitter-adjusted when `--retry-backoff-jitter` is set).
* **Collection** — `_run_unit` now builds an
  `attempts_log` list alongside the retry loop, appending
  a record right after each `runner.run_case` call.
  Returns a tuple `(result, attempts_log)` instead of
  just `result`; the gather splits them back apart via
  `zip(task_meta, timelines, results)`.
* **Sleep duration** — `_apply_retry_backoff` now returns
  the actual `ms` slept (was `None`), so the timeline
  records what really happened rather than re-deriving it
  from config. With jitter enabled, different runs
  produce different `sleep_before_ms` values per attempt,
  which is exactly what operators want to diff.
* **Parent-dir creation** — mirrors `--summary-json` and
  `-o`: `args.retry_report.parent.mkdir(parents=True,
  exist_ok=True)`. Operators can point the flag at
  `reports/2026-04-24/retry.json` without pre-creating
  the chain.

**Verification.** `python3 -m pytest -q` → 717 passed in 2.66s
(8 new). Tests cover: parser default `None`, parser
accepts Path, single-attempt pass (one entry with
`sleep_before_ms=0`), multi-attempt with errors (each
entry carries the specific error string, sleeps from
attempt 2 onward), exhausted retries (every attempt
logged with `passed=False`), no-flag writes no file,
missing parent dir is created, `--repeat 2` + two cases
produces 4 entries in submission order `[(alpha,0),
(alpha,1), (beta,0), (beta,1)]`.

**Decisions / trade-offs.**
* Timelines are collected ALWAYS (even when the flag
  isn't set), not just when `--retry-report` is set.
  Bookkeeping is a handful of dict appends per attempt —
  trivial cost. Doing it unconditionally keeps the
  code path single-shaped and opens the door for future
  features (retry-report-append, telemetry span
  emission) without refactoring.
* Split `_run_unit`'s return into a tuple rather than
  stashing the timeline on `EvalResult`. Timelines are a
  CLI concern, not a library concern — attempts already
  live on `EvalResult`, but the per-attempt record
  (error string, sleep ms) belongs to the CLI retry
  loop. Keeping them separate respects the library
  contract.
* Recorded `sleep_before_ms` is the actual slept value,
  not the configured base. Under jitter, each attempt's
  sleep differs; the JSON must faithfully record what
  happened, not what was configured (operators can go
  back to the flag values for that).
* `passed` appears both on the top-level case object
  (terminal verdict after the retry loop) and on each
  attempt (per-try verdict). Both are useful: the former
  matches the summary JSON's perspective; the latter
  shows the inside-the-loop view.
* No gating on `--retry > 0`. Writing a single-attempt
  timeline for a no-retry run is valid baseline data —
  operators flipping `--retry` on later can diff the
  before/after. Hard-erroring on no-retry would break
  that workflow.
* Submission-order entries (not pass-first, not grouped
  by case name). Matches the `asyncio.gather` contract
  that preserves submission order regardless of
  completion order — same mental model as every other
  CLI output in the tool.

**Next suggested action:** `Extend Phase 5 §23 with a
\`frok run --retry-report-diff A B\` subcommand (or
sibling CLI) that loads two retry-report JSONs, matches
(case, repeat) pairs across them, and prints a markdown
table flagging cases whose attempt count grew, cases
whose error shape changed, and cases that newly appeared
/ disappeared. Gives operators a single-command creeping-
flake detector — today's retry-report vs last Friday's,
one glance tells the trend.`

## 2026-04-24 — Phase 5 §21: retry-backoff

**Shipped** ``frok run --retry-backoff MS`` +
``--retry-backoff-jitter FRACTION`` — a sleep-between-retries
knob that fires BEFORE each retry (not after the final
attempt) and is skipped on every early break. Closes the
last practical gap in `--retry` for rate-limited APIs:
hammering xAI again 10ms after a 429 just trips the same
429, so operators need a back-off knob that's cheap to
reach for.

* **CLI flags** — `--retry-backoff MS` (int, default 0) and
  `--retry-backoff-jitter FRACTION` (float, default 0.0).
  Base sleep is `MS / 1000.0` seconds; jitter applies a
  symmetric multiplier `random.uniform(1 - F, 1 + F)` so
  `--retry-backoff 1000 --retry-backoff-jitter 0.5` spreads
  sleeps across `[0.5s, 1.5s]`.
* **Retry-loop placement** — the sleep sits at the top of
  iterations 2+ (`if i > 0 and args.retry_backoff > 0`), so:
  (a) it never fires before the first attempt; (b) every
  existing `break` path (pass, `TimeoutError`,
  `--retry-on-error` filter miss) short-circuits the sleep
  for free; (c) no sleep happens after the final attempt —
  a trailing sleep adds cost with zero value.
* **Test seam** — module-level `_retry_sleep = asyncio.sleep`
  can be monkeypatched by tests to record call durations
  without actually waiting, mirroring
  `frok.clients.grok`'s existing `sleep` injection style.
  Production code still goes through `asyncio.sleep`
  untouched.
* **Validation** — four new guards:
  - `--retry-backoff < 0` → CliError
  - `--retry-backoff-jitter` outside `[0.0, 1.0]` → CliError
  - jitter > 0 without `--retry-backoff > 0` → CliError
    (nothing to scale)
  - `--retry-backoff > 0` without `--retry > 0` → CliError
    (no retries to sleep between)
  The last three mirror §18/§20's "flag requires the
  budget" guard shape so operators see a consistent set of
  misuse messages.

**Verification.** `python3 -m pytest -q` → 709 passed in 2.59s
(14 new). Tests cover: parser defaults (0, 0.0), parser
accepts int/float, `_apply_retry_backoff` unit sleeps
`ms/1000`, no-op when ms <= 0, jitter keeps sleeps in
`[base*(1-F), base*(1+F)]`, N-1 sleeps for N attempts,
first-pass-no-sleep, no sleep after the final failed
attempt, jitter uses `random.uniform` end-to-end, no sleep
when `--retry-on-error` filter stops the loop, all four
validation paths.

**Decisions / trade-offs.**
* Linear backoff, not exponential. Exponential is usually
  overkill for eval regression suites where most retries
  are single-digit; the jitter fraction adds the
  randomness that prevents synchronized thundering-herd
  retries. Exponential can come later if an operator needs
  it; a linear floor is the 80% case.
* Millisecond granularity. Operators benchmark rate limits
  in "seconds per request"; ms lets them dial "retry after
  500" without typing `0.5`. The seconds-in-sleep
  conversion is internal.
* Sleep BEFORE retry, not after the failed attempt. Both
  positions are semantically equivalent except on the final
  attempt — and "no sleep after final" is the right
  behaviour (trailing sleep = pure cost, zero value). The
  `if i > 0` guard is simpler than a "and i < budget-1"
  trailing guard.
* Module-level `_retry_sleep` seam rather than plumbing a
  sleep fn through every layer. Only one place needs to
  wait; exposing it as a rebindable module attribute keeps
  tests ergonomic without polluting `run_cmd`'s signature.
* Jitter uses the process-wide `random` module (not a
  dedicated `Random()` instance). The existing `--seed S`
  flag already bumps `random.seed`, so jitter becomes
  deterministic under seeded runs — matches the Phase-3
  §10 contract that "seeded runs are reproducible."
* Rejecting `--retry-backoff > 0` without `--retry > 0` as
  a CliError. A silent no-op would be friendlier but also
  more confusing ("why isn't my backoff firing?"). Hard
  errors on obvious misuse save an operator debugging hour.

**Next suggested action:** `Extend Phase 5 §22 with a
\`frok run --retry-report\` flag that writes a sibling JSON
file (next to --summary-json) listing every case's retry
timeline — a per-attempt record of [attempt_number,
passed, error, sleep_before_ms] so CI can diff retry
behaviour across runs. Catches "Tuesday's suite passed on
attempt 4, today's is passing on attempt 6 across three
cases" — a creeping flake signal the current report would
miss because attempts still fit under the budget.`

## 2026-04-24 — Phase 5 §20: retry-on-error

**Shipped** ``frok run --retry-on-error REGEX`` — an
error-shape filter that narrows `--retry` to failures whose
`observation.error` matches at least one regex. Closes the
remaining misuse of §16 `--retry`: blanket retries were
masking both flaky network calls (which we want to retry)
AND genuine correctness regressions that happened to raise
(which we don't). Now `--retry-on-error '429|Connection'`
expresses exactly "retry transient network errors, never
scorer or assertion failures."

* **CLI flag** (`frok/cli/run.py`) — `action="append"` with
  `default=[]`, `metavar="REGEX"`. Patterns compile once via
  `re.compile` (raw Python regex, not the glob+`re:` grammar
  used for case-name selectors — errors are already strings
  that lean on regex syntax, and operators will paste
  regex-shaped text here).
* **Retry-loop gate** — after a failing attempt, compute the
  observation error string. Existing `TimeoutError` short-
  circuit runs unchanged. If any `--retry-on-error` pattern
  is set AND (the error is empty OR no pattern matches), the
  loop breaks. Scorer-only failures (no observation error)
  are never retried under this flag by explicit design —
  they're almost always real regressions, and `.*` would
  otherwise match an empty string and silently turn
  assertion failures into infinite retries.
* **Validation** — `args.retry_on_error and args.retry == 0`
  → `CliError` (same shape as §18's `--retry-on` guard).
  Invalid regex surfaces inline: "`invalid regex in
  --retry-on-error '[invalid': ...`".
* **Composes with `--retry-on`** via AND semantics: a case
  must be in the name-selector AND its error must match the
  error-selector for a retry to be eligible. This is the
  cleanest layering — each flag owns one dimension, both
  must agree for the retry to fire.

**Verification.** `python3 -m pytest -q` → 695 passed in 2.83s
(10 new). Tests cover: parser default empty, parser append-
able, matching error triggers retry, non-matching error runs
once, scorer-only failure runs once (the empty-error edge
case), multiple patterns any-match-wins, timeout still
short-circuits even when pattern would match `TimeoutError`,
`--retry-on` + `--retry-on-error` AND composition
(flaky-net retries on 429, deterministic doesn't retry
despite matching error because it doesn't match the name
selector), `--retry-on-error` without `--retry` is CliError,
invalid regex is CliError.

**Decisions / trade-offs.**
* Regex grammar, not glob+`re:`. Error strings like
  "`ConnectionResetError: peer closed`" lean on regex
  syntax already (`|`, `.*`, `^`/`$`). Forcing operators to
  opt into regex via a `re:` prefix would have meant every
  invocation starts with `re:`, which is just noise. `--
  retry-on` keeps the glob syntax because case names are
  typically simple identifiers where globs feel natural.
* Scorer-only failures never retry under the filter, even
  when `.*` is specified. `.*` matching the empty string
  would have made `--retry-on-error .*` equivalent to
  `--retry` alone; that's a footgun. Explicitly short-
  circuiting on empty-error makes the flag always mean
  "retry only errors I know about."
* Timeouts still win the short-circuit race. §16's design
  stands: a case-level timeout is operator intent, not
  flakiness. Operators who truly want to retry timeouts can
  raise `--timeout-s`. `--retry-on-error TimeoutError`
  doesn't override this because that would break the layer
  between "operator-set cap" and "flake absorption" — two
  distinct concerns.
* AND semantics with `--retry-on`, not OR. If both flags are
  set, an operator is expressing "retry X *kinds* of cases
  when they fail in Y *way*" — a conjunction. OR would
  broaden retries unpredictably. The tests lock in this
  behaviour end-to-end.
* Budget still gets allocated even when the error filter
  stops the loop early. A case that matched `--retry-on` but
  whose first error didn't match `--retry-on-error` shows
  `1/4` in the markdown — used 1 of 4 allocated attempts,
  with the specific error visible in `observation.error`.
  That's diagnostic gold: "operator allocated 4 retries;
  case used 1 because the error wasn't retry-eligible."

**Next suggested action:** `Extend Phase 5 §21 with a
\`frok run --retry-backoff MS\` flag that sleeps for MS
milliseconds between retries (linear); optionally
\`--retry-backoff MS --retry-backoff-jitter FRACTION\` for
\`random.uniform(1 - F, 1 + F) * MS\` jitter. Mainly useful
against rate-limited APIs like 429-on-xAI, where
immediately retrying just hits the same rate limit again.
Default 0 (no sleep) preserves every existing test's
behaviour; negatives rejected; the sleep goes before the
next attempt, not after the final one.`

## 2026-04-24 — Phase 5 §19: retry-budget

**Shipped** ``EvalResult.retry_budget`` — the attempt
allowance the CLI allocated to each result, alongside the
already-surfaced `attempts` count. The markdown Attempts
column becomes `Attempts/Budget` (e.g. "3/5") and the
summary line reads "used A of B attempts". Catches the
scenario where `--retry` masks a caught-late flake into
PASS: the binary retried/not-retried flag would have missed
"used 4 of 5 attempts" as a flake signal.

* **`EvalResult.retry_budget: int = 1`** — default keeps
  existing library-level callers unchanged. `to_summary()`
  emits the field when > 1, so passing runs without
  `--retry` still produce the same summary shape.
* **CLI plumbing** — the retry loop now stamps both
  `attempts` and `retry_budget` onto the final result via
  `dataclasses.replace`. Budget is `args.retry + 1` for
  retry-eligible cases and `1` for cases that
  `--retry-on PATTERN` excluded. The stamp happens whenever
  either `attempt_count > 1` or `budget > 1`, so budget-
  allocated-but-unused cases are captured too.
* **Report surfacing** — both flat and aggregated markdown
  trigger the Attempts/Budget column on
  `_has_retries or _has_retry_budget`. The summary line
  "Retried cases: K (used A of B attempts)" replaces the
  old "total attempts N" phrasing. `EvalReport.total_budget`
  is a new computed property; `to_summary()` gains
  `total_budget` alongside `total_attempts` and
  `retried_cases` when any result was retry-eligible.
* **Aggregated sums** — when `--repeat N --retry M` compose,
  both fields sum across a case's repeats. A case with
  `attempts=[1,4]` and `budget=[4,4]` across two repeats
  shows "5/8" in the aggregated row — used 5 of 8 allocated
  attempts, making a caught-late pattern visible even
  without dropping into per-repeat detail.

**Verification.** `python3 -m pytest -q` → 685 passed in 2.38s
(12 new + 3 existing updated for the new surfacing). Tests
cover: field default = 1, summary omit/include gating,
report `_has_retry_budget`/`total_budget` properties,
summary surfaces budget when allocated-but-unused, flat
markdown shows `N/M` per row + summary phrasing, aggregated
markdown sums across repeats, CLI stamps `retry+1` on
matched cases and `1` on `--retry-on`-excluded cases, end-
to-end markdown shows "2/3" / "1/3" for retried / untouched
cases.

**Decisions / trade-offs.**
* Budget surfaces even when unused. The operator allocated
  it — showing "used 1 of 5 attempts" surfaces that the
  retry budget is much larger than needed, which is itself
  a cost signal. Hiding it would have lost that.
* Changed the gating from `_has_retries` to
  `_has_retries or _has_retry_budget`. Three existing tests
  needed updating (two directly-constructed `EvalResult`
  tests that set `attempts=3` without matching budget, and
  one CLI pass-first test that asserted a clean summary
  under `--retry 3`). The per-test updates make the budget
  semantic explicit.
* Column format is `attempts/budget`, not two separate
  columns. Keeps the aggregated markdown readable on narrow
  terminals; the slash format is the universal "X of Y"
  shorthand.
* Budget stamping happens whenever `attempt_count > 1 or
  budget > 1`, not just when retries happened. Allocated-
  but-unused budget still signals operator intent and
  shouldn't silently collapse to the default.
* Kept the summary line "Retried cases: K" as the headline
  number rather than "Budget-allocated cases: K". The
  former is what operators scan for; the budget is context
  for the count.
* No warning when a case consistently uses 0 of N
  allocated retries. That would cross into advice-giving
  territory and is better left to the operator (or a
  follow-up §20 lint pass that scans reports for "budget
  never used" patterns).

**Next suggested action:** `Extend Phase 5 §20 with a
\`frok run --retry-on-error REGEX\` flag that narrows the
retry loop to failures whose observation.error matches
REGEX — complementing --retry-on (case-name selection) with
error-shape selection. Useful for "retry only on 429 /
connection-reset / timeout-on-network-call" without
retrying AssertionError-style scorer failures, which are
almost always real regressions. Combines cleanly:
--retry-on cases AND --retry-on-error REGEX means both
gates must match for a retry to be eligible.`

## 2026-04-24 — Phase 5 §18: retry-on-pattern

**Shipped** ``frok run --retry-on PATTERN`` — a case-name
selector that narrows `--retry`'s budget to matching cases,
keeping strict single-attempt discipline on the rest of the
suite. Closes a real operational gap: one suite had two flaky
external-API cases buried among 40 deterministic ones, and
the blanket `--retry 3` was masking every deterministic
failure into a PASS.

* **CLI flag** (`frok/cli/run.py`) — `action="append"` with
  `default=[]`, `metavar="PATTERN"`. Same syntax as
  `--filter` / `--exclude` (glob default; `re:` prefix for
  regex). Repeatable — any match wins.
* **Validation** — `args.retry_on and args.retry == 0` →
  `CliError` ("`--retry-on requires --retry > 0`"). Without
  a budget the flag is a no-op with a misleading name; hard-
  erroring surfaces the mistake. Invalid regexes bubble up
  through the existing `_compile_pattern` path with the
  regex error message inline.
* **Budget plumbing** — patterns compile once before the
  case loop. Inside `_run_unit`, a per-case `budget`
  computation decides between `args.retry + 1` (case
  matches) and `1` (case doesn't match, run once). Rest of
  the retry loop is unchanged — still breaks on pass, still
  short-circuits on `TimeoutError`.
* **Composes cleanly** with `--filter` (which decides which
  cases to run at all), `--fail-on-regression` (exhausted
  retries on matched cases still flip the exit code), and
  `--repeat` (each repeat of a matched case gets its own
  retry budget).

**Verification.** `python3 -m pytest -q` → 673 passed in 2.57s
(12 new). Tests cover: parser default empty, parser
`append`-ability, match with `flaky-*` glob gives attempts=3,
no-match runs all cases once (attempts omitted from
summary), `re:^net-` matches only names starting with
"net-", repeatable flag with two distinct patterns, matched
case passes first attempt stays at 1, `--retry-on` without
`--retry` is a CliError, explicit `--retry 0 + --retry-on`
is a CliError, invalid regex surfaces inline,
`--fail-on-regression` returns 1 on exhausted matched case,
composes with `--filter`.

**Decisions / trade-offs.**
* `--retry-on` narrows retry *budget*, not case *selection*.
  `--filter` already does case selection; stacking another
  filter with subtly different semantics would have made the
  mental model opaque. Now each flag has one job: `--filter`
  decides what runs; `--retry-on` decides what retries.
* Reject `--retry-on` without `--retry`. A silent no-op is
  worse than a hard error here — operators specifying
  `--retry-on` without `--retry` almost always meant
  `--retry 3 --retry-on X` and dropped the budget by
  accident. Failing loudly catches that.
* Compile patterns once, outside the retry loop. Matches
  `filter_cases` style; keeps per-case cost down under
  `--jobs > 1` where the retry loop runs concurrently.
* Reused `_compile_pattern` / `_pattern_matches` verbatim.
  Operators already know the glob+`re:` syntax from
  `--filter`; introducing a different pattern grammar for
  `--retry-on` would have been gratuitous.
* No warning when `--retry-on PATTERN` matches zero cases.
  `--filter` raises in that situation because "nothing to
  run" is always an operator bug; `--retry-on` matching
  nothing just means "no case got a retry budget", which
  mirrors the default `--retry` behaviour exactly and can
  be legitimate (e.g. suite with no flaky cases anymore —
  keep the flag in CI for future flakes). A warning would
  create noise.

**Next suggested action:** `Extend Phase 5 §19 with
\`EvalReport\` markdown surfacing the retry budget *spent*
vs *available*: show each retried case's "attempts / budget"
ratio in the aggregated row (e.g. "3/5" for a case that
passed on attempt 3 out of a 5-retry allowance). Caught-it-
late retries still mask into PASS but show up as "used most
of the budget" — a softer flakiness signal than the binary
retried/not-retried flag.`

## 2026-04-24 — Phase 5 §17: attempts-field

**Shipped** ``EvalResult.attempts`` — a count of how many
runner invocations produced each result, plumbed through
`to_summary()` and `to_markdown()` so flaky cases stay
visible in the verdict doc even when `--retry` successfully
masks their failure.

* **`EvalResult.attempts: int = 1`** — new dataclass field,
  default 1 preserves existing behaviour for every code path
  that doesn't retry. `to_summary()` omits the key when 1
  (clean baseline) and emits the integer when higher, so
  passing runs produce the same summary shape they did before
  §17.
* **CLI retry loop** updates the attempts count on the final
  result via `dataclasses.replace(result, attempts=N)`. The
  replace happens only when `attempt_count > 1`, so single-
  attempt results keep the library-default 1. This leaves the
  runner's contract untouched ("one `run_case` → one
  `EvalResult`") and puts the attempt count where the only
  layer that knows it lives — the CLI retry loop.
* **`EvalReport` gains** `_has_retries` (any result with
  `attempts > 1`), `total_attempts` (sum across all results),
  and `retried_cases` (count of cases where any repeat
  needed more than one attempt). The summary dict grows
  `total_attempts` and `retried_cases` when any result was
  retried; the markdown report grows an Attempts column in
  both the flat and aggregated forms plus a "Retried cases: K
  (total attempts N)" summary line. All additions are gated
  on `_has_retries` so runs without `--retry` produce the
  exact same summary/markdown shape as before.
* **Aggregated form per-case total** — when repeats and
  retries compose (`--repeat N --retry M`), the aggregated
  row sums `attempts` across the repeats for that case. A
  case with attempts `[1, 3]` across two repeats shows total
  4 in the aggregated table; flaky + retried is the most
  diagnostic signal, so it gets the cleanest surfacing.

**Verification.** `python3 -m pytest -q` → 661 passed in 2.77s
(16 new). Tests cover: field default = 1, summary omit vs
include, `_has_retries` / `total_attempts` / `retried_cases`
properties, flat markdown column + header line, aggregated
markdown column + header line, CLI with no-retry leaves
attempts off summary, CLI with retry + pass-first leaves
attempts=1, CLI with fail-then-succeed records attempts=3,
CLI with exhausted retries records attempts=retry+1, CLI with
`--timeout-s` short-circuit leaves attempts=1.

**Decisions / trade-offs.**
* `attempts` lives on `EvalResult`, not `EvalReport`, so the
  runner and baseline diff machinery can both interrogate it
  per-case. The report-level totals (`total_attempts`,
  `retried_cases`) are computed properties, not stored state,
  so reports composed from arbitrary result lists always
  produce a consistent rollup.
* Default 1, not 0. A result you got back from the runner was
  produced by at least one attempt; modelling it as zero would
  be a lie.
* Gate all surfacing on `_has_retries`. Existing runs should
  produce byte-identical summaries and markdown; tests lock
  in that behaviour. Anyone rolling out `--retry` gets the
  new columns automatically.
* CLI uses `dataclasses.replace` rather than mutating the
  result in-place. Matches the frozen-adjacent style used
  elsewhere (scorers are frozen dataclasses) and keeps the
  retry loop's intermediate `result` objects logically
  immutable.
* Didn't add a `retry_budget` field or similar. The report
  only needs to say what happened, not what was budgeted —
  the CLI flag captures operator intent; the result captures
  actual behaviour. Keeping them separate avoids misleading
  "budget 5, used 1" rows that look like flakiness.

**Next suggested action:** `Extend Phase 5 §18 with a
\`frok run --retry-on PATTERN\` flag that narrows the retry
loop to cases whose names match a glob / regex (same
\`re:\`/glob syntax as --filter / --exclude). Lets operators
retry only known-flaky cases while keeping strict single-
attempt discipline on the rest of the suite — useful when a
handful of cases depend on flaky external services and the
blanket --retry would hide genuine regressions elsewhere.`

## 2026-04-24 — Phase 5 §16: cli-retry

**Shipped** ``frok run --retry N`` — a per-case retry loop that
re-runs failing cases up to N times and accepts the case if
*any* attempt wins. The mirror opposite of `--repeat` in intent:
`--repeat` surfaces flake, `--retry` absorbs it.

* **CLI flag** (`frok/cli/run.py`) — int, default 0,
  `metavar="N"`. `args.retry < 0` → `CliError`. `args.retry > 0`
  combined with `--capture-baseline` → `CliError` (retries
  would overwrite the previous attempt's captured JSONL, same
  shape of failure as the `--repeat > 1 + --capture-baseline`
  guard).
* **Retry loop** — wrapped inside `_run_unit` right around the
  existing `runner.run_case` call. A `for _ in range(args.retry
  + 1):` loop retains `retry=0`'s "run once" baseline. Breaks
  at the first `result.passed`. Also breaks when the
  observation error starts with `"TimeoutError"` — timeouts are
  a case-level cap (§14), not flakiness, and retrying them
  would undo the operator's explicit budget.
* **Composes with `--repeat`** by contrast. `--repeat N` runs
  every attempt and reports each as its own result (pass-rate
  aggregation surfaces flake). `--retry N` collapses the
  attempts into one verdict (pass-on-any, no new EvalResult per
  attempt). Both flags together work: each repeat gets its own
  retry budget.
* **Composes with `--fail-on-regression`** too — exhausted
  retries still leave the case FAIL, so CI gates exactly as
  you'd expect.

**Verification.** `python3 -m pytest -q` → 645 passed in 2.69s
(12 new). Tests cover: parser default 0, parser accepts int,
retry=0 runs once, pass-first-attempt consumes no retry,
fail-then-succeed flips verdict to PASS, always-fail exhausts
`retry+1` attempts, `--timeout-s` + `--retry 5` runs exactly
once (timeout short-circuit), `--fail-on-regression` returns 1
when retries exhaust and 0 on eventual pass, `--retry -1`
errors with "`--retry must be >= 0`", `--retry 1 +
--capture-baseline` errors, `--retry 0 + --capture-baseline` is
fine (explicit-zero doesn't trigger the guard).

**Decisions / trade-offs.**
* Kept retries out of `EvalRunner` itself — the runner's
  contract is "one case → one EvalResult". Retry is a
  higher-level operator knob, identical to `--repeat`, which
  also lives in the CLI. Keeping it in the CLI means library
  users get a stable `run_case` without retry semantics leaking
  through.
* Chose pass-on-any over "all-must-pass". Opposite semantics
  exist (`--repeat` + manual aggregation) and a scorer can
  always assert `InvocationsWithin` / `LatencyWithin` on the
  winning run. The common operator need here is flake
  absorption, not quorum.
* Timeouts skip the retry loop. `TimeoutError` is semantically
  "operator's explicit cap was exceeded" — retrying it silently
  turns a 30s cap into a 90s cap without the operator asking.
  Flakiness is a property of the network/model/seed; case-level
  timeout is a property of the operator's intent.
* `--capture-baseline` conflict follows the exact shape of the
  existing `--repeat > 1` guard: both would overwrite per-case
  `<slug>.jsonl` files. Explicit `--retry 0` is allowed through
  (mirrors "no retry requested, no conflict").
* `--retry` is orthogonal to `--jobs`. The retry loop runs
  within a unit's semaphore hold, so concurrency bounds still
  apply and parallel retries don't oversubscribe CPU.
* No exponential backoff / sleep between retries. Cases run
  against user-controlled transports (stubs, memoised clients,
  live xAI). A fixed-sleep retry is wrong for all three; if a
  case wants its own backoff it can layer it in the transport.
  Keeping the loop tight also makes `--retry` cheap for pure-
  stub CI suites.

**Next suggested action:** `Extend Phase 5 §17 with an
\`EvalResult.attempts\` field surfacing how many retry attempts
each case consumed, plumbing it through \`to_summary()\` and
the report markdown so flaky cases are visible in the verdict
doc even when \`--retry\` successfully masks their failure.
Catches \"this case passes in CI but only on attempt 3/3\"
regressions before they become full failures.`

## 2026-04-23 — Phase 5 §15: cli-timeout-default

**Shipped** ``frok run --timeout-s SECONDS`` — a suite-wide
default for `EvalCase.timeout_s`, filled in per case where the
case itself hasn't opted out. Operators who want "no case
should ever take more than 30s" can now set it once at the
command line instead of editing every case file.

* **CLI flag** (`frok/cli/run.py`) — registered as a float
  with `metavar="SECONDS"`. Default is `None` (no fill).
* **Runner fill** — after `load_case_file` + `--use-baseline`,
  if `args.timeout_s is not None`, iterate `loaded.cases` and
  set `case.timeout_s = args.timeout_s` for any case whose
  own value is `None`. Per-case overrides win by construction.
* **Validation** — negative `--timeout-s` raises `CliError`
  ("`--timeout-s must be >= 0`", exit 2). Zero is allowed —
  `asyncio.wait_for(0)` short-circuits every unconfigured case
  before it runs, which is a legitimate "pre-flight check the
  loader, skip execution" move. Per-case `timeout_s=0` already
  has the same semantics (§14).

**Verification.** `python3 -m pytest -q` → 633 passed in 2.58s
(9 new). Tests cover: parser default `None`, parser accepts
float + zero, no-flag leaves cases untouched (existing
behaviour preserved), `--timeout-s 0.05` on a 5s-sleep
transport fires the timeout with both marker + configured
value in `observation.error`, mixed-case file with one
`timeout_s=0.02` + one None + `--timeout-s 0.10` honours both
boundaries simultaneously, `--timeout-s 0` short-circuits,
`--fail-on-regression` returns 1 on a timeout case,
`--timeout-s -1` is a `CliError`.

**Decisions / trade-offs.**
* Fill at the runner layer, not on the EvalCase directly at
  load time. Cases authored in the file are the source of
  truth for their own `timeout_s`; the CLI is a fallback for
  un-opinionated cases. Filling only the `None` slots keeps
  that layering clean.
* Negative is a hard error. Existing flags (`--repeat`,
  `--jobs`) follow the same rule; zero is a valid edge-case
  for "don't actually execute" but negatives are always bugs.
* Mirrors `--use-baseline` semantics. That flag fills
  `case.baseline` for cases whose own is None; this fills
  `case.timeout_s` for cases whose own is None. Consistent
  precedence ladder, consistent operator mental model.
* No validation that `--timeout-s` is above some floor
  (e.g. "not less than 1ms"). Unit tests often need sub-
  millisecond timeouts to exercise the error path
  deterministically, and operators trying `--timeout-s 0.0001`
  on a live call will see the same `TimeoutError` the case-
  level setting produces — the failure is already clean.

**Next suggested action:** `Extend Phase 5 §16 with a
\`frok run --retry N\` flag wiring \`asyncio\` retry loops
around each case: on a failing case (not a timeout — those
are by design), re-run up to N times and mark the case passed
if any attempt succeeds. Useful for shaking out genuinely
flaky cases from regressions. Combines cleanly with
\`--repeat\` (which runs N times and reports every outcome)
by contrast — retry stops at the first win.`

## 2026-04-23 — Phase 5 §14: case-timeout

**Shipped** ``EvalCase.timeout_s`` — a hard wall-clock cap per
case, enforced by the runner via ``asyncio.wait_for``. Closes a
real operational gap: ``LatencyWithin`` / ``LatencyDeltaWithin``
only assert after the case completes; a case that's *actually*
stuck hangs the suite until the operator ctrl-C's. Setting
``timeout_s`` turns that into a clean case-level failure.

* **`EvalCase.timeout_s: float | None = None`** — default
  None preserves existing behaviour (no wait_for wrapping);
  any positive value caps the case's runtime.
* **Runner enforcement** — `EvalRunner.run_case` wraps the
  `_execute` coroutine in `asyncio.wait_for(..., timeout_s)`
  when set. On timeout, Python cancels the underlying task;
  cancellation unwinds through every open `async with` span
  (so spans close with errors marked), `asyncio.wait_for`
  translates to a `TimeoutError`, and the runner builds a
  clean Observation with `error="TimeoutError: case
  exceeded timeout_s=N.N"`.
* **Partial events preserved** — the InMemorySink the
  runner passes into the factory catches span events as they
  close during unwinding. The timeout-produced Observation
  carries those partial events, so trace-inspect / scorer
  post-mortems aren't left empty.
* **Composition** — timeout applies per case per repeat, not
  per suite. `--repeat 5 timeout_s=10.0` gives each of the
  five runs its own 10s budget; a slow repeat doesn't eat
  budget from the others.

**Verification.** `python3 -m pytest -q` → 624 passed in 2.43s
(8 new). Tests cover: default `timeout_s=None` preserves the
no-wait behaviour, generous timeout + fast transport still
passes, tiny timeout (50ms) + slow transport (2s) surfaces
`TimeoutError` + the configured value in `observation.error`,
`NoErrors` scorer fires on the timeout error (with
`TimeoutError` in its detail), content scorers see an empty
answer when `final_response is None`, partial `grok.chat`
span events survive on the sink with their `error` field
populated from cancellation unwinding, per-repeat budget
composes correctly with `--repeat`, and `timeout_s=0.0` fires
immediately (correct contract — "don't run at all").

**Decisions / trade-offs.**
* Wrap `_execute`, not scorers. Scorers are assertion
  machinery; timing them would tangle "the model took
  forever" with "my Python scorer is slow". The timeout
  gates the chat/tool work; scorers run post-hoc on
  whatever partial observation the runner salvaged.
* Partial events preserved rather than emptied. A
  cancelled run is often the most interesting one to
  inspect (which span hung?); keeping the sink's events
  means `trace inspect` works on timeout failures too.
* `asyncio.TimeoutError` not `asyncio.CancelledError`.
  `wait_for` already translates the cancel to a TimeoutError
  under the hood; the runner just catches the translated
  form, keeping the `Observation.error` message
  operator-readable.
* `timeout_s=0.0` fires immediately by design. Python's
  `wait_for(..., 0)` raises before scheduling the
  coroutine, so the case never runs. An operator explicitly
  passing 0 is saying "short-circuit this case" — that's a
  feature, not a bug. Documented.
* Timeout wraps a single coroutine per repeat, not the
  whole suite. `--repeat 5 timeout_s=10.0` → 50s max across
  the five; gating the whole suite at once would punish
  slower repeats that are still within budget individually.

**Next suggested action:** `Extend Phase 5 §15 with a
\`frok run --timeout-s N\` CLI flag: set a default
\`timeout_s\` on every loaded case whose own \`timeout_s\` is
None. Mirrors how \`--use-baseline\` fills in
\`case.baseline\` — operators get a suite-wide default
without editing every case file, while per-case
overrides still win.`

## 2026-04-23 — Phase 5 §13: latency-delta

**Shipped** ``LatencyDeltaWithin(max_ms)`` — the wall-clock
twin of §12's ``TokenDeltaWithin``. Operators regression-testing
a prompt change now have one scorer stack that asserts both
"tokens didn't drift by more than N" and "wall-clock didn't
drift by more than M", both anchored to the same captured
baseline.

* **`diff_event_streams` extension** — added a
  ``_root_duration_ms(events)`` helper matching
  ``Observation.total_latency_ms`` semantics (first root span's
  `duration_ms`), plus three new keys on the diff dict:
  ``{a_label}_latency_ms``, ``{b_label}_latency_ms``,
  ``latency_delta_ms``. Existing callers and tests aren't
  affected — they check specific keys, not shape equality.
* **`LatencyDeltaWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring ``TokenDeltaWithin`` line-for-line.
  `__post_init__` rejects negative `max_ms`; zero is allowed as
  exact-parity.
* **Shared baseline loader** — pulled out a private
  ``_load_baseline_diff(case, sname, obs)`` helper that both
  baseline-aware scorers call. Returns a `Score` on error
  paths (no baseline attached / missing file / unreadable) or
  the diff dict on success. Keeps the two scorers from
  drifting on error messages.
* **Failure detail** surfaces baseline + observed + signed
  delta, same shape as the token scorer; ``measure`` carries
  the signed latency delta as a float.

**Verification.** `python3 -m pytest -q` → 616 passed in 1.45s
(21 new). Library tests cover the five new diff-field paths
(identical streams → zero latency delta, root span only (nested
spans don't contribute), signed delta direction preserved,
custom labels rename the keys, missing root span → 0.0), plus
16 scorer tests mirroring ``TokenDeltaWithin``'s coverage:
construction rejects negative / zero allowed, no-baseline +
missing-file fail cleanly, zero delta passes, small positive +
small negative deltas pass, inclusive at-threshold in both
directions, over-threshold positive + negative both fail with
baseline + observed + signed delta in detail, ``max_ms=0``
enforces exact parity, scorer name reflects the cap, measure
preserves direction. Two integration tests use a deterministic
clock injected into `Tracer(clock=...)` so wall-clock noise
doesn't flake: the parity case passes, the drift case fails
with ``+990.0`` in the detail.

**Decisions / trade-offs.**
* Extended `diff_event_streams` rather than duplicating the
  root-span lookup in the scorer. One canonical helper keeps
  the live-vs-captured differ and the scorer in lockstep —
  exactly the parity ``diff_against_baseline`` already
  delegates through.
* Root-span duration, not sum-of-all-spans. Matches
  ``Observation.total_latency_ms`` semantics so a case's
  runtime wall-clock and the captured baseline compare
  apples-to-apples.
* Symmetric `abs(delta_ms)` gate. A sudden latency collapse
  is as much a regression signal as a latency spike (usually
  means the model bailed early); operators who want one-sided
  can layer a future variant.
* Shared `_load_baseline_diff` helper is module-private.
  Public API is the two scorer classes; operators don't need
  to know they share plumbing.
* Integration tests inject a deterministic `Tracer(clock=)`
  rather than relying on `asyncio.sleep` timing. Wall-clock
  tests on CI are flaky; synthetic clocks are the way.

**Next suggested action:** `Extend Phase 5 §14 with an
\`EvalCase.timeout_s\` field + runner enforcement:
asyncio.wait_for wraps each case execution, failing the case
with a clean \`TimeoutError\` observation.error when it
exceeds timeout_s. Closes the gap that today's
LatencyWithin / LatencyDeltaWithin close only after the run
completes — a truly-stuck case hangs the whole suite until
the operator hits Ctrl+C.`

## 2026-04-23 — Phase 5 §12: token-delta

**Shipped** ``TokenDeltaWithin(max_delta)`` — the first
baseline-aware scorer. Reads ``case.baseline``, diffs baseline
vs observed token totals, fails when ``abs(delta) > max_delta``.
The existing baseline differ already reports the delta but never
gated CI on it; this scorer closes that loop for operators who
want "token cost shouldn't move by more than N between captured
baselines".

* **`TokenDeltaWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass. `__post_init__` rejects negative `max_delta`;
  zero is allowed as "tokens must match baseline exactly".
* **Baseline loading** — when `case.baseline` is None, fails
  cleanly with a message pointing at how to attach one
  (``case.baseline=`` or CLI ``--use-baseline``). When the
  file is missing, fails with the exact path. Both error
  paths are test-covered.
* **Symmetric by design** — ``abs(delta)`` comparison catches
  prompt changes that doubled tokens (positive delta) *and*
  changes that collapsed the answer to a one-liner (negative
  delta, often signalling the model bailed). Operators who
  only care about one direction can layer a future
  one-sided variant.
* **Delta diff reuses the existing core** — ``diff_event_streams``
  from `frok.evals.baseline` is imported at module top; no
  duplication between this scorer and the single-observation
  baseline differ already powering `EvalCase.baseline_diff`.
* **Failure detail** surfaces baseline tokens, observed
  tokens, and the signed delta — triage can tell at a glance
  which direction drifted. ``measure`` carries the signed
  delta (positive = observed used more) for aggregated
  trend-scanning.

**Verification.** `python3 -m pytest -q` → 595 passed in 1.54s
(16 new). Tests cover: construction rejects negative
`max_delta`, zero `max_delta` is allowed, no-baseline case
fails cleanly with guidance, missing-baseline-file fails with
the exact path, zero delta passes, small positive + small
negative deltas pass under threshold, inclusive at-threshold
in both directions, over-threshold positive + negative both
fail with baseline + observed + signed delta in detail,
``max_delta=0`` enforces exact parity, scorer name includes
the configured cap, and `measure` carries the signed delta
direction. Two integration tests wire the scorer through
`EvalRunner` end-to-end: the parity case passes, the drift
case (10 token baseline vs 100 token observed) fails with
``+90`` in the detail.

**Decisions / trade-offs.**
* Symmetric ``abs(delta)`` gate, not asymmetric `max_increase`
  / `max_decrease`. A one-liner bail is a real regression signal;
  treating positive and negative drift as equally suspect
  reflects that. YAGNI for the asymmetric form.
* Scorer loads the baseline file itself rather than relying on
  the runner's `baseline_diff`. `baseline_diff` is populated
  *after* scorers run (it's an `EvalResult` field), so a scorer
  that wanted to read it would need a runner refactor. Loading
  via `read_jsonl` keeps the scorer self-contained.
* `max_delta=0` is allowed as "exact parity". A case that's
  genuinely deterministic (`--seed` + stub transport) should
  trip on *any* token drift; forcing a positive minimum would
  rule that out.
* No separate "tokens drifted" telemetry event emitted. The
  eval report already surfaces the scorer's failure; adding
  a telemetry fire-and-forget would be double-reporting.

**Next suggested action:** `Extend Phase 5 §13 with
\`LatencyDeltaWithin(max_ms)\`: mirrors TokenDeltaWithin but
on root-span duration. Closes the second half of the
baseline-drift gate — operators regression-testing a prompt
change care about wall-clock impact as much as token cost,
and today there's no one-shot "tokens + latency both within
5% of baseline" assertion pair.`

## 2026-04-23 — Phase 5 §11: answer-length

**Shipped** ``AnswerLength(min_chars=None, max_chars=None)`` —
the shape gate complementing ``AnswerContains`` / ``AnswerMatches``
(content). Catches prompt regressions that start producing
one-word replies (set ``min_chars``) or runaway prompts that
emit long preambles before the actual answer (set ``max_chars``).

* **`AnswerLength`** (`frok/evals/scorers.py`) — frozen
  dataclass. Reads ``len(obs.answer)`` (which returns "" when
  no final response, so length 0 — consistent with the rest of
  the scorer family).
* **Construction validation** — ``__post_init__`` raises
  `ValueError` for the four malformed cases:
    * both bounds None (nothing to assert)
    * negative ``min_chars``
    * negative ``max_chars``
    * ``min_chars > max_chars`` (contradictory)
  ``min_chars == max_chars`` is allowed as "exact length".
* **Scorer name** dynamically reflects active bounds:
  ``answer_length[>=5]`` for min-only, ``answer_length[<=100]``
  for max-only, ``answer_length[>=3,<=10]`` for both. Aggregate
  reports can grep on exact / asymmetric / two-sided variants.
* **Measure** carries the observed length whether pass or
  fail — useful when post-hoc scanning runs to spot trends
  (e.g. "the 95p answer length crept from 80 to 150 chars
  over the last 20 baselines").

**Verification.** `python3 -m pytest -q` → 579 passed in 1.75s
(17 new). Tests cover: all four construction-error branches,
``min == max`` allowed as exact-length, min-only passes at/above
+ fails below, max-only passes at/below + fails above, both
bounds' closed-range pass + below-min + above-max fail paths,
empty answer (``obs.final_response is None``) correctly reports
length 0, scorer name formatting for min-only / max-only /
both, and measure always carries the observed length.

**Decisions / trade-offs.**
* Character-based, not token-based. Operators who need token
  ceilings layer ``TokensWithin`` alongside; a character
  gate doesn't need a tokenizer dependency and works
  identically across models.
* At-least-one-bound required at construction, not at call
  time. Fails fast when the case file loads, not on every
  invocation that silently asserts nothing.
* Empty answer (no final response) has length 0 — same
  contract the rest of the scorer family uses. Cases that
  need to fail on "no response at all" pair this with
  ``NoErrors``.
* ``min_chars == max_chars`` is allowed. An operator asserting
  a specific-length response (e.g. "yes/no answer") is a
  legitimate use; rejecting equality would force them to
  write two inequality scorers.

**Next suggested action:** `Extend Phase 5 §12 with a
\`TokenDeltaWithin(max_tokens, baseline=None)\` scorer: when a
baseline capture is attached (via \`case.baseline\`), assert
the token delta between observed and baseline runs stays
within a threshold. The existing baseline differ reports the
delta but never gates CI on it; this scorer lets operators
catch a prompt change that quietly doubled tokens without
diverging tool order (which would trip the existing
regressed=True flag).`

## 2026-04-23 — Phase 5 §10: invocations-ceiling

**Shipped** ``InvocationsWithin(max_count)`` — the aggregate
"don't loop forever" cap. `ToolCalled(..., times=N)` pins
per-tool counts; this scorer pins the total across every tool,
so a prompt regression that starts over-calling an arbitrary
tool surfaces without one scorer per tool.

* **`InvocationsWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring `LatencyWithin` / `TokensWithin` shape.
  Reads ``len(obs.invocations)`` — every tool call the
  orchestrator actually dispatched, regardless of which tool.
  Inclusive at-limit comparison; failure detail surfaces both
  actual and ceiling; measure carries the actual count.
* **Edge cases** — zero invocations passes any non-negative
  threshold (no-tools cases, blocked-before-tools cases, run-
  errored cases all report ``len([]) == 0``). Same-tool
  repeated invocations count as separate entries, which is the
  right behaviour for a "loop cap" assertion.
* **Exports** — added to `frok.evals.__all__` alphabetically.

**Verification.** `python3 -m pytest -q` → 562 passed in 1.65s
(7 new). Tests cover: pass under the ceiling with `measure`
populated, inclusive at-limit passes, over-ceiling fails with
both values in detail, zero invocations passes any non-
negative threshold, no-tools case passes any cap,
same-tool-repeated correctly counts each invocation, and the
scorer name includes the configured ``max_count`` for
aggregated reports to grep on.

**Decisions / trade-offs.**
* Aggregate across every tool, not per-tool. The per-tool
  variant is already ``ToolCalled(name, times=N)``. This is
  the "don't loop forever" cap; enumerating every tool's
  count would bury the real signal.
* Same-tool repeated invocations each count as one. A case
  that legitimately calls ``search`` three times can set
  ``max_count=3``; a case that calls it twice on purpose
  then blows up to 15 on a prompt regression will fire the
  scorer.
* No matching ``min_count`` ("at least N calls"). Operators
  who want "tool was called at least once" use
  ``ToolCalled(name)``; "at least N across any tool" hasn't
  come up. YAGNI.
* Zero-invocations path passes by default. A case that
  failed before any tool dispatch has a real signal
  (``NoErrors``, missing final response); double-tapping via
  an invocation-cap assertion would bury it.

**Next suggested action:** `Extend Phase 5 §11 with an
\`AnswerLength(min_chars=None, max_chars=None)\` scorer:
assert the assembled response length falls within a range.
Today's scorers assert answer CONTENT (\`AnswerContains\`,
\`AnswerMatches\`) but never answer LENGTH. A prompt
regression that starts producing one-word replies — or a
runaway prompt that emits 4000 tokens of preamble before the
actual answer — would both slip through the current scorer
set without a dedicated length gate.`

## 2026-04-23 — Phase 5 §9: latency-ceiling

**Shipped** ``LatencyWithin(max_ms)`` — the wall-clock gate that
pairs with ``TokensWithin`` (cost). CI runs now have a cheap way
to catch a prompt or tool-use pattern that quietly doubled
latency after a model swap.

* **`LatencyWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring ``TokensWithin``'s shape. Reads
  ``obs.total_latency_ms`` (the root span's ``duration_ms``).
  Inclusive comparison: at-limit passes, strictly-over fails.
  Failure detail surfaces both the actual and the ceiling;
  ``measure`` carries the observed duration for aggregate
  reports.
* **Zero-latency fallback** — a run that errors before a root
  span closes reports 0.0 ms from the underlying `Observation`
  helper. The scorer passes any non-negative threshold in that
  case: the right signal for a failed run is ``NoErrors``, not
  a latency assertion. Documented in the scorer docstring.
* **Exports** — added to `frok.evals.__all__` so case-file
  authors can ``from frok.evals import LatencyWithin``.

**Verification.** `python3 -m pytest -q` → 555 passed in 1.68s
(7 new). Tests cover: pass under the ceiling with measure
populated, inclusive at-limit passes, over-limit fails with
both values in detail, missing root span → zero latency →
passes a non-negative threshold, missing root span + a
negative ceiling (pathological, but documents the compare),
run-error observation still passes (not the scorer's job),
and the scorer name includes the configured ``max_ms`` for
aggregated reports to grep on.

**Decisions / trade-offs.**
* Read from the observation's ``total_latency_ms``, not
  wall-clock time measured by the scorer. Cases run under
  repeats / parallel jobs / streaming — the only honest
  duration is what the root span recorded.
* Inclusive at-limit. An operator setting ``max_ms=500``
  usually means "at most 500 ms", not "strictly less than
  500 ms". Mirrors ``TokensWithin``.
* Zero-latency fallback passes by default. Failed runs
  already fail through the scorer stack (no final response,
  ``NoErrors`` trips, etc.); having latency-ceiling double-
  tap would bury the real failure under a misleading one.
* No separate ``min_ms`` (latency floor). We haven't seen a
  real need for "assert the model took at least N ms"; add
  if and when it comes up. YAGNI.

**Next suggested action:** `Extend Phase 5 §10 with an
\`InvocationsWithin(max_count)\` scorer: assert the total
number of tool invocations on a case stays below a threshold.
Complements \`ToolCalled(..., times=N)\` (per-tool exact count)
with an aggregate "don't loop forever" cap. Catches a prompt
regression that starts over-calling tools without having to
enumerate them in a scorer per tool.`

## 2026-04-23 — Phase 5 §8: tool-args-regex

**Shipped** ``ToolArgsMatch(name, regex, field=None, flags=0)`` —
the fuzzy counterpart to ``ToolArgsSubset``'s exact-equality
check. Operators can now assert "the tool call's query field
contains the user's question verbatim" without hand-writing a
scorer per case.

* **`ToolArgsMatch`** (`frok/evals/scorers.py`) — frozen
  dataclass. Two modes:
  * ``field=None`` — matches against ``json.dumps(args,
    sort_keys=True, default=str)``. Useful for "something
    anywhere in the args" assertions; sorted keys mean a
    regex can safely anchor on layout.
  * ``field="<key>"`` — matches against ``str(args[field])``.
    Missing keys surface as ``<missing>`` in the failure
    detail rather than silently skipping.
* **Matching semantics** — ``re.search`` (partial, like the
  existing ``AnswerMatches``); operators anchor with
  ``^``/``$`` when they want exact match. ``flags`` passes
  through so ``re.IGNORECASE`` etc. work.
* **Error handling** — invalid regex patterns fail the
  scorer with ``"invalid regex 'pat': <re.error>"`` rather
  than raising out of the runner. Matches the pattern used
  everywhere else in the codebase (e.g. `--filter re:...`).
* **Scorer name** — ``tool_args_match[<tool>:<field>]`` when
  a field is pinned, ``tool_args_match[<tool>]`` otherwise.
  Aggregate reports can grep by tool, field, or both.
* **Measure** — on success, the haystack that matched
  (JSON string or field value). Useful when post-hoc diffing
  runs.

**Verification.** `python3 -m pytest -q` → 548 passed in 1.57s
(14 new). Tests cover every branch: field-specific match /
fail / missing-field-placeholder, non-string values
stringified before regex (ints, lists), whole-args matching
anywhere in the JSON, sort-keys behaviour lets a regex anchor
on layout, tool-not-invoked fails cleanly, multi-invocation
semantics (any single match wins, no-match lists everything
seen), ``re.IGNORECASE`` via flags, anchored regex via
``re.search`` + ``^/$``, invalid regex degrades to a clean
fail, and scorer-name formatting covers both field-pinned and
whole-args modes.

**Decisions / trade-offs.**
* Field OR whole-args, not both. An operator who needs
  "any of two fields" can write two scorers; keeping the API
  one-argument-at-a-time keeps the signature readable.
* Measure carries the full haystack on pass, not just the
  matched substring. Easier for aggregated reports to surface
  "what the model actually sent"; the regex caller already
  has the pattern.
* Non-string args (ints, lists, dicts) are ``str()``'d before
  regex. Catches "the model called this with a numeric id
  ending in 42" without forcing the operator to JSON-encode
  the field by hand. The full-args mode JSON-encodes instead,
  which is the right choice when the shape matters.
* Invalid regex fails the scorer, doesn't raise. Every other
  user-facing regex in the codebase (CLI ``--filter re:...``,
  ``AnswerMatches``) follows this rule; cases shouldn't be
  able to crash the runner with a typo.

**Next suggested action:** `Extend Phase 5 §9 with a
\`LatencyWithin(max_ms)\` scorer: assert the case's root-span
duration_ms stays below a threshold. Complements
\`TokensWithin\` (cost ceiling) with a wall-clock ceiling for
CI — cheap way to catch a prompt or tool-use pattern that
quietly doubled latency on a model swap.`

## 2026-04-23 — Phase 5 §7: response-model-scorer

**Shipped** ``ResponseModelIs(expected)`` — completes the
model-regression loop. ``EvalCase.model`` (§6) pins the
*request*; this scorer pins the *response*. Together they catch
silent provider-side swaps that a request-only assertion would
miss.

* **`ResponseModelIs`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring every other scorer shape.
  `obs.final_response` None → clean ``Score.fail`` ("no final
  response — run failed before a model could be reported");
  mismatch → fail with both expected + actual in the detail;
  empty-string model is treated as a mismatch, not a pass.
  `measure` carries the actual model string so aggregated
  reports can surface which model actually served.
* **Export** — added to `frok.evals` public `__all__` so
  case-file authors can ``from frok.evals import
  ResponseModelIs``.

**Verification.** `python3 -m pytest -q` → 534 passed in 1.48s (7
new). Unit tests cover match (passes, measure carries value),
mismatch surfaces both values in detail + measure, missing
final-response fails cleanly, empty-string model is a
mismatch, and the generated scorer name includes the expected
value (grepped by aggregated reports). Integration tests run
the scorer through ``EvalRunner`` end-to-end: a case with
``model="grok-4-fast"`` + ``ResponseModelIs("grok-4-fast")``
passes when the server honours the pin, fails when the server
silently echoes ``grok-4-STALE`` — exactly the silent-swap
scenario the scorer was written for.

**Decisions / trade-offs.**
* Named `ResponseModelIs`, not `AnswerMatchesModel`. The
  suggestion in the prior §'s "next action" used the looser
  phrasing; renaming here for parity with `ToolCalled` /
  `NoErrors` / `ResponseModelIs` reads as "predicate about
  the response's model". Scorer names are API; getting them
  right matters.
* Strict string equality, no fuzzy matching. A "starts-with"
  or regex variant can layer on later if operators need to
  pin a model family (e.g. ``grok-4*``); today's need is
  exact-version regression.
* Empty-string model fails rather than passing on string
  equality with ``""`` (if expected happened to be empty).
  A server that returned no model isn't honouring the pin
  by accident — fail loudly.
* No special-case for no-tools vs tools paths. The scorer
  reads ``obs.final_response.model``; both paths populate
  that identically, so one implementation handles both.

**Next suggested action:** `Extend Phase 5 §8 with a
\`ToolArgsMatch(name, regex=...)\` scorer: assert that at
least one invocation of tool \`name\` has arguments matching
a regex (or a JSON-schema predicate). The existing
\`ToolArgsSubset\` only checks exact key/value matches;
regex / schema unlocks fuzzier assertions like "the query
string contains the user's question verbatim" without the
operator hand-writing a scorer per case.`

## 2026-04-23 — Phase 5 §6: model-override

**Shipped** per-call model overrides. Case authors can now pin a
specific model per `EvalCase` without scaffolding a second client
— the thing you need when regression-testing a model-version
upgrade (grok-4 → grok-4-fast, etc.).

* **`GrokClient`**
  * ``chat(..., model=...)`` and ``chat_stream(..., model=...)``
    accept an explicit override. Precedence:
    ``model kwarg > self.model``. Unlike ``tool_choice`` there
    is no "omit" path — a model is always on the wire.
  * ``effective_model = model or self.model`` computed once per
    call and used for the payload, the ``grok.chat`` /
    ``grok.chat_stream`` span attr, and the fallback used when
    the server's response omits the ``model`` field.
* **`ToolOrchestrator.model`** — new field, defaults to
  ``None`` (defer to ``client.model``). Passed to both
  ``chat()`` (non-stream path) and ``_streamed_turn``'s
  ``chat_stream()`` call, so every turn of a multi-turn tool
  run uses the same model.
* **`EvalCase.model`** — new optional field. The runner wires
  ``case.model`` into the orchestrator (tools path) and into
  both ``chat()`` / ``chat_stream()`` calls (no-tools path,
  streaming or not). ``None`` defers to the client default.

**Verification.** `python3 -m pytest -q` → 527 passed in 1.55s (13
new). Tests cover: ``chat`` without kwarg uses ``client.model``,
kwarg overrides, server response with no ``model`` field falls
back to ``effective_model`` (not ``client.model``), same three
paths for ``chat_stream``, ``grok.chat`` and ``grok.chat_stream``
span attrs report the effective model, orchestrator's ``model``
flows through *every* turn of a multi-turn run, orchestrator
defaults to ``client.model`` without override, ``EvalCase.model``
reaches the wire on no-tools / tools / streaming paths, and
``EvalCase.model=None`` correctly defers to ``client.model``.

**Decisions / trade-offs.**
* Two-level precedence (explicit > client), not three like
  ``tool_choice``. A model must always be on the wire, so there
  is no "omit the key" tier; the client default is the floor.
* ``EvalCase.model = None`` defers to the client default. We
  could have defaulted to ``"grok-4"`` and let ``None`` mean
  "use newest", but that couples the schema to a specific
  model name. Deferring to ``client.model`` keeps the case
  portable across client configurations.
* Span attr reflects the *effective* model, not the request or
  response. If a case overrides to ``grok-4-fast`` the span
  says ``grok-4-fast`` even if the server returns something
  odd. Post-hoc trace inspection needs the effective
  declaration, not the server echo.
* ``ToolOrchestrator.model`` is a field rather than a per-run
  argument. The orchestrator is already constructed per-case
  in the runner; adding one more constructor kwarg is lower-
  ceremony than threading it through ``run()``.
* ``EvalCase.model`` is a plain ``str | None``; the case-file
  API stays simple. When richer model-routing is needed (per-
  turn swaps, fallback chains), it can layer on via a custom
  ``make_client`` or a future ``frok.models`` module without
  breaking this surface.

**Next suggested action:** `Extend Phase 5 §7 with
\`AnswerMatchesModel(expected)\` scorer: asserts the
assembled GrokResponse.model equals the expected string.
Complements \`EvalCase.model=...\` by proving the right model
actually served the request (guards against silent mid-flight
model swaps on the provider side). Small but exactly the kind
of assertion a model-upgrade regression test needs.`

## 2026-04-23 — Phase 5 §5: tool-choice

**Shipped** a first-class ``tool_choice`` surface so cases can
assert the model *will* / *won't* / *must use tool X* rather than
hoping `"auto"` does the right thing. The orchestrator
hard-coded ``"auto"`` until today; lifting it to an explicit
kwarg unlocks pinned-behaviour tests.

* **`GrokClient`**
  * New ``tool_choice: str | dict | None = None`` field — the
    client-level default; ``None`` omits the key from the
    payload entirely.
  * ``chat(..., tool_choice=...)`` and
    ``chat_stream(..., tool_choice=...)`` accept an explicit
    kwarg. Precedence: explicit kwarg > client-level default >
    omit. Value flows to the top-level ``tool_choice`` field of
    the request body (same JSON shape xAI/OpenAI already
    consumes).
* **Config**
  * ``ClientConfig.tool_choice: str | dict | None`` plumbs
    through ``build_client`` → ``GrokClient.tool_choice``. Env
    ``FROK_CLIENT_TOOL_CHOICE=required`` works; dict-shaped
    values come through file (JSON / TOML) or CLI overrides.
  * ``to_toml`` emits dicts as TOML inline tables
    (``tool_choice = {type = "function", function = {name =
    "add"}}``) which ``tomllib`` round-trips cleanly.
  * ``to_env`` JSON-encodes dict values so the output is
    shell-injectable: ``FROK_CLIENT_TOOL_CHOICE={"type":...}``.
  * ``to_json`` was already dict-friendly; no change needed.
  * The unset-value render path still prints
    ``# tool_choice  (unset)`` in TOML.
* **`ToolOrchestrator`**
  * Switched to passing ``tool_choice`` via the new explicit
    kwarg instead of stuffing it into ``extra``. Cleaner;
    ``_streamed_turn`` also uses the explicit kwarg.
  * Default remains ``"auto"``.
* **`EvalCase.tool_choice`** — cases can pin behaviour without
  a custom client. The runner forwards
  ``case.tool_choice`` into ``ToolOrchestrator(tool_choice=…)``;
  ``None`` falls back to the orchestrator's ``"auto"``. No-tools
  cases ignore it (the orchestrator isn't engaged).

**Verification.** `python3 -m pytest -q` → 514 passed in 1.56s (21
new). Tests cover: ``chat`` omits the key by default, explicit
kwarg passes through, client-default applies when kwarg absent,
explicit wins over client default (including dict-shaped), same
three paths for ``chat_stream``, orchestrator forwards its
``tool_choice`` on *every* turn (not just the first), the default
is ``"auto"``, EvalCase string + dict values reach the wire via
the runner, config defaults to ``None``, env sets a string,
file accepts a dict, ``build_client`` propagates, render for all
three formats + inline-table TOML + JSON-in-env + the unset
comment.

**Decisions / trade-offs.**
* Three-level precedence (explicit > client > omit). "Omit"
  means the server picks, which is the right default for
  free-form chats; the client-level override is a convenient
  middle ground for config profiles (e.g. "force no tools in
  prod"), and the explicit kwarg is per-call surgery.
* Dropped the "stuff into extra" trick. Two paths to the same
  field are a smell; one typed kwarg makes the intent visible
  in every call site and in the spans.
* `EvalCase.tool_choice` defaults to ``None`` (fall back to
  orchestrator's ``"auto"``), not ``"auto"`` directly. Keeps
  the runner aware of "user didn't opt in"; a future global
  eval-harness config could apply a different default without
  having to parse out ``"auto"``.
* Render layer now handles dicts natively. We committed to
  supporting non-string `tool_choice` values; the
  ``config show`` output would otherwise stringify them into
  garbage. Inline-table TOML is the cleanest representation
  for our shallow nested schemas.
* Env-var JSON encoding is a compromise. Operators who want a
  dict via env need ``FROK_CLIENT_TOOL_CHOICE='{"type":...}'``,
  which is ugly but unambiguous; string values like
  ``"none"`` / ``"required"`` stay plain.

**Next suggested action:** `Extend Phase 5 §6 with
GrokClient.chat(..., model=...): allow per-call model overrides
so EvalCase authors can pin a specific model for a case
(regression-testing a model upgrade without scaffolding two
whole clients). Same precedence ladder as tool_choice —
explicit kwarg > client.model > no override — and surface on
EvalCase.model.`

## 2026-04-23 — Phase 5 §4: stream-tools

**Shipped** streaming through the `ToolOrchestrator` loop. `frok
run --stream` on a tools-enabled case now gives live feedback for
every chat turn instead of silently falling back.

* **`ToolOrchestrator.run(stream_sink=...)`** — new kwarg. Each
  loop iteration checks ``self.client.streaming_transport``:
  * **Available.** Issues `chat_stream` for the turn, forwards
    content deltas to the sink, and emits a ``\n>>> turn N\n``
    marker before each call. Final answer streams token-by-
    token; earlier tool-call turns are marker-only (their SSE
    payload has no content).
  * **Missing.** Falls back to non-stream `chat` silently —
    same behaviour callers already relied on. Preserves the
    "pass stream_sink unconditionally" contract.
* **Runner wiring** — `EvalRunner._execute` now forwards
  `stream_sink` into `orch.run(..., stream_sink=...)` instead of
  dropping it on the tools path. The "tools always silently
  fall back" comment disappears.
* **Telemetry** — `tool.run` span gains a ``streamed`` attr
  (True when the orchestrator used `chat_stream`, else False).
  Operators grepping the JsonlSink can now spot which runs
  streamed without replaying.
* **Helper extracted** — `ToolOrchestrator._streamed_turn`
  consumes `chat_stream`, forwards deltas, returns the final
  `GrokResponse`. Keeps the loop body readable and fails loudly
  (`ToolError`) if the stream ends before a final chunk
  arrives.

**Verification.** `python3 -m pytest -q` → 493 passed in 1.55s (7
new). Library tests cover: two-turn stream emits per-turn
markers + final-answer deltas in the right order + both turns
sent `stream=true`, fallback when `streaming_transport` is
missing (non-stream transport serves both turns, sink stays
empty), backward-compat path where `stream_sink` is None
continues to use `chat()` even when `streaming_transport`
exists, `tool.run.streamed` attr is True under streaming and
False without it, and short-stream (no explicit `[DONE]`) still
produces a clean final. CLI test
``test_stream_flows_through_tool_orchestrator_when_streaming_transport_set``
closes the end-to-end loop: a case with `tools=[add]` +
`streaming_transport` + `--stream` actually emits the turn
markers + streamed final answer via `frok run`.

**Decisions / trade-offs.**
* Per-turn markers (``>>> turn N``) rather than silent
  streaming. Tool-use cases have natural turn boundaries; the
  marker gives operators something to anchor on when scanning
  live output.
* Marker printed even for tool-call turns that produce no text
  content. Without it, the operator would see "nothing" for
  the first N-1 turns — indistinguishable from a hung process.
* Streaming capability is detected via `streaming_transport`
  presence, not a separate flag. One knob per concept;
  operators who configure a streaming transport implicitly
  opt into per-turn streaming.
* Telemetry gets a `streamed=bool` attr rather than a
  separate span name. Eval-harness scorers and trace-inspect
  renderers can already filter on span data; splitting the
  span into `tool.run.streamed` vs `tool.run.chat` would
  fragment the trace tree for no payoff.
* Kept the orchestrator non-stream path untouched when
  `stream_sink is None`. Existing callers (and the 74 tests
  covering them) continue to exercise the same code they did.

**Next suggested action:** `Extend Phase 5 §5 with
GrokClient.chat(..., tool_choice=) and a matching config knob:
expose "force call tool X" / "forbid tool use" semantics so
cases can assert that the model either uses a specific tool or
stays free-form. The orchestrator currently hard-codes
tool_choice="auto" — graduating it to a configurable argument
unlocks tests that pin tool-selection behaviour.`

## 2026-04-23 — Phase 5 §3: stream-cli

**Shipped** ``frok run --stream`` — live progress at the CLI. Long
answers no longer look hung; operators see tokens as the model
produces them while the `EvalReport` and scorers still get the
same assembled `GrokResponse` they did before.

* **`EvalRunner.run_case(..., stream_sink=callable)`** threads a
  per-delta callback into `_execute`. No tools: the runner uses
  ``client.chat_stream`` and forwards each content delta to
  `stream_sink` as it arrives, finalising into the same
  `GrokResponse` shape the non-stream path produces. Tools
  present: silently falls back to the non-stream orchestrator
  loop so callers can pass `stream_sink` unconditionally.
* **`build_client`** learned a `streaming_transport` kwarg; the
  `_default_client_factory` wires
  ``frok.clients.transports.urllib_streaming_transport`` so
  `--transport real` + `--stream` works out of the box.
* **`frok run --stream`** CLI flag
  * Per-case stderr header: ``\n>>> <case-name>\n``; each delta
    flushes to stderr raw; a trailing newline separates the
    stream from the report.
  * Incompatible with ``--jobs > 1`` — raises `CliError`.
    Interleaved stderr from concurrent tasks would be useless;
    operators who want both should use ``--summary-json`` and
    parse the machine-readable output instead.
  * Compatible with ``--repeat`` (serial stream per repeat),
    ``--capture-baseline``, ``--use-baseline``,
    ``--fail-on-regression``.

**Verification.** `python3 -m pytest -q` → 486 passed in 1.52s (8
new). Tests cover: argparse default + flag recognition,
``--stream`` writes the per-case header + every delta to stderr
(stub streaming transport scripts "Hello", ", ", "stream!"),
scorers still see the assembled final (case passes under
``--fail-on-regression``), tools-enabled case silently falls back
(header still prints, no deltas, non-stream transport fires),
``--stream`` + ``--jobs 2`` rejected with a specific error,
``--stream --jobs 1`` allowed, and a case whose `make_client`
omits `streaming_transport` surfaces the client's "no
streaming_transport" error as a case-level failure (not a CLI
crash).

**Decisions / trade-offs.**
* Output lands on stderr, not stdout. The Markdown report is
  stdout's job; streaming deltas are operator feedback that
  should survive pipes redirecting stdout.
* Tools-enabled cases silently fall back rather than streaming
  through the orchestrator loop. Each orchestrator iteration
  is its own chat call with its own streamed deltas —
  merging those into a coherent single-case display would need
  per-iteration headers / markers, which is design-work we
  haven't done yet. Fall-back keeps the flag usable now.
* ``--jobs > 1`` is a hard error, not a soft one. We could have
  serialised the stderr writes with a lock, but the result
  would be a jumble of "case A token / case B token" that
  nobody could read. Two concurrent cases can still run under
  ``--jobs 2`` — they just can't both stream.
* `streaming_transport` kwarg on `build_client` rather than a
  second factory. One config, one builder; the extra parameter
  defaults to None so existing callers are unchanged.
* Newline after every stream. The Markdown report starts on a
  fresh line regardless of whether the last delta ended with
  one.

**Next suggested action:** `Extend Phase 5 §4 with streaming
through the ToolOrchestrator loop: when --stream is set on a
tools-enabled case, yield deltas from each chat turn prefixed
with a per-turn marker (e.g. >>> turn 1, >>> turn 2), so tool-
use runs get the same live feedback as no-tools runs. Removes the
current silent fallback.`

## 2026-04-23 — Phase 5 §2: streaming

**Shipped** ``GrokClient.chat_stream`` — an async generator that
yields ``StreamChunk``s as SSE data arrives. Today's ``chat``
waits for the whole response; streaming unlocks live progress
indicators in the CLI and cuts apparent latency on long answers.

* **`StreamingTransport` protocol** (`frok/clients/grok.py`) —
  one-call shape returning ``(status, headers,
  AsyncIterator[bytes])``. Consistent with the existing
  `Transport` contract; callers await once, then iterate.
* **`StreamChunk(delta, tool_calls, finish_reason, is_final,
  response)`** frozen dataclass. Non-final chunks carry
  incremental text; the final chunk has ``is_final=True`` +
  ``response`` = the assembled `GrokResponse` (post-flight
  safety applied).
* **`GrokClient.chat_stream(messages, …)`**
  * Pre-flight safety runs on every inbound message (same shape
    as `chat`); a blocked prompt raises before any network call.
  * POST carries ``stream: true`` + an ``Accept: text/event-
    stream`` header; SSE chunks are parsed line-by-line via a
    module-level ``_iter_sse_events`` helper that tolerates
    blank / comment lines and malformed JSON.
  * Content deltas are yielded live as ``StreamChunk(delta=…)``.
    Tool-call deltas are accumulated via
    ``_merge_tool_call_delta`` and materialised as ``ToolCall``s
    on the final chunk.
  * After the stream ends (either ``[DONE]`` sentinel or
    connection close), post-flight safety runs on the
    accumulated content. If blocked, the generator raises
    ``GrokError`` instead of yielding the final chunk — the
    deltas already emitted are the caller's problem to redact;
    the contract is documented.
  * Emits a ``grok.chat_stream`` telemetry span with ``model``,
    ``message_count``, ``chunks``, ``content_chars``,
    ``tool_calls``, ``finish_reason``, and safety counts.
  * Shared pre-flight logic extracted into ``_preflight`` so
    `chat` and `chat_stream` can't drift on safety semantics.
* **`urllib_streaming_transport`** (`frok/clients/transports.py`)
  — stdlib streaming transport. Line-by-line read via
  ``asyncio.to_thread`` so the event loop isn't blocked; swap in
  httpx/aiohttp when production volume arrives. Handles 4xx/5xx
  by returning the status + a one-shot body iterator so
  `chat_stream` can surface a meaningful `HttpError`.

**Verification.** `python3 -m pytest -q` → 478 passed in 1.49s (19
new). Library tests cover `_iter_sse_events` (happy-path JSON,
``[DONE]`` sentinel, non-data/blank/comment lines, malformed-JSON
tolerance), `_merge_tool_call_delta` (fragment assembly, index
growth), and `chat_stream`: deltas yielded in order + request
body carries ``stream: true`` + ``Accept: text/event-stream``,
stream without ``[DONE]`` sentinel still produces a final chunk,
pre-flight blocks unsafe prompts before any network hit, PII
rewrites on prompts reach the wire, post-flight blocks unsafe
accumulated content (deltas already emitted), empty ruleset
skips safety, missing streaming_transport / empty messages / 4xx
all error correctly, tool-call deltas reassemble across fragments
and land as `ToolCall` on the final chunk, telemetry span carries
the expected attrs + records ``safety_blocked`` on a prompt
block.

**Decisions / trade-offs.**
* Post-flight safety runs *after* the stream completes, not
  chunk-by-chunk. Partial-text regex matching would be
  unreliable (a rule that fires on ``"guarantee"`` would miss a
  stream that yields ``"guar"`` + ``"antee"``); waiting for the
  full content is the honest contract.
* Live deltas are the caller's responsibility to redact when
  safety blocks the final. A CLI that renders live tokens
  should clear its buffer on `GrokError` rather than trust
  what it already drew — documented in the method docstring.
* New `StreamingTransport` protocol rather than overloading the
  existing `Transport`. Different return shape, different
  consumer pattern; muddling them would cost more than a second
  protocol type.
* Shared `_preflight` helper rather than duplicating the safety
  loop. The stream branch and the non-stream branch can't
  silently diverge on what counts as a blocked prompt.
* Ships with a stdlib streaming transport because the lack of
  one would be the first blocker for any real use. Throughput
  is modest (thread-hop per line); good-enough for a CLI live-
  progress display; operators with volume swap in httpx.

**Next suggested action:** `Extend Phase 5 §3 with \`frok run
--stream\`: flip the runner to use \`chat_stream\` + print each
delta to stderr as it arrives, so a live \`frok run cases/\*\`
gives operators a progress indicator. Cases still assemble a
normal \`EvalReport\` (stream finalises into the same
\`GrokResponse\`), so scorers and baseline diffs remain
untouched. Closes the "why does my long answer look hung?" UX
gap.`

## 2026-04-23 — Phase 5 §1: init-transport

**Shipped** ``frok init --transport {stub,real}`` — the "how do
I flip from stub to real?" gap-closer. Every example's docstring
previously told operators to swap the transport by hand; now
there's a flag that produces a ready-to-run live template.

* **New template** — ``_SMOKE_CASE_REAL`` is a ~20-line
  module: a single ``EvalCase`` with loose scorers
  (``AnswerMatches(r"\S")``, ``NoErrors()``), no ``make_client``,
  no ``_StubTransport``. The runner's default factory picks it up
  and wires ``frok.clients.transports.urllib_transport`` +
  whatever `FrokConfig.client` carries, so the only thing the
  operator needs to set is ``FROK_CLIENT_API_KEY``.
* **`_TRANSPORT_TEMPLATES`** map — ``stub`` → existing
  scripted-fake template; ``real`` → the live template. Keeps
  argparse's ``choices=`` list and the template lookup in one
  place.
* **Next-steps message is conditional**. Stub path still says
  "no API key is required yet"; real path walks the operator
  through setting ``FROK_CLIENT_API_KEY`` → running ``frok
  doctor`` → running the case for real.
* **Composition preserved**. ``--transport real --example
  tools`` still scaffolds the stub-backed ``cases/tools.py``;
  only the *smoke* case gets swapped. The examples rely on
  scripted tool-call sequences / canned descriptions that the
  real model can't be asked to reproduce deterministically.

**Verification.** `python3 -m pytest -q` → 459 passed in 1.56s (11
new). Tests cover: argparse default + real + bogus rejection,
stub default preserves every previously-asserted marker
(``_StubTransport`` / ``make_client`` / ``api_key="stub"``) and
the "no API key is required" next-steps line, real-template
content (no stub markers, FROK_CLIENT_API_KEY surfaced in the
docstring, module parses via ``ast.parse``, loose scorers
present), real template's next-steps block mentions
FROK_CLIENT_API_KEY + ``frok doctor``, real case errors with
exit 2 on a missing api_key (surfaced as ``ConfigError``), real
case runs green end-to-end when ``urllib_transport`` is
monkey-patched to a stub and an api_key is set (exercising the
exact default-factory code path), and real + ``--example``
composes correctly (smoke swapped, example stubs intact).

**Decisions / trade-offs.**
* Only the smoke case gets a real-transport variant. Examples
  script specific tool calls; the live model can't be promised
  to emit exactly those, and a "real" example that sometimes
  fails would undermine the first-impression principle the
  examples were written for.
* Loose scorers on the real smoke case (``\S`` regex). The point
  is "the call succeeded and the model said something"; tight
  assertions would force every operator to tune them per model
  on the first run.
* Default stays ``stub``. Backwards compatibility with the §1
  scaffold + zero surprise on a first-time ``frok init`` with
  no flags.
* Test for live-path uses a monkey-patched ``urllib_transport``
  imported into ``frok.cli.run``'s namespace. Production code
  paths are exercised end-to-end except for the wire itself —
  which is exactly the boundary a unit test should cut at.

Phase 5 opens with real-integration scaffolding; the remaining
§s can focus on the actual xAI API contract (streaming, tool-
choice hints, model-version swapping) now that the flip-to-real
path is a flag rather than a manual edit.

**Next suggested action:** `Extend Phase 5 with streaming support
in GrokClient: \`chat_stream(messages, …)\` yields content tokens
as they arrive over the wire, honoring the same safety / telemetry
hooks as \`chat()\`. Today a live run waits for the whole response;
streaming unlocks live progress indicators in the CLI and shorter
apparent latency on long answers.`

## 2026-04-23 — Phase 4 §6: help-polish

**Shipped** the root `frok --help` rewrite. First-time operators
who type `frok --help` now see what to do, not just a list of
subcommand names.

* **Description** names the "onboarding triple" (`init`,
  `doctor`, `run`) alongside a one-line mission statement. This
  block prints BEFORE the subcommand table so readers don't have
  to guess which three verbs to try first.
* **Epilog** lists the everyday operations (`config show`, `run
  --list`, `trace inspect`, `eval diff`, `eval summarize`) as
  copy-pasteable one-liners plus a "Reporting bugs: include the
  output of `frok version`" pointer.
* **Subcommand order** reshuffled for help-output UX: init →
  doctor → run → config → eval → trace → version. Argparse
  displays subparsers in registration order; the previous order
  was chronological by feature development, which is exactly
  backwards from what an operator wants to read.
* **`RawDescriptionHelpFormatter`** preserves the multi-line
  description + epilog layout. Default `HelpFormatter` collapses
  newlines, which would have reduced the block to one paragraph.
* **No external URLs** in the epilog. `CLAUDE.md` guidance says
  never to emit URLs we're not certain of, so the help points at
  local commands and files rather than a README link.

**Verification.** `python3 -m pytest -q` → 448 passed in 1.40s (9
new). Tests lock in: description names the ecosystem + onboarding
triple, epilog includes the quick-start and everyday-ops blocks
and the bug-report pointer, the raw formatter is the one actually
wired (preventing a silent regression to collapsed whitespace),
subcommand listing starts with the onboarding triple and ends
with `version`, and the parser still requires a subcommand when
none is passed.

**Decisions / trade-offs.**
* Onboarding triple before alphabetical. Operators read the
  listing top-down; the first three names should be the ones
  they should type first.
* Epilog is text, not a table. A table reads well in tabular
  data but not as "here are some useful commands"; a plain
  two-column text block composes with every terminal and pipe.
* Pointer at `frok version` for bug reports rather than an
  issue-tracker URL. We don't publish that URL from this tree,
  and the command is the thing triage actually needs.
* Formatter choice is tested. Defaulting back to
  `HelpFormatter` silently would undo the layout without any
  functional breakage — exactly the kind of regression that
  asymptotically costs you users.

Phase 4 is now closed at the onboarding layer. Next up is Phase
5-ish work: real-integration scaffolding (`urllib_transport` swap
recipes, end-to-end live smoke harness, multi-repo release
plumbing).

**Next suggested action:** `Begin Phase 5 with \`frok init
--transport real\`: when set, the generated cases/smoke.py swaps
the stub transport for \`urllib_transport\` + a config-driven
api_key check, so operators graduating past the stub get a
ready-to-run live template instead of hand-editing the file.
Closes the "how do I flip from stub to real?" gap surfaced by
every example's docstring.`

## 2026-04-23 — Phase 4 §5: version

**Shipped** ``frok version`` — the triage primitive. Prints the
installed frok version, the Python it's running on, and the
platform string. Small but load-bearing: every bug report starts
with "what version?", and this answers it with one command.

* **`VersionInfo`** dataclass + `collect_version_info()` helper in
  `frok/cli/version.py`. Pulls `frok.__version__`,
  `platform.python_version()`, `platform.platform(aliased=True)`.
* **Output modes**:
  * default — ``frok 0.24.0 (Python 3.11.15, Linux-6.18.5-x86_64-with-glibc2.39)``
    on one line, pipe-friendly and eye-friendly.
  * ``--short`` — just the frok version
    (``$(frok version --short)`` is shell-usable).
  * ``--json`` — ``{"frok": …, "python": …, "platform": …}``.
* **Flag precedence**: ``--short`` wins over ``--json`` when both
  are passed. ``--short`` is the most specific ask and scripting
  users pass it for a reason.

**Verification.** `python3 -m pytest -q` → 439 passed in 1.33s (8
new). Tests cover: argparse defaults + flag recognition,
`VersionInfo` matches `frok.__version__` / runtime values, default
one-line shape + regex-verified Python version, ``--short`` emits
only the version string, ``--json`` is parseable + complete,
``--short`` + ``--json`` both set → short wins (not JSON), exit
code 0 across all three modes.

**Decisions / trade-offs.**
* ``--short`` wins over ``--json`` silently. Erroring on the
  combination would be strictly-correct but unhelpful; the
  interpretation is obvious.
* ``platform(aliased=True)`` rather than `system()` alone. Bug
  triage wants the glibc / kernel / arch string, not just
  "Linux".
* No ``--verbose`` mode that dumps site-packages, interpreter
  path, etc. YAGNI — operators who need that run the one-liner
  directly.

**Next suggested action:** `Wrap Phase 4 with a \`frok --help\`
polish pass: a root-level description line pointing operators at
\`frok init\` / \`frok doctor\` / \`frok run\` as the onboarding
triple, plus a short epilog linking the README. Small but makes
the first \`frok\` invocation self-explanatory instead of just
listing subcommands.`

## 2026-04-23 — Phase 4 §4: doctor

**Shipped** ``frok doctor`` — the "does my setup actually work?"
preflight. Loads the resolved `FrokConfig` (same env + file +
profile merging the real run uses), runs one check per Phase-2
subsystem, and reports a PASS / FAIL / SKIP line for each.

* **`Check(name, status, detail)`** dataclass; ``PASS`` / ``FAIL`` /
  ``SKIP`` constants used everywhere for consistent filtering.
* **Library-level checks** (`frok/cli/doctor.py`)
  * ``check_config`` — reports the resolved profile + source.
  * ``check_safety`` — builds the ruleset and reports active /
    disabled rule counts.
  * ``check_telemetry`` — builds the configured sink, then closes
    it. `jsonl` without a path fails here.
  * ``check_memory`` — SKIP when disabled; otherwise builds the
    store, does a `remember → recall → forget` round-trip, and
    reports ok. Fails loudly on unsupported embedders or I/O
    errors.
  * ``check_multimodal`` — reports vision/voice toggle state.
  * ``check_client_live`` — skipped without ``client.api_key`` or
    with ``--no-live``; otherwise fires a real
    ``client.chat([GrokMessage("user", "ping")])`` through
    ``urllib_transport`` and reports token usage + model.
    Transport is injectable for tests.
* **`frok doctor` CLI** — wraps `_collect_checks` + `render_markdown`
  (default) / `render_json` (``--json``). Flags: ``-c/--config``,
  ``-p/--profile``, ``-o/--output``, ``--json``, ``--no-live``,
  ``--fail-on-skip``. Exit codes: 1 on any FAIL, 1 on any SKIP
  under ``--fail-on-skip``, else 0. Config load failure surfaces
  as ``CliError`` (exit 2) — same shape as the rest of the
  Phase-3 family.

**Verification.** `python3 -m pytest -q` → 431 passed in 1.32s (26
new). Library tests cover each check (config source reporting,
safety rule counting + disabled-rule surfacing, telemetry null /
jsonl-missing-path / jsonl-valid-path, memory skip / round-trip /
unsupported embedder, multimodal toggle reflection, client-live
skip-without-api-key / skip-under-no-live / pass-with-stub /
fail-on-500) and the renderers (markdown section presence + total
line, JSON shape + round-trip). CLI tests cover argparse shape +
defaults, happy-path markdown, ``--json`` parseability, ``-o``
file write, ``--fail-on-skip`` exit 1 when anything skips,
telemetry-failure producing exit 1, ``--no-live`` skipping
client-live even with an api_key present, config-load failure
surfacing as CliError, and an explicit ``-c`` flag reaching the
config check.

**Decisions / trade-offs.**
* Live chat hits the real API by default when an api_key is
  present. The alternative — opt-in with `--live` — would
  silently SKIP the check that most operators actually want
  when they run doctor. ``--no-live`` is the escape hatch for
  offline / CI-without-secret cases.
* Memory check does a full remember → recall → forget cycle
  rather than just opening the DB. Catches embedder
  misconfigurations and WAL-mode surprises that a pure
  open-and-close wouldn't.
* ``--fail-on-skip`` opt-in. A SKIP almost always means "not
  configured yet, but not broken" — the default exit code
  should keep that honest. Operators enforcing a fully
  configured stack in CI get the strict mode with one flag.
* Transport is injectable on ``check_client_live`` but not on
  the other checks. Memory and telemetry are covered by the
  Phase-2 tests; what we need to isolate here is the network
  call.

**Next suggested action:** `Extend Phase 4 with \`frok version\`:
print the installed package version (from \`frok.__version__\`) and
the Python runtime it's running on (platform.python_version()).
Small but essential for bug reports — the first thing any triage
asks is "what version?"`

## 2026-04-23 — Phase 4 §3: init-list-examples

**Shipped** ``frok init --list-examples`` — a discoverability flag
that prints every available ``--example`` name alongside its
one-line description, so operators can explore the scaffold
catalog without reading the source. Mirrors the ``frok run
--list`` pattern that already closes the "what am I about to run?"
gap; this closes the "what could I scaffold?" gap.

* **`_example_summary(src)`** (``frok/cli/init.py``) — parses a
  template's module-level docstring via ``ast.get_docstring`` and
  returns the first non-empty line. Syntax errors / missing
  docstrings degrade to an empty string rather than raising — a
  broken template shouldn't prevent `--list-examples` from
  surfacing the names.
* **`format_examples_list()`** — sorts the examples alphabetically,
  computes a shared left-column width based on the longest name,
  and returns a two-column text block terminated by a trailing
  newline. Pipe-friendly out of the box (``frok init
  --list-examples | cut -d' ' -f1`` gives just the names).
* **CLI short-circuit** — ``--list-examples`` branches off at the
  top of ``init_cmd`` before any existence check or directory
  creation. ``--example`` / ``--force`` / ``path`` are ignored
  when ``--list-examples`` is set; no files are ever written.

**Verification.** `python3 -m pytest -q` → 405 passed in 1.18s (12
new). Tests cover: argparse shape (default False + flag
recognition), every example name appears in output, descriptions
match each template's docstring first line, output is
alphabetically sorted, `_example_summary` handles a syntax error
and a docstring-less module gracefully, CLI output matches
``format_examples_list()``, no files are written under any
combination of flags, and an existing ``CLAUDE.md`` in the target
directory is preserved verbatim (proves the short-circuit
precedes every write path).

**Decisions / trade-offs.**
* ``ast.get_docstring`` rather than regex splicing. The templates
  are real Python; parsing them is the right tool and costs
  nothing at run time (this flag is rare).
* Two-column text, no table-drawing chars or colors. Fits
  anywhere (CI logs, terminals without unicode, files), and is
  trivial to pipe through ``awk``/``cut``.
* Alphabetical sort rather than insertion order. Stable + obvious
  from the CLI output; operators don't have to guess the
  canonical order.
* ``--list-examples`` ignores the rest of the flags rather than
  erroring on unknown combinations. A preview flag shouldn't be
  strict about what else the operator typed — they're discovering
  the space, not committing to an action.

**Next suggested action:** `Extend Phase 4 with \`frok doctor\`:
a preflight health check that loads the resolved config, attempts
a tiny \`client.chat(...)\` through \`urllib_transport\` if
\`client.api_key\` is set (otherwise skips), verifies
\`MemoryStore\` can open + write to \`memory.path\` when
\`memory.enabled\`, and reports a concise pass/fail per subsystem.
Gives new users a definitive "your setup works" signal before
their first real run.`

## 2026-04-23 — Phase 4 §2: init-examples

**Shipped** ``frok init --example {tools,multimodal,memory}`` — a
repeatable flag that adds working reference cases alongside the
basic smoke scaffold. Each example runs green out of the box,
demonstrates one major Phase-2 surface, and carries a "production
swap" docstring pointing at the real transport/store choices.

* **`cases/tools.py`** — `@tool def add(a,b)` + a stub transport
  scripted for one tool call + one final answer; scorers:
  `AnswerContains("42")`, `ToolCalled("add", times=1)`,
  `NoErrors()`. Proves the ToolOrchestrator drives the loop
  end-to-end.
* **`cases/multimodal.py`** — a `GrokMessage` with `parts=(text,
  image_url)` built via `ImageRef.from_bytes(...).to_content_part()`
  and a stub that returns a canned description. The case runs
  without vision creds and shows the exact wire shape Grok
  expects for image messages.
* **`cases/memory.py`** — shared ``MemoryStore(":memory:",
  HashEmbedder(dim=64))`` exposed as two typed tools
  (``remember(text)``, ``recall(query, k)``). Stub scripts a
  remember → recall → final-answer sequence; ToolCalled + answer
  scorers confirm the model exercised both paths. Demonstrates
  the typical "memory as tools" pattern.
* **CLI wiring** — `--example NAME` is an `action="append"` with
  `choices=sorted(EXAMPLE_TEMPLATES)`. Unknown values are
  rejected by argparse before any I/O. `init_cmd` composes
  `TEMPLATES | {f"cases/{n}.py": EXAMPLE_TEMPLATES[n]}` so every
  existence check and ``--force`` guarantee from §1 applies to
  the example files too.

**Verification.** `python3 -m pytest -q` → 393 passed in 1.20s (16
new). Tests cover: argparse accepting known names and rejecting
unknown ones, default `--example` list is empty, no-flag scaffold
matches §1 exactly, each of the three examples scaffolds its
file, multi-flag composition, existence-abort on a pre-existing
example file, ``--force`` overwrite, each example running green
under ``frok run --fail-on-regression`` (parametrized over all
three), a tools-specific check that `ToolCalled` actually passed
(proves the orchestrator fired), a multimodal check that the
content parts hit the wire via direct import + runner, and a
memory check that both `remember` and `recall` were invoked.

**Decisions / trade-offs.**
* Examples live as template constants in `frok/cli/init.py`
  alongside the base templates — same zero-ceremony pattern from
  §1. Edits are Python commits.
* Each example uses a stub transport rather than
  ``urllib_transport``. The docstring calls out the swap; green
  runs out of the box matter more than "realistic" network
  behaviour.
* Memory example uses `:memory:` SQLite + a module-level shared
  store. The state survives the whole (case, run) and dies when
  the module is GCed. Production users swap to a file path;
  that's one line.
* Multimodal example builds parts directly in the `GrokMessage`
  rather than spinning up a `MultimodalAdapter`. The adapter is
  showcased implicitly via `ImageRef.to_content_part()`; going
  through the adapter would have required its own chat
  invocation wrapper, which doesn't map cleanly to an
  `EvalCase`. The example's docstring points at the adapter for
  production use.
* ``--example`` uses argparse `choices=` for validation rather
  than a post-hoc `CliError`. Tightens the bad-input path with
  less code.

**Next suggested action:** `Extend Phase 4 with \`frok init
--list-examples\`: print the available \`--example\` names along
with each one's docstring first line, so operators can
discover what's available without reading the source. Closes
the "what examples do I have?" discoverability gap parallel to
\`frok run --list\` closing the "what cases am I about to run?"
gap.`

## 2026-04-23 — Phase 4 §1: init-scaffold

**Shipped** ``frok init [PATH]`` — the onboarding command that
closes the "okay how do I actually start using this" gap.
Writes four files; the generated project runs end-to-end with no
further setup because the smoke case uses a stub transport.

* **Templates** (`frok/cli/init.py`, inline constants)
  * ``CLAUDE.md`` — project-scoped instructions linking the
    operator to the key subcommands and the baseline workflow.
  * ``frok.toml`` — every `FrokConfig` section populated, with a
    ``[profiles.prod.telemetry]`` override showing how profile
    merging works.
  * ``cases/smoke.py`` — one `EvalCase` + a ``make_client`` that
    returns a `GrokClient` wired to a stub transport. Replacing
    the transport with `urllib_transport` is the documented next
    step.
  * ``.github/workflows/frok.yml`` — PR-gating workflow using
    ``--fail-on-regression`` + an artifact upload, with a
    commented-out baseline-capture job on `main`.
* **`frok init`** — abort-if-any-exists by default
  (``CliError`` listing the offending files); ``--force`` to
  overwrite. Directories are `mkdir -p`'d. Writes a Next-steps
  block to stdout so the operator sees the three commands they
  should run next. ``path`` defaults to ``.``.

**Verification.** `python3 -m pytest -q` → 377 passed in 1.10s (14
new). Tests cover: argparse shape + default path, full-scaffold
write, nested path creation, existing-files abort + file
preservation, `--force` overwrite behaviour, generated
``frok.toml`` loading via `load_config` (base + `prod` profile),
``tomllib.loads`` round-trip of the template, the generated
smoke case running green via `frok run --fail-on-regression`,
``frok run --list`` over the generated case, the generated
``CLAUDE.md`` and workflow containing their promised references,
and an all-or-nothing guarantee (a partial existing tree doesn't
get half-scaffolded).

**Decisions / trade-offs.**
* Templates live as inline string constants rather than package-
  data files. No MANIFEST / package_data / importlib.resources
  ceremony; edits to the templates are an ordinary Python
  commit.
* The smoke case uses a stub transport, not real xAI. ``frok
  init && frok run cases/smoke.py`` passing out-of-the-box is
  the single best signal that the install works.
* Abort-if-any-exists is stricter than "skip if exists" — a
  partial scaffold is more confusing than a loud ``--force``
  requirement.
* The workflow comments out the baseline-capture job. It's a
  real pattern but requires a decision about where baselines
  live; better to enable it consciously than have a workflow
  fail on the first run because a secret's unset.

**Next suggested action:** `Extend Phase 4 with \`frok init
--example tools\` / \`--example multimodal\` / \`--example
memory\`: the basic smoke scaffold plus a second case file
showcasing the ToolOrchestrator / MultimodalAdapter / MemoryAgent
respectively. Closes the "great, now how do I wire up more of the
stack?" gap with working, runnable reference cases.`

## 2026-04-23 — Phase 3 §11: parallel-jobs

**Shipped** ``frok run --jobs N`` — concurrent case execution
under an `asyncio.Semaphore`. Default stays serial (N=1), so
every existing test and operator muscle-memory run is unchanged.
With N>1, up to N (case, repeat) units run at once; results come
back in submission order so the `EvalReport` always reflects the
case file's ordering regardless of which unit finished first.

* **Unified unit coroutine** in `run_cmd`: each
  `(case, repeat_idx)` pair maps to a task that acquires the
  shared semaphore, applies the seed (if any), runs through
  `EvalRunner.run_case`, and closes its JsonlSink in ``finally``.
  All tasks are created up front and driven by one
  ``asyncio.gather``; the order of the resulting list mirrors the
  order of creation.
* **Clamp to `os.cpu_count()`**: `jobs = min(args.jobs, cpu_cap)`.
  Requesting 1000 workers silently becomes whatever the box can
  actually run. `cpu_count()` returning `None` falls back to 1.
* **Mutual-exclusion guards**:
  * `--seed` + `--jobs > 1` raises `CliError`. Python's `random`
    state is process-global; parallel tasks would step on each
    other's seeding and no "determinism" would survive.
  * `--jobs 0` (and negative) raises at the CLI layer, same
    shape as the existing `--repeat` guard.
  * `--capture-baseline` still works with `--jobs > 1` — each
    case owns its own `<slug>.jsonl`; no collisions because
    `--repeat > 1` was already excluded.

**Verification.** `python3 -m pytest -q` → 363 passed in 0.97s (11
new). Tests cover: defaults (--jobs 1 == no flag), explicit serial
matches default, --jobs 4 preserves case order across 6 cases,
--jobs 3 with --repeat 3 produces 18 runs (6 cases × 3 repeats),
--jobs 4 with --capture-baseline writes all per-case JSONL files,
silent clamping to a monkey-patched `os.cpu_count() == 2`,
`cpu_count() is None` fallback, --jobs 0 / negative errors, --seed
+ --jobs > 1 errors, --seed + --jobs 1 still works, and a smoke
test that a parallel run completes without deadlocking.

**Decisions / trade-offs.**
* Semaphore over task pool. `asyncio.Semaphore(jobs)` is the
  simplest primitive that gets "at most N in flight" right. No
  need for a worker pool; `gather` collects everything.
* Submission-order, not completion-order, results. The Markdown
  report reads top-to-bottom the way the case file is authored.
* Seed + jobs are mutually exclusive rather than partially
  compatible. Any scheme that tried to serialise just the
  seed-touching work would either reintroduce global ordering
  (defeating --jobs) or fragment the abstraction. Explicit
  error is cleaner.
* Clamp is silent. Operators who want to know actually ran `K`
  workers can check the system's `os.cpu_count()` — surfacing it
  on every invocation would spam CI logs.

**Next suggested action:** `Begin Phase 4 with \`frok init\`:
scaffold a new project — create a CLAUDE.md stub, a minimal
case file, a \`frok.toml\` config template, and a
\`.github/workflows/frok.yml\` snippet demonstrating capture /
diff / fail-on-regression. Closes the "okay how do I actually
start using this" gap for new users.`

## 2026-04-23 — Phase 3 §10: repeat-runs

**Shipped** ``frok run --repeat N --seed S`` — executes each case
N times with a deterministic seed so operators can cleanly
separate "the case regressed" from "the scorer is flaky". The
``EvalReport`` aggregates by case name with a pass rate; any case
in (0, 1) is surfaced as `FLAKY` distinctly from `FAIL`.

* **`EvalResult`** grew optional ``repeat`` (0-based index) and
  ``repeats`` (total) fields. Defaults (0/1) preserve the existing
  shape; `to_summary()` only surfaces the new fields when
  ``repeats > 1``.
* **`EvalReport`** now exposes ``by_case`` / ``case_pass_rates``
  / ``total_cases`` / ``passed_cases`` / ``flaky_cases`` /
  ``failed_cases``. The Markdown renderer has two paths:
  * flat (existing) when every case has ``repeats == 1`` — no
    downstream test asserting on the current shape had to change.
  * aggregated when any case has ``repeats > 1`` — one row per
    case with a pass-rate column, a FLAKY/FAIL/PASS verdict, and
    the per-repeat failure list below for non-all-passing cases.
    The failure list uses scorer-name union across repeats.
* **`EvalRunner.run(cases, *, repeats=1)`** / ``run_case(case, *,
  repeat, repeats)`` — runner loops repeats internally when
  invoked via ``run`` and accepts explicit positions via
  ``run_case`` so the CLI can stamp them.
* **CLI `--repeat N` / `--seed S`** (`frok/cli/run.py`)
  * ``--repeat`` validates ``>= 1`` at the CLI layer.
  * ``apply_seed(seed, repeat_index)`` calls ``random.seed(seed +
    repeat_index)`` and publishes ``FROK_RUN_SEED`` per repeat
    before `make_client` runs, so a case file's stub transport
    can read the env var and react deterministically.
  * ``--repeat > 1`` + ``--capture-baseline`` raises ``CliError``
    — the per-case JSONL filenames would collide. Operators are
    directed to capture once and use ``--use-baseline`` on
    subsequent repeat runs.

**Verification.** `python3 -m pytest -q` → 352 passed in 0.90s (17
new). Library tests cover default repeat fields, flat-format
preservation on single-repeat runs, ``by_case`` grouping,
``case_pass_rates`` across flaky + all-pass + all-fail cases,
aggregated-markdown column presence + FLAKY verdict + per-repeat
detail, summary shape for both single- and multi-repeat runs.
CLI tests cover the ``apply_seed`` helper (env var + `random`
determinism + per-repeat shift), end-to-end ``--repeat 3``
flaky-case production (2/3 pass), aggregated markdown column +
FLAKY surfacing, ``--fail-on-regression`` flipping exit on any
failed repeat, ``--seed`` publishing ``FROK_RUN_SEED`` before
``make_client`` (verified through the aggregated Failed-scorers
column), and both error paths (``--repeat 0`` and
``--repeat > 1`` + ``--capture-baseline``).

**Decisions / trade-offs.**
* Aggregate Markdown only when ``repeats > 1``. The existing flat
  table is optimized for single-run output; changing it globally
  would break operator muscle memory and churn test assertions.
* Seed is ``S + repeat_index``, not ``S``. Two repeats of the
  same case need distinct stochastic paths, otherwise a flaky
  case would appear deterministic.
* ``FROK_RUN_SEED`` env var rather than a constructor argument.
  Case-file ``make_client`` functions don't have a stable
  contract for receiving runner-internal state; an env var is
  the Unix-native escape hatch.
* ``--repeat > 1`` + ``--capture-baseline`` fails loudly rather
  than silently overwriting the JSONL. If operators want a
  repeat-with-capture flow, they can capture the first repeat
  manually or use ``--use-baseline`` against a one-shot capture.

**Next suggested action:** `Extend Phase 3 with the final CI-
ergonomics flag \`frok run --jobs N\`: run cases in parallel
across N workers (respecting --repeat so each case gets its N
repeats, but different cases can interleave). Default stays
serial (N=1). Caps at os.cpu_count(). Closes the "my eval suite
takes forever" complaint without compromising determinism — each
case's output is still collected in the same EvalReport order.`

## 2026-04-23 — Phase 3 §9: eval-dirdiff

**Shipped** ``frok eval summarize <a> --diff-against <b>`` — the
one-shot "did this PR regress any of my captured baselines?"
command. Two directories of `<slug>.jsonl` captures, one report,
CI-gateable.

* **Library** (`frok/evals/baseline.py`)
  * ``CaseDiff`` — one matched pair (name, a_path, b_path, and
    the ``diff_event_streams`` payload). ``.regressed`` mirrors
    the payload.
  * ``DirectoryDiff`` — matched list + ``only_in_a`` /
    ``only_in_b`` slug sets + ``regressed_cases`` +
    ``regressed`` rollup. The rollup flips on either a matched-
    case regression *or* slug divergence — operators opting into
    ``--diff-against`` probably want to know about both.
  * ``diff_directories(a, b)`` walks each side via `<dir>/*.jsonl`
    (sorted, empty captures silently skipped) and diffs each
    matched pair through the shared ``diff_event_streams`` core.
  * ``directory_diff_to_markdown`` / ``_to_json`` renderers;
    Markdown hides Only-in / Regression-details sections when
    they'd be empty.
* **CLI** (`frok/cli/eval.py`)
  * `frok eval summarize <DIR>` gained ``--diff-against <DIR>``
    that short-circuits the single-dir rollup into directory-
    diff mode.
  * Companion ``--fail-on-regression`` flag (distinct from the
    existing ``--fail-on-errors`` which remains in single-dir
    mode). Missing / not-a-directory `--diff-against` targets
    raise ``CliError`` via a shared ``_require_dir`` helper.

**Verification.** `python3 -m pytest -q` → 335 passed in 0.87s (19
new). Library tests cover identical directories, added /
removed slugs, tool-order regression, token-only delta not
regressing, new-error regression, empty-capture skipping, missing-
directory errors, Markdown section presence + hiding on clean
diffs, and JSON round-trip. CLI tests cover argparse shape, clean
exit-0 under ``--fail-on-regression``, tool-order divergence
flipping exit to 1, slug divergence flagged in both JSON and
Markdown, token-only delta staying clean, ``-o`` file write,
missing / not-a-dir ``--diff-against`` errors, and — crucially —
that the single-dir path still works unchanged when
``--diff-against`` is absent.

**Decisions / trade-offs.**
* Reused ``summarize`` as the subcommand verb rather than adding
  a new one. The flag cleanly toggles modes, help output shows
  both, and operators don't have to memorise a second command
  name.
* Slug divergence is treated as a regression by default. A case
  silently appearing or disappearing between runs is almost
  always a bug to investigate; the operator can still post-
  process the JSON if they disagree.
* Matching is by exact slug (file stem). Fuzzy matching across
  renames is out of scope — if a case got renamed, the operator
  explicitly handles that via the list the CLI surfaces in
  ``only_in_a`` / ``only_in_b``.
* Per-case regression details section only renders for the
  cases that actually regressed. Markdown stays tight when the
  PR is clean; the info is there when it isn't.

**Next suggested action:** `Extend Phase 3 with \`frok run
--repeat N\` + \`--seed S\`: execute each case N times with a
deterministic seed so flaky-scorer investigations can quickly
separate "the case regressed" from "the case is inherently
non-deterministic". The repeat aggregate becomes a pass-rate in
the EvalReport; the seed lets CI re-stage the same run
identically.`

## 2026-04-23 — Phase 3 §8: eval-summarize

**Shipped** ``frok eval summarize <dir>`` — a directory-wide
rollup over a bag of `JsonlSink` captures. Closes the last
discoverability gap: today operators could `trace inspect` one
file or `eval diff` two; now they can point at a
``--capture-baseline`` directory and get one report.

* **`frok.telemetry.analysis`** (extension)
  * ``CaseSummary`` — per-capture rollup: name (file stem),
    path, span count, total tokens (from `grok.chat`), error
    count, duration (sum of root spans), tool counts, errored
    tool counts.
  * ``DirectorySummary`` — cases + aggregate properties
    (``total_spans`` / ``total_tokens`` / ``total_errors`` /
    ``tool_counts`` / ``errored_tool_counts``) and leader
    methods (``slowest(n)`` / ``heaviest_tokens(n)`` /
    ``most_errors(n)``).
  * ``summarize_directory(dir)`` walks ``<dir>/*.jsonl`` in
    sorted order, skipping empty captures; raises
    ``NotADirectoryError`` if the path isn't a directory.
  * ``dir_summary_to_markdown`` + ``dir_summary_to_json``
    renderers. Markdown hides leader sections that'd be empty
    (no errored tools, no errored cases) so a clean run's report
    stays tight.
* **`frok eval summarize <dir>`** (`frok/cli/eval.py`)
  * Flags: `-o/--output`, `--json`, `--top N` (default 5),
    `--fail-on-errors` for CI. Missing / not-a-dir / empty
    directory all raise ``CliError`` (exit 2); full traces in
    empty JSONL files are silently skipped so a partial capture
    doesn't tank the whole report.
  * Lives under the existing `eval` subparser alongside
    `eval diff`.

**Verification.** `python3 -m pytest -q` → 316 passed in 0.89s (24
new). Library tests cover the directory walker (sorted order,
non-jsonl files ignored, missing dir errors, empty captures
skipped); CaseSummary field correctness (token aggregation, chat+
tool error counting, tool/errored tool counts, root-span duration
summation with nested children excluded); DirectorySummary
aggregates (tool merging, errored-tool merging, slowest/heaviest/
most-errors leader ordering); renderers (all section headers
present, empty leader sections hidden, JSON round-trips). CLI
tests cover argparse shape, Markdown + JSON outputs, `-o` writes
+ stdout suppression, `--top` caps leader rows but not per-case
rollup, `--fail-on-errors` flips the exit code, error paths
(missing dir, not-a-directory, empty directory), and an end-to-
end interop test that pipes a `frok run --capture-baseline` run
directly into `frok eval summarize` and asserts both case names
appear.

**Decisions / trade-offs.**
* Directory walker silently skips empty JSONL files rather than
  erroring — a half-written capture from a crashed run
  shouldn't prevent the operator from summarising the 99 that
  succeeded.
* `--top` caps only the leader tables, not the per-case rollup.
  A dashboard for 200 cases should list all 200 but highlight
  the top-N on each dimension.
* Errored-tool and errored-case sections are hidden on clean
  runs. Operators who scroll a perfectly-green report shouldn't
  be made to stare at empty "## Tools with errors" headers.
* Directory aggregation reuses the single-capture `summarize`
  helper so the two entry points can't drift on what counts as
  a tool invocation, a token, or an error.

**Next suggested action:** `Extend Phase 3 with \`frok eval
summarize --diff-against <dir>\`: two directories, each a set of
\`<slug>.jsonl\` captures; surface per-case diffs (tokens,
tool-order, errors) where the slugs match, and flag slugs that
appear in one side but not the other. Makes it a one-shot "did
the PR regress any of my captured baselines?" command.`

## 2026-04-23 — Phase 3 §7: eval-diff

**Shipped** ``frok eval diff <a.jsonl> <b.jsonl>`` — symmetric
two-capture comparison for A/B testing prompt / model / config
changes. Complements the single-capture ``trace inspect`` and the
per-case ``--use-baseline`` with a general two-sided diff that
lives outside a live run.

* **Library refactor** (`frok/evals/baseline.py`)
  * Extracted the comparison core into
    ``diff_event_streams(a_events, b_events, *, a_label, b_label)``.
    Returns tool-order match, per-side tools / tokens / errors /
    span counts, deltas (`token_delta`, `span_delta`), and a
    ``regressed`` verdict (tool-order divergence or new errors in
    ``b``). Labels parameterise the dict keys.
  * ``diff_against_baseline(obs, path)`` now delegates to the
    above with legacy labels ``"baseline"``/``"observed"`` —
    existing `EvalRunner` consumers and every previously-shipped
    assertion key are preserved.
  * Added ``diff_to_markdown(diff, *, a_label, b_label, a_path,
    b_path)`` for a compact verdict rendering with tool-order /
    tokens / errors sections.
* **`frok eval diff` CLI** (`frok/cli/eval.py`)
  * `a` is the reference ("before"), `b` is the candidate
    ("after"). Missing / empty / malformed captures raise
    `CliError` (exit 2), matching `trace inspect`'s semantics.
  * Flags: `-o/--output`, `--json`, `--fail-on-regression`.
    JSON output includes `a_path` / `b_path` so downstream
    tooling has everything it needs in one payload.

**Verification.** `python3 -m pytest -q` → 292 passed in 0.73s (19
new). Tests cover: `diff_event_streams` across identical, tool-
order divergence, token-delta-only (no regression), new errors in
``b`` (regression), fewer errors in ``b`` (floor at zero), custom
label key-rename, span-count delta; `diff_to_markdown` sections +
signed token delta; CLI argparse shape, identical captures clean
exit, divergence regresses under `--fail-on-regression`, clean
diff stays 0, `--json` parseable with paths, `-o` writes file and
suppresses stdout, and all three error paths (missing / empty /
malformed).

**Decisions / trade-offs.**
* One pure-function helper shared between "live vs captured" and
  "captured vs captured" paths — same matcher, same semantics, so
  the two tools can't drift on what counts as a regression.
* `a` and `b` labels in the general helper, `baseline` /
  `observed` in the back-compat wrapper. Downstream code reading
  either set of keys keeps working.
* Token deltas reported but don't flip ``regressed``. Longer
  correct answers shouldn't fail CI; tool-order and errors are
  the trust-relevant signals.
* The CLI preserves exit-code semantics across the Phase-3
  family: ``--fail-on-regression`` → 1 on divergence; CliError
  → 2 on operator mistakes; 0 otherwise.

**Next suggested action:** `Extend Phase 3 with \`frok eval
summarize <dir>\`: walk a baseline directory, run \`trace
inspect\` across every \`<slug>.jsonl\` in it, and emit an
aggregated Markdown (or JSON) report — per-case span-count /
token / error rollups plus cross-case leaders (slowest cases,
most-errored tools). Closes the last gap: today operators can
inspect one capture or diff two, but there's no "scan my whole
baseline folder" command.`

## 2026-04-23 — Phase 3 §6: list-preview

**Shipped** ``frok run --list`` — an early-exit preview that prints
the resolved case names (after ``--filter`` / ``--exclude``) one per
line and returns without constructing a client or running any
case. Completes the discoverability loop alongside ``config show``
and ``trace inspect``.

* **`run_cmd` short-circuit**: after filter application, if
  ``--list`` is set, print names and ``return 0`` — before any
  ``build_client`` / ``JsonlSink`` / ``runner.run_case`` work. No
  api_key is required, no capture files are written.
* **Output format**: one case name per line with a trailing
  newline. Pipe-friendly by construction
  (``frok run cases.py --list | grep safety``).
* **Flags reused**: ``-o/--output`` writes to a file (parents are
  `mkdir -p`-ed) and suppresses stdout; ``--filter`` / ``--exclude``
  apply normally.

**Verification.** `python3 -m pytest -q` → 273 passed in 0.62s (10
new). Tests cover: basic output + ordering, filter / exclude /
regex-prefix interop, zero-match still errors (filters apply
before the list branch), ``-o`` writes file + blanks stdout, the
empty stub transport is NOT called under ``--list``, api-key-free
case files still list fine, and ``--list --capture-baseline``
writes nothing since the loop never runs.

**Decisions / trade-offs.**
* Minimal format: just names. Richer previews (scorer / tool
  counts, baseline status) can be bolted on via a future
  ``--list --format=table`` without breaking the simple
  lines-on-stdout contract.
* ``--list`` runs AFTER filter application but BEFORE client
  construction — so the printed list is exactly what a non-list
  invocation would execute, giving operators a faithful preview.
* Zero-match still errors (exit 2) under ``--list``. Operators
  using ``--list`` to sanity-check filters should get the same
  feedback they'd get on a real run; silent empty output would be
  a worse experience than the "no cases matched" message that
  lists available names.

**Next suggested action:** `Extend Phase 3 with \`frok eval diff
<a.jsonl> <b.jsonl>\`: diff two JsonlSink captures side-by-side
(tool-call order, token delta, new errors, span count) and print
a compact report. Complements \`trace inspect\` (single capture)
and \`--use-baseline\` (per-case diff) with a general two-capture
comparison for A/B testing prompt / model / config changes.`

## 2026-04-23 — Phase 3 §5: case-filter

**Shipped** ``frok run --filter <pattern>`` / ``--exclude <pattern>``
so CI and local iteration can re-run a subset of cases without
editing the case file to comment cases out.

* **`frok.cli.run.filter_cases(cases, *, includes, excludes)`** —
  pure-function helper. A case is kept when (includes empty OR any
  include matches) AND no exclude matches.
* **Pattern syntax**: fnmatch glob by default (``safety-*``),
  `re:` prefix for a Python regex (``re:^tool-``). Glob comparison
  is case-sensitive (`fnmatchcase`); regex uses `re.search` so
  partial matches work the same way people expect from `grep`.
* **Flags** (repeatable, union semantics):
  * `--filter PATTERN` — keep matches.
  * `--exclude PATTERN` — drop matches. Exclude wins over filter.
* **Error paths**:
  * Invalid regex → ``frok: error: invalid regex in pattern
    're:[': …``, exit 2.
  * Zero matches → ``frok: error: no cases matched the filters
    (filter=…, exclude=…); available: [names…]``, exit 2. Surfacing
    the full case-name list makes typos self-diagnosing.
* **Interop.** Filters compose with `--capture-baseline` so only the
  filtered cases produce capture files; with `--use-baseline` so
  selective re-runs still regress against the recorded baseline.

**Verification.** `python3 -m pytest -q` → 263 passed in 0.58s (16
new). Tests cover: every library-level matcher (no filters, glob,
multi-glob union, case-sensitivity, `re:` prefix, partial regex
via search, exclude-only, filter+exclude intersect, invalid
regex); CLI paths (single glob, regex prefix, exclude, filter +
exclude, zero-match error with case list surfaced, invalid regex
error); and a `--filter` + `--capture-baseline` interop test
confirming only filtered cases produce capture files.

**Decisions / trade-offs.**
* Prefix-based syntax (`re:`) rather than a second flag. Keeps one
  consistent knob for both `--filter` and `--exclude`, matches the
  user's example syntax, and `re:` collisions with real case names
  are implausible.
* Glob is the default because most filter invocations are "give me
  every safety-* case"; regex is the escape hatch for anchoring
  (`re:^tool-`) or boundary-sensitive matches.
* Zero matches is a hard error rather than a silent pass. A filter
  that accidentally removes every case almost always means a typo;
  we'd rather flag it than emit an empty report.

**Next suggested action:** `Extend Phase 3 with \`frok run --list\`:
print the resolved case names (after config + filter application)
and exit, so operators can preview what a given invocation would
run before committing to the full execution. Completes the
discoverability loop alongside \`config show\` and \`trace
inspect\`.`

## 2026-04-23 — Phase 3 §4: baseline-capture

**Shipped** the missing piece of the baseline-regression loop:
``frok run --capture-baseline <dir>`` records per-case telemetry
JSONL; ``--use-baseline <dir>`` auto-attaches those files as each
case's baseline on subsequent runs. The §2 #8 differ then fires
automatically and a regression (tool-order divergence or new
errors) turns the exit code red under ``--fail-on-regression``.

* **`Tracer.with_added_sink(tracer, extra)`**
  (`frok/telemetry/tracer.py`) — returns a new tracer whose sink
  fans out to the original plus ``extra``. `NullSink` is collapsed
  away; `MultiSink` is extended; anything else is wrapped. `clock`
  and `id_gen` are preserved so deterministic-clock tests survive.
* **`--capture-baseline <DIR>`** (`frok/cli/run.py`)
  * Slugs each case name (`[^A-Za-z0-9._-]+` → `_`, fallback
    `"case"`), rejects slug collisions within a single run, and
    creates `<DIR>/<slug>.jsonl` via a `JsonlSink` layered onto the
    client's tracer with `with_added_sink`.
  * Runs cases one at a time (`runner.run_case`) so each capture
    closes cleanly. Doesn't change the observed report.
* **`--use-baseline <DIR>`** — iterates cases, and for any case
  without an explicit `baseline=`, sets `case.baseline =
  DIR/<slug>.jsonl` when that file exists. Missing captures leave
  the case alone; non-directory paths are `CliError`.
* The two flags compose: first-run captures; subsequent run with
  `--use-baseline <same-dir>` diffs automatically. Regressed
  cases still propagate through `--fail-on-regression`.

**Verification.** `python3 -m pytest -q` → 247 passed in 0.54s (13
new). Tests cover `case_slug` across safe / symbol-heavy / empty
inputs, `with_added_sink` under `NullSink` / plain / `MultiSink`
bases with `clock`/`id_gen` preservation, per-case file creation
at nested paths, slug-based collision rejection, normal-report
output isn't disturbed by capture, `--use-baseline` attachment
behaviour (match, no-match, non-directory), and the full
capture-then-use round-trip catching an answer regression via
`--fail-on-regression`.

**Decisions / trade-offs.**
* Baseline file per *case*, not per *run*. The §2 #8 differ takes
  one baseline path per case, so sharding by case name keeps the
  existing contract.
* Case slug is the filename; collisions within one run are an
  error because the second capture would silently overwrite the
  first. Explicit is better than a confusing partial capture.
* `--capture-baseline` and `--use-baseline` can point to the same
  directory simultaneously; the user is explicitly opting into
  "diff against the baseline I'm recording this run", which is a
  valid "smoke test the capture itself" use case. We don't block
  it.
* The per-case JsonlSink is layered via `with_added_sink` instead
  of modifying the factory signature — means case-file authors'
  `make_client(config, sink)` contract is untouched, and any
  existing MultiSink fan-out from config's `telemetry.sink` is
  preserved.

**Next suggested action:** `Extend Phase 3 with \`frok run
--filter=<pattern>\`: filter the case list by glob or regex before
execution, so CI jobs can re-run only the cases that failed last
time (e.g. \`frok run cases.py --filter="safety-*"\` or \`--filter
"^tool-"\`). Keeps local iteration fast without editing case files
to comment cases out.`

## 2026-04-23 — Phase 3 §3: config-show

**Shipped** ``frok config show [--format=toml|json|env]`` — renders
the resolved `FrokConfig` after file + env + CLI + profile merging,
so operators can sanity-check which settings actually got applied
before running anything. Closes the config <-> runtime loop the
same way `trace inspect` closes the telemetry <-> eval loop.

* **`frok.config.render`** — three pure functions producing
  strings: `to_toml`, `to_json`, `to_env`. All three serialise the
  same `_as_plain_dict` so the three formats agree on content.
  `SENSITIVE_FIELDS = {("client", "api_key")}` drives masking; last
  four characters preserved, rest replaced with ``****``. Unset
  (``None``) values survive the round-trip:
    * JSON: native `null`
    * TOML: commented-out key with `(unset)` marker (TOML has no null)
    * env: `# FROK_<SECTION>_<FIELD>=` comment line
* **`frok config show`** (`frok/cli/config.py`)
  * Loads config via `load_default_config(file=args.config,
    profile=args.profile)`, applies the selected renderer, writes
    stdout or `-o/--output`.
  * `--reveal` flips sensitive values plain; default is masked.
  * Config load failures surface as `CliError` → ``frok: error:
    config load failed: …`` → exit 2, same as `run` and
    `trace inspect`.

**Verification.** `python3 -m pytest -q` → 234 passed in 0.48s (18
new). Tests cover every renderer (shape + masking + reveal + short-
key handling + special-char escaping in TOML + dotenv-shape env
keys), TOML round-trip through stdlib `tomllib`, and the CLI paths
(default toml, `--format=json` parsability, env matches loader
keys, `-c/-p` pickup including profile merging, `-o` writes file +
suppresses stdout, missing-config-file error).

**Decisions / trade-offs.**
* Minimal in-house TOML emitter rather than a third-party dep —
  the schema is fixed and flat, no heroics needed. Round-trip via
  `tomllib` is asserted in the test suite.
* No `--set key=val` on `config show` — if operators want to try
  overrides they can prepend env vars or pass `-c` to a tweaked
  file. The command's job is *showing* what's resolved, not
  mutating it.
* Masking is opt-out (`--reveal`) rather than opt-in. Accidental
  copy-paste of an api_key into a paste buffer is worse than the
  mild annoyance of re-running with `--reveal`.

**Next suggested action:** `Extend Phase 3 with \`frok run
--capture-baseline <path>\`: run a case set and write the captured
telemetry to \`<path>\` as a JsonlSink, so the next run can diff
against it via EvalCase.baseline automatically. Closes the
baseline-capture loop — today operators have to set
\`telemetry.sink=jsonl\` + \`telemetry.path=...\` by hand to feed
§2 #8's baseline differ.`

## 2026-04-23 — Phase 3 §2: trace-inspect

**Shipped** a library-level trace analysis surface plus the
``frok trace inspect <jsonl>`` CLI — post-hoc regression triage off
a `JsonlSink` capture without rebuilding the agent stack.

* **`frok.telemetry.analysis`**
  * `build_tree(events) -> list[TraceNode]` — reconstructs the
    parent/child tree from `span.end` events; children sorted by
    start time; orphaned parents (capture truncation, filtering)
    surface as roots rather than being dropped.
  * `summarize(events) -> TraceSummary` — per-name stats
    (count, total / mean / p50 / p95 / max ms, error_count), errored
    span list (ordered by start_ts), and top-tool aggregates
    (`tool.invoke` spans grouped by `data["tool"]`, sorted by count
    then total-ms, `errors` column). Empty-input safe.
  * `summary_to_markdown` / `render_tree` / `summary_to_json` for
    the three output formats the CLI emits.
* **`frok trace inspect <jsonl>`** (`frok/cli/trace.py`)
  * Reads a JsonlSink capture via `read_jsonl`, summarises, and
    prints. Flags: `-o/--output`, `--tree`, `--json`, `--top N`.
  * Catches malformed JSONL and empty files as `CliError` so the
    operator sees ``frok: error: ...`` not a stack trace.
* **CLI refactor.** `frok/cli/__init__.py` now owns the top-level
  parser and `main()`; `run.py` and `trace.py` each export a
  `register(sub)` helper. Adding a third subcommand is one more
  `register` call — no growing God function.

**Verification.** `python3 -m pytest -q` → 216 passed in 0.46s (23
new). Tests cover tree nesting + orphan handling, per-name stat
aggregation (mean / percentile / error-count), tool ranking (count
tiebreak by total_ms), empty-input safety, JSON round-trip, tree +
markdown rendering, and CLI paths: help shape, md / json / tree /
output-file output, `--top` capping, missing / empty / malformed
input errors.

**Decisions / trade-offs.**
* Token / latency deltas between two trace captures live in
  `frok.evals.baseline.diff_against_baseline`; the inspect
  subcommand stays single-capture and focused on "where did the
  time and errors go in *this* run?".
* Renderers are pure functions producing strings so operators can
  pipe the output into mail / Slack / `jq` without a plugin system.
* JSON output uses the same shape the Python API returns from
  `summary_to_json`, so downstream scripts and the CLI agree on one
  schema.

**Next suggested action:** `Extend Phase 3 with \`frok config show
[--format=toml|json|env]\`: render the resolved FrokConfig (after
file+env+CLI+profile merging) so operators can sanity-check which
settings actually got applied before running anything. Closes the
config <-> runtime loop the same way trace inspect closes the
telemetry <-> eval loop.`

## 2026-04-23 — Phase 3 §1: cli-runner

**Shipped** a single-invocation entry point that turns a Python case
file into a verdict doc, closing the loop between Phase-2 config /
evals / telemetry and a CI-runnable command.

* **`frok.cli.run`** — `frok run <case-file>` wires
  `load_default_config(file=…, profile=…)` → builds the full stack
  via the Phase-2 builders → executes the case set through
  `EvalRunner` → prints (or writes) `EvalReport.to_markdown()`.
  Flags: `-c/--config`, `-p/--profile`, `-o/--output`,
  `--summary-json`, `--fail-on-regression`.
* **Case-file conventions.** A `.py` file must expose either
  `CASES: list[EvalCase]` (plain list) or
  `build_cases(config) -> list[EvalCase]` (parameterised by the
  resolved `FrokConfig`). Optional `make_client(config, sink) ->
  GrokClient` lets CI wire a stub transport; without it the default
  factory uses `frok.clients.transports.urllib_transport` + the
  config's `telemetry.sink` fan-out (`MultiSink(in_memory,
  config_sink)` so scorers keep their per-case InMemorySink while
  operators still get JsonlSink captures when configured).
* **`frok.clients.transports.urllib_transport`** — a stdlib-only
  `Transport` that runs `urllib.request` under `asyncio.to_thread`.
  Zero deps, modest throughput, good enough for a CLI and CI. Swap
  in httpx/aiohttp behind the Protocol when volume arrives.
* **Entry points** — `python -m frok` via `src/frok/__main__.py`
  and a console script (`[project.scripts] frok = "frok.cli:main"`).

**Verification.** `python3 -m pytest -q` → 193 passed in 0.41s (12
new). Tests cover: CASES-list + `build_cases(config)` paths,
`make_client` override, missing case-file / missing CASES / empty
CASES errors, `--fail-on-regression` exit-code behaviour on pass +
fail, `-o` writing Markdown to a nested path (and suppressing
stdout), `--summary-json` shape, default factory raising when
`client.api_key` is unconfigured, and the argparse shape.

**Decisions / trade-offs.**
* Case files are Python, not YAML/TOML. Python gives direct access
  to `EvalCase`, `Scorer`, and `GrokMessage` without a mini-DSL;
  `build_cases(config)` is the escape hatch when cases need to
  parameterise themselves.
* `ConfigError` and `CliError` are both caught at `main()` boundary
  and printed as ``frok: error: <msg>`` so operators get a single
  consistent failure surface regardless of whether the problem is
  config shape, missing case file, or api-key.
* The default factory fans out per-case InMemorySink ⊕
  ``telemetry.sink`` via `MultiSink`. Scorers still get their
  hermetic in-memory view; operators still get persistent capture
  when they want it. One flag, two observers.

**Next suggested action:** `Extend Phase 3 with \`frok trace
inspect <jsonl>\`: a sibling subcommand that loads a JsonlSink
capture via \`read_jsonl\`, reconstructs the trace tree, and prints
a summary (per-span durations, error hot-spots, top tool
invocations). Closes the telemetry <-> eval loop for post-hoc
regression triage.`

## 2026-04-23 — §2 #9 config-loader

**Shipped** `frok.config`: a typed, layered config surface that's the
single place the rest of the stack reads runtime settings from.

* **`FrokConfig`** (`schema.py`) — one top-level dataclass with
  sub-dataclasses per concern: `ClientConfig`, `SafetyConfig`,
  `TelemetryConfig`, `MemoryConfig`, `MultimodalConfig`. No logic,
  just shape. A `SECTIONS` map is exposed so the loader can
  enumerate fields programmatically.
* **`load_config(file=, env=, cli=, profile=)`** (`loader.py`) —
  deterministic precedence: defaults < file < env < CLI. File is
  JSON (always) or TOML (stdlib `tomllib`, 3.11+) detected by
  extension. Env vars are `FROK_<SECTION>_<FIELD>` with per-field
  type coercion (including `tuple[str, ...]` from comma lists). CLI
  accepts either a nested dict or a flat dict keyed by
  ``"section.field"``; `None` values are ignored so forwarding
  `vars(argparse.Namespace())` Just Works.
* **Profiles** — a config file may declare `[profiles.NAME]` blocks;
  when a profile is selected (explicit arg → CLI → env
  `FROK_PROFILE` → file's own `profile = "..."`), that section is
  deep-merged on top of the base. Dev / prod swap is one flag.
* **Builders** (`builders.py`) — `build_safety_ruleset`,
  `build_telemetry_sink`, `build_tracer`, `build_client`,
  `build_memory_store`, `build_multimodal_adapter`. Each consumes
  `FrokConfig` + optional overrides, validates required fields
  (e.g. `client.api_key`, `telemetry.path` for jsonl), and returns
  the live component. Downstream code keeps taking narrow types —
  nothing else needs to know `FrokConfig` exists.
* **`load_default_config(**overrides)`** — the ergonomic wrapper that
  sources `os.environ` + optional `FROK_CONFIG_FILE` + explicit
  overrides. `load_config()` with all `None` args stays hermetic for
  tests.

**Verification.** `python3 -m pytest -q` → 181 passed in 0.38s (33
new). Tests cover defaults, env coercion across every type, JSON +
TOML file loading, nested + flat CLI overrides, file-vs-env-vs-CLI
precedence, profile merging via arg and env, unknown-section /
unknown-field / bad-shape errors, and per-builder wiring (safety
rule exclusion, sink construction, memory disabled-by-default,
explicit tracer override, end-to-end full-stack build from one
config).

**Decisions / trade-offs.**
* Opted against auto-reading `~/.frok/config.toml`. `load_config()`
  is inert without explicit args; `load_default_config()` is the
  "do the thing" entry point. Splitting them keeps tests hermetic
  without an env-scrubbing harness.
* Memory defaults to `enabled=False`. Forcing opt-in keeps
  first-time callers from accidentally writing a SQLite file into
  their working directory.
* Unknown sections / fields *fail loudly* at load time rather than
  being silently ignored — typos in config are the single biggest
  "huh, why isn't X working" time-sink I've seen, and we have the
  schema so we may as well police it.

**Next suggested action:** `Continue Phase 3 with a CLI runner that
wires load_default_config into a \`frok run <case-file>\` entry
point driving the §2 #8 eval harness, so a single invocation loads
config -> builds client/memory/adapter -> runs a case set -> prints
the markdown verdict doc.`

## 2026-04-23 — §2 #6 agent-team-runtime

**Shipped** `frok.team`: a deliberately small multi-agent scheduler
that composes every Phase-2 wrapper (`MemoryAgent`,
`MultimodalAdapter`, `ToolOrchestrator`, bare `GrokClient`) as a
named `Role` inside one transcript-driven loop.

* **`TeamMessage`** — frozen `(from_, to, content, meta, step)`; the
  only data type that flows through the system.
* **`Role`** — name + an async `respond(transcript) -> str`. The
  runtime passes each role only the messages addressed to it (or
  `to="all"`) so roles don't have to filter.
* **`TeamRuntime.run(initial)`** — loops until the router returns
  `None` (clean termination → `to="user"` on the final message) or
  `max_hops` trips (raises `TeamError`). Each hop is wrapped in a
  `team.hop` span nested under a `team.run` span; both share a
  `trace_id` and carry `hops` / `terminated` so evals can regress on
  the team tree alongside `grok.chat` / `tool.invoke` children.
* **Routers** — three built-ins:
  * `pipeline_router(["researcher", "writer", "editor"])` — fixed
    linear pipeline, terminates after the last role.
  * `callback_router(fn)` — identity passthrough for hand-written
    supervisors.
  * `loop_until(predicate, next_=..., max_rounds=...)` — keep
    dispatching to `next_` until either the predicate matches on the
    reply or the per-sender round cap is hit.
* **Role adapters** — `chat_role_from_client(name, client, system=...)`
  flattens the transcript into alternating `assistant` / `user`
  turns with `[sender->recipient]` prefixes so the model can see the
  hand-off. `echo_role(name)` is the deterministic test fixture.

**Verification.** `python3 -m pytest -q` → 148 passed in 0.31s (12
new). Tests cover single-role termination, unknown-role guard,
pipeline walking, supervisor-style branching, `loop_until` predicate
and round-cap paths, `max_hops` error + span metadata, per-role
transcript filtering, and a composition test that runs two
`GrokClient`-backed roles and asserts the telemetry tree
(`team.run` → `team.hop` → `grok.chat`) reconstructs under one
`trace_id`.

**Decisions / trade-offs.**
* Replies are routed **directly** to the next role (not via a
  supervisor indirection) so every role's filtered transcript
  includes its predecessor's hand-off. A terminal reply is addressed
  to `"user"` — the caller.
* The probe `TeamMessage` passed to the router has `to=""`; it's the
  router's job to decide. This keeps the router signature from
  depending on prior routing state.
* No DSL for inter-role protocols. Roles are async callables,
  routers are async callables, transcripts are lists. If a team
  needs custom protocol logic it lives in user code, not the
  runtime.

**Next suggested action:** `Continue Phase 2 with §2 #9 config-loader:
a layered config loader (env vars -> file -> CLI overrides) that
produces a single typed \`FrokConfig\` object, wires the default
\`GrokClient\` / \`MemoryStore\` / \`MultimodalAdapter\` / tracer
instances from it, and makes it trivial to swap dev vs production
profiles without touching call sites.`

## 2026-04-23 — §2 #5 multimodal-adapter

**Shipped** `frok.multimodal`: a typed image + audio IO surface that
routes through `GrokClient` (so safety + telemetry + retries come
along for free) and falls back to short text descriptors when a
modality is disabled.

* **`frok.multimodal.encoding`** — MIME tables for the image formats
  Grok actually accepts (png / jpeg / gif / webp / bmp / tiff) and
  audio formats (wav / mp3 / m4a / flac / ogg / opus / webm), plus a
  `to_data_url()` helper + base64 encoder. Zero deps.
* **`ImageRef` / `AudioRef`** — frozen dataclasses with three
  consistent factories each: `from_path`, `from_bytes`, `from_url`.
  `to_content_part()` emits the OpenAI-compatible chat content part
  (URLs stay as URLs, bytes/paths become `data:` URLs). Audio has a
  sibling `to_transcribe_payload()` for the voice endpoint.
  `describe()` gives a short text fallback (`alt_text` first, then
  URL / path / bytes summary).
* **`MultimodalAdapter`** — wraps a `GrokClient`. Public API:
  * `describe_image(image, prompt=...)` — one-shot vision chat.
  * `chat([parts...])` — mixed text + images + audio.
  * `transcribe_audio(audio)` — routes to a configurable endpoint
    (default `/audio/transcriptions`) via the new
    `GrokClient.request_json()` helper; returns descriptor when voice
    is disabled so callers always get *something*.
  * `AdapterConfig` toggles vision / voice, configurable fallback
    prefixes, transcribe path, voice model. Default is
    vision-enabled, voice-disabled.
* **`GrokMessage.parts`** — new optional `tuple[dict, ...]` carrying
  OpenAI-style content parts. When set, safety pre-flight rewrites
  only `{"type": "text"}` parts and leaves image / audio parts
  untouched. The payload emits the parts list as `content`. Safety
  blocks on any text part short-circuit before the network.
* **`GrokClient.request_json(path, payload)`** — public POST for
  non-chat endpoints (audio / embeddings / …). Bypasses chat safety
  but inherits retries, auth, and the tracer (`grok.request` span).

**Verification.** `python3 -m pytest -q` → 136 passed in 0.37s (25
new). Tests cover MIME/format detection, three-way ref factories,
data-URL round-trips, vision-enabled + vision-disabled fallback,
voice-enabled endpoint routing (base64 + model name + path), voice-
disabled descriptor path, safety rewriting text parts while leaving
image parts alone, and block-before-network on unsafe text parts.

**Decisions / trade-offs.**
* Adapter builds exactly one user message carrying a list of content
  parts. Multi-turn multimodal chats are still one `client.chat`
  call each — no hidden state in the adapter.
* Audio transcription currently expects a JSON endpoint returning
  `{"text": "..."}`. If a real xAI voice endpoint takes multipart,
  `GrokClient.request_json` is the narrow hook to swap (or add a
  sibling `request_multipart`). Tests pin the JSON shape so the swap
  is observable.
* Fallback descriptors are surfaced as plain text parts, not system
  prompts, so they flow with the user's other text in order — a
  vision-disabled model still sees the image in the "right place"
  relative to the prompt.

**Next suggested action:** `Continue Phase 2 with §2 #6 agent-team-
runtime: a lightweight multi-agent scheduler that composes multiple
MemoryAgent / MultimodalAdapter / ToolOrchestrator instances as named
roles, routes messages between them, and reports a run trace through
the telemetry sink so §2 #8 evals can regress the team's behaviour.`

## 2026-04-23 — §2 #8 eval-harness

**Shipped** `frok.evals`: declarative cases, composable scorers, a
runner that re-plays through any `GrokClient`, and a baseline-trace
differ that diffs captured `JsonlSink` runs against live candidates.

* **`frok.evals.case`** — `EvalCase` (messages, tools, scorers,
  optional baseline path, max-steps, dry-run), `Observation`
  (final response + invocations + full event stream + aggregates like
  `total_tokens` / `total_latency_ms` / `tool_call_order`), `Score`
  (ok / fail factories), `EvalResult`, `EvalReport` with
  `to_summary()` and `to_markdown()` verdict rendering.
* **`frok.evals.scorers`** — 10 composable, pure-function scorers:
  * truthfulness: `AnswerContains`, `AnswerMatches`, `AnswerAbsent`,
    `NoSafetyBlocks`
  * tool-behavior: `ToolCalled` (with count), `ToolNotCalled`,
    `ToolArgsSubset`, `ToolSequence` (prefix match)
  * perf / trace: `TokensWithin`, `NoErrors` (covers both run-level
    exceptions and any errored span)
* **`frok.evals.runner.EvalRunner`** — factory-per-case pattern
  (`(sink) -> GrokClient`) so each case gets a fresh `InMemorySink`
  and independent state. Uses `ToolOrchestrator` when the case
  declares tools, otherwise a single `client.chat` call. Runner
  swallows exceptions into `Observation.error` so one bad case
  doesn't abort the report.
* **`frok.evals.baseline`** — `diff_against_baseline(obs, path)`
  reads a `JsonlSink` capture with `telemetry.read_jsonl`, compares
  the tool-call order, token totals, and error count, and marks
  `regressed=True` on tool-sequence divergence or new errors (token
  deltas alone do not regress). The runner escalates
  `regressed=True` to an overall case failure.
* **Tracer tweak** — `SpanHandle.fail(reason)` lets callers mark a
  span as errored without re-raising. Wired through the tool
  orchestrator's caught-exception paths so "model recovers from a
  handler exception" still surfaces to `NoErrors` as a regression.

**Verification.** `python3 -m pytest -q` → 111 passed in 0.34s (21
new). The runner tests exercise both paths (chat-only + tools),
handler-error recovery, and the full Markdown-report shape.

**Decisions / trade-offs.**
* Scorers are *pure callables*, not a class hierarchy — keeps
  composition trivial (`scorers=[AnswerContains("42"),
  ToolCalled("add")]`) and sidesteps registration overhead.
* Baseline regressions check structural behaviour (tool order +
  errors), not tokens. Token deltas are reported for visibility but
  a longer answer shouldn't fail a regression test when the answer
  is still right.
* No case-file format yet (YAML/TOML) — cases are Python values.
  Fine for §2 #8 scope; a format loader is a cheap follow-up once
  real cases accumulate.

**Next suggested action:** `Continue Phase 2 with §2 #5 multimodal-
adapter: a typed IO surface that accepts images (path / bytes /
URL) and audio, routes them to Grok's vision + voice endpoints
through the GrokClient transport, and falls back to a text
description when a modality is unsupported.`

## 2026-04-23 — §2 #7 telemetry

**Shipped** `frok.telemetry` and wired it into every Phase-2 producer so
§2 #8 evals can regress on structured traces.

* **`frok.telemetry.sink`** — canonical `Event` dataclass (`ts`,
  `trace_id`, `span_id`, `parent_span_id`, `kind`, `name`,
  `duration_ms`, `data`, `error`) plus four sinks:
  * `NullSink` — default; tracers fast-path around it so the
    zero-consumer case is free.
  * `InMemorySink` — collects events with `find` / `spans` / `errors`
    query helpers; the shape the eval harness will consume.
  * `JsonlSink` — append-only newline-delimited JSON, thread-safe, with
    a `read_jsonl()` replay helper.
  * `MultiSink` — fan-out across several sinks.
* **`frok.telemetry.tracer`** — `Tracer.span(name, **attrs)` is an async
  context manager that emits `span.start` + `span.end` and records
  parent/child through `contextvars`. Exceptions are captured on the
  span as `error` and re-raised. A `SpanHandle.set(**kwargs)` lets
  producers attach measurements (tokens, hit-count, …) once known. The
  `NullSink` fast-path short-circuits all allocation when no consumer
  is attached.
* **Wiring** (all backwards-compatible — defaults keep the null tracer):
  * `GrokClient.chat` → `grok.chat` span with `model`,
    `message_count`, `has_tools`, `prompt_tokens`, `completion_tokens`,
    `total_tokens`, `tool_calls`, `finish_reason`, `safety_findings`,
    plus a `safety_blocked` attr on ingress/egress blocks.
  * `MemoryStore.remember/recall/forget` → `memory.remember`,
    `memory.recall` (with `candidates` / `hit_count`), `memory.forget`.
  * `ToolOrchestrator` → root `tool.run` span wrapping the loop and
    a nested `tool.invoke` per call (`tool`, `call_id`, `dry_run`,
    `error_kind`, `result_len`). Nested spans inherit `trace_id` so
    a full run reconstructs as a single tree.

**Verification.** `python3 -m pytest -q` → 90 passed in 0.40s (18 new).
Integration tests pin the event shape + nesting contract so §2 #8 can
rely on it.

**Decisions / trade-offs.**
* Clock + id generator are injectable on `Tracer` — tests want
  determinism; production gets `time.time` + `secrets.token_hex(8)`.
* No sampling / batching yet. `JsonlSink` flushes on every event; if it
  becomes a bottleneck we can add buffering behind the same interface
  without touching producers.
* Span data is deliberately small (ints, floats, short strings) so it
  can survive JSON round-trips. No message bodies / tool args are
  emitted — PII already leaks into logs faster than people think.

**Next suggested action:** `Continue Phase 2 with §2 #8 eval-harness:
a deterministic replay/diff runner that re-plays a captured JsonlSink
trace through a candidate model/client, scores truthfulness +
tool-behavior regressions, and produces a compact verdict doc.`

## 2026-04-23 — §2 #4 tool-use-orchestrator

**Shipped** `frok.tools` + tool-use plumbing on `GrokClient`.

* **`GrokClient` / `GrokMessage` / `GrokResponse` extension**
  * New `ToolCall` dataclass (`id`, `name`, `arguments` as a JSON string).
  * `GrokMessage` carries optional `tool_calls` + `tool_call_id`; its
    payload emits `content: null` alongside `tool_calls` as the xAI /
    OpenAI spec expects for assistant turns.
  * `GrokResponse` exposes `tool_calls` and `finish_reason`. Safety
    pre-flight now preserves `tool_calls` + `tool_call_id` across its
    rebuild (fix caught by tests).
* **`frok.tools.schema`** — zero-dep Draft-07 subset validator (type,
  enum, required, additionalProperties, items, min/max, length) plus a
  `infer_schema(fn)` that turns a Python signature into a JSON Schema —
  handles `Optional`, PEP-604 `A | B`, `Literal`, `Enum`, `list[T]`,
  `dict`, and defaults.
* **`frok.tools.registry`** — `Tool`, a `@tool` decorator (param/no-param
  forms), and `ToolRegistry` with `.spec()` (OpenAI-compatible) and
  `.dispatch(name, args, dry_run=...)` that validates args, awaits
  async handlers, stringifies structured results, and honours
  `side_effects=False` / a custom `dry_run_handler`.
* **`frok.tools.orchestrator`** — `ToolOrchestrator` runs the full loop
  against `GrokClient`: send → if `tool_calls` → dispatch each → append
  assistant + tool messages → repeat until `finish_reason != tool_calls`
  or `max_steps`. Bad-arg / unknown-tool / handler-raised errors are
  surfaced *back to the model* as tool-message content so it can
  recover rather than crashing the run.

**Verification.** `python3 -m pytest -q` → 72 passed in 0.22s (30 new).

**Decisions / trade-offs.**
* Parallel `tool_calls` in one turn execute sequentially on purpose —
  deterministic ordering matters more than latency at this stage, and
  `asyncio.gather` is a one-line swap when it doesn't.
* Dry-run policy is per-tool: side-effectful tools stub to a predictable
  `[dry-run] name({args})` string unless they provide a `dry_run_handler`;
  read-only tools (`side_effects=False`) run for real. This lets the
  loop still make forward progress under dry-run.
* Schema inference stays permissive on unknown annotations (empty
  schema) rather than failing import-time — a broken annotation
  shouldn't break registration.

**Next suggested action:** `Continue Phase 2 with §2 #7 telemetry — a
pluggable structured-log / trace sink that every GrokClient.chat,
MemoryStore op, and ToolOrchestrator invocation can emit to, so #8
evals can regress on runs later.`

## 2026-04-23 — §2 #3 persistent-memory

**Shipped** `frok.memory` on top of Phase 2 #1/#2.

* **`Embedder` protocol + `HashEmbedder`** (`memory/embedder.py`)
  * Deterministic feature-hashing fallback (blake2b → signed bucket),
    L2-normalised. Zero deps, zero network — lets tests and offline
    smoke runs produce meaningful cosine distances without a real
    embedding provider. `Embedder` is a `@runtime_checkable` Protocol so
    real xAI/Voyage/OpenAI embedders drop in.
* **`MemoryStore`** (`memory/store.py`)
  * SQLite-backed, embeddings stored as packed float32 BLOBs alongside
    rows. Cosine similarity computed in Python — adequate for the
    small-agent case; swap to sqlite-vss / ANN behind the same surface
    when §2 #7 telemetry shows it's needed.
  * API: `remember`, `remember_many`, `forget`, `recall` (k, kind, time
    window, min-score), `recent`, `count`. Persists across reopen.
* **`MemoryAgent`** (`memory/agent.py`)
  * Wraps `GrokClient`. Each turn: sanitise user text via the client's
    ruleset, recall top-k similar memories, inject them as a system
    message, send to Grok, then store both turns (sanitised user +
    assistant + usage metadata). PII-blocked prompts never reach the
    store or the network.

**Verification.** `python3 -m pytest -q` → 42 passed in 0.22s (18 new).

**Decisions / trade-offs.**
* Kept a single long-lived SQLite connection per `MemoryStore`. Simpler
  and fine for single-agent use; a pool is trivial to add later.
* Default recall `min_score=0.1` in `MemoryAgent` — filters out the
  near-orthogonal junk the hash embedder produces on unrelated text.
  Real embedders will want a different threshold; it's a field on the
  agent.
* Chose to sanitise user text **before** recall so prompt-injection and
  PII shapes don't influence the recalled context either.

**Next suggested action:** `Continue Phase 2 with §2 #4 tool-use-
orchestrator: a Tool registry + dispatch layer that plugs into
GrokClient.chat(tools=...) and routes the model's function calls to
typed handlers, with schema validation and a dry-run mode.`

## 2026-04-23 — Phase 2 kickoff (branch `claude/super-ai-frok-phase-2-bWvah`)

**Shipped** §2 items #1, #2, #10 as a usable first slice of the Super AI
Frok core.

* **§2 #1 grok-safety-rules** (`src/frok/safety/rules.py`)
  * Declarative rule engine. Four built-ins: anti-sycophancy (REWRITE),
    no-overclaim (BLOCK), PII redaction for email/phone/SSN (REWRITE),
    prompt-injection (WARN).
  * `SafetyRuleSet.apply()` applies non-overlapping rewrites right-to-left
    so spans stay valid, and preserves original text on BLOCK.
* **§2 #2 grok-client** (`src/frok/clients/grok.py`)
  * Async `GrokClient` for xAI `/chat/completions`. Transport is a protocol
    (no hard httpx/aiohttp dependency) so it's trivially testable.
  * Exponential backoff + jitter on 429/5xx; 4xx other than 429 raise
    immediately. Lifetime prompt/completion token totals are tracked.
  * Pre-flight runs the ruleset over every inbound message; post-flight
    runs it over the model output. Callers can opt out with an empty
    ruleset.
* **§2 #10 content** (`src/frok/content/x_post.py`)
  * `normalize_post()` accepts X API v2 payloads (with or without
    `includes`) and loose scrape dicts, falling back to text extraction
    when `entities` is missing.
  * `thread_from_posts()` union-finds on `reply_to_id` + `conversation_id`
    and returns chronologically-sorted threads.
  * Media refs are deterministically ordered by `media_key`.

**Interpretation note.** The kickoff prompt referenced "§2 #10's content"
without a pre-existing ROADMAP. I interpreted #10 as X-platform content
ingestion because it's the most mission-aligned reading ("X real-time data
agents"). `ROADMAP.md` §2 #10 is marked as a chosen interpretation — if a
different #10 was intended, the module is self-contained and easy to
rename or replace.

**Verification.** `python3 -m pytest -q` → 24 passed in 0.08s.

**Decisions / trade-offs.**
* Kept zero runtime dependencies. Transport is injected; a production
  httpx adapter is a ~10-line follow-up, not a core concern.
* Safety rules are heuristic and deterministic by design — auditable
  first, classifier-augmented later (§2 #7 telemetry + §2 #8 evals).
* `XPost` is frozen so it's safe to hand across agent-team boundaries
  once §2 #6 lands.

**Next suggested action:** `Continue Phase 2 with §2 #3 persistent-memory
(episodic + vector store) backed by SQLite + a pluggable embedder, wired
through the grok-client for long-running agent context.`

## 2026-04-23 — repo bootstrap
Initial commit of master instructions and empty progress/changelog.
