# Bootstrap vscode-grok-yaml v0.1.0 — read-only schema validation against grok-yaml-standards

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #16 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/vscode-grok-yaml
- **Risks closed**: partial GOV-3 (S3) — from `audits/98-risk-register.md`. Full GOV-3 closure also requires the sibling §2 #15 landing (description honesty) + an analogous bootstrap on `grok-agent-orchestra` (§2 #17).
- **Source audits**: `[→ 07 §9 row 2]`. Supporting: `audits/07-vscode-grok-yaml.md §1, §4, §8, §10`. Cross-cut: `audits/00-ecosystem-overview.md §7.2` (governance-file gap), `§4` (schema-draft matrix — relevant once the extension fetches schemas).
- **Effort (§2)**: M — "read-only schema validation against `grok-yaml-standards`" is the Minimum-Viable-Extension bar, and it's still non-trivial (VS Code extension scaffold + schema fetch + `yaml-language-server` integration + CI).
- **Blocked by (§2)**: #15 — `vscode-grok-yaml`'s landing description needs to be honest about the pre-alpha state before bootstrap begins, so contributors aren't confused mid-flight.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/15a-vscode-grok-yaml-description.md`](15a-vscode-grok-yaml-description.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft if the prerequisite issue (§2 #15a) is substantially rewritten during upstream review. Both of #15a's options converge on "the description is honest about pre-alpha state" — either option leaves this bootstrap draft's assumptions intact. Only a rewrite that keeps #15a's description *promissory* (e.g. "supports all 14 standards today") would invalidate this draft's framing in §Context; surface that divergence here rather than silently editing.

- **Suggested labels**: `bootstrap`, `v0.1.0`, `vscode`, `schema-validation`, `phase-1b`

---

## Context

`vscode-grok-yaml` is advertised as "the VS Code extension for all
14 YAML standards" but the repo today contains LICENSE + README +
a `media/` directory — no source, no `package.json`, no CI. It is
the largest gap between marketing and substance in the Grok
ecosystem: a shell repo shaped like a shipped product.

§2 #15 (the prerequisite to this issue) downgrades the README and
GitHub description to honestly describe the current state. Once
that lands, contributors can onboard without surprise at the
empty repo. This issue is the next step: ship a v0.1.0 that
delivers the *minimum* visible value — **read-only schema
validation in the editor**, with no authoring features, no
IntelliSense beyond the schema-driven one that
`yaml-language-server` already provides for free, no linting
beyond what a schema can express.

The minimum-viable extension has three upsides:

1. **Grok YAML authors get immediate value.** Saving a malformed
   `.grok/grok-install.yaml` turns red in the editor without
   leaving VS Code. That is already more than every other
   ecosystem consumer currently offers.
2. **It sets a floor.** Later features (deeper IntelliSense,
   snippets, Quick Fix suggestions, cross-file validation) layer
   on top of a shipped extension. A shipped v0.1.0 is infinitely
   more maintainable than a "coming soon" shell.
3. **It pins a schema-consumption pattern the ecosystem can
   reuse.** §2 #8 (draft-2020-12 migration in
   `grok-yaml-standards`) has landed or is landing; this
   extension's schema-fetch contract becomes a reference
   implementation for other consumers.

The extension is built on top of the existing `redhat.vscode-yaml`
extension's `yaml-language-server` — the standard way VS Code
does YAML schema validation. This repo's contribution is a
*schema-association manifest* plus packaging, not a new language
server.

## Evidence

From `main` snapshot on 2026-04-23 (WebFetch; paths stable).

**Current repo state** — `audits/07-vscode-grok-yaml.md §1, §2, §11`:
- Repo contents: `LICENSE`, `README.md`, `media/` (appears
  empty/unpopulated — no files enumerated on the tree view).
- No `package.json`, no `src/`, no CI workflows, no tests.
- 7 commits total; 1 open PR; 0 stars, 0 forks.
- README / landing description says the extension supports "all
  14 YAML standards" — the phrasing §2 #15a fixes (to
  "12 standards" per `version-reconciliation.md`) and §2 #14b
  fixes at the description layer.

