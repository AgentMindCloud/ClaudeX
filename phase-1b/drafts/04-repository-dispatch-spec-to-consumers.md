# Wire repository_dispatch from grok-install → grok-docs, grok-install-action, grok-agents-marketplace

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #4 (`audits/99-recommendations.md`)
- **Target repos (4)**: AgentMindCloud/grok-install *(primary — owns the publisher workflow)*; AgentMindCloud/grok-docs, AgentMindCloud/grok-install-action, AgentMindCloud/grok-agents-marketplace *(subscribers — one short cross-ref issue each after the primary merges)*.
- **Filing strategy**: primary in `grok-install`. Three subscriber cross-ref issues opened **after** the primary merges — each installs its own `repository_dispatch` listener workflow. Pattern mirrors §2 #18's "coordination-issue + per-adopter follow-up" structure.
- **Risks closed**: VER-4 **trigger** (dispatch closes the 24h drift window to seconds; the docs-content side of VER-4 is closed by §2 #10); partial DOC-1 (cross-repo standards-count coherence updates fan out automatically after this lands).
- **Source audits**: `[→ 00 §9.E]` *(verbatim: "No release-dispatch between spec and consumers")*. Supporting: `audits/05-grok-docs.md §5, §11 row 4` (current daily cron at 03:00 UTC); `audits/04-grok-install-action.md §6` (hard-coded `cli-version` default); `audits/08-grok-agents-marketplace.md §8` (no dispatch from spec updates).
- **Effort (§2)**: M — ~15 lines per repo per §9.E, but four repos + three subscriber cross-refs + secret/token coordination is what makes this M rather than S.
- **Blocked by (§2)**: #10 — v2.14 content must exist in `grok-docs` before the dispatch is wired, else the dispatched event fires into an empty target. §2 #10 is drafted in this repo as of the fourth pass; this draft is speculative-on-#10 until #10 merges upstream.

### Speculative-draft discipline (mandatory — gated on in-repo prerequisite)

- **Prerequisite status**: drafted in [`phase-1b/drafts/10-grok-docs-v2-14-plus-7-standards-reference.md`](10-grok-docs-v2-14-plus-7-standards-reference.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft's §Acceptance Part B (subscriber workflow in `grok-docs`) if #10's Part C (publication layer — nav + version banner + Mike archive) is substantively changed during upstream review. Specifically: if §10's `docs/assets/schemas/latest/VERSION` convention is renamed, moved, or replaced, Part B's subscriber workflow in `grok-docs` changes its trigger path. Parts A (publisher) and B's subscriber workflows in `grok-install-action` and `grok-agents-marketplace` are unaffected by #10's internals.

- **Suggested labels**: `ci`, `automation`, `version-coherence`, `ecosystem`, `phase-1b`

---

## Context

When `grok-install` cuts a new spec version (e.g. v2.13 →
v2.14), three downstream repos need to notice:

- **`grok-docs`** — republish the schemas + refresh content.
  Currently relies on a daily cron (`sync-schemas.yml` at
  03:00 UTC); up to 24h drift after a release.
- **`grok-install-action`** — bump the `cli-version` default
  and the "validates spec v2.X" claim in the README.
  Currently does neither automatically; pin is a hard-coded
  default.
- **`grok-agents-marketplace`** — validate that the submission
  form's accepted spec versions still include the new one, and
  render any new `grok-install.yaml` fields (e.g. v2.14's
  `visuals:` block). Currently has no dispatch from
  `grok-install` at all.

The cumulative effect is observable: on 2026-04-23, the docs
site still advertised v2.12 while the spec had shipped v2.14
two releases earlier (VER-4). Part of that gap is the content
itself (§2 #10 closes it); the other part is the *trigger* —
there is no automated signal telling consumers a new release
landed.

The fix is a standard GitHub pattern: `repository_dispatch`
from the source-of-truth repo (`grok-install` — whichever
workflow cuts the release) → a per-consumer listener workflow
in each of the three downstream repos. The dispatched payload
carries the version string; the listener decides what to do
(rebuild docs, bump a pin, re-validate accepted spec versions).

The design constraint that keeps this as M-effort: each
consumer's listener does slightly different work, so the
"dispatch event" contract has to be uniform enough for all
three while leaving subscriber logic per-repo. The issue
below specifies the contract explicitly (Part A) before each
subscriber implements its listener (Part B).

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**Current state of spec → consumer synchronisation** — sourced
verbatim from `audits/00-ecosystem-overview.md §9.E`:

> "The current sync model for spec→consumer is daily cron
> (`grok-docs/sync-schemas.yml` at 03:00 UTC). This creates up
> to a **24-hour drift window** on every spec release.
> `awesome-grok-agents` does not auto-validate against a new
> spec version; `grok-agents-marketplace` has no dispatch from
> `featured-agents.json` updates. `grok-install-action` pins
> `cli-version` as a hard-coded default.
>
> The fix is a `repository_dispatch` from `grok-install`'s
> release workflow to each downstream repo — a ~15-line
> addition per repo that closes drift from hours to seconds."

**Current workflows that would gain a dispatch step** —
`audits/01-grok-install.md §5`:
- `grok-install/.github/workflows/validate.yml` (validation-
  only; not a release workflow).
- A dedicated release/publish workflow: not enumerated in the
  Phase-1A probe. If it exists, the dispatch step adds ~15
  lines. If it does not, this rec's Part A creates one.
  Flag for reviewer confirmation during PR review.

**Current consumer-side entry points (where listeners land)**:

- **`grok-docs`** — `audits/05-grok-docs.md §5, §11 row 4`:
  `.github/workflows/sync-schemas.yml` exists. Listener can
  either extend it (add a `repository_dispatch` trigger
  alongside the existing `schedule` + `workflow_dispatch`) or
  ship as a sibling workflow. Either works.
- **`grok-install-action`** —
  `audits/04-grok-install-action.md §5, §6`: CI workflows
  exist (`test.yml`, `release.yml`); no spec-sync listener
  today. New file: `.github/workflows/spec-dispatch.yml`.
- **`grok-agents-marketplace`** —
  `audits/08-grok-agents-marketplace.md §5`: 3 workflows
  (`ci.yml`, `dependency-review.yml`, `lighthouse.yml`); no
  spec-sync listener. New file:
  `.github/workflows/spec-dispatch.yml`.

**Risk register** — `audits/98-risk-register.md`:
- **VER-4** (S2, L-high, `open`): "`grok-docs` advertises spec
  **v2.12**; current spec is **v2.14**. Two-minor-version lag
  in the canonical documentation site." *(The trigger half
  closes with this rec; the content half closes with §2 #10.)*
- **DOC-1** (S2, L-high, `open` — implied from audit 00 §7.1):
  "14/12/5 standards-count drift across surfaces." *(Partially
  closed by this rec — consumer-side number claims that depend
  on spec version can rebuild automatically on dispatch. The
  hard-coded '14 standards' / '5 file types' prose changes
  covered by §2 #14a/#14b + §2 #10 are a separate axis.)*

**Prerequisite state**:
- §2 #10 draft: [`phase-1b/drafts/10-grok-docs-v2-14-plus-7-standards-reference.md`](10-grok-docs-v2-14-plus-7-standards-reference.md)
  — ships v2.14 content + 7 reference pages + publication
  layer. Not filed upstream.

**Related §2 cross-refs**:
- §2 #10 — the prerequisite. Without v2.14 content, the
  dispatch fires into an empty target.
- §2 #3 (SHA-pin actions) — applies to all four repos'
  workflow files touched by this rec. Keep SHA-pinning as a
  separate concern; don't bundle.
- §2 #7 (grok-install-cli tagged releases) — §7's first tagged
  release is *itself* a release event that could fire this
  dispatch. Good reason to ship §2 #7 first if possible, but
  not required — the dispatch can be wired against the
  `grok-install` spec-repo's releases independently of §7's
  CLI releases.
- §2 #14a/#14b — prose-level "14 → 12 standards" fixes stand
  alone; dispatch does not force their adoption.

## Acceptance criteria

Two parts. Part A lands in `grok-install` (the publisher).
Part B lands as three short follow-up issues / PRs in each
subscriber. The issue closes when Part A merges and all three
subscriber workflows respond to a test dispatch (verified via
`gh api repos/.../dispatches` from a maintainer's machine, or
by cutting a dry-run release tag).

### Part A — Publisher workflow in `grok-install`

The publisher side is a single workflow file (or a ~15-line
addition to whatever release workflow exists) that fires a
`repository_dispatch` event at each of the three subscriber
repos whenever a new spec version ships.

- [ ] **Confirm publisher trigger.** The dispatch should fire
      when a new spec version is *released*, not on every
      push. Two honest options:
      - **A1 — on GitHub release publish**: use
        `on: release: types: [published]`. Cleanest if
        `grok-install` already cuts GitHub releases (confirm
        from repo `releases` page; Phase 1A did not record
        this).
      - **A2 — on tag push matching a spec-version pattern**:
        use `on: push: tags: ['v[0-9]+.[0-9]+']`. Works if
        releases are cut as tags without GitHub Release pages.

      Default recommendation: **A1**. GitHub Releases already
      carry human-readable release notes; their "published"
      event is the canonical ecosystem-wide signal. If
      `grok-install` doesn't cut GitHub Releases today, adding
      them is a one-time setup — worth the 10 minutes.

- [ ] **Add `.github/workflows/fan-out-spec-release.yml`**
      (name is a suggestion — match existing naming conventions
      in the repo):

      ```yaml
      name: Fan out spec release to downstream consumers

      on:
        release:
          types: [published]
        workflow_dispatch:
          inputs:
            version:
              description: 'Version string to dispatch (e.g. v2.14)'
              required: true
              type: string

      permissions:
        contents: read

      jobs:
        dispatch:
          runs-on: ubuntu-latest
          strategy:
            fail-fast: false
            matrix:
              target:
                - { owner: AgentMindCloud, repo: grok-docs }
                - { owner: AgentMindCloud, repo: grok-install-action }
                - { owner: AgentMindCloud, repo: grok-agents-marketplace }
          steps:
            - name: Fire repository_dispatch
              env:
                GH_PAT: ${{ secrets.FANOUT_DISPATCH_PAT }}
                VERSION: ${{ github.event.release.tag_name || inputs.version }}
              run: |
                curl -sS -X POST \
                  -H "Accept: application/vnd.github+json" \
                  -H "Authorization: Bearer ${GH_PAT}" \
                  -H "X-GitHub-Api-Version: 2022-11-28" \
                  "https://api.github.com/repos/${{ matrix.target.owner }}/${{ matrix.target.repo }}/dispatches" \
                  -d "{\"event_type\":\"grok-install-release\",\"client_payload\":{\"version\":\"${VERSION}\",\"source_repo\":\"${{ github.repository }}\",\"release_url\":\"${{ github.event.release.html_url }}\"}}"
      ```

- [ ] **Define the dispatch-event contract** (put this in a
      `CONTRIBUTING.md` subsection or a new
      `docs/ci-dispatch.md` in `grok-install`):

      - **Event type**: `grok-install-release`.
      - **Client payload shape**:
        ```json
        {
          "version": "v2.14",
          "source_repo": "AgentMindCloud/grok-install",
          "release_url": "https://github.com/AgentMindCloud/grok-install/releases/tag/v2.14"
        }
        ```
      - **Payload stability**: additive-only. Subscribers may
        rely on `version`, `source_repo`, `release_url`
        existing on every event. New fields may be added; no
        field will be renamed or removed without a new
        `event_type` (e.g. `grok-install-release-v2`).
      - **Retry semantics**: publisher retries are out of
        scope. If a subscriber misses a dispatch (e.g. secret
        expired), the subscriber's daily cron (where it
        exists) is the safety net. The dispatch closes the
        drift window in the happy path, not in every failure
        mode.

- [ ] **PAT / token strategy**: `repository_dispatch` from one
      repo to another requires a token with `repo` scope on
      the target repo (org-owned fine-grained PAT or a GitHub
      App). Maintainer one-time setup:
      1. Generate a fine-grained PAT (or install a GitHub App)
         scoped to the three subscriber repos only,
         `repo → contents: read, metadata: read`.
      2. Add as `FANOUT_DISPATCH_PAT` secret on
         `grok-install`.
      3. Do NOT use the default `GITHUB_TOKEN` — it has no
         permission to dispatch to sibling repos.

- [ ] **Dry-run validation**: with the workflow in place,
      trigger `workflow_dispatch` manually with
      `version: v2.14-test`. All three subscriber workflows
      (once Part B lands) receive the event and log it
      without doing destructive work (each subscriber Part B
      spells out a `dry-run` branch that's safe to exercise).

- [ ] **CHANGELOG** entry on `grok-install` under
      `[Unreleased]`: "Added fan-out release-dispatch to
      grok-docs / grok-install-action / grok-agents-marketplace.
      Subscribers wire their listeners per §2 #4 Part B
      follow-ups."

- [ ] **README cross-link** (one line near the top, under the
      "contributing" or "workflow" section):
      *"Spec releases fan out to downstream repos via
      `repository_dispatch`; see `docs/ci-dispatch.md`."*
