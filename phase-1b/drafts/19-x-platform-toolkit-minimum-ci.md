# Add minimum CI to x-platform-toolkit (html-validate + stylelint + link-check + Live-vs-Spec consistency)

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #19 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/x-platform-toolkit
- **Risks closed**: SUP-5 (S3) outright — from `audits/98-risk-register.md`.
- **Source audits**: `[→ 11 §9 row 1]`. Supporting: `audits/11-x-platform-toolkit.md §5, §7, §11 row 1` (no workflows directory; `.editorconfig` only; weakest CI posture in the ecosystem).
- **Effort (§2)**: M — four jobs (html-validate + stylelint + lychee link-check + Live-vs-Spec consistency) in one workflow file plus per-tool config where needed. S-adjacent in pure engineering; M because the 20-tool monorepo shape means iterating the workflow's matrix / per-tool handling takes a pass or two.
- **Blocked by (§2)**: none — non-speculative, independent of every other §2 rec.
- **Suggested labels**: `ci`, `supply-chain`, `quality`, `phase-1b`

---

## Context

`x-platform-toolkit` is the only repo in the Grok ecosystem
with **zero CI**. No `.github/workflows/` directory, no
linter config beyond `.editorconfig`, no test runner (by
design — the 8 Live tools are single-file HTMLs meant to be
opened directly). Every supply-chain or quality regression
that would be caught elsewhere — a broken link in a
per-tool README, a malformed HTML attribute on a Live
tool, a `style.css` rule using an undefined token,
adding an `index.html` while forgetting to re-label the
tool's status to Live in the top-level README — lands on
`main` unobserved.

The fix is not a full CI pipeline. It's a minimum four-job
workflow that catches the classes of regression the repo
is most likely to ship:

1. **`html-validate` on the 8 Live `index.html` files** —
   catches malformed tags, missing required attributes,
   broken `<script>` or `<link>` references, accessibility
   basics (alt text, labelled inputs).
2. **`stylelint` on `shared/ui-kit/*.css`** — the inlined
   tokens and components CSS is the one shared asset the
   Live tools consume by copy. Linting it once prevents
   20-downstream propagation of the same rule-ordering or
   token-naming error.
3. **`lychee` link-check on all `*.md` files** — the repo
   has 20 per-tool READMEs + a top-level README + SPEC.md
   files in 12 tool directories. External link rot is the
   most visible quality regression on a "plans" artefact.
4. **Live-vs-Spec consistency check** (repo-specific;
   small Bash or Python script) — asserts the invariant
   that each tool's status in the top-level README matches
   whether its directory contains `index.html`. A tool
   listed as "Live" with no `index.html` is a lie; a tool
   listed as "Spec'd" with an `index.html` is drift the
   next contributor won't notice.

This is the single highest-leverage CI addition in the
ecosystem because the floor is zero. Every other CI-enabled
repo can debate whether to add a new lint layer; this repo
debates whether to lint at all. M-effort is honest — four
jobs, some per-tool matrix, one repo-specific consistency
script — but every job is independently useful and
incremental landing works.

Closes SUP-5 outright. This is the last §2 rec undrafted
after six passes; drafting it completes the §2 top-20.
