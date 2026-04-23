# Ship grok-docs v2.14 content + reference pages for the 7 undocumented standards

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #10 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/grok-docs
- **Risks closed**: VER-4 (S2) outright, DOC-2 (S2) outright — both from `audits/98-risk-register.md`.
- **Source audits**: `[→ 05 §9 row 1]`. Supporting: `audits/05-grok-docs.md §1, §4, §11 row 2` (current v2.12 advertisement + 5-of-12 standards coverage + full nav); `audits/00-ecosystem-overview.md §4` (schema-draft matrix), `§5` (standards-count coherence — 12 is authoritative), `§7.1` (version-drift table).
- **Effort (§2)**: L — content-writing cost dominates. Spec-page rewrite from v2.12 → v2.14 is M in isolation; adding 7 new standard-reference pages (`grok-config` / `grok-update` / `grok-test` / `grok-docs` / `grok-tools` / `grok-deploy` / `grok-analytics` / `grok-ui` — minus `grok-docs` which is the repo itself, so 7 pages) is what pushes this to L. No coding required; all Markdown.
- **Blocked by (§2)**: none — content is ready to lift from `grok-yaml-standards/grok-*/` spec folders + `standards-overview.md` + `version-reconciliation.md`, plus the `grok-install` v2.14 spec + CHANGELOG.
- **Unblocks (§2)**: #4 — `repository_dispatch` from `grok-install` → `grok-docs`, `grok-install-action`, `grok-agents-marketplace`. Without v2.14 docs existing, a dispatch-on-release trigger fires into an empty target. Once this rec ships, #4 becomes drafteable.
- **Suggested labels**: `docs`, `v2.14`, `standards-reference`, `content`, `phase-1b`

---

## Context

`grok-docs` is the ecosystem's canonical documentation site at
`agentmindcloud.github.io/grok-docs/`. Every adopter lands here
first. Today it ships **two drift gaps** that compound:

1. **Spec-version lag.** The site advertises `grok-install` spec
   **v2.12**. The spec is currently at **v2.14** — two minor
   versions ahead. VER-4 in the risk register captures this
   directly.

2. **Catalogue-coverage gap.** The site's nav references **5**
   YAML file types (`grok-install`, `grok-agent`, `grok-workflow`,
   `grok-security`, `grok-prompts`). `grok-yaml-standards` v1.2.0
   ships **12** (8 core + 4 extensions). Seven standards are
   undocumented: `grok-config`, `grok-update`, `grok-test`,
   `grok-tools`, `grok-deploy`, `grok-analytics`, `grok-ui`.
   DOC-2 in the risk register captures this.

   (`grok-docs` the standard is self-documenting via the nav
   itself — the site IS its own `grok-docs` standard reference;
   no separate page is required.)

