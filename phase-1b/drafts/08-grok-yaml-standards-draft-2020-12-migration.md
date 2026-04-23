# Migrate grok-yaml-standards schemas to JSON Schema draft-2020-12 for v1.3

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #8 (`audits/99-recommendations.md`)
- **Target repo (primary)**: AgentMindCloud/grok-yaml-standards
- **Downstream validators (coordination, not filing)**: AgentMindCloud/grok-install (v2.14 already on draft-2020-12), AgentMindCloud/vscode-grok-yaml (future consumer), AgentMindCloud/grok-docs (mirrors schemas daily), AgentMindCloud/grok-install-cli, AgentMindCloud/grok-build-bridge, AgentMindCloud/awesome-grok-agents (ajv-cli@5 validators)
- **Filing strategy**: single issue in `grok-yaml-standards`. The migration is local to this repo's 12 schemas; downstream validators inherit via their existing schema fetches. No cross-ref issues needed — downstream repos already depend on whatever draft `$schema` declares.
- **Risks closed**: VER-2 (S2) outright — from `audits/98-risk-register.md`.
- **Source audits**: `[→ 02 §9 row 1]`. Cross-cut evidence in `audits/00-ecosystem-overview.md §4` (draft-07/draft-2020-12 matrix).
- **Effort (§2)**: M — 12 schemas × $schema swap + ajv-cli + Python validator swap + CI update + release coordination. Per-schema work is small; coordination cost lives in ensuring consumers downstream re-validate without flags being added.
- **Blocked by**: none
- **Cross-refs**: §2 #18 (CI template adoption — the promoted template already validates with Draft202012Validator; once §8 ships, `grok-yaml-standards` inherits cleanly without a parameterised validator). §2 #5 (safety-profile rubric schema uses draft-2020-12 already; if §5 lands first, §8 simply extends the pattern to the rest of the repo).
- **Suggested labels**: `schema`, `migration`, `v1.3`, `ecosystem`, `phase-1b`

---
