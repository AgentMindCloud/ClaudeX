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
