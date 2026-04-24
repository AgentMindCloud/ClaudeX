# ClaudeX — Super AI Frok + Grok/xAI Accelerator

> Status: **Phase 0 — Bootstrap.** No product code yet. This repo currently holds master instructions, a roadmap, and progress logs. See [ROADMAP.md](./ROADMAP.md) to pick the first real phase.

## What this repo is
A working space for an autonomous Claude-driven agent whose job is to accelerate xAI's Grok ecosystem and build the **Super AI Frok** project. The agent reads [CLAUDE.md](./CLAUDE.md) on every run to understand its mission, workflow, and autonomy rules.

## Repo layout (current)
```
.
├── CLAUDE.md      # Master instructions for the autonomous agent
├── ROADMAP.md     # Proposed phases — user picks which one goes live
├── PROGRESS.md    # Per-session log: what was done, why, what's blocked
├── CHANGELOG.md   # User-facing summary of notable changes
└── README.md      # This file
```

Future directories will appear once a Phase 1 candidate is selected in `ROADMAP.md` (e.g. `frok-super-agent/`, `grok-client/`, `x-stream-agent/`, `audits/`).

## How to work with the agent
1. Open [ROADMAP.md](./ROADMAP.md), pick a Phase 1 candidate (1A–1D) or write your own, and mark its status `approved`.
2. Fill [CLAUDE.md](./CLAUDE.md) lines 8–15 ("Primary Repos & Focus Areas") with the real repo URLs the agent should read.
3. Kick off an autonomous run, e.g.:
   ```
   claude --permission-mode auto -p "Begin Phase 1B autonomously, up to 20 iterations."
   ```
4. Review [PROGRESS.md](./PROGRESS.md) after each session; redirect by editing `ROADMAP.md` or replying with a new prompt.

## Conventions
- **Branching**: feature work lands on `claude/<slug>` branches, PR'd into `main`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`…). Subject ≤ 72 chars; body explains *why*.
- **Docs**: every phase updates `PROGRESS.md` (detailed) and `CHANGELOG.md` (one-line user-facing summary).
- **No hallucination**: the agent will pause and ask rather than fabricate capabilities, repos, or benchmarks.

## Contributing
This is a single-operator project right now. If that changes, contribution guidelines will appear in `CONTRIBUTING.md`.
