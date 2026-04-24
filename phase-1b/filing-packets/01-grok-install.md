# Filing packet — AgentMindCloud/grok-install

- **Target repo**: https://github.com/AgentMindCloud/grok-install
- **New issue URL**: https://github.com/AgentMindCloud/grok-install/issues/new
- **Drafts primary-targeting this repo**: 3 (§2 #9, §2 #3, §2 #4 — latter added fifth pass, speculative)
- **Cross-ref / adopter follow-ups**: 1 (§2 #18 adopter)

## Primaries to file

### Issue 1 — §2 #9: Migrate the remaining 5 examples to v2.14 schema and gate them in CI

- **Draft source**: [`phase-1b/drafts/09-v2-14-examples-coverage.md`](../drafts/09-v2-14-examples-coverage.md)
- **Title** (paste verbatim): `Migrate the remaining 5 examples to v2.14 schema and gate them in CI`
- **Suggested labels**: `bug`, `spec`, `ci`, `version-coherence`, `S1`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/09-v2-14-examples-coverage.md` below the first `---` separator.

### Issue 2 — §2 #3: Pin every GitHub Action by commit SHA across the ecosystem, with Renovate / Dependabot keeping them fresh

- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Title** (paste verbatim): `Pin every GitHub Action by commit SHA across the ecosystem, with Renovate / Dependabot keeping them fresh`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `ecosystem`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/03-sha-pin-actions-ecosystem.md` below the first `---` separator.
- **Filing note**: this is the coordination issue per the draft's metadata; `grok-install` is the recommended primary because it is the ecosystem spec root. If you prefer 8 per-repo variants instead, file the same body against each of the 8 CI-enabled repos (see `../README.md §Troubleshooting → coordination-issue alternative`).

### Issue 3 — §2 #4: Wire repository_dispatch from grok-install → 3 consumers (speculative — fifth pass)

- **Draft source**: [`phase-1b/drafts/04-repository-dispatch-spec-to-consumers.md`](../drafts/04-repository-dispatch-spec-to-consumers.md)
- **Title** (paste verbatim): `Wire repository_dispatch from grok-install → grok-docs, grok-install-action, grok-agents-marketplace`
- **Suggested labels**: `ci`, `automation`, `version-coherence`, `ecosystem`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE)**: this draft is speculative on §2 #10. Do NOT file until §2 #10 has merged upstream in `grok-docs` — the `grok-docs` subscriber workflow in Part B references the `mkdocs.yml extra.spec_version` convention §2 #10 Part C establishes.
- **Filing note**: Part A (publisher side) lives in this repo. Part B (3 subscriber listener workflows) are **separate cross-ref follow-up issues**, opened AFTER this primary merges. Subscriber packets: `04-grok-install-action.md` (listener), `05-grok-docs.md` (listener), `08-grok-agents-marketplace.md` (listener).
- **Filing note**: one-time maintainer setup required — generate a fine-grained PAT scoped to the 3 subscriber repos (`repo → contents: read, metadata: read`) and add as `FANOUT_DISPATCH_PAT` secret on this repo. The draft's Part A spells out the exact PAT scope and includes an alternative GitHub-App path for orgs that prefer it.
- **Filing note**: Part A recommends Option A1 (trigger `on: release: [published]`) over A2 (trigger on tag push). If `grok-install` does not currently cut GitHub Releases, adding them is a one-time setup (10 minutes) and is worth doing for human-readable release notes regardless.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge` (see `09-grok-build-bridge.md`).
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `grok-install` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `supply-chain`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  This repo is listed in Part 2 of the coordination issue as an adopter.
  The template extracts grok-build-bridge's current ci.yml (lint / strict
  mypy / OS × Python matrix / --cov-fail-under=85 / draft-2020-12 schema
  validation / safety-scan / build).

  Adoption for this repo:
  - Existing validate.yml: roll up into the template, keep the YAML-lint
    + schema-validate jobs as repo-local overrides.
  - Existing ci.yml (audit 01 §5 — not fetched during Phase 1A):
    replace with a call to the reusable workflow (Option A in the
    coordination issue) or vendor the template (Option B).

  Gated on:
  - <TODO: primary URL> landing.
  - §2 #3 SHA pinning in this repo (optional but recommended first so
    the adopted template inherits SHA pins).
  - §2 #13 blocking pip-audit + secret-scan at the template source
    (optional but recommended — the adopted template will inherit the
    posture fix automatically).
  ```
