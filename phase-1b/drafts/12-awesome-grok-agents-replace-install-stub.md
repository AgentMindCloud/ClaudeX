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

## Context

`awesome-grok-agents`'s `validate-templates.yml` workflow has the
strictest matrix-validation posture in the ecosystem: 7 jobs,
fails on warnings, matrix over all 10 templates. The one hole:
the `validate` matrix uses a locally-vendored `grok_install_stub`
package in `scripts/` rather than the real `grok-install-cli`.

The stub's purpose at repo-creation time was reasonable —
`grok-install-cli` had no PyPI presence, no tagged release, no
npm package that resolves cleanly. Rather than let CI depend on a
broken install path, the stub replicated just enough of the CLI
interface to exercise the templates locally.

The cost of the stub pattern is that stub ↔ real-CLI divergence
is *undetectable* by this repo's CI. A template that passes
`validate_template.py` against the stub may still fail at install
time via the real CLI, because:

- The stub's safety rules may be stricter, looser, or simply
  different from `grok-install-cli/src/grok_install/safety/`
  (UNV-4 in the risk register).
- The stub's schema interpretation may drift from
  `grok-yaml-standards`' schemas if either repo updates in ways
  the stub doesn't track.
- The stub's subcommand surface (`init` / `validate` / `scan` /
  `run` / `deploy`) may diverge from the real CLI's over time.

Replacing the stub with the real CLI closes all three at once —
the CLI *is* the source of truth, so its behaviour is what the
templates validate against.

The catch that kept this rec blocked: until §2 #6 picks an
install channel (Python / npm / both) and §2 #7 cuts a tagged
release on that channel, there is nothing stable to pin against.
Once both merge upstream, this rec becomes a small workflow
edit.
