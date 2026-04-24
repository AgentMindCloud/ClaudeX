# Filing packet — AgentMindCloud/grok-agents-marketplace

- **Target repo**: https://github.com/AgentMindCloud/grok-agents-marketplace
- **New issue URL**: https://github.com/AgentMindCloud/grok-agents-marketplace/issues/new
- **Drafts primary-targeting this repo**: 1 (§2 #20 — third pass)
- **Cross-ref / adopter follow-ups**: 3 (§2 #3 variant, §2 #18 adopter, §2 #4 subscriber)

The third-pass draft §2 #20 (triage the 12 open PRs, publish
`CODEOWNERS`, document a review SLA) now targets this repo. §2 #20
closes GOV-2 outright and is M-effort with no blockers. Filing it
before the two cross-refs below makes those adoptions cheaper,
because CODEOWNERS routes their reviews to a named maintainer from
day one.

## Primaries to file

### Primary A — §2 #20: Triage the 12 open PRs, publish CODEOWNERS, document a review SLA

- **Draft source**: [`phase-1b/drafts/20-grok-agents-marketplace-pr-triage-codeowners.md`](../drafts/20-grok-agents-marketplace-pr-triage-codeowners.md)
- **Suggested title**: `Triage the 12 open PRs, publish CODEOWNERS, document a review SLA`
- **Suggested labels**: `governance`, `review-process`, `CODEOWNERS`, `phase-1b`
- **Filing notes**:
  - Three independently-landable parts: PR triage sweep (Part A),
    CODEOWNERS + governance files (Part B), review SLA doc (Part
    C). Each can merge in its own PR or all three in one. The
    draft does not force an order — Part B (CODEOWNERS) is the
    cheapest to ship first and starts routing new PRs immediately.
  - **Maintainer-availability caveat in the draft's Notes**: if
    the repo has one maintainer today, the SLA targets (5 / 10 /
    14 / 30 business days) are aggressive. Dial back to what one
    maintainer can reliably hit; an SLA routinely missed is worse
    than an honest four-week one.
  - **Intentionally out of scope** (flagged in the draft): caret-
    ranged deps (SUP-2 / audit 08 §9 row 1), lighthouse thresholds
    (§9 row 5), telemetry schema docs (§9 row 4). Each is a
    future-row candidate in `99-recommendations.md §3.2`, not
    smuggled into this issue.
  - **Cross-ref interaction**: filing §2 #20 before the two cross-
    refs below (§2 #3 variant + §2 #18 adopter) means those PRs
    land with CODEOWNERS routing already in place. Not strictly
    required — cross-refs can ship without CODEOWNERS — but
    filing order matters a little here.

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

### Cross-ref C — §2 #4 subscriber: Install spec-release listener workflow

- **Open only after**: §2 #4's primary issue lands in `grok-install` (see `01-grok-install.md` Issue 3).
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/04-repository-dispatch-spec-to-consumers.md`](../drafts/04-repository-dispatch-spec-to-consumers.md) — §Part B, "Subscriber 3 — grok-agents-marketplace".
- **Suggested title**: `Install spec-release listener workflow (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `automation`, `spec-release`, `phase-1b`
- **Suggested body**: paste only Subscriber-3's section from Part B. The listener opens a tracking issue (not a PR) on every spec release because this repo's follow-up work is often rendering-logic-flavoured (non-mechanical — submission-form accepted versions, `visuals:` block rendering, etc.).
- **Filing note**: pairs with §2 #20's CODEOWNERS landing — once CODEOWNERS is in place, the auto-opened issue routes to a named owner and surfaces under the SLA clock (see §2 #20's Part C).
