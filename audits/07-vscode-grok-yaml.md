# Audit: vscode-grok-yaml

- **Upstream**: https://github.com/AgentMindCloud/vscode-grok-yaml
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (7 commits total)

## 1. Summary

`vscode-grok-yaml` is described on its landing page as "Official community VS Code extension … Full IntelliSense, live validation, safety scanning, template gallery, and one-click deployment for all 14 YAML standards." **The extension does not yet exist in this repo.** The repository contents are, in total: `LICENSE`, `README.md`, and an apparently empty `media/` directory. There is no `package.json`, no `extension.ts`, no `src/`, no build config, no publisher manifest, and no Marketplace listing mechanism. The README is entirely a media-asset specification / brand wire-up guide for a future extension. Maturity is pre-alpha (7 commits, 0★, 0 forks, 1 open PR). Headline findings: this is a **marketing-polished shell repo** — the description promises a feature set the repo has not begun to implement; and like `grok-install-action`, it advertises "14 YAML standards" while `grok-yaml-standards` ships 12 per `version-reconciliation.md`.

This audit is necessarily shorter than the others because there's no extension code to audit.

## 2. Structural map

Top-level tree:

```
.
├── LICENSE
├── README.md       # media-asset spec + brand-token wire-up instructions
└── media/          # intended for icon.png, icon-dark.png, banner.png; appears empty
```

**Entry points**: none. No VS Code extension manifest present.

**Language mix**: linguist bar not surfaced for a repo this small; README-only repo.

## 3. Dependency graph

- **Inbound**: none (nothing ships for consumers yet).
- **Outbound** (intended, per README description):
  - `grok-yaml-standards` schemas (for IntelliSense + validation).
  - `grok-install-cli` (for one-click deployment feature promised in landing description).
  - Future npm / vsce toolchain for VS Code extension publishing.
- **External runtime deps**: none today.

## 4. Documentation quality

- **README.md**: present but off-topic for an extension repo. Covers:
  - Target asset paths: `icon.png` (128×128 transparent), `icon-dark.png` (128×128 on `#0A0A0A`), `banner.png` (1376×400).
  - "Wire-up" reference snippets for a future `package.json` (`icon` field + `galleryBanner.color/theme`).
  - Locked brand palette: cyan `#00F0FF`, green `#00FF9D`, deep-space black `#0A0A0A`.
  - Legal disclaimer: "independent, unaffiliated with xAI or X".
- **No CONTRIBUTING.md, no SECURITY.md, no CHANGELOG.md** at repo root.

**Score: 1/5** — the README that does exist is internally-focused (asset prep), not user-facing. Landing-page description overstates the repo's state.

## 5. Tests & CI

None. No `.github/workflows/` directory present in top-level listing.

## 6. Security & safety signals

- **No source code** → no runtime safety signals to assess.
- **No secret surface** yet (no CI, no publisher token in use).
- **Landing-description vs reality**: calling the repo "safety scanning" when no code exists is an honesty-of-capability issue for the ecosystem narrative. Aligned with the ecosystem's own anti-hallucination rules, this description should be tagged "planned" or "vaporware" until the extension ships.

## 7. Code quality signals

N/A — no code.

## 8. Integration contract

- **Planned surface** (from landing description): IntelliSense, live validation, safety scanning, template gallery, one-click deployment.
- **Current surface**: none. Not on VS Code Marketplace `(inferred — no publisher ID visible; no `.vsix` present)`.
- **Brand tokens** are the only concrete artefact: the cyan/green/black palette + media asset dimensions. These would constrain the future extension's visual design.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Downgrade the landing-page description to accurately reflect "pre-alpha / media assets only" state | S | 4 | Current description promises a shipped extension. Directly conflicts with ecosystem's anti-hallucination posture (see `grok-install/SECURITY.md`). | None |
| 2 | Bootstrap a minimal extension skeleton: `package.json` (publisher id, activationEvents), `src/extension.ts` registering a YAML language contribution that points at `grok-yaml-standards/schemas/*` | L | 5 | Without this, the entire repo's stated purpose is aspirational. Shipping even a read-only "validation-only" v0.1.0 would be the single highest-leverage move. | Author time |
| 3 | Consume the already-synced schemas from `grok-docs` Pages (`/docs/assets/schemas/latest/`) rather than duplicating | S | 4 | The docs site already republishes the 12 schemas daily. The extension can fetch from there, avoiding a fourth schema-distribution point. | `grok-docs` must be v1.3-schema-ready (cross-ref reco) |
| 4 | Align "14 standards" wording in landing description to "12 standards" per `grok-yaml-standards/version-reconciliation.md` | S | 2 | Same drift as `grok-install-action`. PR language is in the reconciliation doc. | None |
| 5 | Add CI that lints README + validates future `package.json` on PR | S | 2 | Gets the basic governance in place before code lands. | None |

## 10. Open questions / unknowns

- Is there development happening on a private branch / fork before landing on `main`? `(needs maintainer input)`
- What VS Code publisher identity is planned (e.g. `agentmindcloud` on the Marketplace)? `(needs maintainer input)`
- Does the open PR introduce the extension skeleton, or is it another asset-related change? `(needs org MCP / clone)`
- Is the "one-click deployment" planned to invoke `grok-install-cli run/deploy` from within VS Code, or to spawn a shell task? `(design question)`
- Will the extension support the `@grok <command>` YAML-comment triggers from `grok-yaml-standards`? `(design question)`
- Is there an intent to use the LSP pattern (for multi-IDE support) or keep it VS Code-specific? `(design question)`
- Is the cyan/green/black palette reused elsewhere in the ecosystem (marketplace / docs) for visual coherence? `(needs cross-repo check)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/vscode-grok-yaml | Repo landing: description (extension for "all 14 YAML standards"), 0★, 0 forks, 1 open PR, Apache-2.0, 7 commits; top-level tree contains only `LICENSE`, `README.md`, `media/` directory. |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/vscode-grok-yaml/main/README.md | README fetched; content is a media-asset spec + package.json wire-up instructions + brand palette (cyan `#00F0FF`, green `#00FF9D`, black `#0A0A0A`); independence disclaimer; no shipped features documented. |
| 3 | https://github.com/AgentMindCloud/vscode-grok-yaml/tree/main/media | `media/` directory appears empty/unpopulated (no files enumerated on tree view). |
