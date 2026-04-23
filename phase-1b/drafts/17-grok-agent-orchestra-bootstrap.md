# Bootstrap grok-agent-orchestra with a working multi-agent pattern + a behavioural Lucas safety veto

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #17 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/grok-agent-orchestra
- **Risks closed**: partial GOV-3 (S3) — from `audits/98-risk-register.md`. Full GOV-3 closure also requires the sibling §2 #16 bootstrap (`vscode-grok-yaml`) + §2 #15 landing the honesty-fix on both shell repos. Also closes UNV-3 (S3) — Lucas safety veto becomes behaviourally defined once this rec lands.
- **Source audits**: `[→ 10 §9 row 2]`. Supporting: `audits/10-grok-agent-orchestra.md §1, §2, §10` (LICENSE-only repo + advertised-but-undefined "Lucas" veto), `audits/10 §9 rows 4, 5` (the Lucas definition + shared safety-layer recs this draft absorbs).
- **Effort (§2)**: L — bootstrap of a shell repo means source + CI + docs + tests + release from zero. The multi-agent pattern itself is the biggest chunk.
- **Blocked by (§2)**: #5 — Lucas's veto semantics can only be defined in terms of the published safety-profile rubric; without the rubric, "Lucas" is branding without a contract (UNV-3).

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative. Also depends on [`phase-1b/drafts/01-shared-grok-safety-rules-package.md`](01-shared-grok-safety-rules-package.md) as a day-one dependency — that draft is itself speculative on #5, so this is two layers of speculation.
- **Re-review trigger**: rewrite this draft if either prerequisite is substantively rewritten during upstream review. Specifically: (a) §2 #5's seven-axis rubric shape drives the Lucas veto's normative definition in Part B; if axes are added/removed, the veto rule changes. (b) §2 #1's package API drives the orchestra's imports in Part A; if the package lands under a different name or with a different API, Part A's imports need updating. If §2 #1 is NOT filed or merged before this draft is filed, fall back to pinning `grok-install-cli`'s `safety/` module directly with a "TODO: migrate to grok-safety-rules once shipped" comment in Part A — marginal cost, easy to clean up.

- **Suggested labels**: `bootstrap`, `v0.1.0`, `multi-agent`, `lucas-veto`, `phase-1b`

---
