# Audit: grok-install

- **Upstream**: https://github.com/AgentMindCloud/grok-install
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23

## 1. Summary

`grok-install` is the spec-root repo of the ecosystem — "the open standard to make any AI agent installable with one click on X using Grok." It houses the versioned YAML specification (v2.12 / v2.13 / v2.14 kept side-by-side for back-compat), a JSON Schema set, example agent definitions, a browser-side `index.html` / `my-agents.html`, and CI that validates examples against schemas. Maturity is early (1★, 0 forks, 0 open issues, 259 commits, solo maintainer @JanSol0s) but the spec artefacts are production-shaped: versioned schemas, contributing docs, security policy, dedicated anti-slop / release / pages workflows. Headline risk: **v2.14 schema is validated against only one example** (`examples/janvisuals/grok-install.yaml`), while the other five top-level examples are still validated against v2.13 — the v2.14 migration is half-done, and downstream consumers pinning v2.14 may get lax validation coverage.

## 2. Structural map

Top-level tree (2 levels, from GitHub file browser):

```
.
├── .github/workflows/        # anti-slop.yml, ci.yml, pages.yml, release.yml, validate.yml
├── assets/                   # logos, hero images
├── docs/                     # specification docs
├── examples/
│   ├── janvisuals/           # v2.14 flagship example (only one CI validates against v2.14)
│   ├── minimal.yaml
│   ├── multi-agent.yaml
│   ├── research-swarm.yaml
│   ├── voice-agent.yaml
│   └── x-reply-bot.yaml
├── schemas/
│   ├── v2.14/schema.json                   # current
│   ├── grok-install-v2.13.schema.json      # retained for back-compat
│   ├── featured-agents-v1.schema.json
│   └── trending-v1.schema.json
├── spec/
│   ├── v2.12/                # retained
│   ├── v2.13/
│   └── v2.14/spec.md
├── CONTRIBUTING.md, LICENSE, README.md, SECURITY.md
├── grok-install.yaml, featured-agents.json, trending.json
└── index.html, my-agents.html
```

**Entry points**
- **Spec**: `spec/v2.14/spec.md` (human-readable), `schemas/v2.14/schema.json` (machine-readable).
- **Browser**: `index.html`, `my-agents.html` (GitHub Pages published via `.github/workflows/pages.yml` `(inferred)`).
- **Runtime registry**: `featured-agents.json`, `trending.json` — consumed by `grok-agents-marketplace` per Phase 1 inventory `(inferred — registry schema present but cross-repo consumption not verified in this audit)`.

**Language mix**: Not displayed in linguist bar; README references YAML-heavy content with Python/HTML adjuncts `(WebFetch-limited)`.

## 3. Dependency graph

- **Inbound** (per Phase 1 inventory; schema link confirmed in CI):
  - `grok-install-cli` — pins v2.14.0 of the spec (per Phase 1 probe; not re-verified in this audit).
  - `grok-install-action` — pins CLI v2.14.0 (per Phase 1 probe; not re-verified).
  - `grok-docs` — republishes schemas via CI sync `(needs clone to verify)`.
  - `grok-agents-marketplace` — consumes `featured-agents.json` registry `(inferred)`.
  - `awesome-grok-agents` — template validation references the schema `(inferred)`.
  - `vscode-grok-yaml` — IntelliSense uses the JSON Schema `(inferred)`.

