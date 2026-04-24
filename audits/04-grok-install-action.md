# Audit: grok-install-action

- **Upstream**: https://github.com/AgentMindCloud/grok-install-action
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (release `v1.0.0` tagged 2026-04-21)

## 1. Summary

`grok-install-action` is the ecosystem's GitHub-native "certification" surface: a composite Node-20 action that installs `grok-install-cli`, runs `validate` + `scan`, converts results into inline PR annotations and a pinned PR comment, then generates an SVG badge at `/badges/grok-native-certified.svg` committed on main. `action.yml` is disciplined (8 inputs, 5 outputs, strict/warn mode switch, pinnable `cli-version` defaulting to 2.14.0, graceful `github-token` fallback). Two significant cross-repo inconsistencies surface:

1. **README claims "validation against 14 YAML specifications"** — but `grok-yaml-standards` explicitly ships 12 and `version-reconciliation.md` declined the 14-count. The action's docs predate or ignore that reconciliation.
2. **The action installs the CLI via `npm install -g grok-install-cli@...`** — but the `grok-install-cli` repo is Python (`pyproject.toml`, entry point `grok_install.cli:app`, ruff, pytest). Either an npm wrapper package exists that's not documented in the CLI repo, or the action expects a package that isn't the one I audited.

Maturity is early (0★/0/0/0, no forks, released 2 days before this audit), but the action surface is production-shaped. Headline risk: **the npm-vs-Python CLI installation mismatch**.

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/        # release.yml, test.yml
├── docs/
├── scripts/
│   ├── annotations.js        # GitHub Check annotations from report.json
│   ├── badge.js              # SVG badge generator
│   ├── comment.js            # Pinned PR-comment upsert
│   └── run.sh                # CLI invocation + report capture
├── tests/
│   └── sample-agent/         # used by workflows-examples integration test
├── workflows-examples/
├── action.yml, marketplace.yml, package.json
├── CHANGELOG.md, CONTRIBUTING.md, LICENSE, SECURITY.md, README.md
```

**Entry points**
- `action.yml` (composite action, `runs.using: composite`).
- `scripts/run.sh` orchestrates CLI invocation + report emission.
- `scripts/annotations.js`, `comment.js`, `badge.js` consume `report.json`.

**Language mix**: JavaScript 82.7%, Shell 17.3% (linguist bar).

## 3. Dependency graph

- **Inbound**: any repo that adopts the action via `uses: AgentMindCloud/grok-install-action@v1`.
- **Outbound**:
  - `grok-install-cli` — installed globally via `npm install -g grok-install-cli@${{ inputs.cli-version }}` (default `2.14.0`). *See §1 headline risk.*
  - `actions/checkout@v4`, `actions/setup-node@v4` — both major-tag pinned.
  - Node 20 runtime; action's own `package.json` installed via `npm ci --omit=dev --no-audit --no-fund`.
- **External runtime deps**: whatever `scripts/annotations.js` / `comment.js` / `badge.js` import (not sampled this iteration — `(WebFetch-limited)`).

## 4. Documentation quality

- **README.md**: Quick-start with full permissions block, input descriptions inline in `action.yml`. Contains the suspect "14 specifications" phrasing.
- **SECURITY.md**: present; content not fetched `(WebFetch-limited)`.
- **CHANGELOG.md**: present; content not fetched beyond the v1.0.0 release note summary (CLI pinning, visuals-preview, release automation).
- **`marketplace.yml`**: present (GitHub Marketplace metadata); not fetched.
- **`workflows-examples/`**: reference implementations directory; not sampled.
- **Inline docs in `action.yml`**: strong — every input has a clear description, every output is typed.

**Score: 4/5** — `action.yml` itself is exemplary; README has the 14-vs-12 drift.

## 5. Tests & CI

Two workflows:

| Workflow | Purpose |
|----------|---------|
| `test.yml` | `unit` job: `npm ci`, `npm test`. `integration` job (depends on `unit`): invokes `./` against `tests/sample-agent` with `mode: warn`, `update-badge: false`, `comment-on-pr: false` (self-test on the action repo). |
| `release.yml` | `(not fetched)` |

- **Test framework**: `npm test` (framework not identified — `(WebFetch-limited)` — likely mocha/jest/vitest).
- **Integration coverage**: end-to-end self-test is a strong pattern; runs the real action surface on a fixture agent.
- **Permissions**: `contents: read`, `pull-requests: write`, `checks: write` — principle-of-least-privilege discipline.
- **Action pinning in workflows**: major tag (`@v4`) — same ecosystem pattern.

## 6. Security & safety signals

- **Dependency pinning**: action installs CLI at an exact pinnable version (default `2.14.0`); GitHub actions pinned by major tag, not SHA; `package.json` lockfile discipline `(not verified — package-lock.json not fetched)`.
- **Badge-commit bot**: writes directly to `main` as `grokinstall-bot <bot@grokagents.dev>` on push events; workflow token used for `git push`. Mitigation: commit has `[skip ci]` to prevent loops, and diff-check avoids no-op commits. Risk: any repo enabling the badge feature gives the action `contents: write` — broader than needed for strict mode.
- **Permissions required by consumers**: `contents: write`, `pull-requests: write`, `checks: write` (from README). `contents: write` is only needed if `update-badge: true`. Downgrade path for readonly consumers should be documented.
- **Strict-mode failure**: `::error title=GrokInstall::...; exit 1` — correct hard-fail pattern.
- **No SHA-pinned CLI install**: `npm install -g grok-install-cli@2.14.0` fetches whatever is on the registry at that semver; an attacker who compromises the CLI's npm publishing could swap the artefact. Lockfile pinning at the action level doesn't cover the globally-installed CLI.
- **Schema-count drift**: "14 specifications" in README vs. 12 in `grok-yaml-standards` — cosmetic but signals the docs aren't automatically synced from the standards repo.

## 7. Code quality signals

- **Linter/formatter**: not verified `(WebFetch-limited — package.json not fetched)`; presence of ruff is expected since the ecosystem uses it in Python repos, but this is a JS repo so likely eslint.
- **Error handling**: `action.yml` steps use `if: always() && <guard>` correctly (badge + comment steps only run when a report exists) and fall back to `github.token` when `github-token` input is empty.
- **Module cohesion**: clean — one JS file per responsibility (annotations / comment / badge) + a shell orchestrator.
- **Composite action pattern**: appropriate choice (no Docker build needed, fast cold-start, deterministic).

## 8. Integration contract

- **Public surface (`action.yml`)**:
  - Inputs: `working-directory` (default `.`), `mode` (`strict`/`warn`, default `strict`), `cli-version` (default `2.14.0`), `visuals-preview` (default `false`, requires CLI ≥2.14.0), `update-badge` (default `true`), `comment-on-pr` (default `true`), `github-token` (optional override).
  - Outputs: `passed`, `safety-score` (0–100), `report-path`, `badge-path`, `visuals-preview-url`.
  - Branding: `icon: shield`, `color: blue`.
- **Marketplace publication**: `marketplace.yml` present (not fetched).
- **Breaking-change posture**: v1.0.0 is the first tag; major-version rollover via `@v1` tag.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Reconcile the CLI-install mechanism: clarify whether the npm package `grok-install-cli` is the same artefact as the Python repo; document the path; or switch to `pip install grok-install` if the Python CLI is canonical | M | 5 | Largest ecosystem drift: the action installs via npm, the source repo is Python. Anyone debugging a failed install hits this wall immediately. | Maintainer decision |
| 2 | Sync the "14 specifications" phrasing in README with `grok-yaml-standards` `version-reconciliation.md` (12 standards) | S | 3 | Wrong number in the README of the most-adopted consumer surface is a credibility hit. Reconciliation doc even provides PR language. | None |
| 3 | Pin `actions/checkout`, `actions/setup-node` by SHA in `action.yml` + `test.yml` | S | 4 | An action is a supply-chain vector; ecosystem-consistent posture already uses SHA pinning elsewhere `(cross-repo reco)`. | None |
| 4 | Add lockfile (`package-lock.json`) validation + `npm ci --audit` to `test.yml` | S | 3 | `--no-audit` + implicit lockfile means silent dep vulnerabilities. The action itself runs safety scans on consumers; it should be clean on its own deps. | None |
| 5 | Document the "reduced-permissions" path (readonly consumer): `update-badge: false` + `contents: read` | S | 3 | The current quick-start demands `contents: write`; many secure orgs default to readonly. A documented downgrade pathway aids adoption. | None |

## 10. Open questions / unknowns

- Does the npm `grok-install-cli` package exist and match the Python repo's behaviour? `(needs npm registry check)`
- What test framework does `npm test` run (mocha/jest/vitest)? What's the unit-test coverage of `annotations.js`/`comment.js`/`badge.js`? `(WebFetch-limited)`
- What triggers `release.yml` and does it auto-publish to GitHub Marketplace? `(WebFetch-limited)`
- What is the JSON schema of `report.json` that `annotations.js` consumes? `(needs source read)`
- Does `scripts/run.sh` handle non-zero CLI exit codes gracefully vs propagating? `(not fetched)`
- Is `marketplace.yml` the actual Marketplace listing metadata? What's the category? `(not fetched)`
- Does the bot commit use `[skip ci]` in all paths — or can it trigger workflow loops on forks? `(source read needed)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-install-action | Repo landing: description, stars (0), forks (0), issues (0), PRs (0), license (Apache-2.0), top-level tree, linguist (JS 82.7% / Shell 17.3%), latest release v1.0.0 (2026-04-21), "CLI pinned to 2.14.0" in v1.0 notes. |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-install-action/main/action.yml | Full composite action: 8 inputs (`working-directory`, `mode`, `cli-version` default `2.14.0`, `visuals-preview`, `update-badge`, `comment-on-pr`, `github-token`), 5 outputs; runs `npm install -g grok-install-cli@<cli-version>` then `scripts/run.sh`, then annotations/comment/badge JS; conditional badge-commit on push-to-main with `[skip ci]`. |
| 3 | https://github.com/AgentMindCloud/grok-install-action/tree/main/scripts | 4 files: `annotations.js`, `badge.js`, `comment.js`, `run.sh`. |
| 4 | https://github.com/AgentMindCloud/grok-install-action/tree/main/.github/workflows | 2 workflows: `release.yml`, `test.yml`. |
| 5 | https://raw.githubusercontent.com/AgentMindCloud/grok-install-action/main/.github/workflows/test.yml | Triggers: PR + push-main; unit job (`npm ci`, `npm test`) + integration job (self-test via `./` on `tests/sample-agent`, `mode: warn`, badge/comment off); permissions `contents: read`, `pull-requests: write`, `checks: write`; `setup-node@v4` major-tag. |
