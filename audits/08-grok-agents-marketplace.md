# Audit: grok-agents-marketplace

- **Upstream**: https://github.com/AgentMindCloud/grok-agents-marketplace
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (`package.json` v0.1.0; 11 commits)

## 1. Summary

`grok-agents-marketplace` is the consumer surface of the ecosystem — the Next.js 15 / TypeScript web app at `https://grokagents.dev` that discovers, renders, and routes installs for `awesome-grok-agents` templates. Stack: Next.js 15, React 18, Biome (lint+format in one tool), Tailwind, Vercel KV, `@octokit/rest` (GitHub API), `zod` (validation), `shiki` (code highlight), `recharts` (stats), Vitest. CI is disciplined (4 jobs: typecheck → lint → test → build with explicit dependencies, concurrency cancelling, npm-ci caching, 10–15min timeouts) and includes a separate `dependency-review.yml` + `lighthouse.yml` — the only ecosystem repo with a performance-audit workflow. Maturity is early (0★, 0 issues, 11 commits, Node engine `>=20`) but the repo is by far the **most actively developed**: **12 open PRs** — a 10× multiple on any other repo in this ecosystem. One migration file (`migrations/001_telemetry.sql`) signals a persistent telemetry layer beyond Vercel KV. Headline risk: **deps are caret-ranged (`^`), not pinned**, including critical infra (`next ^15.1.8`, `@vercel/kv ^3.0.0`, `zod ^4.3.6`) — inconsistent with the ecosystem's spec-repos which pin exactly.

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/       # ci.yml, dependency-review.yml, lighthouse.yml
├── migrations/              # 001_telemetry.sql
├── public/                  # static assets
├── src/                     # components, pages, utilities (TS 98.4%)
├── package.json, tsconfig.json
├── next.config.ts, tailwind.config.ts, vitest.config.ts
```

**Entry points**
- Live site: `https://grokagents.dev` (Vercel-hosted).
- Routes mentioned in README: `/` (landing + marketplace grid), `/stats` (adoption dashboard), agent detail pages, client-side agent-submission form that generates pre-filled PRs to `awesome-grok-agents`.

**Language mix**: TypeScript 98.4%, CSS 1.6%.

## 3. Dependency graph

- **Inbound**: end users (browsers).
- **Outbound**:
  - `awesome-grok-agents` — reads `featured-agents.json` registry + per-template manifests `(inferred)`.
  - GitHub API (via `@octokit/rest`) — fetches agent-repo metadata + opens PRs for submissions.
  - `grok-install.yaml` schema — likely used for validation of submitted agents `(inferred)`.
- **External runtime deps** (from `package.json`):
  - Runtime (13): `@octokit/rest ^21.0.2`, `@vercel/kv ^3.0.0`, `clsx ^2.1.1`, `lucide-react ^0.454.0`, `next ^15.1.8`, `next-themes ^0.3.0`, `react ^18.3.1`, `react-dom ^18.3.1`, `recharts ^2.13.3`, `shiki ^1.24.0`, `swr ^2.4.1`, `tailwind-merge ^2.5.4`, `zod ^4.3.6`.
  - Dev (9): `@biomejs/biome 1.9.4` (exact!), `@types/*`, `autoprefixer ^10.4.20`, `postcss ^8.4.49`, `tailwindcss ^3.4.15`, `typescript ^5.6.3`, `vitest ^2.1.9`.
  - Engine: Node `>=20`.
- **Infra deps**: Vercel (hosting), Vercel KV (key-value store), Plausible (analytics per README).

## 4. Documentation quality

- **README.md**: present; lists routes and feature set clearly (landing, detail pages, `/stats`, Hall of Fame, client-side submission form). Calls out v2.14 "Visuals Renderer" integration.
- **Missing**: no SECURITY.md / CONTRIBUTING.md / CHANGELOG.md verified at repo root (not enumerated in top-level listing). Migration-driven schema docs not visible.
- **Inline docs**: not sampled `(WebFetch-limited — `src/` not walked)`.

**Score: 3/5** — README is clear but missing the ecosystem's standard governance files that other repos include. Active PR traffic suggests governance is happening in issues/PRs not in docs.

## 5. Tests & CI

Three workflows:

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | 4-job fan-in: `typecheck` (`tsc --noEmit`), `lint` (`biome check .`), `test` (`vitest run`), `build` (depends on prior 3; `next build` with `NEXT_TELEMETRY_DISABLED=1`); 10–15min timeouts; concurrency cancel-in-progress. |
| `dependency-review.yml` | `(not fetched)` — likely `actions/dependency-review-action` for supply-chain on PRs. |
| `lighthouse.yml` | `(not fetched)` — performance/accessibility audit on deploys. |

- **Test framework**: Vitest (modern, fast). Actual tests not sampled `(needs content fetch)`.
- **Typecheck discipline**: strict — separate job, fails CI hard.
- **Lint+format**: Biome 1.9.4 (exact-pinned) — single tool for both, faster than eslint+prettier combo.
- **Build gate**: build depends on typecheck+lint+test passing, so a broken PR can't get a green `build` badge without clean upstream.
- **Action pinning**: `actions/checkout@v4`, `actions/setup-node@v4` — major tag (ecosystem pattern).
- **Concurrency cancel**: resource-efficient on a high-PR-volume repo.

## 6. Security & safety signals