**What schema-validation consumers exist elsewhere**:
- `grok-docs/docs/assets/schemas/latest/` — daily mirror of
  `grok-yaml-standards/schemas/` *(audit 05 §5 `sync-schemas.yml`)*.
  Audit 07 §9 row 3 already recommends this repo consume the
  mirrored schemas rather than creating a fourth schema-distribution
  location.
- `grok-yaml-standards/schemas/grok-<name>.json` — 12 draft-07
  schemas today; migrating to draft-2020-12 under §2 #8.
  `ajv-cli@5.0.0 + ajv-formats@3` already honour `$schema`
  keyword. *(audit 02 §5, §11 row 5.)*
- `grok-install/schemas/v2.14/schema.json` — the outer spec's
  schema. Draft-2020-12. *(audit 01 §7.)*

**Standard VS Code YAML validation path** (widely used; no
original research required):
- The `redhat.vscode-yaml` extension (12M+ installs on the
  marketplace) bundles `yaml-language-server`.
- Schemas attach via either the extension's `yaml.schemas`
  setting OR a consumer extension contributing to the
  `redhat.vscode-yaml` schema-association API via the
  `yamlValidation` `contributes` point in its `package.json`.
- Our extension uses the *contributes* path — `package.json`
  declares which file patterns map to which schema URLs. That
  is the complete integration; the heavy lifting (parsing,
  AST, diagnostics) is done by the Red Hat language server.

**Governance surface** —
`audits/00-ecosystem-overview.md §7.2`: `SECURITY.md` /
`CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` all missing on this
repo today. Adding them in the bootstrap PR (see Part A below)
closes part of GOV-4 at the same time.

**Risk register** — `audits/98-risk-register.md`:
- **GOV-3** (S3, L-high, `open`): "`vscode-grok-yaml` and
  `grok-agent-orchestra` are LICENSE+README only — no source,
  no CI, no issues template. The marketing-polished surface
  implies a working product that does not exist."

