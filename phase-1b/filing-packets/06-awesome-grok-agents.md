# Filing packet — AgentMindCloud/awesome-grok-agents

- **Target repo**: https://github.com/AgentMindCloud/awesome-grok-agents
- **New issue URL**: https://github.com/AgentMindCloud/awesome-grok-agents/issues/new
- **Drafts primary-targeting this repo**: 0
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

This repo has no Phase-1B drafts primary-targeting it. Future recs
that *will* target this repo — §2 #11 (add a permissive-profile
exemplar, blocked by §2 #5) and §2 #12 (replace `grok_install_stub`
with a real CLI invocation, blocked by §2 #6 + #7) — are both
catalogued in `phase-1b/ISSUES.md §Post-filing follow-ups` and
should not be drafted until their prerequisites land upstream.

## Primaries to file

None from Phase 1B so far. §2 #11 and §2 #12 are future work,
gated on other primaries merging first.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the #3 draft content below the first `---` separator; keep only the `awesome-grok-agents` checklist row. Library deps here are major-pinned (`ajv-cli@5`, `ajv-formats@3`) — out of scope for *this* issue but worth mentioning so reviewers don't confuse the two.

### Cross-ref B — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge`.
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `awesome-grok-agents` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  Template adoption here is also the natural moment to wire up §2 #12
  (replace `grok_install_stub` with a real CLI invocation) — once §2 #6
  + #7 land, the adopted safety-scan job can run the live CLI against
  templates in CI.

  Gated on:
  - <TODO: primary URL> landing.
  - §2 #6 + §2 #7 landing in grok-install-cli (if §2 #12 work is
    bundled into the same PR).
  ```
