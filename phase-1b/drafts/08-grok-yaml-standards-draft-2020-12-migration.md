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

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**In this repo** (`grok-yaml-standards` v1.2.0):

| Path | Current draft | Source |
|------|---------------|--------|
| `schemas/grok-agent.json` | draft-07 | `audits/02-grok-yaml-standards.md §2, §5, §11 row 3` |
| `schemas/grok-analytics.json` | draft-07 | same |
| `schemas/grok-config.json` | draft-07 | same |
| `schemas/grok-deploy.json` | draft-07 | same |
| `schemas/grok-docs.json` | draft-07 | same |
| `schemas/grok-prompts.json` | draft-07 | same |
| `schemas/grok-security.json` | draft-07 | same |
| `schemas/grok-test.json` | draft-07 | same |
| `schemas/grok-tools.json` | draft-07 | same |
| `schemas/grok-ui.json` | draft-07 | same |
| `schemas/grok-update.json` | draft-07 | same |
| `schemas/grok-workflow.json` | draft-07 | same |
| `.github/workflows/validate-schemas.yml` — `schema-smoke` job | asserts `$schema` is draft-07 (will need flip) | `audits/02-grok-yaml-standards.md §5` |
| `.github/workflows/validate-schemas.yml` — `ajv-validate` job | `ajv-cli@5.0.0` + `ajv-formats` (supports draft-2020-12) | `audits/02-grok-yaml-standards.md §5, §11 row 5` |

**Migration target already visible downstream:**

- `grok-install/schemas/v2.14/schema.json` — draft-2020-12,
  validated via `ajv-cli` in `schema-v2-14` CI job (1 of 6
  examples validated against it). *Source: `audits/01-grok-
  install.md §7, §11; audits/00-ecosystem-overview.md §4
  table row 1`.*
- `grok-build-bridge/grok_build_bridge/schema/bridge.schema.json`
  — draft-2020-12, validated via Python
  `jsonschema.Draft202012Validator` in the `schema-check` CI
  job. *Source: `audits/09-grok-build-bridge.md §5, §7`.*

**Mirror / sync jobs that follow this repo's draft choice
automatically** (they will pick up the new draft without code
changes once `$schema` flips):

- `grok-docs/.github/workflows/sync-schemas.yml` — daily mirror
  of `grok-yaml-standards/schemas/` to
  `docs/assets/schemas/`. *Source: `audits/05-grok-docs.md §5,
  §11 row 2`.*
- `awesome-grok-agents/.github/workflows/validate-templates.yml`
  — `ajv-cli@5 + ajv-formats@3` honours whatever `$schema` the
  schema declares. *Source: `audits/06-awesome-grok-agents.md §5`.*

**Risk register** — `audits/98-risk-register.md`:

- **VER-2** (S2, L-med, `open`): "`grok-yaml-standards` is on
  JSON Schema **draft-07**; `grok-install` v2.14 is on
  **draft-2020-12**. The two spec roots disagree on the
  meta-schema; alignment explicitly deferred to v1.3 in
  `standards-overview.md`."

**Syntactic differences between drafts that touch this repo**
(authoring-time checklist, see Part A):

- `$id` — same in both drafts; keep existing values.
- `definitions` → `$defs` — draft-07 uses `definitions`,
  draft-2020-12 uses `$defs`. Any schema using `definitions`
  needs renaming and `$ref` path updates.
- `examples` — draft-2020-12 standardises; any schema using
  it should gain a keyword-version check.
- `dependencies` → `dependentRequired` + `dependentSchemas` —
  split in draft-2019-09+. Any schema using `dependencies`
  needs rewriting.
- `exclusiveMinimum` / `exclusiveMaximum` — boolean in draft-07,
  numeric in draft-2020-12. Already numeric in every modern
  schema; no-op if the authors followed draft-07's newer
  behaviour.

