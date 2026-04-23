# Extract a shared grok-safety-rules package consumed by every safety-aware repo

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #1 (`audits/99-recommendations.md`)
- **Target repo (primary)**: AgentMindCloud/grok-install-cli *(primary — owns the most mature safety-rules implementation today; extraction happens here first)*. Alternative primary: a new `AgentMindCloud/grok-safety-rules` repo if the team prefers a separate home. The draft body below is written for the "extract from `grok-install-cli`" path and flags the new-repo alternative in §Notes.
- **Consumer repos (adoption follow-ups)**: AgentMindCloud/grok-build-bridge, AgentMindCloud/grok-agents-marketplace *(via the CI layer)*, AgentMindCloud/grok-agent-orchestra *(via §2 #17)*, AgentMindCloud/awesome-grok-agents *(via §2 #12's stub removal — already covered)*.
- **Filing strategy**: coordination issue in `grok-install-cli` describing extraction + release + consumer adoption. Consumer-repo adoption follow-ups open **only after** this primary merges AND the first release of the extracted package ships.
- **Risks closed**: UNV-4 (S3) outright *(the "three parallel implementations drift silently" underlying cause is resolved by the extraction)*; partial SEC-1 (S1) *(the bridge's LLM-audit prompt-injection fragility is unchanged; the static-scan layer that feeds it becomes shared + auditable, reducing the surface the LLM has to work around)*. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 09 §9 row 4]`, `[→ 03 §9 row 3]`, `[→ 10 §9 row 5]`, `[→ 06 §9 row 2]`. Cross-cut evidence in `audits/00-ecosystem-overview.md §6.3` (three parallel implementations enumerated) + `§9.B` if present.
- **Effort (§2)**: L — extraction + packaging + three consumer-repo PRs + coordinated release. The rubric from §2 #5 gives the shared contract; this rec ships the shared *code* that implements it.
- **Blocked by (§2)**: #5 — the shared package needs the rubric as its behavioural contract. Without it, the extraction locks in three-way drift behind a single import name.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft if §2 #5's normative seven-axis rubric table is substantively changed during upstream review (e.g. axes added/removed, profile names changed). This draft's package API enumerates the seven axes; if the rubric's axis count shifts, the API shape shifts with it.

- **Suggested labels**: `extraction`, `shared-library`, `safety`, `ecosystem`, `phase-1b`

---
