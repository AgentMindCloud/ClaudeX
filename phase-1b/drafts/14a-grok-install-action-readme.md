# Align README "14 YAML specifications" with grok-yaml-standards (12)

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #14 (`audits/99-recommendations.md`) — target-repo variant A of 2
- **Target repo**: AgentMindCloud/grok-install-action
- **Sibling draft**: `phase-1b/drafts/14b-vscode-grok-yaml-landing.md` (same §2 #14, different target repo — file both; they share a canonical source)
- **Risks closed**: DOC-1 — from `audits/98-risk-register.md` (partial: closes the
  `grok-install-action` limb; fully closed when sibling 14b also lands)
- **Source audits**: `[→ 04 §1]`, `[→ 04 §4]`, `[→ 04 §7]`, `[→ 04 §9 row 2]`
- **Canonical source**: `AgentMindCloud/grok-yaml-standards/version-reconciliation.md`
- **Blocked by**: none
- **Suggested labels**: `docs`, `version-coherence`, `ecosystem`, `good-first-issue`, `phase-1b`

---

## Context

`grok-install-action`'s README advertises "validation against **14 YAML
specifications**" in its quick-start and value-prop sections. The
canonical number from the schema-root repo, `grok-yaml-standards`, is
**12** — and the discrepancy is not an omission: the `14` count was
actively declined.

`grok-yaml-standards/version-reconciliation.md` is the authoritative
record here. It:

- Enumerates the 12 standards (8 core + 4 extensions landed in v1.2.0).
- Documents why `grok-cache.yaml` and `grok-auth.yaml` were declined
  (CI complexity and forward-compat risk respectively), which is what
  a naïve "14" count would include.
- Provides ready-to-use PR language for downstream docs fixes — the
  work in this issue is a direct paste of that language into the
  README, not a fresh editorial judgement.

Practical effect of the current drift: a maintainer or adopter who
reads the README and then opens the standards repo sees two different
numbers on day one of onboarding. `grok-install-action` is the most
visible consumer of the standards (it's the GitHub-native
certification surface), so this is the README where the inconsistency
has the highest blast radius.

## Evidence

On `main` as of 2026-04-23 (WebFetch, paths stable):

- `README.md` — the suspect phrasing lives in the quick-start / value
  prop block ("validation against 14 YAML specifications …"). Exact
  wording varies by section.
- `action.yml` — no numeric claim; untouched by this issue.
- `grok-yaml-standards/standards-overview.md` — canonical table,
  categorises 8 core + 4 extensions = 12.
- `grok-yaml-standards/version-reconciliation.md` — declines
  `grok-cache.yaml` and `grok-auth.yaml`; these are the two
  "phantom" entries that inflate to 14.
- Risk register — `98-risk-register.md`:
  - **DOC-1** (S2, likelihood high): "5 / 12 / 14 standards phrasing
    inconsistency: `grok-install-action` README and `vscode-grok-yaml`
    landing claim '14 YAML specifications', `grok-docs` covers 5,
    `version-reconciliation.md` enumerates 12. New users cannot tell
    which number is canonical."

*(Sources: audit 04 §1 summary headline, audit 04 §4 docs quality,
audit 04 §7 code quality — schema-count drift, audit 04 §9 row 2.)*

## Acceptance criteria

- [ ] Every occurrence of "14 YAML specifications" / "14 standards" /
      "14 spec" (or equivalent variant) in `README.md` is replaced
      with "**12 YAML standards**" (or the maintainer's preferred
      equivalent phrasing, provided the number is 12).
- [ ] The first mention links to
      `AgentMindCloud/grok-yaml-standards/version-reconciliation.md`
      as the canonical source — so future drift has a single source
      of truth to re-sync against.
- [ ] No change to `action.yml`, `CHANGELOG.md` entry, or
      `marketplace.yml` is required unless a maintainer sees
      sympathetic drift there.
- [ ] A one-line `CHANGELOG.md` entry under `[Unreleased]`
      acknowledging the docs correction.

## Notes

- Sibling issue `phase-1b/drafts/14b-vscode-grok-yaml-landing.md`
  carries the same fix into `vscode-grok-yaml`'s landing
  description. DOC-1 is only fully closed when both land.
- `grok-docs` covers 5 of the 12 standards (per DOC-1 text), which
  is a separate gap — §2 #10 (ship `grok-docs` v2.14 content and
  reference pages for the 7 undocumented standards) closes it.
  Out of scope here.
- If the maintainer wants to pair this with §2 #3 (SHA-pin actions)
  — the next batch candidate in `phase-1b/ISSUES.md` — both are
  tiny docs-or-config touches and can land in the same PR.
