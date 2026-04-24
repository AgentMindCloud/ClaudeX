# Audit: grok-docs

- **Upstream**: https://github.com/AgentMindCloud/grok-docs
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (5 commits total)

## 1. Summary

`grok-docs` is the documentation site for the grok-install ecosystem — an MkDocs Material static site published to `agentmindcloud.github.io/grok-docs/`. It covers getting-started, 5-file-type spec reference, multi-agent guides, CLI reference, a live playground, and an "xAI adoption" section. Build deps are **exactly pinned** (`requirements.txt`: mkdocs, mkdocs-material, etc., all `==`). A `sync-schemas.yml` workflow pulls schemas daily (cron `0 3 * * *`) from `grok-yaml-standards` into `docs/assets/schemas/`. Maturity is very early (5 commits total, 1★, 0 issues, 0 PRs). Headline risk: **double drift** — the docs site currently advertises spec v2.12 while `grok-install` is at v2.14, and it references **5 YAML schemas** in the nav (grok-install, grok-agent, grok-workflow, grok-security, grok-prompts) while `grok-yaml-standards` ships **12** (the 8 core + 4 extensions). Over 50% of the standards are undocumented on the user-facing site.

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/   # deploy.yml, link-check.yml, sync-schemas.yml
├── docs/
│   ├── assets/schemas/  # synced by sync-schemas.yml
│   └── (content pages)
├── overrides/           # MkDocs Material template overrides
├── mkdocs.yml
├── requirements.txt
├── LICENSE, README.md, .gitignore
```

**Entry points**
- `mkdocs serve` (local) → http://localhost:8000.
- Published site at `https://agentmindcloud.github.io/grok-docs/`.
- Schema sync job idempotently refreshes `docs/assets/schemas/latest/` + `docs/assets/schemas/<VERSION>/`.

**Language mix**: HTML 100% (linguist — the rendered site; content is Markdown). Ruby/Python tooling not in linguist view.

## 3. Dependency graph

- **Inbound**: end users (readers), ecosystem docs links from `grok-install`, `grok-yaml-standards`, and `grok-install-cli` READMEs `(inferred)`.
- **Outbound**:
  - `grok-yaml-standards` main branch (via `sync-schemas.yml`).
  - Python/pip deps from `requirements.txt` (exact pins; see below).
- **External deps (exact pinned)**:
  - `mkdocs==1.6.1`
  - `mkdocs-material==9.5.44`
  - `mkdocs-material-extensions==1.3.1`
  - `mkdocs-minify-plugin==0.8.0`
  - `mkdocs-git-revision-date-localized-plugin==1.2.9`
  - `mkdocs-mermaid2-plugin==1.2.1`
  - `pymdown-extensions==10.12`
  - `pygments==2.18.0`

## 4. Documentation quality

Subjective but critical since this *is* the documentation repo.

- **Nav coverage (from `mkdocs.yml`)**:
  - Getting started (installation / first agent / production deployment).
  - Spec → **only 5 file types** (`grok-install`, `grok-agent`, `grok-workflow`, `grok-security`, `grok-prompts`).
  - Guides (multi-agent swarms, tool schemas, safety profiles, deployment, X integration).
  - CLI reference.
  - Gallery (single-agent / multi-step / swarm).
  - Playground (live client-side validator).
  - Ecosystem (xAI SDK, LiteLLM, Semantic Kernel).
  - For xAI section, Contributing.
- **Spec version advertised**: v2.12 `(per repo description + Phase 1 probe)`. Current `grok-install` = v2.14.
- **Missing standards from nav**: grok-config, grok-update, grok-test, grok-docs, grok-tools, grok-deploy, grok-analytics, grok-ui (7 of 12 undocumented).
- **Build-reproducibility**: excellent — all deps pinned `==`.
- **Theme polish**: Material theme with dark/light toggle, instant navigation, Mermaid support, minification, Mike versioning plugin enabled.

**Score: 2/5** — theme and build hygiene are strong, but *as a documentation site for the ecosystem* it lags the spec version by ≥2 minor versions and covers <42% of the standards. For an early-stage ecosystem this is fixable, but it is the ecosystem's single most visible drift.

## 5. Tests & CI

Three workflows:

| Workflow | Purpose |
|----------|---------|
| `deploy.yml` | Presumably `mkdocs gh-deploy` or `peaceiris/actions-gh-pages` `(not fetched)` |
| `link-check.yml` | Checks doc-site link integrity `(not fetched)` |
| `sync-schemas.yml` | Daily cron (`0 3 * * *`) + manual dispatch + on-change-to-self. Pulls `agentmindcloud/grok-yaml-standards@main`, copies schemas to `docs/assets/schemas/{latest,<VERSION>}/`; idempotent diff-check; commit message `chore(schemas): sync from grok-yaml-standards@[VERSION]`. |

- **Link-check presence**: good hygiene signal.
- **Schema-sync pattern**: sound — schemas are the live artefact; docs-site copy is a snapshot. Mike versioning plugin suggests the site can publish per-version docs.
- **Action pinning**: `actions/checkout@v4` — major-tag (same ecosystem pattern).

## 6. Security & safety signals

