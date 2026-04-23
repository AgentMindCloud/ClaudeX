# Downgrade landing-page / README description to reflect pre-alpha state

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #15 (`audits/99-recommendations.md`) — target-repo variant A of 2
- **Target repo**: AgentMindCloud/vscode-grok-yaml
- **Sibling draft**: `phase-1b/drafts/15b-grok-agent-orchestra-description.md` (same §2 #15,
  different target repo — file both; they share the same precedent citation)
- **Risks closed**: GOV-3, DOC-3 — from `audits/98-risk-register.md` (both partial: closes the
  `vscode-grok-yaml` limb of each; fully closed when sibling 15b also lands)
- **Source audits**: `[→ 07 §1]`, `[→ 07 §2]`, `[→ 07 §6]`, `[→ 07 §9 row 1]`
- **Ecosystem precedent**: `AgentMindCloud/grok-install/SECURITY.md` — "Verified by
  Grok" / Enhanced Safety & Verification 2.0 posture requires calibrated claims
  about shipped capabilities
- **Blocked by**: none
- **Unblocks**: §2 #16 (bootstrap a real `vscode-grok-yaml` v0.1.0)
- **Suggested labels**: `docs`, `truthful-marketing`, `governance`, `phase-1b`

---

## Context

`vscode-grok-yaml`'s GitHub description and README currently advertise a
production-ready VS Code extension: "Official community VS Code
extension … full IntelliSense, live validation, safety scanning,
template gallery, and one-click deployment for all N YAML standards."

The repository contents are, in total:

- `LICENSE`
- `README.md` (a media-asset spec / brand wire-up guide for a future
  extension — not code)
- `media/` (apparently empty)

There is no `package.json`, no `extension.ts`, no `src/`, no build
config, no publisher manifest, no Marketplace listing mechanism. The
description promises a feature set the repo has not begun to
implement. A new user landing here cannot tell from the description
that the extension does not exist yet.

The ecosystem has already set its own precedent for calibrated
claims: `grok-install/SECURITY.md` documents Enhanced Safety &
Verification 2.0 and the "Verified by Grok" badge — both require
that advertised capabilities actually exist in the installed
artefact. Applying the same standard to this repo's description is
an internal consistency fix, not a new policy.

## Evidence

From `main` on 2026-04-23 (WebFetch; line numbers omitted, paths
stable):

- Repo top-level tree: `LICENSE`, `README.md`, `media/` (no source,
  no manifest). *(Audit 07 §2.)*
- GitHub repo description (short tagline, "About" panel): advertises
  full IntelliSense / live validation / safety scanning / template
  gallery / one-click deployment. *(Audit 07 §1.)*
- `README.md` opening paragraph: repeats that surface claim verbatim
  or near-verbatim.
- No CI workflows, no issue templates, no `package.json`. *(Audit
  07 §6 — "no extension code to audit".)*
- Risk register — `98-risk-register.md`:
  - **GOV-3** (S3, likelihood high): "`vscode-grok-yaml` and
    `grok-agent-orchestra` are LICENSE+README only — no source, no
    CI, no issues template. The marketing-polished surface implies
    a working product that does not exist."
  - **DOC-3** (S3, likelihood high): "`vscode-grok-yaml`
    ('Production-grade VS Code extension for Grok YAML') and
    `grok-agent-orchestra` … describe products that don't exist —
    both repos are LICENSE+README only. Description-vs-reality
    mismatch."

## Acceptance criteria

Pick **one** of (A) or (B); either closes this issue.

### Option A — Minimal-change downgrade

- [ ] GitHub repo description (settings → "About") rewritten to
      describe the current state. Suggested phrasing:
      "*Pre-alpha: placeholder repo for an official community VS
      Code extension for Grok YAML. No code shipped yet — see
      ROADMAP / open issues for status.*"
- [ ] `README.md` rewritten (or a prominent top-of-file banner
      added) stating the same pre-alpha status in the first
      paragraph. Media-asset / brand wire-up content can stay
      below that banner.
- [ ] A `ROADMAP.md` (or a `## Roadmap` section in `README.md`)
      pointing at §2 #16 as the bootstrap target and listing the
      capabilities the current description promises, each marked
      as `not-yet-implemented` / `planned`.

### Option B — Roadmap-up-front rewrite

- [ ] `README.md` is rewritten to lead with the roadmap: phase 0
      (current: media + license), phase 1 (schema-validation-only
      extension — the §2 #16 scope), phase N (everything the
      current description promises). Each advertised capability
      carries a status flag.
- [ ] Repo description updated to the phase-0 summary.
- [ ] No promised capability appears in the description or
      README intro without an adjacent status flag.

Either option satisfies the underlying rule:
**no advertised capability without a matching status indicator.**
Pick whichever is cheaper for the maintainer.

## Notes

- The sibling issue `phase-1b/drafts/15b-grok-agent-orchestra-description.md`
  applies the same fix to `grok-agent-orchestra`. GOV-3 and DOC-3 are
  only fully closed when both land.
- The adjacent §2 #14 fix (14 → 12 YAML standards count — see
  `phase-1b/drafts/14b-vscode-grok-yaml-landing.md`) touches the
  same README/description. If both land in one PR, make sure the
  count-correction from #14 is preserved in the rewritten text.
- §2 #16 (bootstrap a real v0.1.0 extension) is `Blocked by` this
  issue in `audits/99-recommendations.md` — bootstrap should begin
  *after* the description has been honest, so a contributor reading
  the repo mid-bootstrap isn't confused about what exists.
- `grok-install/SECURITY.md`'s Enhanced Safety & Verification 2.0
  language is cited as ecosystem precedent, not policy; no update
  to that file is implied by closing this issue.
