# Downgrade landing-page description to reflect skeleton state

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #15 (`audits/99-recommendations.md`) — target-repo variant B of 2
- **Target repo**: AgentMindCloud/grok-agent-orchestra
- **Sibling draft**: `phase-1b/drafts/15a-vscode-grok-yaml-description.md` (same §2 #15,
  different target repo — file both; they share the same precedent citation)
- **Risks closed**: GOV-3, DOC-3 — from `audits/98-risk-register.md` (both partial: closes the
  `grok-agent-orchestra` limb of each; fully closed when sibling 15a also lands)
- **Source audits**: `[→ 10 §1]`, `[→ 10 §2]`, `[→ 10 §6]`, `[→ 10 §9 row 1]`
- **Ecosystem precedent**: `AgentMindCloud/grok-install/SECURITY.md` — "Verified by
  Grok" / Enhanced Safety & Verification 2.0 posture requires calibrated claims
  about shipped capabilities
- **Blocked by**: none
- **Unblocks**: §2 #17 (bootstrap a single working multi-agent pattern wired to
  the unified safety rubric)
- **Suggested labels**: `docs`, `truthful-marketing`, `governance`, `phase-1b`

---

## Context

`grok-agent-orchestra`'s GitHub description advertises a Python
framework for multi-agent orchestration built on xAI's Grok models,
with 5 patterns (hierarchical, dynamic-spawn, debate-loop,
parallel-tools, recovery) and a "Lucas safety veto" gating
mechanism.

The repository currently contains:

- `LICENSE` (Apache 2.0)

That is the entire repo, at 1 commit on `main`. No `README.md`, no
`pyproject.toml`, no `.github/workflows/`, no source tree, no
patterns, no safety-veto implementation. The description promises a
feature set that does not yet exist.

This is the second of two "marketing-polished shell repos" in the
ecosystem (the first is `vscode-grok-yaml`; see sibling draft
`phase-1b/drafts/15a-vscode-grok-yaml-description.md`). The
ecosystem's own spec repo (`grok-install`) ships Enhanced Safety &
Verification 2.0 and a "Verified by Grok" badge, both of which
depend on advertised capabilities matching shipped artefacts.
Having an org-level repo whose description fails that same check is
an internal inconsistency worth closing independently of any code
bootstrap.

## Evidence

From `main` on 2026-04-23 (WebFetch; line numbers omitted, paths
stable):

- Repo top-level tree: `LICENSE` only. No `README.md`,
  `pyproject.toml`, `.github/`, or source. *(Audit 10 §2.)*
- 1★, 0 forks, 0 issues, 0 PRs, 1 commit. *(Audit 10 §1.)*
- GitHub repo description (short tagline): advertises 5
  orchestration patterns and "Lucas safety veto" as shipped
  capabilities. *(Audit 10 §1.)*
- "Lucas safety veto" is a term distinctive to AgentMindCloud —
  semantics unverifiable without source; an anti-hallucination
  concern flagged in audit 10 §6.
- Risk register — `98-risk-register.md`:
  - **GOV-3** (S3, likelihood high): "`vscode-grok-yaml` and
    `grok-agent-orchestra` are LICENSE+README only — no source, no
    CI, no issues template. The marketing-polished surface implies
    a working product that does not exist." *(Note: this repo is
    currently even thinner — LICENSE-only — a superset of the
    GOV-3 text.)*
  - **DOC-3** (S3, likelihood high): "`grok-agent-orchestra`
    ('Multi-agent orchestration with Lucas safety veto') describes
    products that don't exist. Description-vs-reality mismatch."

## Acceptance criteria

Pick **one** of (A) or (B); either closes this issue.

### Option A — Minimal-change downgrade

- [ ] GitHub repo description (settings → "About") rewritten to
      describe the current state. Suggested phrasing:
      "*Pre-alpha: placeholder repo for a planned multi-agent
      orchestration framework on xAI Grok. No code shipped yet —
      see ROADMAP / open issues for status.*"
- [ ] A `README.md` is added (there isn't one today) that states
      the same pre-alpha status in the first paragraph. Aspirational
      design (5 patterns, Lucas veto) may appear below the status
      banner, each flagged `not-yet-implemented` / `planned`.
- [ ] A `ROADMAP.md` (or a `## Roadmap` section in the new
      `README.md`) pointing at §2 #17 as the bootstrap target.

### Option B — Roadmap-up-front rewrite

- [ ] `README.md` is created, leading with the roadmap: phase 0
      (current: LICENSE only), phase 1 (one working pattern
      end-to-end — the §2 #17 scope), phase N (the full 5
      patterns + safety veto). Each advertised capability carries
      a status flag.
- [ ] Repo description updated to the phase-0 summary.
- [ ] "Lucas safety veto" is either scoped (per §2 #17's behavioural
      definition) or explicitly flagged as
      `undefined — design pending`.

Either option satisfies the underlying rule:
**no advertised capability without a matching status indicator.**

## Notes

- The sibling issue `phase-1b/drafts/15a-vscode-grok-yaml-description.md`
  applies the same fix to `vscode-grok-yaml`. GOV-3 and DOC-3 are
  only fully closed when both land.
- §2 #17 (bootstrap a single working multi-agent pattern + define
  "Lucas safety veto" behaviourally) is the natural follow-up; it
  is `Blocked by` §2 #5 (unified safety-profile rubric) per
  `audits/99-recommendations.md` — this description-downgrade issue
  is not on that blocked chain, so it can land first.
- §3.1 in `audits/99-recommendations.md` records that the per-repo
  rec "*Document 'Lucas safety veto' concretely*" (audit 10 §9 row
  4) is absorbed by §2 #17 at bootstrap time, not by this issue.
  Closing this issue does not require defining the veto; it requires
  not advertising it as shipped.
- `grok-install/SECURITY.md`'s Enhanced Safety & Verification 2.0
  language is cited as ecosystem precedent, not policy; no update
  to that file is implied by closing this issue.