- **Dependency pinning**: exact `==` pins in `requirements.txt` — best-in-class in this ecosystem.
- **Secret handling**: no runtime secrets in a static-site repo. Schema-sync uses default `GITHUB_TOKEN` `(inferred)`.
- **Safety-profile integration**: `Guides → safety profiles` is a nav entry, but not yet cross-verified with `grok-install-cli/src/grok_install/safety/rules.py` or the `grok-security` standard. The "safety profiles" page is likely the ecosystem's user-facing explanation of strict/standard/permissive, but its content wasn't read `(needs content fetch)`.
- **Disclosure**: `SECURITY.md` not present at repo root `(verified from landing page listing)`. Disclosure presumably defers to `grok-install`'s policy.

## 7. Code quality signals

- **Linter**: no markdown lint config visible at repo root `(WebFetch-limited)`; `deploy.yml` might include one.
- **Content quality signals**: Mike versioning plugin in `mkdocs.yml` implies docs are versioned — but the nav currently shows v2.12 content only. Version switcher likely hidden until v2.14 docs ship.
- **Theme overrides**: `overrides/` directory signals intentional UI customisation.
- **Module cohesion**: standard MkDocs layout; no drift.

## 8. Integration contract

- **Published artefact**: the MkDocs site at `agentmindcloud.github.io/grok-docs/`.
- **Schema republishing contract**: `sync-schemas.yml` guarantees that `docs/assets/schemas/latest/` mirrors `grok-yaml-standards@main` (within 24h of changes landing on that branch). Downstream consumers (vscode-grok-yaml, third-party validators) can rely on this URL for canonical schemas.
- **Version sources of truth**: spec vocabulary → `grok-install`; file-type catalogue → `grok-yaml-standards`; runtime semantics → `grok-install-cli`. This repo aggregates.
- **Breaking-change posture**: Mike versioning plugin enables multi-version archives; no policy doc visible.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Publish v2.14 spec docs + document the 7 missing standards (grok-config/update/test/docs/tools/deploy/analytics/ui) | M | 5 | This is the single most visible drift in the ecosystem. Every adopter lands here first and sees outdated v2.12 content covering <42% of standards. | Content writing |
| 2 | Gate every release of `grok-install`/`grok-yaml-standards` on a `repository_dispatch` to this repo's sync workflow | S | 4 | Currently sync-schemas.yml polls daily at 03:00 UTC; dispatch-on-release closes the drift window from 24h to seconds and makes drift visible in commit history. | Upstream repo consent |
| 3 | Add a top-of-site "version: vX.Y" banner sourced from `docs/assets/schemas/latest/` VERSION file | S | 4 | Readers today can't easily tell they're reading stale docs. Auto-surfaced version is a 5-line change in a Jinja override. | None |
| 4 | Add schema-validated Mermaid diagrams of the dependency graph (from this audit) to the "Ecosystem" nav entry | M | 3 | Self-documents ecosystem shape; reduces per-repo duplication in READMEs. | Graph source of truth |
| 5 | Pin `actions/checkout` by SHA in all three workflows | S | 3 | Match ecosystem-consistent supply-chain posture (same cross-repo rec). | None |

## 10. Open questions / unknowns

- What does `deploy.yml` actually do (Pages / manual hosting / both)? `(WebFetch-limited — not fetched)`
- What does `link-check.yml` use (lychee / html-proofer / markdown-link-check)? Does it fail CI on broken links? `(not fetched)`
- Does the Playground page validate against the schemas in `docs/assets/schemas/latest/` or fetch from `grok-install` at page-load? `(needs content fetch)`
- What actual VERSION is currently live in `docs/assets/schemas/latest/` — is it still v1.1.0 or has the sync caught v1.2.0? `(needs content fetch)`
- Is Mike configured to serve `/v2.12/` archives separately, or just one "latest" alias? `(WebFetch-limited)`
- Are the "safety profiles" and "tool schemas" pages cross-linked to the CLI's rules.py and to `grok-yaml-standards/grok-security` spec? `(needs content fetch)`
- Single-maintainer signal: only 5 commits total; who reviews docs changes? `(needs maintainer input)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-docs | Repo landing: description, 1★, 0/0/0/0, Apache 2.0, 5 commits total, linguist HTML 100%, top-level tree. |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-docs/main/mkdocs.yml | Site URL, theme config, nav (5 spec entries, Guides, CLI ref, Gallery, Playground, Ecosystem), plugins (search/minify/git-revision-date/Mike), Material theme, edit_uri `edit/main/docs/`. |
| 3 | https://github.com/AgentMindCloud/grok-docs/tree/main/.github/workflows | 3 workflows: `deploy.yml`, `link-check.yml`, `sync-schemas.yml`. |
| 4 | https://raw.githubusercontent.com/AgentMindCloud/grok-docs/main/.github/workflows/sync-schemas.yml | Daily cron 03:00 UTC + manual dispatch + on-self-change; sources `agentmindcloud/grok-yaml-standards@main`; copies to `docs/assets/schemas/{latest,<VERSION>}/`; commit `chore(schemas): sync from grok-yaml-standards@[VERSION]`; checkout@v4 major-tag. |
| 5 | https://raw.githubusercontent.com/AgentMindCloud/grok-docs/main/requirements.txt | 8 exact-pinned deps: mkdocs 1.6.1, mkdocs-material 9.5.44, mkdocs-material-extensions 1.3.1, mkdocs-minify-plugin 0.8.0, mkdocs-git-revision-date-localized-plugin 1.2.9, mkdocs-mermaid2-plugin 1.2.1, pymdown-extensions 10.12, pygments 2.18.0. |
