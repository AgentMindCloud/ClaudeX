# Filing packet — AgentMindCloud/grok-install-action

- **Target repo**: https://github.com/AgentMindCloud/grok-install-action
- **New issue URL**: https://github.com/AgentMindCloud/grok-install-action/issues/new
- **Drafts primary-targeting this repo**: 1 (§2 #14a)
- **Cross-ref / adopter follow-ups**: 3 (§2 #6 cross-ref, §2 #3 variant, §2 #18 adopter)

## Primaries to file

### Issue 1 — §2 #14a: Align README "14 YAML specifications" with grok-yaml-standards (12)

- **Draft source**: [`phase-1b/drafts/14a-grok-install-action-readme.md`](../drafts/14a-grok-install-action-readme.md)
- **Title** (paste verbatim): `Align README "14 YAML specifications" with grok-yaml-standards (12)`
- **Suggested labels**: `docs`, `version-coherence`, `ecosystem`, `good-first-issue`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/14a-grok-install-action-readme.md` below the first `---` separator.
- **Filing note**: sibling draft `14b` is filed in `vscode-grok-yaml` (see `07-vscode-grok-yaml.md` Issue 1). DOC-1 fully closes only when both are filed.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #6 companion pointer: npm-vs-Python CLI install mismatch

- **Open only after**: §2 #6's primary issue lands in `grok-install-cli` (see `03-grok-install-cli.md` Issue 1).
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL from grok-install-cli>`
- **Draft source**: [`phase-1b/drafts/06-cli-install-mechanism.md`](../drafts/06-cli-install-mechanism.md)
- **Suggested title**: `Track CLI install-mechanism reconciliation (tracks <TODO: primary URL>)`
- **Suggested labels**: `bug`, `version-coherence`, `S1`, `phase-1b`
- **Suggested body**:

  ```
  Short companion to <TODO: primary URL> (filed in grok-install-cli).

  This repo's action.yml currently installs the CLI via
      npm install -g grok-install-cli@2.14.0
  while the upstream CLI repo is Python at pyproject.toml 0.1.0.

  Whichever install path the primary issue lands on — Python canonical
  (pip / pipx + setup-python), npm wrapper canonical, or both — this
  action must be updated to match:

  - action.yml input default for `cli-version`
  - action.yml install step (setup-python vs setup-node)
  - README quick-start
  - workflows-examples/ (any that echo the install command)
  - CHANGELOG.md under [Unreleased]

  Gated on the primary's resolution option being chosen.
  ```

### Cross-ref B — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the content of the #3 draft below the first `---` separator; keep only the `grok-install-action` checklist row. The scope here is slightly larger — `action.yml` itself embeds `actions/checkout@v4` + `actions/setup-node@v4`, not just `.github/workflows/test.yml`, so both files need the SHA-pin sweep.

### Cross-ref C — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge`.
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `grok-install-action` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  Caveat: this repo is a Node 20 composite action, not a Python package.
  The template is Python-centric; adopt the portions that translate:
  - test.yml → template's test + build jobs (Node matrix)
  - release.yml stays bespoke

  The §2 #18 primary flags a parallel JS-flavour reusable workflow as a
  possible follow-up if the straight adoption proves awkward.
  ```
