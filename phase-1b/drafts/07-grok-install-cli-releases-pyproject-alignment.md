# Publish grok-install-cli GitHub releases whose tag matches pyproject.toml; align grok-install-action's pin

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #7 (`audits/99-recommendations.md`)
- **Target repos (2)**: AgentMindCloud/grok-install-cli *(primary — owns the release)*; AgentMindCloud/grok-install-action *(cross-ref follow-up after primary merges — pin alignment)*
- **Filing strategy**: primary in `grok-install-cli` (release-cut semantics live here). A short pointer issue in `grok-install-action` links to this primary once the release ships, tracking the action's `cli-version` input bump. Do NOT file the pointer before the primary merges — the pin's target form (PyPI tag vs. npm tag vs. both) depends on which of §2 #6's three acceptance options wins.
- **Risks closed**: VER-3 (S1) — same S1 as #6, different layer. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 03 §9 row 1]`. Supporting evidence in `audits/03-grok-install-cli.md §1, §4, §11 row 2` (pyproject.toml at `0.1.0`, no releases tagged) and `audits/04-grok-install-action.md §1, §6` (action's `cli-version` default `2.14.0` pin).
- **Effort (§2)**: S — release cut is small; the cross-repo pin bump is small; the interpretation cost (which of #6's three options is canonical) is what kept this from being instant.
- **Blocked by (§2)**: #6 — the CLI install mechanism must be resolved before a release can be cut against a canonical distribution channel. Whether that channel is PyPI, npm, or both determines the release pipeline's shape.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/06-cli-install-mechanism.md`](06-cli-install-mechanism.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft's §Acceptance Part B if the prerequisite issue (§2 #6) is substantively rewritten during upstream review. #6 ships three acceptance options (A: Python is canonical, B: npm wrapper is canonical, C: both are canonical); this draft's Part B enumerates the release-pipeline + pin-alignment behaviour under each, so #6's outcome determines which branch of this draft applies. If #6 lands a materially different option (e.g. a fourth path, or declines all three), rewrite Part B entirely.

- **Suggested labels**: `release`, `version-coherence`, `packaging`, `S1`, `phase-1b`

---
