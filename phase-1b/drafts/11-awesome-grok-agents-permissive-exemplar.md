# Add a permissive-profile exemplar template to awesome-grok-agents

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #11 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/awesome-grok-agents
- **Risks closed**: closes the "missing-exemplar" finding in `audits/00-ecosystem-overview.md §6.2` (the 6-strict / 4-standard / **0-permissive** distribution across the 10 featured agents). Contributes indirectly to full closure of the safety-profile contract `grok-yaml-standards` publishes under §2 #5.
- **Source audits**: `[→ 06 §9 row 1]`. Supporting: `audits/00-ecosystem-overview.md §6.1, §6.2` (tripartite model, distribution table).
- **Effort (§2)**: S — a single template + `featured-agents.json` entry + CI passes. The "wait on §5" is the blocker, not the work itself.
- **Blocked by (§2)**: #5 — the permissive template's `grok-install.yaml` needs to be honest against the published rubric. Before the rubric exists, "permissive" is prose; after, it is a seven-axis contract. The exemplar only means what it says once the contract exists.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft's §Acceptance Part A template fields if §2 #5's `permissive` row (Part A of that draft) is substantively changed during upstream review. The exemplar template's `grok-install.yaml` body has to match whatever the rubric's final `permissive` column says.

- **Suggested labels**: `template`, `safety-profile`, `permissive`, `phase-1b`

---
