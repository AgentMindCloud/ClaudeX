# ROADMAP — Super AI Frok + Grok/xAI Accelerator

Living document. Proposed by the autonomous agent on 2026-04-23 as a starting point for user review. Reorder, edit, or delete phases freely — the agent will only pull from phases the user has marked `status: approved`.

Phase status legend: `proposed` (drafted, needs review) · `approved` (agent may work on it) · `in-progress` · `done` · `shelved`.

---

## Phase 0 — Bootstrap (done)
Establish the skeleton so later phases have somewhere to land.

Scope:
- Rename `CLAUDE.me` → `CLAUDE.md`. ✅
- Seed `README.md`, `ROADMAP.md`, `PROGRESS.md`, `CHANGELOG.md`. ✅
- Fill `CLAUDE.md` "Current Active Phase" with this phase. ✅
- Surface the remaining placeholder: `CLAUDE.md` "Primary Repos & Focus Areas" still needs real repo URLs from the user. (Carried into Phase 1A risk register as `GOV-5`.)

Exit: User approved Phase 1A (the codebase audit). Closed 2026-04-23.

---

## Phase 1 (1A `done`; 1B upstream-drafting `in-progress`; 1C / 1D / 1E still `proposed`)

### 1A. Codebase audit of existing Grok/X repos (done)
- User supplied 12 AgentMindCloud repos at Phase 0 close.
- Agent audited each via WebFetch (one local for ClaudeX self-audit), mapped structure, and produced an audit report with the top-5 highest-leverage improvements per repo.
- Output: `audits/01-grok-install.md` … `audits/12-claudex.md` + cross-cuts `audits/00-ecosystem-overview.md`, `audits/97-methodology.md`, `audits/98-risk-register.md`, `audits/99-recommendations.md`.
- **Backlog for the next phase lives in `audits/99-recommendations.md`** — 20 ecosystem-wide top-line recommendations + 28 deferrals, each cross-linked to its source audit and risk-register row.

