# Triage the 12 open PRs, publish CODEOWNERS, document a review SLA

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #20 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/grok-agents-marketplace
- **Risks closed**: GOV-2 (S2) outright — from `audits/98-risk-register.md`.
- **Source audits**: `[→ 08 §9 row 2]`. Supporting context in `audits/08-grok-agents-marketplace.md §1` (12 open PRs, 0 visible reviewers, highest-velocity repo in the ecosystem) and `audits/00-ecosystem-overview.md §7.2` (governance-file gaps across the ecosystem).
- **Effort (§2)**: M — three independently-testable parts; triage of 12 PRs is the unknown-shape half of the effort, the other two parts are small.
- **Blocked by**: none
- **Cross-refs**: §2 #3 variant (SHA-pin GitHub Actions) and §2 #18 adopter (CI baseline template adoption) already target this repo — see `phase-1b/filing-packets/08-grok-agents-marketplace.md`. Publishing CODEOWNERS here makes those cross-ref adoptions cheaper because reviewer routing is already set up.
- **Suggested labels**: `governance`, `review-process`, `CODEOWNERS`, `phase-1b`

---

## Context

`grok-agents-marketplace` is the most actively-developed repo in
the Grok ecosystem: **12 open PRs** at audit time (2026-04-23) —
a 10× multiple on any other repo in the ecosystem. The same
audit observed **zero visible reviewers** on those PRs and **no
`CODEOWNERS` file** at the repo root. Contributor PRs stall; the
incentive to fork instead of contribute rises with each unreviewed
week.

The repo is also the ecosystem's **consumer surface** — the
Next.js app at `grokagents.dev` is what actual users see. The
gap between "most contributor energy in the ecosystem" and
"slowest review throughput in the ecosystem" concentrates
governance risk here more than anywhere else.

This issue's job is to close GOV-2 in three independently-landable
parts:

1. **Triage the 12 open PRs** — one timeboxed first-pass per PR,
   producing one of four outcomes (merge / request-changes /
   close-as-wontfix / escalate). This is the only half-variable
   part of the issue — triage output depends on what's actually
   in the PRs.

2. **Publish `CODEOWNERS`** — route future PRs to the right
   reviewer automatically. Routing is what prevents the problem
   from recurring.

3. **Document a review SLA** — set expectations for contributors
   (how long until first review? how long from first review to
   decision?) so the "filed two weeks ago, radio silence" pattern
   becomes a visible deviation, not an unspoken norm.

The three parts have no forced filing order: CODEOWNERS can ship
before triage finishes (new PRs route correctly from day one);
the SLA doc can be drafted in parallel. Triage is the slowest
gate because it depends on maintainer time and on reviewers
actually being available.