**Relationship to prerequisite (§2 #15a)** —
[`phase-1b/drafts/15a-vscode-grok-yaml-description.md`](15a-vscode-grok-yaml-description.md):
  Both of #15a's acceptance options produce an honest README and
  repo description ("pre-alpha / empty shell" OR "marker repo
  placeholder awaiting bootstrap PR"). Either outcome makes it
  safe for this issue to land a real `package.json` + source
  tree without the README still promising a shipped product.

## Acceptance criteria

Two parts. Part A is the repo contents that constitute v0.1.0.
Part B is the schema-fetch strategy plus CI. The issue closes
when the extension is published to the VS Code Marketplace under
publisher `agentmindcloud` at version `0.1.0`, and CI is green
on `main`.

### Part A — Minimum-viable extension contents

Land a `feat/v0.1.0-bootstrap` PR containing:

- [ ] **`package.json`** at repo root with:
      - `"name": "vscode-grok-yaml"`, `"publisher": "agentmindcloud"`,
        `"version": "0.1.0"`, `"engines": {"vscode": "^1.90.0"}`.
      - `"extensionDependencies": ["redhat.vscode-yaml"]` —
        hard dependency; we contribute to their schema
        association API.
      - `"contributes": { "yamlValidation": [ ... ] }` — an
        array of `{ "fileMatch": "...", "url": "..." }` entries,
        one per Grok YAML file pattern (see Part B for the URL
        choice).
      - `"categories": ["Other", "Linters"]`,
        `"activationEvents": []` (implicit via file match).
      - Scripts: `compile`, `watch`, `vscode:prepublish`,
        `lint`, `test`.
      - DevDeps: `@types/vscode`, `@vscode/test-electron`,
        `typescript`, `eslint`, `vsce`. Versions exact-pinned
        (match the ecosystem's `grok-yaml-standards` pinning
        discipline, not the `grok-agents-marketplace` caret
        style).

- [ ] **`src/extension.ts`** — minimum activate / deactivate.
      Activate can be a no-op (since schema association is
      declarative in `package.json`); include the file so the
      extension is identifiable as a TS-sourced project rather
      than pure JSON.

- [ ] **`tsconfig.json`** — strict mode, target ES2022.

- [ ] **`README.md`** — rewrite per §2 #15a's guidance from the
      prerequisite draft. Replace the promissory language with:
      - One sentence: *"Read-only schema validation for Grok
        YAML files (the 12 standards defined in
        `grok-yaml-standards` v1.3+)."*
      - "Requirements" section linking to the required
        `redhat.vscode-yaml` extension.
      - "What this extension does" + "What it does not yet do"
        sections — the latter sets expectations for future
        features without promising them.
      - Link to `CHANGELOG.md` and the Marketplace listing.

- [ ] **`CHANGELOG.md`** — Keep-a-Changelog format. Seed with
      `[0.1.0]` section documenting the bootstrap.

- [ ] **`LICENSE`** — already present; confirm it is Apache-2.0
      (matches the rest of the ecosystem post-v1.2.0
      relicensing).

- [ ] **`CONTRIBUTING.md`** — minimum: how to build
      (`npm install && npm run compile`), how to test
      (`npm test`), how to run the extension in a VS Code
      Extension Development Host (`F5` from the TypeScript
      project).

- [ ] **`SECURITY.md`** — matches the ecosystem pattern: point
      at `grok-install/SECURITY.md §Enhanced Safety & Verification
      2.0`; declare this extension's disclosure channel.

- [ ] **`.vscodeignore`** — exclude `src/`, `node_modules/`,
      `tsconfig.json`, `*.ts`, `.github/`, `CONTRIBUTING.md`,
      test fixtures from the published `.vsix` package.

- [ ] **`tests/fixtures/`** — a minimal `grok-install.yaml` per
      profile (strict / standard / permissive) that the
      integration tests validate against the shipped schema
      associations. Drives the `npm test` invocation.

- [ ] **Publish to the VS Code Marketplace** under publisher
      `agentmindcloud`. Version `0.1.0`. Marketplace listing
      matches the rewritten README's honesty (no "14 standards"
      holdovers).

### Part B — Schema-fetch strategy + CI

The extension's usefulness is only as good as the schemas it
ships with. Pick **one** of (B1) or (B2) as the source of truth,
and wire the CI that keeps it fresh. Audit 07 §9 row 3 already
makes the case for B1; included here so the choice is explicit
in the issue thread.

#### Option B1 — Fetch from `grok-docs` daily mirror (recommended)

- [ ] Each `yamlValidation` entry's `url:` points at the mirrored
      schema in `grok-docs` Pages:
      `https://agentmindcloud.github.io/grok-docs/assets/schemas/latest/grok-<name>.json`.
      `latest/` is a convention on the docs site that resolves to
      the newest `grok-yaml-standards` release's schemas (daily
      mirror job — audit 05 §5 `sync-schemas.yml`).
- [ ] Benefit: no schema duplication in this repo; the extension
      tracks upstream automatically. If §2 #8 ships draft-2020-12
      schemas, this extension picks them up with zero code
      changes (the `yaml-language-server` honours the `$schema`
      keyword).
- [ ] Risk: the docs site's `latest/` path must exist and be
      stable. Confirm with `grok-docs` maintainers before
      shipping. If `latest/` is not yet a published convention,
      either (a) coordinate with `grok-docs` to add it (small
      Pages config change), or (b) pin to an explicit version:
      `/assets/schemas/v1.3.0/...`. The version-pinned form needs
      a bump PR per `grok-yaml-standards` release — acceptable
      cost given the low release cadence.

#### Option B2 — Bundle schemas in the extension itself

- [ ] Each `yamlValidation` entry's `url:` is a relative path
      resolving to a schema vendored into `schemas/grok-*.json`
      inside this repo.
- [ ] Benefit: offline-capable (no network fetch); no dependency
      on `grok-docs` infra.
- [ ] Cost: schemas become the fourth copy in the ecosystem
      (audit 06 §9 row 5 already flags this as drift risk).
      Requires a Renovate / Dependabot-equivalent job that bumps
      the bundled schemas on each `grok-yaml-standards` release,
      otherwise this repo silently pins to the version it was
      last bumped to.
- [ ] Pick only if B1 proves impractical.

#### CI (applies to either option)

- [ ] `.github/workflows/ci.yml` with three jobs:
      - `lint` — `npm run lint` (eslint) + `tsc --noEmit`.
      - `test` — `xvfb-run -a npm test` (integration tests run
        in a VS Code Extension Host via `@vscode/test-electron`;
        `xvfb-run` is the standard GitHub-hosted Linux runner
        shim).
      - `package` — `vsce package` produces a `.vsix` artefact,
        retained for 7 days. Does NOT publish automatically;
        publish is a manual `vsce publish` step on the
        maintainer's machine (or a tag-triggered separate
        workflow, out of scope for v0.1.0).
