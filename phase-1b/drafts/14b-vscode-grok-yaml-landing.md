# Align landing-page "14 YAML standards" with grok-yaml-standards (12)

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #14 (`audits/99-recommendations.md`) — target-repo variant B of 2
- **Target repo**: AgentMindCloud/vscode-grok-yaml
- **Sibling draft**: `phase-1b/drafts/14a-grok-install-action-readme.md` (same §2 #14,
  different target repo — file both; they share a canonical source)
- **Risks closed**: DOC-1 — from `audits/98-risk-register.md` (partial: closes the
  `vscode-grok-yaml` limb; fully closed when sibling 14a also lands)
- **Source audits**: `[→ 07 §1]`, `[→ 07 §9 row 4]`
- **Canonical source**: `AgentMindCloud/grok-yaml-standards/version-reconciliation.md`
- **Blocked by**: none
- **Suggested labels**: `docs`, `version-coherence`, `ecosystem`, `good-first-issue`, `phase-1b`

---

## Context

The `vscode-grok-yaml` GitHub description (the repo's short tagline —
"Official community VS Code extension … for all **14 YAML
standards**") advertises a standards count that does not match the
canonical source.

The canonical source is `grok-yaml-standards/version-reconciliation.md`:

- 12 standards ship in v1.2.0 (8 core + 4 extensions).
- `grok-cache.yaml` and `grok-auth.yaml` — the two entries that
  would make the count 14 — were explicitly **declined** (CI
  complexity / forward-compat risk). Reconciliation doc records
  both decisions.
- The same doc provides ready-to-use PR language for downstream
  fixes; this issue is a direct application of that language.

Scope note: the README for this repo currently describes planned /
aspirational functionality. That broader accuracy problem is covered
by a separate draft (§2 #15 — see sibling
`phase-1b/drafts/15a-vscode-grok-yaml-description.md`). This issue is
scoped narrowly to the **numeric** "14 → 12" correction; the surface
honesty correction is tracked independently so either can land first.

## Evidence

On `main` as of 2026-04-23 (WebFetch, paths stable):

- GitHub repo description (the short tagline, not the README H1):
  "… full IntelliSense, live validation, safety scanning, template
  gallery, and one-click deployment for all 14 YAML standards."
- `README.md` — same or similar phrasing in the intro paragraph.
- `grok-yaml-standards/standards-overview.md` — 8 core + 4
  extensions = 12.
- `grok-yaml-standards/version-reconciliation.md` — declines the
  two phantom entries and provides fix-up PR language.
- Risk register — `98-risk-register.md`:
  - **DOC-1** (S2, likelihood high): "5 / 12 / 14 standards phrasing
    inconsistency: `grok-install-action` README and `vscode-grok-yaml`
    landing claim '14 YAML specifications', `grok-docs` covers 5,
    `version-reconciliation.md` enumerates 12."

*(Sources: audit 07 §1 summary, audit 07 §9 row 4.)*

## Acceptance criteria

- [ ] GitHub repo description (settings → "About") updated from
      "14 YAML standards" to "12 YAML standards".
- [ ] `README.md` first paragraph updated to match, with a link to
      `AgentMindCloud/grok-yaml-standards/version-reconciliation.md`
      as the canonical source (so future drift has a single
      source of truth).
- [ ] No other file changes required unless symmetric drift is
      found elsewhere (e.g. `package.json` `description` field if
      one lands later).

## Notes

- Sibling issue `phase-1b/drafts/14a-grok-install-action-readme.md`
  carries the same fix into `grok-install-action`. DOC-1 is only
  fully closed when both land.
- §2 #15 (downgrade the landing-page description more broadly — the
  extension doesn't yet exist) is a bigger honesty fix on the same
  README; see sibling draft
  `phase-1b/drafts/15a-vscode-grok-yaml-description.md`. Filing both
  is fine; they touch adjacent text but resolve independently.
- §2 #16 (bootstrap the actual extension) becomes the natural
  follow-up once both this and §2 #15 have landed.
