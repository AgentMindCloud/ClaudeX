# Filing packet — AgentMindCloud/grok-yaml-standards

- **Target repo**: https://github.com/AgentMindCloud/grok-yaml-standards
- **New issue URL**: https://github.com/AgentMindCloud/grok-yaml-standards/issues/new
- **Drafts primary-targeting this repo**: 0
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

This repo has no Phase-1B drafts primary-targeting it. It does carry
the canonical `version-reconciliation.md` (cited by both §2 #14
drafts) and is an §2 #3 + §2 #18 target.

## Primaries to file

None.

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
