# Audit: x-platform-toolkit

- **Upstream**: https://github.com/AgentMindCloud/x-platform-toolkit
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch (4 of 20 tool subdirectories sampled)
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (4 commits total)

## 1. Summary

`x-platform-toolkit` is a monorepo of 20 tools aimed at filling functional gaps in X (formerly Twitter), spanning analytics, AI writing, AI analytics, monetisation, automation, network, and media. Each tool lives in `tools/NN-<slug>/`, and the repo claims **8 "Live" tools shipped as single-file `index.html` implementations**, with the remaining **12 in "Spec'd" phase** (README + SPEC.md only). Shared concerns live in `shared/`: a `grok-client`, an `x-api-client`, and a `ui-kit` (design tokens + CSS). The ecosystem positioning is "solo-builder-friendly" — every tool self-hostable. Maturity is early (1★, 0 PRs, 4 commits total). Headline findings:
1. **Live-vs-spec ratio is 40%/60%.** The repo is more of a planning artefact than a shipping one at this point.
2. **Sampling verified the claim structurally** — 3 of 4 sampled tool directories contained only README+SPEC.md (likely Spec'd), 1 contained README+index.html (Live) — consistent with 8/20 live.
3. **Single-file HTML architecture** inlines `shared/ui-kit/tokens.css` and `components.css` per tool; no build step, easy self-host, but means no cross-tool JS consistency (each tool re-implements its own logic).

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/ISSUE_TEMPLATE/
├── assets/
├── docs/
├── shared/
│   ├── grok-client/
│   ├── ui-kit/
│   │   ├── README.md, components.css, tokens.css, shell.html
│   │   (README says LIVE tools *inline* these into their own index.html)
│   └── x-api-client/
├── tools/
│   ├── 01-thread-decay-tracker/       # (Spec'd — README + SPEC.md)
│   ├── 02-follower-intent-classifier/
│   ├── 03-contextual-reply-suggester/
│   ├── 04-pre-post-virality-scorer/
│   ├── 05-pinned-post-ab-rotator/     # Live — README + index.html
│   ├── 06-digital-product-storefront/ # (Spec'd)
│   ├── 07-content-compound-calculator/
│   ├── 08-follow-unfollow-velocity-map/
│   ├── 09-engagement-quality-score/
│   ├── 10-cross-account-niche-benchmarker/
│   ├── 11-ghostwriter-mode-with-memory/
│   ├── 12-controversy-detector/
│   ├── 13-thread-to-newsletter-converter/
│   ├── 14-warm-introduction-mapper/
│   ├── 15-spaces-recorder-clips/
│   ├── 16-follower-migration-assistant/
│   ├── 17-post-necromancer/
│   ├── 18-emotional-tone-trend-tracker/
│   ├── 19-grok-thread-composer/       # (Spec'd)
│   └── 20-x-articles-optimizer/
├── .editorconfig, .gitignore
├── CHANGELOG.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, LICENSE, README.md
```

**Entry points**
- Each Live tool: open `tools/NN-<slug>/index.html` directly in browser.
- Each Spec'd tool: read README + SPEC.md as an implementation brief.

**Language mix**: HTML 93.4%, CSS 4.7%, JS 1.9% — but concentrated in the 8 Live tools' inline bundles, not in a src/ tree.

## 3. Dependency graph

- **Inbound**: solo builders self-hosting individual tools. Largely orthogonal to the rest of the ecosystem.
- **Outbound**:
  - X API v2 — via `shared/x-api-client/`.
  - xAI Grok — via `shared/grok-client/`.
  - Shared UI: `shared/ui-kit/{tokens,components}.css` inlined into each tool's `index.html`.
- **External runtime deps**: none declared centrally — each tool is a single HTML bundle, possibly with inline CDN-loaded libs `(not verified)`.
- **No dependency on grok-install or grok-yaml-standards** — this sits outside the spec ecosystem.

## 4. Documentation quality

- **README.md (top-level)**: present; clear framing ("X ships ~10% of the tools power users need") and categorisation of all 20 tools with Live/Spec'd status.
- **Per-tool docs**: every tool directory contains a README.md; Spec'd tools additionally have a SPEC.md (implementation brief).
- **`shared/ui-kit/README.md`**: explains the inlined-tokens-and-components architecture.
- **Governance files**: CHANGELOG.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, LICENSE all present.
- **`.github/ISSUE_TEMPLATE/`**: present — tool-request/tool-bug templates `(inferred)`.
- **`docs/`**: present; not sampled.

**Score: 4/5** — strong per-tool documentation; consistent SPEC.md pattern for unshipped tools is a healthy backlog practice. Loses a point because the top-level README's "Live vs Spec'd" labels aren't easily re-derivable from the directory listing without opening each tool.

## 5. Tests & CI

- **No `.github/workflows/` directory visible at repo root** in the top-level listing. The toolkit appears to have **no CI** — uniquely absent in the ecosystem.
- **No test framework** for HTML-only tools (the architecture makes this difficult — each tool is an `index.html` meant to be opened directly).
- **No linter config at repo root** (`.editorconfig` is present, which is helpful but minimal).

This is the weakest CI posture in the ecosystem.

## 6. Security & safety signals

- **No CI = no automated security checks.** No bandit/gitleaks/dependency-review on this repo.
- **X API tokens**: tools that use X API will need user-provided credentials; README doesn't detail the flow `(not verified)`.
- **xAI_API_KEY**: Grok-using tools likely require this; handling mechanism per-tool is not standardised `(inferred)`.
- **Single-file HTML model**: the security boundary is entirely the user's browser. Token input / storage is presumably in localStorage or direct paste — each tool's `shared/grok-client` usage needs review. *This is a real security-audit gap* — an end-user opening an HTML file with token paste fields has no protection against supply-chain issues in the inlined CDN libs.
- **Safety-profile integration**: none — this repo doesn't participate in the `grok-install` safety model.

## 7. Code quality signals

- **No linter / formatter / type-checker** in CI.
- **`.editorconfig`** provides basic consistency (line endings, indentation).
- **Architecture discipline**: inlining shared CSS (tokens + components) rather than linking means visual consistency at the cost of JS duplication — each Live tool re-implements API calls and state.
- **Cohesion via SPEC.md**: the SPEC-first discipline for 12 unshipped tools is a strong planning-layer signal even if the implementation layer is thin.

## 8. Integration contract

- **Public surfaces (per-tool)**: each tool is a self-contained `index.html` OR a SPEC.md. The "public API" of the toolkit is the collection itself — no shared runtime API.
- **`shared/grok-client/`** and **`shared/x-api-client/`** presumably export JS modules for inlining; their interfaces are not verified this iteration `(WebFetch-limited)`.
- **No versioning** — 4 commits total; no release tags.
- **No composition story** — each tool is orthogonal; they don't use each other.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Add a minimal CI workflow: HTML validation (e.g. html-validate), CSS lint (stylelint), broken-link check on per-tool READMEs, a Live-vs-Spec'd consistency check (asserts `index.html` exists iff status is Live) | M | 5 | This is the only repo in the ecosystem without CI. A single `validate.yml` file would cover 80% of quality regressions. | None |
| 2 | Consolidate `shared/grok-client` with `grok-install-cli/xai-sdk` usage (or with `grok-build-bridge/xai_client.py`) via a shared JS package | L | 4 | Fourth place in the ecosystem where a Grok-API wrapper is implemented (spec repo, Python CLI, build-bridge, and now JS here). Shared client avoids drift on auth, error shapes, rate-limit handling. | Ownership decision |
| 3 | Document the token-handling architecture for Live tools (where tokens are stored, whether they persist, what they see) | S | 4 | A security-aware user reading an index.html that asks for an xAI_API_KEY will want a clear statement. Without one, adoption is limited to trust-on-faith. | None |
| 4 | Ship 3 more tools from the "Spec'd" bucket to move the Live ratio above 50% | M | 3 | Repo's position as a "ships" artefact vs. a "plans" artefact flips above 50%. Momentum matters for a 1★ repo. | Author time |
| 5 | Publish a Live-tools index page (could live in `docs/` and deploy via Pages) so the 8 shipping tools are discoverable without cloning | S | 3 | Self-hostability is a feature, but a canonical index-of-links also helps new users evaluate whether to adopt. | None |

## 10. Open questions / unknowns

- Which 8 tools are exactly Live? (Audit sampled 4 of 20; inferred from file listings — need the full matrix.) `(needs full tree walk)`
- What's in `shared/grok-client/` and `shared/x-api-client/` — are they JS modules with TypeScript definitions? How do Live tools inline them? `(needs content fetch)`
- Does `docs/` include a hosted-demo link list? `(not fetched)`
- What's in `assets/` — just branding, or shared illustrations? `(not fetched)`
- Are there any Node-built tools (the 1.9% JS might be inline scripts or might be a package), or is this purely static HTML? `(ambiguous from linguist alone)`
- How do the Live tools handle CORS when calling X API / xAI from the browser? Via a proxy? `(needs source read)`
- Is there a hosted deployment (e.g. `x-platform-toolkit.agentmind.cloud`) — or is self-host the only path? `(not stated in README)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/x-platform-toolkit | Repo landing: description, 1★, 0/0/0/0, Apache 2.0, 4 commits, HTML 93.4%/CSS 4.7%/JS 1.9%; top-level tree with tools/ + shared/ + docs/ + assets/ + `.github/ISSUE_TEMPLATE/`. README declares 20 tools by category with 8 Live / 12 Spec'd. |
| 2 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/tools | 20 subdirectories `01-thread-decay-tracker` … `20-x-articles-optimizer`. |
| 3 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/tools/01-thread-decay-tracker | Contents: `README.md`, `SPEC.md` (Spec'd). |
| 4 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/tools/19-grok-thread-composer | Contents: `README.md`, `SPEC.md` (Spec'd). |
| 5 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/tools/06-digital-product-storefront | Contents: `README.md`, `SPEC.md` (Spec'd). |
| 6 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/tools/05-pinned-post-ab-rotator | Contents: `README.md`, `index.html` (Live — confirmed the Live-vs-Spec'd file shape distinction). |
| 7 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/shared | Three subdirs: `grok-client/`, `ui-kit/`, `x-api-client/`. |
| 8 | https://github.com/AgentMindCloud/x-platform-toolkit/tree/main/shared/ui-kit | Files: `README.md`, `components.css`, `shell.html`, `tokens.css`. README states Live tools inline tokens+components into their own `index.html`. |
