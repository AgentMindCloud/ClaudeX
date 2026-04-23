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

## Context

The two spec roots in the Grok ecosystem target different JSON
Schema meta-schemas:

- `grok-install` v2.14 ships its schema at `schemas/v2.14/
  schema.json` on **draft-2020-12**.
- `grok-yaml-standards` v1.2.0 ships all 12 per-standard schemas
  on **draft-07**.

`grok-yaml-standards/standards-overview.md` already declares a
planned migration to draft-2020-12 for v1.3 — the drift is
*acknowledged* and *scheduled*, not silent. This issue's job is to
land that planned migration so every validator in the chain stops
having to tolerate both drafts.

The cost of the current split is observable in three places:

1. **Downstream validators must support two drafts.** Any tool that
   validates schemas from both spec roots — the hoped-for
   `vscode-grok-yaml` extension, a unified CLI validator, or the
   CI template §2 #18 is promoting — has to run two draft engines.
   The `grok-build-bridge` CI workflow, which §2 #18 promotes as
   the ecosystem baseline, already uses
   `jsonschema.Draft202012Validator`; adopting that template in
   `grok-yaml-standards` today would fail until its schemas
   migrate.

2. **Schema authoring defensively hedges.** New additions to
   `grok-yaml-standards` (the `discussion/new-standard` process
   from `version-reconciliation.md`) are written against draft-07
   even when the authors know draft-2020-12 is coming — producing
   churn at v1.3 bump time.

3. **`grok-docs` mirrors the draft-07 schemas daily** (per audit
   05 §5's `sync-schemas.yml`), which locks draft-07 documentation
   into the published site until upstream migrates. The docs drift
   disappears on its own once this migrates.

The migration itself is mechanical in the hot path (swap
`$schema` URLs + retune any syntactic constructs that moved
between drafts). The M-effort rating comes from the
coordination around the v1.3 release: CI changes, ajv-cli version
confirmation, smoke-testing against consumers.
