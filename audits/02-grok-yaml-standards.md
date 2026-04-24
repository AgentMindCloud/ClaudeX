# Audit: grok-yaml-standards

- **Upstream**: https://github.com/AgentMindCloud/grok-yaml-standards
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (release v1.2.0 tagged 2026-04-17)

## 1. Summary

`grok-yaml-standards` is the schema-root repo that extends `grok-install.yaml` with 12 standardized YAML file types triggered via `@grok` comments on X (e.g. `@grok config`, `@grok spawn agent:<Name>`). Release v1.2.0 shipped 4 spec extensions (`grok-tools`, `grok-deploy`, `grok-analytics`, `grok-ui`) on top of the 8 core standards, relicensed from MIT to Apache 2.0, and added JSON Schemas for every file type. The CI validates all 12 standards via a matrix-driven ajv-validate job — considerably stronger coverage discipline than `grok-install`'s 1-of-6 example gap. Active development (3 releases in 2 days, 2 open issues, 2 open PRs). Headline risk: **schema-draft drift** — this repo targets JSON Schema draft-07 while `grok-install` v2.14 already uses draft-2020; documentation explicitly defers alignment to v1.3 (see §6).

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/               # release.yml, validate-schemas.yml
├── .grok/                           # sample .grok/ folder (ready-to-copy)
├── grok-agent/                      # per-standard folders (spec + example)
├── grok-analytics/
├── grok-config/
├── grok-deploy/
├── grok-docs/
├── grok-prompts/
├── grok-security/
├── grok-test/
├── grok-tools/
├── grok-ui/
├── grok-update/
├── grok-workflow/
├── schemas/                         # README.md + 12 JSON schema files (one per standard)
├── .gitignore, .yamllint
├── CHANGELOG.md, CONTRIBUTING.md, CONTRIBUTORS.md, LICENSE, README.md,
├── ROADMAP.md, SECURITY.md,
├── standards-overview.md            # table + comparison matrix
└── version-reconciliation.md        # authoritative standards-count record
```

**Entry points**
- Per-standard folder `grok-<name>/` with its own spec + `example.yaml`.
- Machine-readable contracts: 12 JSON schemas in `schemas/grok-<name>.json`.
- User-facing onboarding: copy `.grok/` sample folder into any repo, triggers work via `@grok <command>`.

**Language mix**: Not shown in linguist bar; predominantly YAML + Markdown + JSON `(inferred)`.

## 3. Dependency graph

- **Inbound** (per Phase 1 inventory):
  - `vscode-grok-yaml` — IntelliSense uses these schemas.
  - `awesome-grok-agents` — templates reference the 12 standards (`inferred`).
  - `grok-install-cli` — the spec's safety-profile nomenclature (strict/standard/permissive) is enforced here `(inferred; cross-repo grep not possible on WebFetch)`.
  - `grok-docs` — schemas auto-synced to docs site per Phase 1 probe.

- **Outbound**: extends `grok-install.yaml` (the core `grok-install` repo's spec) — this is an additive, domain-specific layer, not a fork.

- **External runtime deps** (from `validate-schemas.yml`):
  - Python 3.12, `yamllint==1.35.1` (exact pin).
  - Node 20, `ajv-cli@5.0.0`, `js-yaml@4.1.0` (exact pins).
  - `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4` — major-tag pinning, not SHA.

## 4. Documentation quality

- **README.md**: present; explains the 12-standard mental model and shows an immediate copy-from-sample workflow. Clear table mapping standard → trigger → purpose.
- **CHANGELOG.md**: present, granular, dated (1.0.0/1.1.0/1.2.0 + Unreleased section).
- **standards-overview.md**: canonical table + compatibility matrix; names the 12 standards and categorises into 8 core + 4 extensions; declares Draft-7 → Draft-2020-12 migration for v1.3.
- **version-reconciliation.md**: *exceptional* artefact — explicitly corrects prior claims of 8 or 14 standards; records why `grok-cache.yaml` and `grok-auth.yaml` were declined (CI complexity, forward-compat risk); provides ready-to-use PR language for downstream fixes.
- **Governance files**: `CONTRIBUTING.md`, `CONTRIBUTORS.md`, `ROADMAP.md`, `SECURITY.md` all present. `Unreleased` section mentions CODEOWNERS/FUNDING pending.

**Score: 4/5** — above ecosystem average. `version-reconciliation.md` is a standout. Loses a point because `standards-overview.md` summary I retrieved skipped the safety-classification column (needs verification with a second fetch) and because per-standard spec content wasn't individually sampled.

## 5. Tests & CI

From `validate-schemas.yml`:

| Job | Purpose |
|-----|---------|
| `yamllint` | Lints `.grok/` and `grok-*/example.yaml` (Python 3.12, yamllint 1.35.1 exact pin). |
| `schema-smoke` | Verifies every schema contains `$id`, `title`, `description`; confirms `$schema` is draft-07. |
| `ajv-validate` | **Matrix over all 12 standards** — validates each `grok-*/example.yaml` against `schemas/grok-<name>.json`. (ajv-cli 5.0.0, js-yaml 4.1.0, draft-07.) |

Second workflow: `release.yml` (content not fetched — `(WebFetch-limited)`).

**Coverage posture**: Full matrix across all 12 standards — stronger than `grok-install`'s validate.yml (which skips 5 of 6 v2.14 examples).

## 6. Security & safety signals

- **Dependency pinning**: exact-version pins on yamllint / ajv-cli / js-yaml (good); major-tag pinning on GitHub actions (not SHA) — same supply-chain pattern as `grok-install`.
- **`SECURITY.md`**: present; content not fetched `(WebFetch-limited)`.
- **Safety-profile integration**: the `grok-security` standard defines the security surface. Per `standards-overview.md`, the 12 standards span security levels from "Low" (prompts, docs) to "Critical" (security, deploy). This is the categorical source for ecosystem safety levels `(needs clone to verify the actual rubric)`.
- **No secrets in repo**: CI uses default GitHub token `(inferred)`.
- **Schema-draft drift**: this repo targets draft-07; `grok-install` v2.14 uses draft-2020. `standards-overview.md` explicitly defers alignment to v1.3 — drift is acknowledged, not silent. Downstream tooling (ajv-cli, vscode-grok-yaml) needs to handle both drafts until then.

## 7. Code quality signals

- **Linter**: yamllint via `.yamllint` config at repo root.
- **Schema discipline**: strong — per-standard $id / title / description enforced by `schema-smoke`.
- **No runtime code**: spec/schema repo only.
- **Module cohesion**: clean per-standard folder layout; easy to locate and version individual standards.
- **Licensing history**: MIT at v1.0.0 → Apache 2.0 at v1.2.0. Signals a deliberate shift to align with xAI/grok-install licensing. Downstream forks pre-1.2.0 carry MIT obligations.

## 8. Integration contract

- **Public surface**:
  - 12 YAML file types (names, versions, compat entries) — one per standard.
  - 12 JSON schemas (draft-07).
  - `.grok/` sample folder as onboarding artefact.
  - `@grok <command>` trigger vocabulary (table in README).
  - `standards-overview.md` as the authoritative compatibility matrix.
- **Current version**: v1.2.0 (2026-04-17).
- **Breaking-change posture**: documented per-standard in CHANGELOG; `version-reconciliation.md` establishes a process for future additions via `discussion/new-standard` issues. Schema-draft upgrade planned for v1.3 will be a cross-ecosystem coordination event.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Ship v1.3 with draft-2020-12 migration aligned with `grok-install` v2.14 | M | 5 | Resolves the only structural drift between the two spec roots; unblocks `vscode-grok-yaml` from maintaining dual-draft validation. Explicit in `standards-overview.md` already. | Coordination with `grok-install` release |
| 2 | Pin GitHub actions by SHA (`checkout`, `setup-python`, `setup-node`) | S | 4 | Matches the exact-version posture already used for ajv-cli/js-yaml/yamllint. Removes last supply-chain looseness in CI. | None |
| 3 | Publish a shared `safety-levels.md` (or extend `standards-overview.md`) defining what "Low / Medium / High / Critical" mean operationally | S | 4 | Table references the levels but the rubric is not extracted. `grok-install-cli` and `awesome-grok-agents` would both benefit from a shared source of truth. | None |
| 4 | Add a `cross-repo-compat` CI job that checks `grok-install` v2.x against standards versions | M | 4 | A simple smoke test that fetches `grok-install`'s latest schema and verifies the `grok-<name>.json` files still slot into the outer spec. Catches drift at the source. | `grok-install` repo consent |
| 5 | Move "deferred CI workflows" (per `[Unreleased]` in CHANGELOG) out of the unreleased bucket — ship or delete | S | 3 | Unshipped CI items accumulate technical debt; explicit decisions close the loop. | None |

## 10. Open questions / unknowns

- What's in `release.yml`? Does it cut GitHub releases, sync schemas downstream, or trigger `grok-docs`? `(WebFetch-limited — not fetched)`
- Per-standard spec content (e.g. what does `grok-security.yaml` actually define?) `(needs deeper sampling — each folder has spec + example; not read this iteration)`
- Does `SECURITY.md` set a disclosure policy beyond `grok-install`'s "repo issue or @JanSol0s X handle"? `(WebFetch-limited — not fetched)`
- Are the 2 open issues / 2 open PRs related to v1.3 migration? `(needs clone / needs org MCP)`
- Does `grok-install-cli` actually validate against *these* 12 schemas at runtime, or does it vendor its own? `(needs clone of CLI repo)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-yaml-standards | Repo landing: description, stars (1), forks (0), issues (2), PRs (2), license (Apache 2.0), top-level tree, 12 `grok-*/` folders. |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-yaml-standards/main/version-reconciliation.md | Authoritative "12 standards" count; declined grok-cache/grok-auth; `discussion/new-standard` issue process. |
| 3 | https://github.com/AgentMindCloud/grok-yaml-standards/tree/main/schemas | 12 JSON schemas enumerated (grok-agent, grok-analytics, grok-config, grok-deploy, grok-docs, grok-prompts, grok-security, grok-test, grok-tools, grok-ui, grok-update, grok-workflow) plus README.md. |
| 4 | https://github.com/AgentMindCloud/grok-yaml-standards/tree/main/.github/workflows | Two workflows: `release.yml`, `validate-schemas.yml`. |
| 5 | https://raw.githubusercontent.com/AgentMindCloud/grok-yaml-standards/main/.github/workflows/validate-schemas.yml | Jobs: `yamllint`, `schema-smoke`, `ajv-validate` (matrix over 12 standards, draft-07, exact pins on yamllint 1.35.1 / ajv-cli 5.0.0 / js-yaml 4.1.0; actions pinned by major tag). |
| 6 | https://raw.githubusercontent.com/AgentMindCloud/grok-yaml-standards/main/CHANGELOG.md | Release history: v1.0.0 (2026-04-16, MIT), v1.1.0 (2026-04-16, draft-7 schemas), v1.2.0 (2026-04-17, +4 extensions, relicense to Apache 2.0). |
| 7 | https://raw.githubusercontent.com/AgentMindCloud/grok-yaml-standards/main/standards-overview.md | 8 core + 4 extensions split; security-level categorisation (Low → Critical); draft-07 → draft-2020-12 migration planned for v1.3. |
