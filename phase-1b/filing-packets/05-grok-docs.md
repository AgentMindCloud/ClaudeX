# Filing packet — AgentMindCloud/grok-docs

- **Target repo**: https://github.com/AgentMindCloud/grok-docs
- **New issue URL**: https://github.com/AgentMindCloud/grok-docs/issues/new
- **Drafts primary-targeting this repo**: 1 (§2 #10 — fourth pass 2026-04-23)
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

The fourth-pass added §2 #10 as the primary for this repo: ship
`grok-docs` v2.14 content + reference pages for the 7 missing
standards. This closes VER-4 + DOC-2 outright and unblocks §2 #4
(`repository_dispatch` wiring) for drafting in a subsequent pass.
L-effort; content-writing dominates.

## Primaries to file

### Issue 1 — §2 #10: Ship grok-docs v2.14 content + 7 undocumented-standards reference pages

- **Draft source**: [`phase-1b/drafts/10-grok-docs-v2-14-plus-7-standards-reference.md`](../drafts/10-grok-docs-v2-14-plus-7-standards-reference.md)
- **Title** (paste verbatim): `Ship grok-docs v2.14 content + reference pages for the 7 undocumented standards`
- **Suggested labels**: `docs`, `v2.14`, `standards-reference`, `content`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note**: three-part acceptance (A: v2.14 spec page; B: 7 new reference pages; C: publication layer — nav, version banner, Mike archive). Parts are independently mergeable — encourage the maintainer to split into 3–4 PRs if capacity is tight. Partial landings still move the site closer to truth.
- **Filing note**: L-effort is content-writing cost. Audit 05 §10 flags the single-maintainer signal; the draft's Notes section spells out a split strategy and a contributor-call option in README.
- **Filing note**: no new CI changes required — `sync-schemas.yml` already republishes the 12 schemas daily, so content pages embedding them via `--8<-- "docs/assets/schemas/latest/..."` just work.
- **Filing note**: interacts with §2 #8 (draft-2020-12 migration) — no coordination overhead either way; embedded schemas rebuild on next sync after #8 lands.
- **Filing note**: **unblocks §2 #4**. Once this primary merges upstream, §2 #4 (`repository_dispatch` from `grok-install` → `grok-docs` + two other consumers) becomes drafteable. Flag in the filed issue so reviewers see the dependency.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the #3 draft content below the first `---` separator; keep only the `grok-docs` checklist row. Note this repo already ships exact `==` pins in `requirements.txt` — ecosystem best-in-class for library deps; only the action-side pinning needs parity.

### Cross-ref B — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge`.
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `grok-docs` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  Template adoption for this repo: apply to the Python + MkDocs build
  pipeline + the link-check job.

  Pair with §2 #10 if convenient — §2 #10 ships v2.14 content and 7
  reference pages, which is the natural moment to regenerate the build.
  ```