- [ ] Pin every action by 40-char commit SHA with trailing
      `# v<tag>` comment (matches §2 #3 discipline — this repo
      is the last CI-enabled repo to adopt it).
- [ ] A daily `cron` workflow (`schedule: - cron: '0 12 * * *'`)
      that runs Option B1's schema URLs against
      `tests/fixtures/` and fails if the schemas have changed
      in a way that breaks the fixtures. Detects upstream-schema
      drift at day granularity. (Skip this job if Option B2
      chosen — B2's schemas don't drift without a repo PR.)

#### CODEOWNERS + SLA (inherit from §2 #20's pattern)

- [ ] `.github/CODEOWNERS` naming the bootstrap maintainer as
      default owner (`*`). This repo is low-traffic — one-line
      CODEOWNERS is enough. The file exists for consistency
      with §2 #20's marketplace pattern.

## Notes

- **What v0.1.0 deliberately does NOT include.**
  - Snippets (triggered by `@grok` prefix). A `snippets/*.code-snippets`
    file can land in v0.2.0.
  - Hover documentation beyond what the schemas contribute (the
    schema's `description` field already drives hover; no code
    needed for that baseline).
  - Quick Fix / code actions. Require AST walking; out of scope.
  - Cross-file validation (e.g. checking that an agent in
    `.grok/agents/foo.yaml` references a tool defined in
    `.grok/tools/bar.yaml`). Requires a proper language server;
    v0.1.0 is intentionally only an association contributor.
  - IntelliSense for non-YAML Grok files. Out of scope for a
    *YAML* extension.

- **Why v0.1.0, not v1.0.0.** SemVer discipline: a single-feature
  extension sets expectations honestly by shipping < 1.0 until
  the feature set feels complete. The ecosystem's `grok-install`
  took several minor releases to stabilise; this extension should
  do the same.

- **Relationship to §2 #8 (draft-2020-12 migration).** The
  `yaml-language-server` is `$schema`-keyword aware (via
  `ajv`-based validation internally). When §2 #8 lands and the
  12 schemas flip to draft-2020-12, this extension picks up the
  change with zero code changes (Option B1) or a schema-bump PR
  (Option B2). No coordination required beyond acknowledging the
  compatibility in CHANGELOG at the time.

- **Relationship to §2 #5 (safety-profile rubric).** The
  `tests/fixtures/strict.yaml` / `standard.yaml` / `permissive.yaml`
  fixtures in Part A call out all three profiles. Once §2 #5
  ships `safety-profile-rubric-v1.values.json`, the fixtures can
  be aligned to the rubric's canonical values — not required for
  v0.1.0 but a natural follow-up.

- **Relationship to §2 #17 (`grok-agent-orchestra` bootstrap).**
  #17 is an analogous bootstrap for the other LICENSE+README-only
  repo in the ecosystem. Both repos close half of GOV-3 each;
  filing order between them does not matter.

- **Pre-filing coordination needed with `grok-docs` maintainers**
  (only if Option B1 is chosen): confirm the
  `/assets/schemas/latest/` convention is either live or easy to
  add. Flag as a single comment on `grok-docs` after this
  bootstrap's §2 #15 prerequisite merges.

- **Filing strategy.** Single primary issue in
  `vscode-grok-yaml`. The §Part-A and §Part-B acceptance bullets
  are likely all landed in one "bootstrap PR" — the issue's job
  is to set expectations and track the launch.

- **Speculative-draft honesty.** This draft's §Part-A rewrites
  the README. The specific language will need to diff-merge with
  whichever option §2 #15a's upstream reviewers chose. Treat this
  draft's README-section text as a *template*, not a final copy.

- **Out of scope here.** §2 #14b (reconciling "14 standards" in
  the landing description to "12") is a separate Phase-1B draft
  that has already shipped in `phase-1b/drafts/14b-vscode-grok-yaml-landing.md`.
  Do not duplicate its text here; cross-reference it in the
  README-rewrite bullet of Part A.
