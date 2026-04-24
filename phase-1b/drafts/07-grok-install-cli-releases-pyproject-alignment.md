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

## Acceptance criteria

Two parts. Part A is the release pipeline and first tagged
release (local to `grok-install-cli`). Part B is the
cross-repo pin alignment on `grok-install-action`. The issue
closes when both land and a consumer can pin against a tag
that resolves to the correct artefact.

### Part A — Publish a tagged GitHub release from `grok-install-cli`

- [ ] **Pick a canonical version string** for the first release.
      Two honest options:
      - **A1 — `0.1.0`**: matches today's `pyproject.toml`; the
        first release honestly reflects the CLI's maturity.
        Downstream consumers (action, marketplace, stub)
        discover this version exists and update their pins.
      - **A2 — `2.14.0`**: matches the spec version the CLI
        implements (`grok-install` v2.14) and the action's
        current pin. Convenient for downstream inertia. Cost:
        the CLI claims to be on v2.14 even though its first
        release is bootstrap-level. Misleads on maturity.

      Default recommendation: **A1**. The ecosystem already has
      separate version axes for spec vs. implementation
      (`00-ecosystem-overview.md §3` pin matrix); aligning the
      CLI's own version to the spec's just because a consumer
      pinned wrong is the wrong fix. The consumer (the action)
      should pin to the CLI's actual version, not vice versa.

- [ ] **Update `publish.yml`** (already exists per audit 03 §11
      row 5) to cut both a **GitHub Release** and a
      **PyPI publication** on push of a tag matching
      `v[0-9]+.[0-9]+.[0-9]+`. Workflow outline:

      ```
      name: Publish
      on:
        push:
          tags: ['v[0-9]+.[0-9]+.[0-9]+']
      jobs:
        release:
          runs-on: ubuntu-latest
          permissions:
            contents: write          # create GitHub Release
            id-token: write           # PyPI Trusted Publisher
          steps:
            - uses: actions/checkout@<SHA>  # v4
            - uses: actions/setup-python@<SHA>  # v5
              with: { python-version: '3.12' }
            - run: python -m pip install --upgrade build
            - run: python -m build           # wheel + sdist
            - uses: pypa/gh-action-pypi-publish@<SHA>  # trusted publisher
            - uses: softprops/action-gh-release@<SHA>  # v2
              with:
                files: dist/*
                generate_release_notes: true
      ```

      All actions SHA-pinned per §2 #3.

- [ ] **Add PyPI Trusted Publisher configuration** (PyPI-side:
      one-time maintainer setup) so the workflow publishes
      without a long-lived `PYPI_TOKEN` secret. PyPI docs:
      https://docs.pypi.org/trusted-publishers/

- [ ] **Tag the first release**. Steps:
      1. Bump `pyproject.toml` if A2 chosen over A1.
      2. Update `CHANGELOG.md` with the new version section.
      3. `git tag -a vX.Y.Z -m "Release X.Y.Z"`.
      4. `git push origin vX.Y.Z` — triggers `publish.yml`.
      5. Verify the release appears on
         `github.com/AgentMindCloud/grok-install-cli/releases`
         AND on `pypi.org/project/grok-install/`.
      6. Verify `pip install grok-install==X.Y.Z` resolves
         from PyPI.

- [ ] **Seed `CHANGELOG.md`** with Keep-a-Changelog sections for
      v0.1.0 (or whichever version is picked). Every subsequent
      release gets its own section before tag-push. The repo
      currently has no CHANGELOG at audit time; adding one is
      part of the release hygiene.

- [ ] **Update README** with an `## Installation` section that
      matches the chosen channel. For A1 + Option A of §2 #6:
      `pip install grok-install`. Version-pin guidance
      (`grok-install>=0.1,<0.2`) inline.

- [ ] **Pin action consumers must update** deferred to Part B.

### Part B — Align `grok-install-action`'s pin (cross-repo follow-up)

This part lands in `grok-install-action`, not `grok-install-cli`.
File as a short cross-ref issue pointing at this primary's URL
**after** this primary's first release ships.

The correct action-pin form depends on which of §2 #6's three
acceptance options wins. All three possibilities are enumerated
below; pick the branch that matches the landed #6 outcome. This
draft is speculative — the actual cross-ref issue body contains
only the one branch that applies.

#### If §2 #6 Option A (Python canonical) landed