- **Outbound**: None (spec repo — it's the root).

- **External runtime deps** (from `.github/workflows/validate.yml`):
  - Node 20, `ajv-cli`, `ajv-formats`, `js-yaml` (schema validation tooling).
  - `ibiqlik/action-yamllint@v3` (YAML lint).
  - `markdownlint-cli2-action@v16` (docs lint).

## 4. Documentation quality

- **README.md**: present. Sections observed: Overview, Key Features, Core Components, Quick Start, v2.14 updates, Community Resources. Missing from what was visible: explicit *Contributing* link, badge row (build/version/license). Style: salesy ("~250 Python lines vs ~30 YAML") rather than reference-grade.
- **SECURITY.md**: present; disclosure channels are repo issues or tagging @JanSol0s on X. Single-point-of-failure signal.
- **CONTRIBUTING.md**: present; content not fetched.
- **`spec/v2.14/spec.md`**: present; single file per version; content not fetched.
- **External docs alignment**: Fresh docs repo exists (`grok-docs`) but drift between `spec/v2.14/spec.md` and grok-docs' published version is unverified from this audit.

**Score: 3/5** — good structure for an early-stage spec repo; README leans promotional; no badges; spec is single-file per version rather than modular.

## 5. Tests & CI

Workflows (5 files in `.github/workflows/`):

| Workflow | Purpose (verified from `validate.yml`) |
|----------|---------------------------------------|
| `validate.yml` | YAML lint + schema validation v2.13 (back-compat, all examples) + v2.14 (flagship only) + markdown lint |
| `ci.yml` | `(not fetched)` |
| `pages.yml` | GitHub Pages publish for `index.html`/`my-agents.html` `(inferred from name)` |
| `release.yml` | Release automation `(not fetched)` |
| `anti-slop.yml` | Suggests content-quality gating `(inferred from name — not fetched)` |

**Release cadence**: v2.14 released recently (latest per README); older versions v2.12/v2.13 retained. Tagging strategy unverified.
**Tests per se**: there is no code test suite (spec-only repo); "tests" are schema-validation CI jobs.

## 6. Security & safety signals

- **Dependency pinning**: `ibiqlik/action-yamllint@v3` (major tag, not SHA); `markdownlint-cli2-action@v16` (major tag). Node deps installed via npm without lockfile visible at repo root `(WebFetch-limited — not yet checked for package-lock.json)`. Action-SHA pinning would strengthen supply-chain posture.
- **Secret handling**: spec repo has no runtime secrets. CI uses default `GITHUB_TOKEN` only `(inferred)`.
- **Safety-profile integration**: the spec *defines* the safety surface (Enhanced Safety & Verification 2.0 per `SECURITY.md`): pre-install file scan for hard-coded secrets, minimum-keys-only, "Verified by Grok" badge, halt-on-anomaly. This is the canonical definition; CLI / templates / standards repos are expected to consume it.
- **Disclosure policy**: repo issues or `@JanSol0s` on X. "Grok will automatically pause installs for that repo until resolved" is the strongest claim but its enforcement point is outside this repo.

## 7. Code quality signals

- **Linter**: YAML lint via `.yamllint.yml` config; markdown lint via `markdownlint-cli2-action@v16`.
- **Typing / schema discipline**: strong — v2.14 uses JSON Schema draft-2020, v2.13 uses draft-7. The *per-version* schema directory is a healthy sign.
- **Error handling**: N/A (no runtime code in this repo).
- **Module cohesion**: clean — specs under `spec/`, schemas under `schemas/`, examples under `examples/`, web under root. No cross-contamination visible.

## 8. Integration contract

- **Public surface**:
  - Schemas: `schemas/v2.14/schema.json` (draft-2020) and `schemas/grok-install-v2.13.schema.json` (draft-7); registry schemas `featured-agents-v1.schema.json`, `trending-v1.schema.json`.
  - Spec: `spec/v2.14/spec.md` (human-readable).
  - Registry JSONs: `featured-agents.json`, `trending.json` (consumed by marketplace/gallery).
  - v2.14 adds optional `visuals:` block (backwards-compatible additive change).
- **Current version**: v2.14 (with v2.12 & v2.13 retained).
- **Breaking-change posture**: additive-only in v2.14; three versions kept simultaneously suggests an informal deprecation window but no explicit schedule. **Back-compat validation is only partial** (v2.14 flagship example is the only one validated against draft-2020).

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Migrate all five top-level examples to v2.14 schema and validate them in CI | S | 5 | Consumers pinning v2.14 inherit weaker validation coverage; `schema-v2-14` job covers 1 of 6 examples. Closing the gap is hours of work. | None |
| 2 | Pin third-party actions by SHA (`ibiqlik/action-yamllint`, `markdownlint-cli2-action`) | S | 4 | Supply-chain hardening matches the ecosystem's own "safety 2.0" posture. Strongest signal to downstream adopters. | None |
| 3 | Publish a formal deprecation schedule for v2.12 → v2.13 → v2.14 | S | 4 | Keeping three spec versions co-located without a sunset policy forces every downstream repo to hedge. A 6-month deprecation window would let the ecosystem converge. | Maintainer decision |
| 4 | Replace repo-issue-or-X-handle disclosure channel with a dedicated `security@` address + PGP key | M | 3 | Solo-maintainer on X DMs is not a production disclosure channel. Risk concentrates on a single human availability. | Governance |
| 5 | Add a `cross-repo-sync` CI job that pings `grok-install-cli`, `grok-docs`, `grok-agents-marketplace` on spec version bumps | M | 4 | Currently the ecosystem upgrades via manual coordination; a dispatch-event on release solves drift at the source. | Release process |

## 10. Open questions / unknowns

- Does `spec/v2.14/spec.md` fully document the `visuals:` block or is it still draft? `(needs maintainer input)`
- How is the "Verified by Grok" badge rendered — is it a service response or a static asset? `(needs clone)`
- What does `anti-slop.yml` actually do (name suggests content quality gating)? `(WebFetch-limited — not fetched)`
- Is there a `package-lock.json` or `package.json` at repo root governing the ajv versions? `(WebFetch-limited)`
- Does `ci.yml` perform any checks beyond what `validate.yml` covers? `(WebFetch-limited — not fetched)`
- Is `JanSol0s` the only committer, or is there a co-maintainer? `(needs clone — blame history)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-install | Repo landing: description, star/fork count (1/0), license (Apache 2.0), top-level tree, commit count (259), maintainer (@JanSol0s). |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-install/main/README.md | README content: overview, v2.14 feature set, quick-start, ecosystem references. |
| 3 | https://github.com/AgentMindCloud/grok-install/tree/main/spec | Spec directory contains v2.12, v2.13, v2.14 subfolders. |
| 4 | https://github.com/AgentMindCloud/grok-install/tree/main/spec/v2.14 | Confirmed single file: `spec.md`. |
| 5 | https://github.com/AgentMindCloud/grok-install/tree/main/schemas | Schemas: `featured-agents-v1.schema.json`, `grok-install-v2.13.schema.json`, `trending-v1.schema.json`, plus `v2.14/` subfolder. |
| 6 | https://github.com/AgentMindCloud/grok-install/tree/main/schemas/v2.14 | Contains `schema.json` (v2.14). |
| 7 | https://github.com/AgentMindCloud/grok-install/tree/main/.github/workflows | Five workflows: `anti-slop.yml`, `ci.yml`, `pages.yml`, `release.yml`, `validate.yml`. |
| 8 | https://raw.githubusercontent.com/AgentMindCloud/grok-install/main/.github/workflows/validate.yml | `validate.yml` jobs: `yaml-lint`, `schema-v2-13` (all examples, draft7), `schema-v2-14` (janvisuals only, draft2020), `markdown-lint`. Third-party actions pinned by major tag. |
| 9 | https://github.com/AgentMindCloud/grok-install/tree/main/examples | Examples: `minimal.yaml`, `multi-agent.yaml`, `research-swarm.yaml`, `voice-agent.yaml`, `x-reply-bot.yaml`, plus `janvisuals/` subfolder. |
| 10 | https://raw.githubusercontent.com/AgentMindCloud/grok-install/main/SECURITY.md | Disclosure channels (repo issues / X DM), "Grok will pause installs automatically", "Verified by Grok" badge, Enhanced Safety 2.0 scan surface. |
