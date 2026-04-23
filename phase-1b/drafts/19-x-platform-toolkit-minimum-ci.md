# Add minimum CI to x-platform-toolkit (html-validate + stylelint + link-check + Live-vs-Spec consistency)

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #19 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/x-platform-toolkit
- **Risks closed**: SUP-5 (S3) outright — from `audits/98-risk-register.md`.
- **Source audits**: `[→ 11 §9 row 1]`. Supporting: `audits/11-x-platform-toolkit.md §5, §7, §11 row 1` (no workflows directory; `.editorconfig` only; weakest CI posture in the ecosystem).
- **Effort (§2)**: M — four jobs (html-validate + stylelint + lychee link-check + Live-vs-Spec consistency) in one workflow file plus per-tool config where needed. S-adjacent in pure engineering; M because the 20-tool monorepo shape means iterating the workflow's matrix / per-tool handling takes a pass or two.
- **Blocked by (§2)**: none — non-speculative, independent of every other §2 rec.
- **Suggested labels**: `ci`, `supply-chain`, `quality`, `phase-1b`

---

## Context

`x-platform-toolkit` is the only repo in the Grok ecosystem
with **zero CI**. No `.github/workflows/` directory, no
linter config beyond `.editorconfig`, no test runner (by
design — the 8 Live tools are single-file HTMLs meant to be
opened directly). Every supply-chain or quality regression
that would be caught elsewhere — a broken link in a
per-tool README, a malformed HTML attribute on a Live
tool, a `style.css` rule using an undefined token,
adding an `index.html` while forgetting to re-label the
tool's status to Live in the top-level README — lands on
`main` unobserved.

The fix is not a full CI pipeline. It's a minimum four-job
workflow that catches the classes of regression the repo
is most likely to ship:

1. **`html-validate` on the 8 Live `index.html` files** —
   catches malformed tags, missing required attributes,
   broken `<script>` or `<link>` references, accessibility
   basics (alt text, labelled inputs).
2. **`stylelint` on `shared/ui-kit/*.css`** — the inlined
   tokens and components CSS is the one shared asset the
   Live tools consume by copy. Linting it once prevents
   20-downstream propagation of the same rule-ordering or
   token-naming error.
3. **`lychee` link-check on all `*.md` files** — the repo
   has 20 per-tool READMEs + a top-level README + SPEC.md
   files in 12 tool directories. External link rot is the
   most visible quality regression on a "plans" artefact.
4. **Live-vs-Spec consistency check** (repo-specific;
   small Bash or Python script) — asserts the invariant
   that each tool's status in the top-level README matches
   whether its directory contains `index.html`. A tool
   listed as "Live" with no `index.html` is a lie; a tool
   listed as "Spec'd" with an `index.html` is drift the
   next contributor won't notice.

This is the single highest-leverage CI addition in the
ecosystem because the floor is zero. Every other CI-enabled
repo can debate whether to add a new lint layer; this repo
debates whether to lint at all. M-effort is honest — four
jobs, some per-tool matrix, one repo-specific consistency
script — but every job is independently useful and
incremental landing works.

Closes SUP-5 outright. This is the last §2 rec undrafted
after six passes; drafting it completes the §2 top-20.

## Evidence

From `main` snapshot on 2026-04-23 (WebFetch; paths stable).

**Repo shape** — `audits/11-x-platform-toolkit.md §1, §2, §11`:
- 20 tools under `tools/NN-<slug>/`. 8 Live (directory
  contains `README.md` + `index.html`); 12 Spec'd
  (directory contains `README.md` + `SPEC.md`).
- `shared/grok-client/`, `shared/x-api-client/`,
  `shared/ui-kit/` (tokens.css, components.css, shell.html,
  README.md). Live tools inline `tokens.css` +
  `components.css` per the `ui-kit` README.
- Top-level files: `.editorconfig`, `.gitignore`,
  `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`,
  `LICENSE`, `README.md`. `.github/ISSUE_TEMPLATE/` present;
  **no `.github/workflows/` directory**.
- Language mix: HTML 93.4%, CSS 4.7%, JS 1.9% — concentrated
  in the 8 Live tools' inline bundles.
- Maturity: 1★, 0 forks, 0 issues, 0 PRs, 4 commits total.

**Verified Live tool** — `audits/11-x-platform-toolkit.md §11 row 6`:
- `tools/05-pinned-post-ab-rotator/` contains `README.md` +
  `index.html`. This is the Live-shape archetype.

**Verified Spec'd tools** — `audits/11-x-platform-toolkit.md §11 rows 3–5`:
- `tools/01-thread-decay-tracker/` — `README.md` + `SPEC.md`.
- `tools/19-grok-thread-composer/` — `README.md` + `SPEC.md`.
- `tools/06-digital-product-storefront/` — `README.md` +
  `SPEC.md`.
- The Spec'd-shape archetype is `README.md` + `SPEC.md`.

**Full 8-Live list not yet enumerated** — `audits/11 §10` flags
"Which 8 tools are exactly Live? Audit sampled 4 of 20; inferred
from file listings". Part B's consistency check is the
mechanism that enumerates them authoritatively.

**Risk register** — `audits/98-risk-register.md`:
- **SUP-5** (S3, L-high, `open`): "`x-platform-toolkit` has
  no CI of any kind — no dependency scanning, no lint, no
  build verification; supply-chain regressions are
  invisible."

