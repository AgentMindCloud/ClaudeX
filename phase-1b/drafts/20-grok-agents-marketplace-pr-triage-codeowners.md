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

## Evidence

From `main` snapshot + repo landing page on 2026-04-23 (WebFetch;
paths stable).

**Repo landing** — `audits/08-grok-agents-marketplace.md §1, §11 row 1`:
- 0 stars, 0 forks, 0 issues, **12 open PRs**, 11 commits,
  Apache 2.0, Node `>=20`, TS 98.4% / CSS 1.6%. Vercel-hosted;
  live site `https://grokagents.dev`.
- "12 open PRs" is a 10× multiple on any other repo in the
  ecosystem at audit time.

**Governance surface observed** —
`audits/08-grok-agents-marketplace.md §4`:
- **Missing** at repo root: `SECURITY.md`, `CONTRIBUTING.md`,
  `CHANGELOG.md` not verified. Expected by the ecosystem
  convention; present in most peer repos.
- **No `CODEOWNERS`** referenced anywhere in the audit.
- README is clear on routes and features (landing, detail pages,
  `/stats`, Hall of Fame, submission form) but governance is
  happening in issues/PRs rather than docs.

**Review capacity** — `audits/08-grok-agents-marketplace.md §7`:
- "12 open PRs is a code-quality signal *and* a reviewer-capacity
  signal: active but likely under-reviewed."

**Source §2 citation** —
`audits/99-recommendations.md §2 #20`:
- Effort M, reach 2, leverage 5.
- "Triage the 12 open PRs on `grok-agents-marketplace`, publish
  `CODEOWNERS`, and document a review SLA. (closes: GOV-2)"

**Risk register** — `audits/98-risk-register.md`:
- **GOV-2** (S2, likelihood L-high, `open`): "12 open PRs on
  `grok-agents-marketplace`, none reviewed; no `CODEOWNERS`. The
  most-active repo has no triage capacity, so contributor PRs
  stall and forks proliferate."

**Ecosystem context** (for CODEOWNERS + SLA precedent) —
`audits/00-ecosystem-overview.md §7.2`:
- `CODEOWNERS` presence across the 12 audited repos is not
  mentioned — none of the per-repo audits flagged an existing
  `CODEOWNERS` file. Publishing one here is a first for the
  ecosystem and sets a template other repos can adopt.

**Open unknowns** (flagged for the triage step) —
`audits/08-grok-agents-marketplace.md §10`:
- Whether the 12 PRs come from Copilot/automation or human
  contributors — `(needs GitHub API / org MCP)`.
  The triage plan below handles both cases (automation PRs often
  close-as-wontfix faster; human PRs take longer).

## Acceptance criteria

Three parts. Each is independently mergeable; the issue closes
when all three are complete. Landing order is flexible; Part B
(CODEOWNERS) can ship first if a maintainer wants new PRs to
route correctly before the Part-A triage is complete.

### Part A — Triage the 12 open PRs (timeboxed first-pass)

The goal is a first-pass decision per PR in a bounded window,
not to merge or close every PR.

- [ ] **Open a tracking issue** in this repo titled *"PR-triage
      sweep 2026"* (or the chosen date) listing all 12 open PRs
      with one row per PR: `#N | title | author-type
      (human/automation/copilot) | first-pass target date |
      outcome`.
- [ ] **Classify each PR** via first-pass review (≤20 minutes per
      PR) into exactly one outcome:
      - **merge** — PR is ready or needs ≤1 cycle of requested
        changes. Merge directly or leave a clear
        `request-changes` review.
      - **request-changes** — PR is substantively reasonable but
        needs non-trivial rework. Leave a `request-changes`
        review with a time-bounded expectation ("if not
        addressed within N days, will close as stale").
      - **close-as-wontfix** — PR's scope is outside the repo's
        direction or overlaps with planned work. Leave a short
        comment + link to the superseding issue/PR if one
        exists.
      - **escalate** — PR requires maintainer discussion that
        can't happen in the triage sweep. Convert to a design
        discussion; assign an owner; leave the PR open but
        re-label `triage:escalated`.
- [ ] **Apply triage labels** to each PR:
      `triage:merge-ready`, `triage:needs-rework`,
      `triage:wontfix`, `triage:escalated`. Create the labels
      if they don't exist (the label set is part of the Part-A
      deliverable, not a prerequisite).
- [ ] **Record outcomes** in the tracking issue. When the final
      PR is classified, close the tracking issue with a one-line
      summary: *"12 PRs → N merged / M request-changes / K
      closed / J escalated. Distribution: …"*
- [ ] **Timebox**: target 10 business days for the sweep. If the
      sweep stretches beyond that, post an interim status update
      in the tracking issue so contributors know where they
      stand.
- [ ] **Fairness note** in the tracking issue: if any PR was
      opened more than 60 days ago, give the author 7 days'
      notice before closing as wontfix or stale. This is
      etiquette, not policy — but documenting it here makes the
      triage sweep a one-time event, not a surprise cliff.

### Part B — Publish `CODEOWNERS`

Route every PR to a named owner by touched-path. Smallest
concrete ask: create the file, populate it, enable required
reviews from code owners for the `main` branch.

- [ ] **Create `.github/CODEOWNERS`** (repo-root alternative also
      works, but `.github/CODEOWNERS` is the GitHub convention
      and avoids colliding with source directories). Seed it with
      a default owner (`*`) and directory-specific overrides:

      ```
      # Default owner — everything not otherwise routed.
      *                          @<default-maintainer>

      # App code
      /src/                      @<frontend-maintainer>
      /next.config.ts            @<frontend-maintainer>
      /tailwind.config.ts        @<frontend-maintainer>

      # Data layer
      /migrations/               @<backend-maintainer>
      /src/**/api/               @<backend-maintainer>

      # Platform / CI
      /.github/                  @<platform-maintainer>
      /package.json              @<platform-maintainer>
      /tsconfig.json             @<platform-maintainer>
      /vitest.config.ts          @<platform-maintainer>

      # Governance files
      /.github/CODEOWNERS        @<default-maintainer>
      /SECURITY.md               @<default-maintainer>
      /CONTRIBUTING.md           @<default-maintainer>
      ```

      The owner placeholders above are literal placeholders; the
      filing maintainer substitutes real GitHub handles. If only
      one maintainer exists today, all rows point at the same
      handle — that is fine and explicit beats implicit. When a
      second maintainer onboards, this file is the first place
      their scope gets recorded.

- [ ] **Enable "Require review from code owners"** on the `main`
      branch protection ruleset. Combined with an existing
      "Require pull request reviews" rule, this forces CODEOWNERS
      routing to actually be honoured.

- [ ] **Add `SECURITY.md`** at repo root (separate from the
      `CODEOWNERS` file but naturally co-filed here). Content:
      disclosure channel (email or private advisory), a
      public-disclosure-window note, and the existing ecosystem
      pointer to `grok-install/SECURITY.md §Enhanced Safety 2.0`.
      This closes the repo's §4 governance-file gap in the same
      PR as CODEOWNERS.

- [ ] **Add `CONTRIBUTING.md`** at repo root: how to run the app
      locally (`npm install && npm run dev`), how to submit a PR,
      reference to the review SLA (Part C). One-screen file;
      link to existing ecosystem-wide ROADMAP / architecture
      docs if they exist.

- [ ] **Update `README.md`** with a one-line pointer under the
      existing features section: *"Contributing? See
      `CONTRIBUTING.md` and `.github/CODEOWNERS`."*
