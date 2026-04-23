# Publish a unified safety-profile rubric (strict / standard / permissive) with conformance tests

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #5 (`audits/99-recommendations.md`)
- **Target repo (primary — owner of the rubric artefact)**: AgentMindCloud/grok-yaml-standards
- **Target repos (consumers / conformance-test adopters)**: AgentMindCloud/awesome-grok-agents, AgentMindCloud/grok-install-cli, AgentMindCloud/grok-build-bridge, AgentMindCloud/grok-agent-orchestra
- **Filing strategy**: one coordination issue in `grok-yaml-standards` (primary — owner of the rubric); consumer-repo checklist rows inside the acceptance criteria. The user may optionally file short cross-reference issues in the four consumer repos once this primary lands, pointing at its `rubric-v1.md` path.
- **Risks closed**: partial UNV-3 (S3) — enables UNV-4 (S3) closure once consumers adopt. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 02 §9 row 3]`, `[→ 06 §9 row 1]`. Substantive cross-cut evidence in `audits/00-ecosystem-overview.md §6` (tripartite safety model, 6/4/0 distribution, three independent static-regex implementations).
- **Effort (§2)**: M — the rubric text itself is small; the conformance-test format + coordination across 4 consumer repos is what makes this M-effort.
- **Blocked by**: none
- **Unblocks**: §2 #1 (shared `grok-safety-rules` package), §2 #11 (permissive-profile exemplar), §2 #17 (`grok-agent-orchestra` bootstrap + Lucas behavioural contract)
- **Suggested labels**: `spec`, `safety`, `ecosystem`, `phase-1b`

---