- **Dependency pinning**: *caret-ranged* across 13 runtime deps including Next.js, Vercel KV, Zod. Any range upgrade (even `^15.1.8` → `^15.1.9`) happens implicitly on `npm install`. This is inconsistent with spec repos' exact `==` / `==` pins.
- **`@biomejs/biome 1.9.4`** is the only exact-pin in the whole `package.json`. Deliberate — Biome's config format can change between patches.
- **dependency-review.yml** workflow suggests PR-time supply-chain checks exist (would compensate for caret pinning).
- **Secret handling**: `@vercel/kv`, `@octokit/rest`, and Plausible all require env-provided secrets (`VERCEL_KV_*`, `GITHUB_TOKEN`, `PLAUSIBLE_*`); Vercel project bindings are the usual storage. Not visible from WebFetch.
- **Safety profile**: this repo doesn't enforce agent safety directly — it displays whatever `featured-agents.json` declares. It's a presentation layer, not an enforcement layer.
- **`migrations/001_telemetry.sql`**: introduces a SQL persistence layer beyond Vercel KV. Schema not read. Telemetry-content sensitivity depends on what it collects `(needs content fetch)`.

## 7. Code quality signals

- **Biome** (lint + format) — stricter than default, single-tool discipline.
- **TypeScript** with strict mode presumably enabled (`tsconfig.json` not fetched but standard Next.js 15 templates enable `strict: true`).
- **`zod ^4.3.6`** for schema validation — appropriate for a submission form that validates agent YAML.
- **Module cohesion**: implied `src/` layout; not walked `(WebFetch-limited)`.
- **12 open PRs** is a code-quality signal *and* a reviewer-capacity signal: active but likely under-reviewed.

## 8. Integration contract

- **Public surfaces**:
  - Web routes (from README): `/`, `/stats`, agent detail pages, submission form.
  - Client-side submission form → pre-filled PRs to `awesome-grok-agents` (so `awesome-grok-agents` is the registry write-path, not this repo).
  - `/stats` API: install counters, X post counts, API savings "live counters" — implies read endpoints aggregating telemetry.
- **Visuals Renderer** (v2.14): renders the optional `visuals:` block from `grok-install.yaml` agents — requires spec v2.14 + CLI 2.14 compatibility.
- **Breaking-change posture**: v0.1.0; no semver discipline yet established on a public URL.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Replace caret-ranged deps with exact pins (or add a `renovate.json` / Dependabot config that batches upgrades) | S | 4 | Production surface pinned to `^next` auto-bumps on every `npm install` in CI. Especially risky for SSR/rendering libs. Matches spec-repo discipline. | None |
| 2 | Review + merge-or-close the 12 open PRs; publish a review cadence / CODEOWNERS | M | 5 | 12 open PRs with 0 visible reviewers is the widest unreviewed surface in the ecosystem. Triaging clears technical debt and sets a review pattern. | Reviewer time |
| 3 | Add a SECURITY.md + `dependency-review` severity thresholds + CSP / security headers doc in `next.config.ts` | M | 4 | This is a user-facing public URL (grokagents.dev) — it's the most exposed surface in the ecosystem. Other repos have SECURITY.md; this one should too. | None |
| 4 | Document the telemetry schema (`migrations/001_telemetry.sql`) + publish a privacy statement for `/stats` | S | 4 | "Live counters" on a public stats page means data is collected; users/contributors should see what's stored. Also reduces GDPR/CCPA risk. | None |
| 5 | Lighthouse CI with published thresholds (`performance ≥ 0.9`, `a11y ≥ 0.95`) blocking PRs | S | 3 | Workflow exists; setting score thresholds prevents visible regressions on the ecosystem's front door. | None |

## 10. Open questions / unknowns

- What's in `migrations/001_telemetry.sql` (schema, columns, retention)? `(needs content fetch)`
- How does `/stats` aggregate install counts — from Vercel KV, from an external database, from GitHub install events? `(needs src walk)`
- Are the 12 open PRs from Copilot/automation or human contributors? `(needs GitHub API / org MCP)`
- Does `dependency-review.yml` block PRs on `high`/`critical` vuln or just report? `(not fetched)`
- What Lighthouse thresholds are enforced in `lighthouse.yml`? `(not fetched)`
- Does the submission form actually validate against the `grok-install.yaml` JSON schema, or is validation deferred to the PR-time CI in `awesome-grok-agents`? `(design question)`
- Is the "Visuals Renderer" implemented or still stubbed? `(needs src walk)`
- Vercel KV quota / cost model at current traffic — is free tier sufficient? `(operational)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-agents-marketplace | Repo landing: description (grokagents.dev marketplace), 0★, 0 forks, 0 issues, **12 PRs**, Apache 2.0, 11 commits, TS 98.4%/CSS 1.6%, top-level tree, Vercel + Vercel KV + Plausible. |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-agents-marketplace/main/package.json | Name `grok-agents-marketplace`, version `0.1.0`, Node `>=20`, scripts (dev/build/start/lint/format/typecheck/test), 13 caret-ranged runtime deps, 9 dev deps (Biome exact-pinned at 1.9.4, rest caret). |
| 3 | https://github.com/AgentMindCloud/grok-agents-marketplace/tree/main/.github/workflows | 3 workflows: `ci.yml`, `dependency-review.yml`, `lighthouse.yml`. |
| 4 | https://raw.githubusercontent.com/AgentMindCloud/grok-agents-marketplace/main/.github/workflows/ci.yml | 4-job CI: typecheck (tsc --noEmit), lint (biome check), test (vitest run), build (next build, depends on prior 3, NEXT_TELEMETRY_DISABLED=1); 10-15min timeouts; Node 20; npm ci cache; concurrency cancel. |
| 5 | https://github.com/AgentMindCloud/grok-agents-marketplace/tree/main/migrations | One file: `001_telemetry.sql`. |
