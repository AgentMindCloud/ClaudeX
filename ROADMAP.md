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

## Phase 1 candidates (1A `done`; 1B/1C/1D still `proposed` — pick one or write your own)

### 1A. Codebase audit of existing Grok/X repos (done)
- User supplied 12 AgentMindCloud repos at Phase 0 close.
- Agent audited each via WebFetch (one local for ClaudeX self-audit), mapped structure, and produced an audit report with the top-5 highest-leverage improvements per repo.
- Output: `audits/01-grok-install.md` … `audits/12-claudex.md` + cross-cuts `audits/00-ecosystem-overview.md`, `audits/97-methodology.md`, `audits/98-risk-register.md`, `audits/99-recommendations.md`.
- **Backlog for the next phase lives in `audits/99-recommendations.md`** — 20 ecosystem-wide top-line recommendations + 28 deferrals, each cross-linked to its source audit and risk-register row.

### 1B. Greenfield `frok-super-agent` v0.1 scaffold
- Agent scaffolds a minimal Python (or TypeScript) package for the Super AI Frok core: agent loop, tool registry, persistent memory stub, Grok API client, X API client, test harness, CI config.
- Output: a runnable `hello-frok` demo that calls Grok and posts to a test X account (mock or real).
- Pick this when: you want to start building Frok from zero in this repo.

### 1C. Grok API wrapper + tool-use library
- Agent builds an SDK wrapping xAI's Grok API: streaming, tool calls, structured output, retries, cost tracking.
- Output: `grok-client/` package with unit tests and a usage example.
- Pick this when: Frok needs a solid foundation before agent-level work.

### 1D. X real-time data agent prototype
- Agent builds a small service that subscribes to X data (firehose or filtered stream), enriches posts via Grok, and emits structured events.
- Output: `x-stream-agent/` with a replayable fixture so it's testable without live X credentials.
- Pick this when: real-time X awareness is the priority.

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
