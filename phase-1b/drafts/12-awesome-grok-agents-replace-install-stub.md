# Replace grok_install_stub with a real grok-install-cli invocation in validate-templates.yml

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #12 (`audits/99-recommendations.md`)
- **Target repos (2)**: AgentMindCloud/awesome-grok-agents *(primary — owns `scripts/grok_install_stub/` and the CI that uses it)*; AgentMindCloud/grok-install-cli *(consumed; no code changes expected in this repo, but flag for awareness)*
- **Filing strategy**: single primary issue in `awesome-grok-agents`. No cross-ref filing needed — `grok-install-cli` is consumed, not modified.
- **Risks closed**: partial UNV-4 (S3) — from `audits/98-risk-register.md`. Full UNV-4 closure also requires §2 #1 (shared `grok-safety-rules` package) landing, so the stub's safety-logic duplication is removed at the source. This draft closes UNV-4 only at the *validation-surface* layer (awesome-grok-agents CI validates against the real CLI, so stub ↔ CLI divergence is detected).
- **Source audits**: `[→ 06 §9 row 2]`. Supporting: `audits/06-awesome-grok-agents.md §5, §7` (stub-based validation + `scripts/grok_install_stub/` existence), `audits/03-grok-install-cli.md §3, §6` (CLI's own safety implementation that the stub mirrors).
- **Effort (§2)**: S — replace one workflow step + a small amount of scaffolding. The wait (for #6 + #7) is the reason this sits in the Session-2 list.
- **Blocked by (§2)**: #6, #7 — needs a working install path (#6's resolution) AND a tagged release (#7's first release) to pin against.

### Speculative-draft discipline (mandatory — this draft is Session 2, deepest speculation)

- **Prerequisite status**: depends on **two** in-repo drafts — [`phase-1b/drafts/06-cli-install-mechanism.md`](06-cli-install-mechanism.md) and [`phase-1b/drafts/07-grok-install-cli-releases-pyproject-alignment.md`](07-grok-install-cli-releases-pyproject-alignment.md). Neither is filed upstream; #7 is itself speculative-on-#6. Speculative.
- **Re-review trigger**: rewrite this draft's §Acceptance Part A if either prerequisite is substantively rewritten during upstream review. Specifically: #6's three-way choice (Python canonical / npm canonical / both canonical) determines the install command in the workflow; #7's first-release version (A1 `0.1.0` vs. A2 `2.14.0`) determines the pin string. Until both prerequisites merge upstream, treat Part A's command+pin as *representative*, not final.

- **Suggested labels**: `ci`, `validation`, `tooling`, `phase-1b`

---
