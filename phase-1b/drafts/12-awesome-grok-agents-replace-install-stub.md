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

## Evidence

From `main` snapshot on 2026-04-23 (WebFetch; paths stable).

**`awesome-grok-agents` CI state** —
`audits/06-awesome-grok-agents.md §5, §11 row 5`:
- `.github/workflows/validate-templates.yml` has 7 jobs:
  `discover`, `yamllint`, `registry`, `schema`, `spec-version`,
  `links`, `validate` (matrix).
- The `validate` matrix step runs, per template:
  `validate_template.py` + `scan_template.py` + `mock_run_template.py`.
- `scan_template.py` **fails on warnings** (strictest signal
  in the ecosystem).
- Python 3.12, Node 20, `ajv-cli@5 + ajv-formats@3`, lychee.
- `scripts/grok_install_stub/` is explicitly audited as the
  stub that `validate_template.py` + `scan_template.py` + `mock_run_template.py`
  consume (see audit 06 §5 "Stub-based validation" caveat).

**Tradeoff audit captured at audit time** —
`audits/06-awesome-grok-agents.md §5` (verbatim):
- *"Stub-based validation: the `grok_install_stub` package in
  `scripts/` means templates are not validated against the
  actual CLI; drift between stub and real CLI goes undetected
  here (tradeoff noted)."*

**Risk register** — `audits/98-risk-register.md`:
- **UNV-4** (S3, L-med, `needs-info`): "Whether `grok-install-cli`'s
  safety rules are a re-implementation of the `grok-yaml-standards/
  grok-security` schema or a divergent ruleset is not stated —
  risks two safety surfaces drifting apart unobserved."
- The stub is a *third* parallel safety implementation
  (alongside `grok-install-cli/safety/rules.py` and
  `grok-build-bridge/_patterns.py`). §2 #1 addresses the
  underlying three-way drift; §2 #12 removes one of the three
  by making the stub consume the real CLI instead of
  re-implementing its behaviour.

**Open questions from audit** —
`audits/06-awesome-grok-agents.md §10`:
- "What does `grok_install_stub/` implement (enough of the CLI
  surface to be meaningful)?" — answered implicitly once the
  stub is removed.
- "Does `scan_template.py` reuse logic from `grok-install-cli/
  src/grok_install/safety/scanner.py`, or is it a parallel
  implementation?" — answered definitively post-migration:
  `scan_template.py` becomes a thin wrapper around `grok-install
  scan`.

**Prerequisite state**:
- §2 #6 draft: [`phase-1b/drafts/06-cli-install-mechanism.md`](06-cli-install-mechanism.md)
  — three acceptance options, none merged upstream at this
  writing.
- §2 #7 draft: [`phase-1b/drafts/07-grok-install-cli-releases-pyproject-alignment.md`](07-grok-install-cli-releases-pyproject-alignment.md)
  — release pipeline + action-pin alignment. Itself speculative
  on #6. Not merged upstream at this writing.

**Related §2 cross-refs**:
- §2 #1 (shared `grok-safety-rules` package) — the stub, the
  CLI's `rules.py`, and the bridge's `_patterns.py` are the
  three parallel implementations #1 extracts. #12 is the
  predecessor: remove the stub before extraction, so the
  extraction works on two parallel implementations rather than
  three.
- §2 #5 (safety-profile rubric) — once shipped, the real CLI's
  behaviour under `scan` is disciplined by the rubric; the
  stub's behaviour is not. Replacing the stub with the real CLI
  means the gallery inherits rubric-disciplined validation for
  free.
