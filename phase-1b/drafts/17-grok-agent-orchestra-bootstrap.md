# Bootstrap grok-agent-orchestra with a working multi-agent pattern + a behavioural Lucas safety veto

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #17 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/grok-agent-orchestra
- **Risks closed**: partial GOV-3 (S3) — from `audits/98-risk-register.md`. Full GOV-3 closure also requires the sibling §2 #16 bootstrap (`vscode-grok-yaml`) + §2 #15 landing the honesty-fix on both shell repos. Also closes UNV-3 (S3) — Lucas safety veto becomes behaviourally defined once this rec lands.
- **Source audits**: `[→ 10 §9 row 2]`. Supporting: `audits/10-grok-agent-orchestra.md §1, §2, §10` (LICENSE-only repo + advertised-but-undefined "Lucas" veto), `audits/10 §9 rows 4, 5` (the Lucas definition + shared safety-layer recs this draft absorbs).
- **Effort (§2)**: L — bootstrap of a shell repo means source + CI + docs + tests + release from zero. The multi-agent pattern itself is the biggest chunk.
- **Blocked by (§2)**: #5 — Lucas's veto semantics can only be defined in terms of the published safety-profile rubric; without the rubric, "Lucas" is branding without a contract (UNV-3).

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative. Also depends on [`phase-1b/drafts/01-shared-grok-safety-rules-package.md`](01-shared-grok-safety-rules-package.md) as a day-one dependency — that draft is itself speculative on #5, so this is two layers of speculation.
- **Re-review trigger**: rewrite this draft if either prerequisite is substantively rewritten during upstream review. Specifically: (a) §2 #5's seven-axis rubric shape drives the Lucas veto's normative definition in Part B; if axes are added/removed, the veto rule changes. (b) §2 #1's package API drives the orchestra's imports in Part A; if the package lands under a different name or with a different API, Part A's imports need updating. If §2 #1 is NOT filed or merged before this draft is filed, fall back to pinning `grok-install-cli`'s `safety/` module directly with a "TODO: migrate to grok-safety-rules once shipped" comment in Part A — marginal cost, easy to clean up.

- **Suggested labels**: `bootstrap`, `v0.1.0`, `multi-agent`, `lucas-veto`, `phase-1b`

---

## Context

`grok-agent-orchestra` is the multi-agent framework the
ecosystem advertises — README describes "5 patterns" and a
"Lucas safety veto". The repo today contains **only LICENSE**:
1 commit total, no README (the description lives on the GitHub
repo landing page), no source, no CI, no issues template. Like
`vscode-grok-yaml`, it is a shell. Unlike `vscode-grok-yaml`,
its advertised feature set is materially more ambitious — a
multi-agent orchestrator with a named safety veto is not a
one-afternoon extension; it is a framework.

Two concrete problems fall out:

1. **The repo's marketing outruns reality.** §2 #15b (already
   drafted + in repo) downgrades the description. This rec
   closes the other half: ship a real v0.1.0 with *one* working
   multi-agent pattern so "multi-agent framework" is a true
   statement.

2. **Lucas has no source.** The "Lucas safety veto" is named on
   the repo landing page but defined nowhere. UNV-3 in the risk
   register. Without a behavioural contract, Lucas is branding.
   This rec defines Lucas in terms of §2 #5's rubric — a named
   function that vetoes multi-agent actions violating the
   *strictest* safety profile claimed by any agent in the team.

The goal for v0.1.0 is **one pattern, done well**, not five
patterns half-done. Candidate: a **plan-execute-critique** loop
— three agents (planner, executor, critic) collaborating on a
single user task, with Lucas checking each proposed action
against the rubric before execution. This is the smallest
pattern that actually exercises multi-agent coordination +
safety-veto integration; the other four patterns the repo
advertised (per README) can layer on top in later releases.

Secondary constraint: the bootstrap must adopt §2 #1's shared
`grok-safety-rules` from day one. The orchestra is the one
repo where "day one" is still ahead of us; adopting the shared
package here avoids adding a fourth parallel safety
implementation that §2 #1 would then immediately retire.

## Evidence

From `main` snapshot on 2026-04-23 (WebFetch; paths stable).

**Current repo state** —
`audits/10-grok-agent-orchestra.md §1, §2, §11 row 1`:
- Repo contents: `LICENSE` only (Apache 2.0).
- **1 commit total**; 1★, 0 forks, 0 issues, 0 PRs.
- Landing page advertises: multi-agent framework, 5 patterns,
  "Lucas safety veto".
- No README file visible in the repo tree (description lives
  on the GitHub repo-landing page).
- No source, no `pyproject.toml` / `package.json`, no CI
  workflows.

**What the ecosystem already has** (so bootstrap does not need
to reinvent):
- `grok-install-cli` (Typer-based CLI with `safety/` layer) —
  `audits/03 §2`.
- `grok-build-bridge` (LLM audit + static scan; mature CI
  template §2 #18 is promoting) — `audits/09 §5`.
- `grok-yaml-standards` (the schema catalogue this orchestra's
  agents will emit) — `audits/02 §2`.
- `awesome-grok-agents` (gallery of 10 template agents the
  orchestra will orchestrate) — `audits/06 §2`.

**Risk register** — `audits/98-risk-register.md`:
- **GOV-3** (S3, L-high, `open`): "`vscode-grok-yaml` and
  `grok-agent-orchestra` are LICENSE+README only — no source,
  no CI, no issues template. The marketing-polished surface
  implies a working product that does not exist." *(This rec
  closes half; §2 #16 closes the other half for vscode-grok-yaml.)*
- **UNV-3** (S3, L-med, `needs-info`): "'Lucas safety veto'
  (advertised on `grok-agent-orchestra`): no source defines
  what Lucas is, what veto authority it carries, or how it
  interacts with the strict / standard / permissive profiles.
  Branding without a behavioural contract." *(This rec closes
  UNV-3 outright by defining Lucas.)*

**Audit recs that this rec absorbs** —
`audits/10-grok-agent-orchestra.md §9`:
- **Row 2** (direct source for §2 #17): "Ship a v0.1.0 with one
  working multi-agent pattern + a behavioural Lucas definition."
- **Row 3**: "Adopt `grok-build-bridge`'s CI template from day
  one." Absorbed into Part A below.
- **Row 4**: "Document 'Lucas safety veto' concretely." Absorbed
  into Part B — Lucas's behavioural contract.
- **Row 5**: "Share safety-layer code with `grok-install-cli`
  and `grok-build-bridge` from the start." Absorbed into Part A
  as the day-one dependency on `grok-safety-rules` (§2 #1).

**Prerequisite state**:
- §2 #5 draft: [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md).
- §2 #1 draft: [`phase-1b/drafts/01-shared-grok-safety-rules-package.md`](01-shared-grok-safety-rules-package.md).
- §2 #15b draft: [`phase-1b/drafts/15b-grok-agent-orchestra-description.md`](15b-grok-agent-orchestra-description.md) — landing description
  honesty for this repo; this rec's Part A assumes that landed.

**Related §2 cross-refs**:
- §2 #15b (honest landing description — first-pass draft).
- §2 #5 (rubric — prerequisite).
- §2 #1 (shared safety-rules package — prerequisite for clean
  adoption; fall-back if #1 not yet merged is flagged in
  metadata header).
- §2 #18 (CI template — adopted from day one per audit 10 §9 row 3).