### 1B. Upstream issue drafting — in-progress (first + second + third + Session 2 + fourth + fifth pass done 2026-04-23)
- Turn `audits/99-recommendations.md §2` top-20 recs into ready-to-file GitHub issue bodies under `phase-1b/drafts/`, indexed by `phase-1b/ISSUES.md`.
- **MCP-scope constraint**: drafts only. The Phase 1B agent's GitHub MCP scope is `agentmindcloud/claudex`-only; it cannot open issues on upstream AgentMindCloud Grok repos. The user files each draft manually and back-fills `phase-1b/ISSUES.md`'s **Filed** column.
- **First-pass slice (S-effort, no blockers)**: 4 §2 recs (#6, #9, #14, #15) → 6 draft files.
- **Second-pass slice (CI + supply-chain floor, no blockers)**: 3 §2 recs (#3, #13, #18) → 3 draft files; #18 is the delivery vehicle propagating #3 + #13's fixes across 7 adopters.
- **Third-pass slice (cross-ecosystem contracts + governance, M-effort, no blockers)**: 3 §2 recs (#5, #8, #20) → 3 draft files. #5 is the highest-fanout unblocker in the §2 graph.
- **Session-2 slice (speculative post-filing follow-ups, variable effort)**: 6 §2 recs (#1, #7, #11, #12, #16, #17) → 6 draft files. Every Session-2 draft carries the mandatory speculative-draft metadata header (prerequisite status + re-review trigger) and cannot be filed upstream until its prerequisite merges upstream first. Deepest speculation: §2 #12 (through #7→#6) and §2 #17 (through #1→#5).
- **Fourth-pass slice (grok-docs v2.14 unblocker, L-effort)**: 1 §2 rec (#10) → 1 draft file. Closes VER-4 + DOC-2 outright. Unblocks §2 #4 drafting.
- **Fifth-pass slice (repository_dispatch wiring, M-effort, speculative-on-#10)**: 1 §2 rec (#4) → 1 draft file. Two-part acceptance (publisher workflow in `grok-install` + three subscriber listener workflows). Closes VER-4 *trigger* side (§2 #10 closed the content side); partial DOC-1. Full VER-4 closure requires both this + #10 to merge upstream.
- **Cumulative**: **18 of 20 §2 recs drafted**; 20 draft files; 0 issues filed upstream (MCP scope limitation).
- **Undrafted §2 residual (2 of 20)**: #2 (shared Grok API client, L, reach 5), #19 (x-platform-toolkit CI, M, reach 2).
- **Tracker**: [`phase-1b/ISSUES.md`](phase-1b/ISSUES.md) — first/second/third/Session-2/fourth-pass/fifth-pass tables; next-pass candidates (§2 #2, #19); post-filing follow-ups (all drafted); blocked-by chains; filing audit trail.
- **Filing packets**: [`phase-1b/filing-packets/`](phase-1b/filing-packets/) — per-upstream-repo filing instructions. Session-2 content lives in packets 03 (§2 #7 + §2 #1), 06 (§2 #11 + §2 #12), 07 (§2 #16), 10 (§2 #17). Fourth-pass content in packet 05 (§2 #10). Fifth-pass content in packet 01 (§2 #4 primary) + subscriber cross-refs in packets 04, 05, 08.
- **Branch**: `claude/phase-1b-session-continuation-zQBET` (branched from Phase-1B tip `e1d32ae`).
- **Status**: five drafting passes complete; filing-packets updated; 20 drafts await upstream filing. One pass away from §2 top-20 completion. Next-pass decision: draft §2 #2, §2 #19, both in one pass, file current drafts, or pause. See `PROGRESS.md` Phase-1B fifth-pass "Next suggested action".

> **Label note**: "1B" here is the upstream issue drafting effort selected after Phase 1A close. The originally-proposed "1B. Greenfield `frok-super-agent` v0.1 scaffold" candidate has been relabelled to **1E** below; its content is unchanged and it remains `proposed`.

### 1C. Grok API wrapper + tool-use library
- Agent builds an SDK wrapping xAI's Grok API: streaming, tool calls, structured output, retries, cost tracking.
- Output: `grok-client/` package with unit tests and a usage example.
- Pick this when: Frok needs a solid foundation before agent-level work.

### 1D. X real-time data agent prototype
- Agent builds a small service that subscribes to X data (firehose or filtered stream), enriches posts via Grok, and emits structured events.
- Output: `x-stream-agent/` with a replayable fixture so it's testable without live X credentials.
- Pick this when: real-time X awareness is the priority.

### 1E. Greenfield `frok-super-agent` v0.1 scaffold *(originally labelled 1B — relabelled after 1B was assigned to upstream issue drafting)*
- Agent scaffolds a minimal Python (or TypeScript) package for the Super AI Frok core: agent loop, tool registry, persistent memory stub, Grok API client, X API client, test harness, CI config.
- Output: a runnable `hello-frok` demo that calls Grok and posts to a test X account (mock or real).
- Pick this when: you want to start building Frok from zero in this repo.

---

## Later phases (sketches, sequenced after Phase 1 selection)

- **Phase 2 — Persistent memory substrate**: vector store + episodic log + retrieval policy; shared by all Frok agents.
- **Phase 3 — Agent team orchestration**: multi-agent planner/worker/critic loop with tool-use budget tracking.
- **Phase 4 — Multimodal (vision/voice)**: image ingestion, audio transcription, voice synthesis hooks.
- **Phase 5 — Safety & alignment scaffolding**: eval harness, red-team suite, constitutional checks, kill-switch patterns.
- **Phase 6 — X-native deployment**: ship Frok as an X account/bot with rate-limit-aware posting and DM handling.
- **Phase 7 — Super-intelligence scaffolding**: self-improvement loop, skill library, long-horizon task decomposition.

---

## How to drive the agent
- Edit a phase's status to `approved` and (optionally) reply: `"Begin Phase 1B autonomously, up to 20 iterations."`
- To redirect mid-phase, edit this file — the agent re-reads it every phase boundary.
- To add a phase, append under the appropriate section; the agent will not reorder your edits.
