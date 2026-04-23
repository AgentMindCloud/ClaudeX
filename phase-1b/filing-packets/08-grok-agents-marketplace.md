# Filing packet — AgentMindCloud/grok-agents-marketplace

- **Target repo**: https://github.com/AgentMindCloud/grok-agents-marketplace
- **New issue URL**: https://github.com/AgentMindCloud/grok-agents-marketplace/issues/new
- **Drafts primary-targeting this repo**: 0
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

This repo has no Phase-1B drafts primary-targeting it. The main rec
that *will* target this repo — §2 #20 (triage the 12 open PRs,
publish `CODEOWNERS`, document a review SLA) — is catalogued as a
**third-pass candidate** in `phase-1b/ISSUES.md`. §2 #20 closes
GOV-2 outright and is M-effort, no blockers; it is a natural
companion to the cross-refs below and could be drafted alongside
them if the next pass runs before this packet gets filed.

## Primaries to file

None from Phase 1B so far. §2 #20 is a third-pass candidate.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the #3 draft content below the first `---` separator; keep only the `grok-agents-marketplace` checklist row. The caret-ranged runtime deps (audit 08 §9 row 1) are a related but separate issue and are out of scope here — call that out explicitly to avoid scope creep.

### Cross-ref B — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge`.
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `grok-agents-marketplace` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  Caveat: this repo is Next.js, not Python. Adopt the portions that
  translate (lint, build, dependency-review); the template's mypy /
  pytest-coverage / schema-check jobs do not port 1:1.

  The primary flags that a parallel JS-flavour reusable workflow may
  be warranted if this adoption proves awkward — surface that here
  as a follow-up sub-issue if needed.
  ```