The two drifts reinforce each other. A new adopter reading the
v2.12 spec page sees 5 file types and assumes the ecosystem
has 5. Another adopter reading `grok-yaml-standards`'
`standards-overview.md` sees 12. `grok-install-action`'s README
advertises 14 (pre-reconciliation — addressed in §2 #14a). A
third adopter reading `vscode-grok-yaml`'s landing description
also sees 14 (addressed in §2 #14b). The ecosystem's official
documentation site is the place that should arbitrate between
these competing numbers, and today it fails that test.

The fix is entirely content-authoring — no code, no CI changes
required (the schema-sync workflow `sync-schemas.yml` already
republishes the 12 schemas daily; it is the nav + content pages
that haven't caught up). L-effort because the content volume is
real: one spec page rewrite + seven new reference pages, each
with conceptual overview + schema reference + usage example +
cross-links. A single motivated author can ship this in a week
of focused time; a reviewer + author pair in two weeks.

Secondary benefit: once v2.14 docs exist, §2 #4 (`repository_
dispatch` wiring from `grok-install` → `grok-docs`) becomes
drafteable. Without this rec, a dispatch-on-release fires into
an empty target; nothing useful rebuilds. This rec is the
only Phase-1B draft that unblocks §2 #4 — hence its inclusion
at this point in the drafting sequence.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**Current nav — 5 spec entries** — `audits/05-grok-docs.md §4`
(sourced from `mkdocs.yml`):
- `grok-install` (core spec)
- `grok-agent`
- `grok-workflow`
- `grok-security`
- `grok-prompts`

**12 standards ratified in `grok-yaml-standards` v1.2.0** —
`audits/02-grok-yaml-standards.md §2, §8, §11 row 2`
(sourced from `standards-overview.md` + `version-reconciliation.md`):

| # | Standard | Status | Documented on docs site today? |
|:-:|----------|--------|-------------------------------|
| 1 | `grok-install` (core spec) | 8-core | Yes (needs v2.12 → v2.14 refresh) |
| 2 | `grok-agent` | 8-core | Yes |
| 3 | `grok-workflow` | 8-core | Yes |
| 4 | `grok-security` | 8-core | Yes |
| 5 | `grok-prompts` | 8-core | Yes |
| 6 | `grok-config` | 8-core | **Missing** |
| 7 | `grok-update` | 8-core | **Missing** |
| 8 | `grok-test` | 8-core | **Missing** |
| 9 | `grok-docs` | 8-core | *Implicit* — the site is its own reference |
| 10 | `grok-tools` | 4-extension | **Missing** |
| 11 | `grok-deploy` | 4-extension | **Missing** |
| 12 | `grok-analytics` | 4-extension | **Missing** |
| 13 | `grok-ui` | 4-extension | **Missing** |

(Wait — the math: 12 standards, 8 core + 4 extensions. `grok-docs`
*is* the 9th core standard in audit 02; counting above gives
13 because `grok-install` is the *outer spec*, not one of the 12.
Correcting: the 12 standards are rows 2–13 above; `grok-install`
at row 1 is the grok-install-spec, which is documented separately
from the 12-standard catalogue. Net: 5 of 12 standards documented
today, 7 missing. The `grok-docs` standard is self-documenting
via the site itself; no standalone reference page needed — so
this rec ships **7 new pages**, not 8.)

**Schema synchronisation already in place** —
`audits/05-grok-docs.md §5, §8, §11 row 4`:
- `.github/workflows/sync-schemas.yml` — daily cron
  (`0 3 * * *`) + manual dispatch + on-self-change.
  Pulls `agentmindcloud/grok-yaml-standards@main`, copies
  schemas to `docs/assets/schemas/{latest,<VERSION>}/`.
  Idempotent; commit message
  `chore(schemas): sync from grok-yaml-standards@[VERSION]`.
- Implication: the 12 schemas are *already* mirrored locally.
  This rec consumes that mirror for reference-page content —
  each new standard-reference page embeds its schema as a
  code block with `--8<-- "docs/assets/schemas/latest/grok-<name>.json"`
  (standard MkDocs snippet syntax).

**Build hygiene already strong** —
`audits/05-grok-docs.md §4, §6, §11 row 5`:
- `requirements.txt` exact-pinned across 8 deps.
- Mike versioning plugin configured (enables per-version archives).
- MkDocs Material with theme overrides in `overrides/`.

**Risk register** — `audits/98-risk-register.md`:
- **VER-4** (S2, L-high, `open`): "`grok-docs` advertises spec
  **v2.12**; current spec is **v2.14**. Two-minor-version lag
  in the canonical documentation site."
- **DOC-2** (S2, L-high, `open`): "`grok-docs` documents **5
  of 12** ratified standards; the remaining 7 have no
  published reference page. The 'official documentation
  site' is structurally incomplete."

**Cross-cut docs-drift context** —
`audits/00-ecosystem-overview.md §7.1` (verbatim):

| Surface | Says | Should say |
|---------|------|------------|
| `grok-docs` (published site) | spec **v2.12** | v2.14 |
| `grok-docs` nav — Spec reference | **5** file types | 1 core spec + 12 standards |

**Related §2 cross-refs**:
- §2 #8 (draft-2020-12 migration) — the schemas the new
  reference pages embed switch from draft-07 to draft-2020-12
  when #8 lands. If #8 lands first, the new pages embed the
  migrated schemas from day one. If this rec lands first, the
  pages embed draft-07 schemas and re-render on the next
  daily sync after #8 merges — no coordination overhead.
- §2 #4 (`repository_dispatch` wiring) — blocked by this rec.
  Drafteable in the next drafting pass once this merges
  upstream.
- §2 #3 (SHA-pin actions) — applies to this repo's 3 workflows;
  separate rec, not coordinated here.

## Acceptance criteria

Three parts. Part A refreshes the existing `grok-install` spec
page to v2.14. Part B adds the 7 missing standard-reference
pages. Part C is the publication-layer wiring (nav, version
banner, Mike archive of v2.12). All three land in the same PR
(or three PRs in any order); the issue closes when the published
site at `agentmindcloud.github.io/grok-docs/` renders v2.14 as
current and all 12 standards have reference pages accessible
from the nav.

### Part A — Refresh the `grok-install` spec page to v2.14

The spec-page rewrite consumes `grok-install/spec/v2.14/spec.md`
and `grok-install/CHANGELOG.md` v2.13 → v2.14 section as source
material. No new vocabulary introduced in this rec — just a
content refresh of what already exists upstream.

- [ ] **Rewrite `docs/spec/grok-install.md`** (or wherever the
      current v2.12 content lives; confirm path from
      `mkdocs.yml` nav entry for "Spec → grok-install"):
      - Top of page: `!!! info` admonition citing the current
        version sourced from
        `docs/assets/schemas/latest/VERSION` (the sync job
        already maintains this file — see Part C's version
        banner for the Jinja override pattern).
      - **Overview** section: what `grok-install.yaml` is,
        how it relates to the 12 file-type standards it
        references, link to `grok-install/spec/v2.14/spec.md`
        as the authoritative canonical copy.
      - **v2.14 additions** section: the optional `visuals:`
        block (per `audits/01 §8`); cite `grok-install
        CHANGELOG.md` v2.14 entry for the exhaustive list.
      - **Schema reference** section: embed
        `docs/assets/schemas/latest/v2.14/schema.json` via
        the MkDocs snippet mechanism:
        ```markdown
        ```json
        --8<-- "docs/assets/schemas/latest/v2.14/schema.json"
        ```
        ```
      - **Validator compatibility** section: flag that v2.14
        uses JSON Schema **draft-2020-12** (vs. v2.13's
        draft-07); consumers pick up the new draft via
        `$schema`-keyword awareness. Cross-link to §2 #8's
        landed migration on `grok-yaml-standards` when that
        issue merges.
      - **Migration from v2.13** section: single-screen guide
        — what changed, what to update, what stays identical.
        Source: `grok-install` `CHANGELOG.md` v2.13 → v2.14
        entry.
      - **Back-compat note**: v2.14 is additive over v2.13;
        v2.12 is retained as an archive under Mike versioning
        (see Part C).

- [ ] **Update `mkdocs.yml` site_description** to drop the
      "v2.12" language if present (not confirmed in audit;
      check during PR).

- [ ] **Update `README.md` at repo root** with the current spec
      version in any headline claim.

- [ ] **Sanity check**: `mkdocs build --strict` passes locally.
      The `--strict` flag fails on ambiguous references and
      missing nav entries, so it catches most content-migration
      mistakes before they reach CI.

- [ ] **Link-check**: the existing `link-check.yml` workflow
      runs on the PR; no new config needed.

### Part B — Add reference pages for the 7 undocumented standards

Seven new Markdown files under `docs/spec/` (or wherever
existing per-standard pages live; path confirmed during PR).
Each follows the same structure so the user experience is
uniform.

**Page template** (identical structure for all 7):

```markdown
# <Standard name> (e.g. grok-config)

<!-- front-matter -->
- **Trigger**: `@grok <command>` (e.g. `@grok config`)
- **Status**: 8-core | 4-extension (per standards-overview.md)
- **Security level**: Low | Medium | High | Critical
  (per grok-yaml-standards/standards-overview.md)
- **Schema**: `schemas/grok-<name>.json` (v1.3+ draft-2020-12;
  fetched daily by sync-schemas.yml from grok-yaml-standards)

## Overview

One paragraph: what this standard is for, which agent lifecycle
moment it governs, why it exists as a separate standard rather
than a field in grok-install.yaml.

## When to use

Two or three bullets of concrete examples (lifted from
grok-yaml-standards/grok-<name>/example.yaml where available).

## Schema reference

```json
--8<-- "docs/assets/schemas/latest/grok-<name>.json"
```

## Example

```yaml
--8<-- "docs/assets/schemas/latest/examples/grok-<name>.yaml"
```
(If no canonical example exists in the mirrored schemas path,
reference the example from grok-yaml-standards/grok-<name>/
example.yaml and flag that the doc site may want its own
canonical example long-term.)

## Fields

Table: field name | type | required | description | default.
Generated from the schema reference above; MkDocs Material has
a `json-schema-to-markdown`-style plugin pattern the team may
want to adopt later — for v2.14 docs, hand-authoring the table
is acceptable.

## Related standards

Bullet list of 1–3 adjacent standards and why they're related
(e.g. grok-test references grok-agent; grok-deploy interacts
with grok-security). Links are internal
`[grok-agent](grok-agent.md)` style.

## See also

- Source spec: `grok-yaml-standards/grok-<name>/`
- Schema: `schemas/grok-<name>.json` on grok-yaml-standards
- CHANGELOG entry (if any): link to the version section that
  added / modified this standard
```

**Concrete pages to write:**

- [ ] **`docs/spec/grok-config.md`** — `@grok config`; governs
      agent-level configuration that isn't profile-specific.
      Security level: Medium per
      `grok-yaml-standards/standards-overview.md`.
- [ ] **`docs/spec/grok-update.md`** — `@grok update`; governs
      how an installed agent pulls and applies spec/CLI
      updates. Security level: Medium.
- [ ] **`docs/spec/grok-test.md`** — `@grok test`; governs
      test configuration and expectations. Security level:
      Low.
- [ ] **`docs/spec/grok-tools.md`** — `@grok tools`; governs
      tool declarations (function schemas). Security level:
      Medium. 4-extension standard.
- [ ] **`docs/spec/grok-deploy.md`** — `@grok deploy`; governs
      deployment target configuration. Security level: High
      (touches external infra). 4-extension standard.
- [ ] **`docs/spec/grok-analytics.md`** — `@grok analytics`;
      governs telemetry / metrics emission. Security level:
      Medium. 4-extension standard.
- [ ] **`docs/spec/grok-ui.md`** — `@grok ui`; governs the
      visuals / UI layer introduced in v2.14. Security level:
      Low. 4-extension standard; tightly coupled to v2.14's
      `visuals:` block in `grok-install.yaml`.

**Authorship notes:**

- Each page is ~150–300 words of original prose (overview +
  when-to-use + fields table commentary). The schema +
  example code blocks are embedded via `--8<--` snippets,
  not duplicated.
- Every claim about a standard's *purpose* or *boundary*
  should cite `grok-yaml-standards/grok-<name>/` or the
  catalogue entry in `standards-overview.md`. If a claim
  cannot be sourced, flag during PR review — the docs site
  should not introduce new semantics the spec doesn't
  already establish.
- Security-level values are authoritatively in
  `grok-yaml-standards/standards-overview.md`; mirror
  exactly, do not paraphrase.
- Field tables for each schema: the initial pass can
  hand-author them from the embedded schema block.
  Auto-generation is a follow-up (tracked as
  `audits/99-recommendations.md §3.2` style hygiene — not
  blocking v2.14).

### Part C — Publication layer: nav, version banner, Mike archive

The content in Parts A + B is useless until the site surfaces
it. Three small changes to the publication infrastructure.

- [ ] **Update `mkdocs.yml` nav** to surface the 7 new pages
      + confirm `grok-docs` the standard is represented by
      the site's root (no separate reference page needed):

      ```yaml
      nav:
        - Getting started: ...
        - Spec:
          - Core:
            - grok-install: spec/grok-install.md
            - grok-agent: spec/grok-agent.md
            - grok-workflow: spec/grok-workflow.md
            - grok-security: spec/grok-security.md
            - grok-prompts: spec/grok-prompts.md
            - grok-config: spec/grok-config.md      # NEW
            - grok-update: spec/grok-update.md      # NEW
            - grok-test: spec/grok-test.md          # NEW
          - Extensions:
            - grok-tools: spec/grok-tools.md        # NEW
            - grok-deploy: spec/grok-deploy.md      # NEW
            - grok-analytics: spec/grok-analytics.md  # NEW
            - grok-ui: spec/grok-ui.md              # NEW
        - Guides: ...
        - CLI reference: ...
      ```

      The two-level grouping (Core / Extensions) matches
      `grok-yaml-standards/standards-overview.md`'s
      categorisation — important for keeping the docs site's
      taxonomy consistent with the spec-catalogue repo's.

- [ ] **Add a top-of-site version banner.** Audit 05 §9 row 3
      calls this out as a stand-alone recommendation; bundling
      it here is efficient because the v2.14 refresh is the
      moment the version claim changes.

      - Add `overrides/main.html` (or extend the existing
        override if `overrides/` already has one):
        ```html
        {% extends "base.html" %}
        {% block announce %}
          <a href="{{ 'spec/grok-install/' | url }}">
            Current spec version: <strong>{{ config.extra.spec_version }}</strong>
          </a>
        {% endblock %}
        ```
      - Add to `mkdocs.yml`:
        ```yaml
        extra:
          spec_version: v2.14
        ```
      - Long-term: source `spec_version` from
        `docs/assets/schemas/latest/VERSION` via a small
        pre-build hook (`hooks:` in mkdocs). Not required for
        v2.14 ship — a hardcoded value + manual bump at each
        spec release is acceptable until §2 #4's dispatch
        wiring lands. Flag as follow-up.

- [ ] **Mike archive v2.12 content.** The Mike versioning
      plugin is already configured. Before the main branch
      rewrite to v2.14 content lands:
      ```
      mike deploy v2.12 --push
      mike deploy v2.14 latest --push --update-aliases
      mike set-default latest --push
      ```
      Users browsing the site see v2.14 as default with a
      version switcher that includes v2.12. Archiving the
      older version is important for users maintaining
      v2.12 agents.

- [ ] **Update `mkdocs.yml` site_description** and any `<meta>`
      tags if they mention v2.12 explicitly.

- [ ] **Release + deployment dry-run**:
      `mkdocs build --strict` locally, then check the
      published site after `deploy.yml` succeeds. Confirm:
      - Banner shows "v2.14".
      - All 7 new pages are reachable from the nav.
      - v2.12 is accessible via the Mike version switcher.
      - `link-check.yml` passes with no broken internal
        links.

- [ ] **Add a short release note** to the site's homepage
      (`docs/index.md`): "Docs are now v2.14. v2.12
      remains available via the version switcher at the
      top-right of this page."

