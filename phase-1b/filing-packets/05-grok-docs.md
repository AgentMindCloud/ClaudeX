# Filing packet — AgentMindCloud/grok-docs

- **Target repo**: https://github.com/AgentMindCloud/grok-docs
- **New issue URL**: https://github.com/AgentMindCloud/grok-docs/issues/new
- **Drafts primary-targeting this repo**: 0
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

This repo has no Phase-1B drafts primary-targeting it. It is an adopter
for the two ecosystem-wide coordination drafts (§2 #3 and §2 #18).

The main rec that *will* primary-target this repo — §2 #10 (ship
`grok-docs` v2.14 content + 7 undocumented-standards reference pages)
— has **not been drafted yet**. §2 #10 is L-effort, no `Blocked by`,
and is catalogued in `phase-1b/ISSUES.md §Post-filing follow-ups` as
an unblocker for §2 #4 (repository_dispatch). File this packet's
cross-refs first, then come back for §2 #10 in a later pass.

## Primaries to file

None from Phase 1B so far. §2 #10 is future work.

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