(Not every schema will touch every construct above; the
migration PR's diff is the ground truth.)

## Acceptance criteria

Two parts. Part A is the migration itself; Part B is the
coordination to land it cleanly across downstream consumers. The
issue closes when both merge and v1.3.0 (or chosen release tag)
ships with the migrated schemas.

### Part A — Core migration (in `grok-yaml-standards`)

- [ ] **Flip `$schema`** across all 12 schema files:
      `"$schema": "http://json-schema.org/draft-07/schema#"`
      → `"$schema": "https://json-schema.org/draft/2020-12/schema"`.
      Do this in one PR per schema, or one PR for all 12; either
      is fine. Landing all 12 together simplifies the CI flip in
      the next bullet.
- [ ] **Rewrite syntactic constructs** that moved between drafts
      (see Evidence §):
      - Rename `definitions` → `$defs`; update every `$ref` that
        pointed at the old name.
      - Replace `dependencies` with `dependentRequired` +
        `dependentSchemas` wherever it is used.
      - Audit numeric/boolean `exclusiveMinimum` / `exclusiveMaximum`
        usage; should already be numeric.
      - Leave `$id` values unchanged (URLs stay stable; the
        schema's identity is the `$id`, not the `$schema`).
- [ ] **Update `schema-smoke` CI job** in
      `.github/workflows/validate-schemas.yml` to assert
      `$schema` is the draft-2020-12 URL instead of draft-07.
      Keep the existing `$id` / `title` / `description` assertions.
- [ ] **Confirm `ajv-validate` CI job still passes** against all
      12 `grok-*/example.yaml`. `ajv-cli@5.0.0` supports
      draft-2020-12 out of the box; no version bump needed.
      If a regression appears, the fix is to add `--spec=draft2020`
      explicitly — but default behaviour honours the `$schema`
      keyword, so no flag should be necessary.
- [ ] **Publish release notes** in `CHANGELOG.md` under `v1.3.0`
      (or `v1.2.1` if the team prefers not to bump minor for a
      migration): call out the `$schema` flip, the `definitions`
      → `$defs` rename, and any other syntactic rewrites. Include
      a "migration notes for consumers" subsection that says
      "drop any draft-07-specific validator flags; default
      `$schema`-keyword-aware behaviour works across every
      validator in the Grok ecosystem today".
- [ ] **Update `standards-overview.md`** to mark the
      draft-07/draft-2020 migration as *complete* rather than
      *deferred* (currently deferred to v1.3 in the document
      body; flip the language once the PR lands).
- [ ] **Update `version-reconciliation.md`** with a one-line
      entry recording when v1.3 closed the draft-07 chapter —
      this is the repo's audit-trail convention for
      version-related changes.

### Part B — Downstream coordination (smoke tests, no code changes required)

Downstream validators pick up the new draft automatically via
`$schema`-keyword awareness. Part B's job is to *verify* that
this is the case before the v1.3 release is cut — and to flag any
unexpected friction so it can be fixed at the source before
release day.

- [ ] **Pre-release smoke test against `grok-install`'s v2.14
      validator.** Run
      `ajv validate -s grok-yaml-standards/schemas/grok-security.json
      -d grok-yaml-standards/grok-security/example.yaml`
      against the migrated schemas with the same `ajv-cli@5`
      version `grok-install` CI uses. Expected: pass. If not,
      capture the failure and fix at the source before release.
- [ ] **Pre-release smoke test against `grok-docs`'s
      `sync-schemas.yml`.** Trigger the daily mirror job manually
      (workflow_dispatch) against a pre-release branch of
      `grok-yaml-standards`; verify the mirrored schemas in
      `grok-docs/docs/assets/schemas/` parse cleanly. Expected:
      pass (mirror job copies verbatim).
- [ ] **Pre-release smoke test against `awesome-grok-agents`'s
      `validate-templates.yml`.** Point that workflow at the
      pre-release `grok-yaml-standards` branch. `ajv-cli@5 +
      ajv-formats@3` is draft-2020-12 aware; the `schema` job
      should continue to pass. If `schema` fails because a
      template's YAML used a draft-07-specific construct that
      draft-2020-12 tightens, flag the template(s) in that
      repo's follow-up issue.
- [ ] **Pre-release smoke test against `grok-install-cli` and
      `grok-build-bridge`'s Python validators.**
      `grok-install-cli` uses `jsonschema>=4.21` (supports both
      drafts); `grok-build-bridge` already hard-binds to
      `Draft202012Validator`. Expected: no changes required in
      either repo. Verify with a smoke run of `grok-install scan`
      against a `grok-security`-using template.
- [ ] **Announce in `grok-install` and `grok-docs`**: once v1.3
      ships, open a one-line follow-up issue in each of those
      two repos (and only those two) confirming "schemas are
      now draft-2020-12 end-to-end". Closes the docs-drift on
      the published site and tightens `grok-install`'s
      own-v2.14-is-1-of-6 validation story (audit 00 §4 row 4).
- [ ] **Do NOT open follow-up issues in `grok-install-cli`,
      `grok-build-bridge`, `awesome-grok-agents`, or
      `grok-agents-marketplace`** unless the smoke tests above
      surface a real problem. The migration is transparent to
      them; follow-up noise dilutes the audit trail.

## Notes

- **Release name.** The `standards-overview.md` body and the
  §2 #8 text both call this the "v1.3 migration". Shipping under
  `v1.3.0` matches the existing expectation. If the team prefers
  `v1.2.1` (no breaking schema semantics in the migration),
  that's fine — but update `standards-overview.md` to match.
  The acceptance criteria above read `v1.3.0 (or chosen release
  tag)` for exactly this reason.

- **Why this is not a breaking change for schema users.**
  `$id` values stay the same; the set of valid documents under
  each schema stays the same (the draft-2020-12 constructs used
  in the migration are strictly more expressive than draft-07,
  not restrictive). Consumers that already validate via
  `$schema`-keyword-aware libraries (ajv-cli v5+, Python
  `jsonschema>=4.17`) pick up the new behaviour transparently.
  Consumers that hard-coded draft-07 in their validator (rare;
  only `grok-yaml-standards/schema-smoke` does this in the
  ecosystem) need one-line fixes.

- **Interaction with §2 #18 (CI template promotion).** §2 #18
  promotes `grok-build-bridge`'s CI workflow as the ecosystem
  baseline. The template's `schema-check` job uses
  `jsonschema.Draft202012Validator`. Once this rec lands,
  `grok-yaml-standards` can adopt the §2 #18 template without
  parameterising the draft version. If §2 #18 lands first (the
  cross-refs in the §2 #18 draft flag this as an option),
  `grok-yaml-standards` adopts the template's schema-check job
  with a `DRAFT=draft07` input or skips that job until this rec
  ships — both paths are documented in the §2 #18 draft.

- **Interaction with §2 #5 (safety-profile rubric).** §2 #5
  ships a new schema (`safety-profile-rubric.schema.json`) that
  already uses draft-2020-12 (per that draft's Part B). If §2 #5
  lands first, the rubric schema is the one draft-2020-12 file
  in an otherwise-draft-07 repo; this rec then extends the
  pattern across the other 12. If §2 #8 lands first, §2 #5's
  schema fits the pattern from day one. Either order is fine.

- **What's *not* in this migration.** Cross-spec validation
  jobs that smoke-test `grok-install` v2.x schemas against
  standards versions (audit 02 §9 row 4 — the
  `cross-repo-compat` job idea) are a separate follow-up and
  live in `audits/99-recommendations.md §3.2` as a deferred
  per-repo row. Not drafted here.

- **Filing strategy.** Single primary issue in
  `grok-yaml-standards`. No cross-ref issues needed — Part B's
  smoke tests happen against the pre-release branch from inside
  the primary PR discussion.