- [ ] `grok-install-action/action.yml` replaces
      `setup-node@v4` + `npm install -g grok-install-cli@${{
      inputs.cli-version }}` with:
      ```yaml
      - uses: actions/setup-python@<SHA>  # v5
        with: { python-version: '3.12' }
      - run: pip install "grok-install==${{ inputs.cli-version }}"
      ```
- [ ] `action.yml` input `cli-version`'s default is updated to
      the tag published in Part A (e.g. `0.1.0`).
- [ ] README + `workflows-examples/` in `grok-install-action`
      use the new command.
- [ ] `grok-install-action/CHANGELOG.md` gets a migration note
      under `[Unreleased]`.

#### If §2 #6 Option B (npm wrapper canonical) landed

- [ ] The npm package's published versions must match this
      repo's tagged releases (lockstep); Part A's `publish.yml`
      above adds an npm-publish step alongside the PyPI publish.
      The npm wrapper's `postinstall` shells out to `pip
      install grok-install==${{npm tag}}` — keeping source of
      truth in Python.
- [ ] `grok-install-action/action.yml` keeps `npm install -g
      grok-install-cli@${{ inputs.cli-version }}` but updates
      the default `cli-version` to the first tagged release
      (e.g. `0.1.0`).
- [ ] `grok-install-action` README updated to reflect the wrapper
      semantics.

#### If §2 #6 Option C (both canonical) landed

- [ ] PyPI and npm publish from the same `publish.yml` run;
      Part A's workflow extends to publish both with a shared
      `VERSION` file.
- [ ] `grok-install-action/action.yml` picks **one** channel
      explicitly and documents why (e.g. npm for zero-Python-
      toolchain dependency on the runner). `cli-version`
      default updated to the first tagged release.
- [ ] `grok-install-action` README documents both install paths.

#### Common to all three branches

- [ ] **Cross-ref in commit message** + linked issue comment on
      this primary when the action PR ships: "*Tracks
      <this-primary-issue-URL>; closes VER-3 at the pin layer.*"
- [ ] **SUP-4** in `98-risk-register.md` moves from `open` to
      `mitigated-partial` on this PR landing. Full `mitigated`
      once §2 #3 (Renovate / Dependabot) lands in the action
      repo — cross-ref §2 #3's primary draft.

## Notes

- **Why not skip Part A and just update the action pin?** The
  action pin is a symptom; the absence of a tagged release is
  the disease. Updating the action's default `cli-version` to
  `0.1.0` today (without the release shipping) would move the
  bug, not fix it — the pin would still resolve to nothing.

- **Why a separate issue from §2 #6?** #6 picks the install
  channel; #7 makes the picked channel coherent with the
  source. Landing them separately lets #6's option-choice
  discussion happen without the release-cut mechanics pulling
  attention. Landing them together is also fine if a maintainer
  prefers one PR with both resolved — #7's Part A is small.

- **What happens to SUP-4 after this rec.** SUP-4's "no
  lockfile guard on the `2.14.0` pin" is partially closed by
  whichever of #6's options wins (Option A's `pip install` uses
  pip's own resolver; Option B's npm install uses
  `package-lock.json` if present). Full SUP-4 closure rides on
  §2 #3 (Renovate / Dependabot) — cross-ref in Part B above.

- **Version bumping cadence going forward.** The release
  pipeline in Part A triggers on `v[0-9]+.[0-9]+.[0-9]+` tags.
  The first release's version (A1 vs. A2) sets the starting
  point; subsequent bumps are per-feature SemVer. No special
  handling required.

- **Relationship to §2 #12 (replace `grok_install_stub`).**
  §2 #12 is speculative-on-both-#6-and-#7. Once #7 ships, the
  stub replacement in `awesome-grok-agents` has a real CLI
  version to pin against. Until then, §12 cannot close.

- **Filing strategy.** Primary in `grok-install-cli`. Cross-ref
  in `grok-install-action` filed **after** the primary's first
  release ships. Do NOT pre-file the cross-ref — it depends on
  the landed #6 outcome determining which Part-B branch applies.

- **Speculative-draft honesty.** Part B enumerates three branches
  because this draft cannot know which of #6's options wins.
  The cross-ref issue filed in `grok-install-action` uses only
  one branch's content — pick the one that matches #6's landed
  resolution, delete the other two.

