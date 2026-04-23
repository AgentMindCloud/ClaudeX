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

## Acceptance criteria

Two parts. Part A is the stub replacement in the workflow. Part B
adds a conformance-check matrix once the rubric (§2 #5) lands.
Part A closes the issue's headline ask; Part B is a natural
follow-up that the same PR may or may not include depending on
§2 #5's merge timing.

### Part A — Replace `grok_install_stub` with the real CLI

Land a single PR that edits
`.github/workflows/validate-templates.yml` +
`scripts/validate_template.py` + `scripts/scan_template.py` +
`scripts/mock_run_template.py` to consume the real
`grok-install-cli` instead of the in-repo stub.

- [ ] **Install the real CLI at workflow start.** Replace the
      implicit `PYTHONPATH` / `sys.path` setup that pulls
      `grok_install_stub` with an explicit install step. The
      exact command depends on which of §2 #6's options landed:
      - If §6 Option A (Python canonical):
        ```yaml
        - uses: actions/setup-python@<SHA>  # v5
          with: { python-version: '3.12' }
        - run: pip install "grok-install==<pin-from-#7>"
        ```
      - If §6 Option B (npm canonical): `npm install -g
        grok-install-cli@<pin-from-#7>`.
      - If §6 Option C (both): pick one path explicitly and
        document the choice in a workflow comment.

      Until #6 merges upstream, this draft treats Option A as
      the *default* example (matches the recommended path in
      #6's draft). Swap at PR time if needed.

- [ ] **Rewrite `validate_template.py` as a thin wrapper** over
      `grok-install validate <path>`. The Typer CLI's exit
      code + stdout become the workflow signal. Drop all logic
      that re-implements validation; the script's job is now
      (a) discover templates, (b) invoke the CLI, (c) format
      output for the matrix job.

- [ ] **Rewrite `scan_template.py`** similarly: thin wrapper
      over `grok-install scan <path>`. Preserve the
      "fail-on-warnings" posture by passing `--strict` (or
      whichever flag the real CLI exposes per §2 #6's
      outcome).

- [ ] **Rewrite `mock_run_template.py`** over `grok-install run
      --dry-run <path>` (or the equivalent subcommand — CLI's
      real surface is `init` / `validate` / `scan` / `run` /
      `deploy` per audit 03 §8).

- [ ] **Delete `scripts/grok_install_stub/`** and its tests.
      The stub existed only because the real CLI had no
      install path; once the real CLI is the source of truth,
      the stub is dead code. Removing it in the same PR keeps
      the repo honest about what's being exercised.

- [ ] **Update `CONTRIBUTING.md`** (and `README.md` if it
      references the stub) to point at the real CLI. Template
      authors now need `pip install grok-install` (or the
      chosen channel) locally to run
      `python scripts/validate_template.py` — flag this as
      onboarding friction and mitigate with a Makefile target
      (`make setup`) that installs the CLI at the pinned
      version.

- [ ] **CHANGELOG** entry under `[Unreleased]` documenting the
      stub removal + real-CLI adoption + the pinned version.

- [ ] **Sanity check**: all 10 templates still pass the rewired
      workflow. If any template passed under the stub but
      fails under the real CLI, that is exactly the drift this
      rec was meant to surface — fix the template (or the
      CLI, if the CLI's behaviour turns out to be wrong), don't
      paper over it with a stub revival.

### Part B — Add rubric-conformance matrix (once §2 #5 lands)

Optional companion: once the safety-profile rubric from §2 #5
ships in `grok-yaml-standards` with the reference validator
(`tools/check_profile_conformance.py`), add a new `conformance`
job that exercises each template against its declared
`safety_profile`.

- [ ] **Add a `conformance` matrix job** to
      `validate-templates.yml`. One row per template; each row
      runs:
      ```
      check_profile_conformance \
          --rubric <mirrored rubric values JSON from grok-yaml-standards> \
          --claim templates/<name>/grok-install.yaml
      ```
      Exit code 0 ⇒ conformant; 1 ⇒ violations; 2 ⇒
      over-conformant (logged, non-fatal); 3 ⇒ schema error
      (fatal).

- [ ] **Fetch the rubric values from `grok-yaml-standards`**
      (the §2 #5 draft publishes
      `schemas/safety-profile-rubric-v1.values.json` at repo
      root). Use the same "pull latest on schedule" pattern
      §2 #16's Part B uses for its schema fetch. Pin to a
      specific version tag (e.g. `v1.3.0`) to avoid surprise
      regressions when upstream bumps.

- [ ] **Update `featured-agents.json` registry** only if Part A's
      stub replacement surfaces a drift between a template's
      declared profile and its behaviour. If drift is found,
      either fix the template to match the profile or update
      the profile in the registry to match observed behaviour —
      do NOT downgrade silently.

- [ ] **Part B scheduling**: land Part A first. Part B can ship
      in the same PR if §2 #5 is already merged upstream at
      write time; otherwise Part B is a follow-up issue/PR once
      §2 #5 merges.

- [ ] **Close linkage to §2 #1**: once this draft's Part A + §2
      #1 both land, the ecosystem has no parallel safety
      implementations inside awesome-grok-agents — the real
      CLI is the source, `grok-safety-rules` is the shared
      library the CLI consumes. UNV-4 closes fully at that
      point.
