# Resolve the npm-vs-Python mismatch in the grok-install-cli install path

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #6 (`audits/99-recommendations.md`)
- **Target repo**: AgentMindCloud/grok-install-cli *(primary — file here by default)*
  - Cross-reference from: AgentMindCloud/grok-install-action (a short pointer issue against the action repo after this one is filed, so adopters on either side land on the same thread)
  - If the maintainer of grok-install-action prefers to own the reconciliation, swap primary/cross-ref — the body below is written to stand as-is in either repo
- **Risks closed**: VER-3 (S1), UNV-1 (S1) — both from `audits/98-risk-register.md`
- **Source audits**: `[→ 03 §1]`, `[→ 03 §9 row 1]`, `[→ 03 §10]`, `[→ 04 §1]`, `[→ 04 §9 row 1]`, `[→ 04 §10]`
- **Blocked by**: none
- **Unblocks**: §2 #7 (release tags that match `pyproject.toml`), §2 #12 (replace `grok_install_stub` with a real CLI invocation)
- **Suggested labels**: `bug`, `version-coherence`, `ecosystem`, `S1`, `phase-1b`

---

## Context

The install path advertised by `grok-install-action` and the packaging of
`grok-install-cli` do not line up:

- `grok-install-action/action.yml` installs the CLI with
  `npm install -g grok-install-cli@${{ inputs.cli-version }}` (default
  `2.14.0`) via `actions/setup-node@v4`.
- `grok-install-cli` is a pure-Python project: `pyproject.toml` declares
  `name = "grok-install"` at version `0.1.0`, entry point
  `grok_install.cli:app` (Typer), Python ≥ 3.10, ruff/pytest. There is
  no `package.json`, no npm tarball shipped from the repo, and no
  GitHub release tagged at the time this issue was drafted.

Two cascading problems fall out of that:

1. **Install may not resolve at all**, or may resolve to an unrelated
   npm package squatting the `grok-install-cli` name. An adopter
   following the documented quick-start cannot tell which of those
   they are hitting.
2. **The `2.14.0` pin has no corresponding artefact** in the source
   repo (latest `pyproject.toml` version is `0.1.0`; no release tags).
   Even if an npm tarball exists somewhere, its provenance chain back
   to this source tree cannot be verified.

The secondary effect is a credibility hit across the ecosystem:
`grok-install-action` is the GitHub-native "certification" surface for
Grok adopters, and its headline install command fails a trivial
provenance check.

## Evidence

All references point at `main` snapshots as of 2026-04-23; line numbers
omitted because the audit was performed via WebFetch, not clone.

- `grok-install-cli` landing + `pyproject.toml`: project name
  `grok-install`, version `0.1.0`, no releases tagged. Layout under
  `src/grok_install/` with `cli.py` (Typer), `core/`, `deploy/`,
  `integrations/`, `runtime/`, `safety/`. *(source: audit 03 §1, §2,
  evidence rows 1–2.)*
- `grok-install-action/action.yml`: composite action, `runs.using:
  composite`, `setup-node@v4` + `npm install -g
  grok-install-cli@${{ inputs.cli-version }}` (default `2.14.0`).
  *(source: audit 04 §1, §3, evidence rows 1–2.)*
- `grok-install-action` README: advertises the same install command
  in the quick-start. *(source: audit 04 §1.)*
- Risk register — `98-risk-register.md`:
  - **VER-3** (S1, likelihood high): "`grok-install-cli` `pyproject.toml`
    is at `0.1.0` and is a Python project; `grok-install-action` pins
    it via `npm install -g grok-install-cli@2.14.0`. Either the action
    installs an unrelated npm package, or the documented install path
    does not actually work."
  - **UNV-1** (S1, likelihood high, status `needs-info`): "The
    advertised install path … does not match the underlying CLI's
    packaging. Without cloning and running both, the audit cannot
    confirm whether the action installs the documented tool."

## Reproduction

From a clean checkout of `grok-install-action` on a standard
GitHub-hosted runner:

```
# What action.yml currently does
npm install -g grok-install-cli@2.14.0
grok-install --help
```

Expected: a Typer CLI whose subcommands match the README of
`grok-install-cli` (`init`, `validate`, `scan`, `run`, `deploy`).

Observed (to be confirmed in-thread by a maintainer with npm-registry
access): either the install fails, resolves to an unrelated package,
or succeeds for a reason not traceable from the `grok-install-cli`
source tree.

A maintainer can verify in under two minutes: `npm view
grok-install-cli` against the live npm registry, then compare the
resulting tarball's `bin`/`main` to `src/grok_install/cli.py` in this
repo.

## Acceptance criteria

The reconciliation can go three ways; this issue is resolved when
**one** of (A), (B), (C) is chosen and documented.

### Option A — Python is canonical (recommended if the source is authoritative)

- [ ] `grok-install-action/action.yml` replaces the npm install with
      `pip install "grok-install==<version>"` (or `pipx install`),
      dropping `setup-node@v4` in favour of `setup-python@v5`.
- [ ] The `cli-version` input's default is updated to a version that
      actually exists on PyPI and corresponds to a tagged release of
      this repo (addressed in §2 #7).
- [ ] `grok-install-action` README quick-start and
      `workflows-examples/` updated to match.
- [ ] `grok-install-cli` README adds a single-line "Install" section
      citing the PyPI command.
- [ ] A migration note lands in `grok-install-action/CHANGELOG.md`
      under `[Unreleased]`.

### Option B — npm wrapper is canonical

- [ ] The npm package `grok-install-cli` exists, is owned by
      AgentMindCloud, and wraps the Python CLI (e.g. via `pip install`
      in a postinstall script, or via a native JS rewrite).
- [ ] Its source tree is either in this repo or in a clearly linked
      sibling repo; its README cross-links to `grok-install-cli`
      (Python) if the wrapper is thin.
- [ ] The npm package's published versions match this repo's release
      tags (addressed in §2 #7).
- [ ] This repo's README "Install" section documents both `pip` and
      `npm` paths, flagging which is canonical.

### Option C — both paths are canonical

- [ ] `pyproject.toml` version and `package.json` version are kept in
      lockstep via a single source of truth (e.g. a `VERSION` file
      consumed by both).
- [ ] CI publishes both artefacts from the same tag, and the tag
      matches the version.
- [ ] `grok-install-action/action.yml` picks **one** path explicitly
      and documents why (e.g. "action uses npm to avoid a Python
      toolchain dependency on the runner"). A `cli-language` input
      can be added if both paths must be first-class, but this is not
      required to close the issue.

Whichever option is chosen, the `cli-version` input of
`grok-install-action` must be updated to a version that the chosen
package registry can actually resolve.

## Notes

- §2 #7 (publish proper GitHub releases whose tag matches
  `pyproject.toml`) depends on this issue resolving; filing #7 before
  this is settled risks publishing releases against whichever install
  path is later deprecated.
- §2 #12 (replace `awesome-grok-agents`'s `grok_install_stub` with a
  real CLI invocation) also depends on this issue — the CI
  integration cannot point at a CLI that doesn't install.
- Secondary risk **SUP-4** (audit 98 row SUP-4, S2) — the `2.14.0`
  pin is not lockfile-guarded — is partially closed by whichever
  option is picked, and fully closed once §2 #3 (SHA-pin all actions
  + Renovate) lands.
- If the cross-reference issue against `grok-install-action` is
  preferred instead of a pointer, the body above works unchanged in
  that repo; flip primary/cross-ref in this file's metadata block.
