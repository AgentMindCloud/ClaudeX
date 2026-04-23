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

## Context

`grok-install-cli`'s `pyproject.toml` declares `name = "grok-install"`
at version `0.1.0`. No GitHub releases are tagged on the repo at
audit time (2026-04-23). Meanwhile, `grok-install-action`'s
`action.yml` pins `cli-version: 2.14.0` and invokes the CLI as an
npm package. The resulting state: the action's `2.14.0` pin has no
corresponding artefact in the CLI's source tree — there is no tag,
no release, no PyPI publication at `2.14.0` traceable to this
repo.

§2 #6 (the prerequisite) reconciles *which install channel is
canonical* — PyPI, npm, or both. This issue (§2 #7) is the next
layer: once the channel is settled, publish proper GitHub releases
whose tag matches a version that actually ships to that channel,
and update the action's pin to match.

The split between #6 and #7 is deliberate:

- #6 is about **which wire format** the CLI is distributed in.
- #7 is about **version coherence** between the CLI's source tree,
  its published release artefacts, and any consumer that pins
  against it.

Both must land to close VER-3, but they close different sides of
it: #6 closes the "install doesn't resolve" side; #7 closes the
"the pin has no corresponding artefact" side.

Secondary benefit: publishing proper GitHub releases gives this
repo a visible release cadence (other ecosystem repos have 1–3;
this one has zero), which itself signals that the CLI is
maintained rather than abandoned. For a repo downstream adopters
pin against on every CI run, release visibility matters.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**`grok-install-cli` repo state** —
`audits/03-grok-install-cli.md §1, §11 rows 1–2`:
- `pyproject.toml` declares `name = "grok-install"`,
  `version = "0.1.0"`, entry point `grok_install.cli:app`
  (Typer). Python ≥ 3.10. Ruff + pytest.
- **No GitHub releases tagged** at audit time.
- Package is a pure-Python project. No `package.json`, no
  `setup.py`, no npm tarball shipped from the repo.
- 3 CI workflows: `ci.yml`, `publish.yml`, `security.yml`.
  `publish.yml` implies a release pipeline exists, but no
  release artefacts correspond to it yet.

**`grok-install-action` pin** —
`audits/04-grok-install-action.md §1, §6`:
- `action.yml` default: `cli-version: 2.14.0`.
- Install command (today): `npm install -g grok-install-cli@2.14.0`
  via `actions/setup-node@v4`.
- The `2.14.0` value has no corresponding release tag on
  `grok-install-cli/releases`. Any resolution path hides a
  supply-chain fragility.

**Risk register** — `audits/98-risk-register.md`:
- **VER-3** (S1, L-high, `open`): "`grok-install-cli`
  `pyproject.toml` is at `0.1.0` and is a Python project;
  `grok-install-action` pins it via
  `npm install -g grok-install-cli@2.14.0`. Either the action
  installs an unrelated npm package, or the documented install
  path does not actually work." *(Same row covers #6 and #7 —
  both close different faces of it.)*
- **SUP-4** (S2, L-med, `open`): the `2.14.0` pin is not
  lockfile-guarded. Partially closed by whichever of #6's
  options wins; fully closed by §2 #3's Renovate /
  Dependabot config landing on the action.

**§2 #6 cross-refs** — the three acceptance options in
[`phase-1b/drafts/06-cli-install-mechanism.md`](06-cli-install-mechanism.md)
give concrete shape to Part B below:
- **Option A (Python canonical)**: `grok-install-action`
  switches to `pip install "grok-install==<version>"`; the
  version here matches PyPI + this repo's tagged release.
- **Option B (npm wrapper canonical)**: an npm package exists
  that wraps the Python CLI; its published versions match this
  repo's tagged releases.
- **Option C (both canonical)**: PyPI and npm publish lockstep;
  a single source of truth (e.g. a `VERSION` file) drives both.

**Intended post-merge state** for `grok-install-cli`:
`pyproject.toml` and the latest GitHub release tag both carry
the same version string (`vX.Y.Z` or `X.Y.Z`), and
`grok-install-action/action.yml`'s `cli-version` default
resolves to that exact artefact on the canonical channel.

**Related §2 cross-refs**:
- §2 #3 (SHA-pin actions + Renovate) — closes SUP-4 at the
  action-pin layer once landed.
- §2 #12 (replace `awesome-grok-agents`'s `grok_install_stub`)
  — needs a working install path (§6) **and** a tagged release
  (§7) to pin against. §12 is this draft's immediate downstream.
