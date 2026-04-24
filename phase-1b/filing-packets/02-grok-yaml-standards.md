# Filing packet — AgentMindCloud/grok-yaml-standards

- **Target repo**: https://github.com/AgentMindCloud/grok-yaml-standards
- **New issue URL**: https://github.com/AgentMindCloud/grok-yaml-standards/issues/new
- **Drafts primary-targeting this repo**: 2 (§2 #5, §2 #8 — both from third pass)
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

This repo is the owner of the ecosystem's schema catalogue. Third-pass
drafts add two primaries here: the safety-profile rubric (§2 #5) and
the JSON Schema draft-2020-12 migration (§2 #8). Both are M-effort; #5
unblocks three downstream recs (#1, #11, #17) and #8 closes VER-2
outright. The repo also carries the canonical `version-reconciliation.md`
(cited by both §2 #14 drafts) and remains an §2 #3 + §2 #18 target.

## Primaries to file

### Primary A — §2 #5: Publish a unified safety-profile rubric with conformance tests

- **Draft source**: [`phase-1b/drafts/05-safety-profile-rubric.md`](../drafts/05-safety-profile-rubric.md)
- **Suggested title**: `Publish a unified safety-profile rubric (strict / standard / permissive) with conformance tests`
- **Suggested labels**: `spec`, `safety`, `ecosystem`, `phase-1b`
- **Filing notes**:
  - The draft is long (metadata header + Context + Evidence +
    four-part Acceptance + Notes). Paste everything below the
    first `---` separator; keep the metadata header in this repo
    for the audit trail.
  - Acceptance has **four independently-testable parts** (rubric
    contents, location in repo, conformance-test format, consumer
    contract). Maintainer may choose to land them as one PR or
    four; the checklist in the draft supports either.
  - Consumer-repo follow-ups (Part D) target `grok-install-cli`,
    `awesome-grok-agents`, `grok-build-bridge`,
    `grok-agent-orchestra`. **Do NOT pre-file them** — the
    rubric's normative values may shift in review. Follow-ups open
    only after this primary merges.
  - If §2 #8 (below) is filed first, the rubric's schema (which
    uses draft-2020-12) slots into the repo's migrated posture
    cleanly. If §2 #5 lands first, the rubric's schema is the one
    draft-2020-12 file in an otherwise-draft-07 repo — the
    `schema-smoke` CI job parameterises to tolerate it. Either
    order is fine; flagged in the draft's Notes.

### Primary B — §2 #8: Migrate grok-yaml-standards schemas to JSON Schema draft-2020-12 for v1.3

- **Draft source**: [`phase-1b/drafts/08-grok-yaml-standards-draft-2020-12-migration.md`](../drafts/08-grok-yaml-standards-draft-2020-12-migration.md)
- **Suggested title**: `Migrate grok-yaml-standards schemas to JSON Schema draft-2020-12 for v1.3`
- **Suggested labels**: `schema`, `migration`, `v1.3`, `ecosystem`, `phase-1b`
- **Filing notes**:
  - The draft has two parts: core migration (Part A, in this
    repo) and downstream smoke-test coordination (Part B, no code
    changes in consumer repos — verification only).
  - Do NOT open follow-up issues in the four Python-validator
    consumer repos (grok-install-cli, grok-build-bridge,
    awesome-grok-agents, grok-agents-marketplace) unless Part B's
    smoke tests surface a real problem. The migration is
    transparent to them; follow-up noise dilutes the audit trail.
  - The draft recommends filing announcement follow-ups in
    `grok-install` and `grok-docs` **only** once v1.3 ships.
    These are the two repos where the draft-07/draft-2020-12 drift
    is user-visible.
  - Release name in acceptance criteria is `v1.3.0 (or chosen
    release tag)` — the draft explicitly names `v1.2.1` as a
    valid alternative if the team prefers not to bump minor for a
    migration.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3 (see `01-grok-install.md` filing note on coordination vs. variants). If you filed §2 #3 as a single coordination issue in `grok-install`, this cross-ref is **subsumed** by that issue's checklist row for `grok-yaml-standards` — do NOT file it separately.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the content of `phase-1b/drafts/03-sha-pin-actions-ecosystem.md` below the first `---` separator. In the per-repo checklist keep only the row for `grok-yaml-standards`; delete the other 7 rows.

### Cross-ref B — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge` (see `09-grok-build-bridge.md`).
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `grok-yaml-standards` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `supply-chain`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  This repo's existing validate-schemas.yml already uses exact pins on
  library deps (yamllint 1.35.1 / ajv-cli 5.0.0 / js-yaml 4.1.0) —
  template adoption only adds the CI-level posture upgrades (matrix,
  strict, coverage floor).

  Keep the schema-validate job as a repo-local override. Retire bespoke
  scaffolding that the template subsumes.

  Interaction with §2 #8 (draft-2020-12 migration for v1.3): the
  adopted template's schema-check job uses draft-2020-12. Until §2 #8
  lands, either skip the schema-check job in this repo's adoption,
  or parameterise the validator draft version.
  ```