**Why reach is 2, not 1** —
`audits/99-recommendations.md §2` (footnote under §2 #19):

> "The toolkit hosts 8 of 20 advertised user-facing tools
> that *read live spec versions*, so a CI consistency check
> there protects every downstream user against silent
> spec-drift. Scored reach=2 on that argument. If a Phase
> 1B reviewer disagrees, demote it to §3."

This draft agrees with the reach=2 argument — the
Live-vs-Spec consistency check (Part B) is what makes this
rec ecosystem-relevant rather than purely local hygiene.
The 8 Live tools that read live spec versions are the
surface where the toolkit's claims can silently become
untrue.

**Related §2 cross-refs**:
- §2 #3 (SHA-pin actions + Renovate) — this repo is in §2
  #3's 8-repo checklist. Landing §2 #19 here first creates
  the `.github/workflows/` directory §2 #3 then adds
  SHA-pinning to. No hard dependency either way.
- §2 #2 (shared Grok API client) — §2 #2's JS consumer path
  is explicitly out of scope. This rec does not coordinate
  with §2 #2.
- No other §2 cross-refs.

**What this rec does NOT close**:
- `shared/grok-client/` consolidation (audit 11 §9 row 2,
  L-effort, separate row).
- Token-handling architecture documentation (audit 11 §9
  row 3, S-effort, separate row).
- Moving Live tools above the 50% threshold by shipping
  more (audit 11 §9 row 4, author time).
- Hosted demo index page (audit 11 §9 row 5, S-effort,
  separate row).

## Acceptance criteria

Two parts. Part A ships the three ecosystem-standard lint /
link jobs (html-validate + stylelint + lychee). Part B ships
the repo-specific Live-vs-Spec consistency check. The issue
closes when CI is green on `main` after all four jobs land
(three in Part A, one in Part B), and a PR that deliberately
introduces a regression (malformed HTML, unknown CSS token,
broken link, mis-labelled tool status) fails CI cleanly.

### Part A — Lint + link-check jobs

Create `.github/workflows/validate.yml` (name matches the
ecosystem convention already used by `grok-install` and
`grok-yaml-standards`). Single workflow, three jobs, runs
on `push` + `pull_request`.

- [ ] **Job 1 — `html-validate`**:
      - Scope: every `tools/*/index.html` (the 8 Live
        tools). Spec'd tools have no HTML to validate.
      - Config: `.html-validate.json` at repo root with
        `extends: ["html-validate:recommended"]`. The
        `recommended` preset covers: required attributes
        (`alt` on `img`, `label` on `input`), closing tags,
        attribute quoting, duplicate `id`, invalid
        nesting, etc.
      - Install: `npm install --no-save html-validate@<pinned>`
        in the workflow step (no `package.json` at repo
        root needed — single dep, no lockfile to maintain).
      - Fail on **error**, warn on **warning** (configurable
        later; default posture is "any error blocks merge").
      - Output: on failure, the GitHub annotation shows
        line numbers in the failing `index.html`.
- [ ] **Job 2 — `stylelint`**:
      - Scope: `shared/ui-kit/*.css` — the two files
        (`tokens.css`, `components.css`) that Live tools
        inline. Per-tool CSS is inside `index.html` and
        covered by the html-validate job's CSS parsing.
      - Config: `.stylelintrc.json` at repo root with
        `extends: ["stylelint-config-standard"]`. The
        `standard` preset covers: no-invalid-hex-colors,
        no-duplicate-selectors, declaration-block-no-shorthand-
        property-overrides, etc.
      - Custom rule: `custom-property-pattern` enforcing
        `tokens.css`'s naming convention (confirm the
        pattern with the maintainer; `^--[a-z][a-z0-9-]+$`
        is the typical starting point).
      - Install: `npm install --no-save stylelint@<pinned>
        stylelint-config-standard@<pinned>` inline in the
        step.
      - Fail on any violation.
- [ ] **Job 3 — `lychee` link-check**:
      - Scope: every `*.md` in the repo — top-level
        `README.md`, 20 × `tools/*/README.md`, 12 ×
        `tools/*/SPEC.md`, `shared/ui-kit/README.md`,
        `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
      - Use the ecosystem-standard `lycheeverse/lychee-action`
        (matches `grok-docs` + `awesome-grok-agents` usage).
      - Accept HTTP 200, 204, 206; tolerant on 403 and 429
        (X / social links rate-limit unauthenticated fetches —
        matches `awesome-grok-agents` pattern per audit 06
        §5).
      - Offline mode OFF (this repo's external-link check
        is the whole point; an offline-only check misses
        X / X-article / SPEC-referenced URLs).
      - Fail on broken links; allow a `.lycheeignore`
        regex file at repo root for known-flaky URLs.
- [ ] **Action pinning**: every action (actions/checkout,
      actions/setup-node, lycheeverse/lychee-action, etc.)
      pinned by 40-char SHA with trailing `# v<tag>`
      comment — matches §2 #3 ecosystem discipline from
      day one. This repo is in §2 #3's checklist; doing
      the pinning here at CI-landing time avoids a later
      SHA-pin-only PR.
- [ ] **Concurrency**: `cancel-in-progress: true` on the
      same ref, to match the ecosystem convention.
- [ ] **Permissions**: workflow-level `contents: read`
      only. No write scopes needed for this lint-only
      workflow.
- [ ] **Install versions exact-pinned**: `html-validate`,
      `stylelint`, `stylelint-config-standard` all at
      specific tagged versions in the workflow step.
      Matches `grok-yaml-standards`' exact-pin discipline
      for `ajv-cli` / `js-yaml` / `yamllint`.
