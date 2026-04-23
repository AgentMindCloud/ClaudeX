# Extract a shared grok-safety-rules package consumed by every safety-aware repo

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #1 (`audits/99-recommendations.md`)
- **Target repo (primary)**: AgentMindCloud/grok-install-cli *(primary — owns the most mature safety-rules implementation today; extraction happens here first)*. Alternative primary: a new `AgentMindCloud/grok-safety-rules` repo if the team prefers a separate home. The draft body below is written for the "extract from `grok-install-cli`" path and flags the new-repo alternative in §Notes.
- **Consumer repos (adoption follow-ups)**: AgentMindCloud/grok-build-bridge, AgentMindCloud/grok-agents-marketplace *(via the CI layer)*, AgentMindCloud/grok-agent-orchestra *(via §2 #17)*, AgentMindCloud/awesome-grok-agents *(via §2 #12's stub removal — already covered)*.
- **Filing strategy**: coordination issue in `grok-install-cli` describing extraction + release + consumer adoption. Consumer-repo adoption follow-ups open **only after** this primary merges AND the first release of the extracted package ships.
- **Risks closed**: UNV-4 (S3) outright *(the "three parallel implementations drift silently" underlying cause is resolved by the extraction)*; partial SEC-1 (S1) *(the bridge's LLM-audit prompt-injection fragility is unchanged; the static-scan layer that feeds it becomes shared + auditable, reducing the surface the LLM has to work around)*. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 09 §9 row 4]`, `[→ 03 §9 row 3]`, `[→ 10 §9 row 5]`, `[→ 06 §9 row 2]`. Cross-cut evidence in `audits/00-ecosystem-overview.md §6.3` (three parallel implementations enumerated) + `§9.B` if present.
- **Effort (§2)**: L — extraction + packaging + three consumer-repo PRs + coordinated release. The rubric from §2 #5 gives the shared contract; this rec ships the shared *code* that implements it.
- **Blocked by (§2)**: #5 — the shared package needs the rubric as its behavioural contract. Without it, the extraction locks in three-way drift behind a single import name.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft if §2 #5's normative seven-axis rubric table is substantively changed during upstream review (e.g. axes added/removed, profile names changed). This draft's package API enumerates the seven axes; if the rubric's axis count shifts, the API shape shifts with it.

- **Suggested labels**: `extraction`, `shared-library`, `safety`, `ecosystem`, `phase-1b`

---

## Context

Three repos in the Grok ecosystem independently implement
"safety rules" — a pattern-based scanner that reads a
`grok-install.yaml` agent definition and flags hardcoded secrets,
over-broad permissions, unsafe external-write patterns, and the
other surface the Enhanced Safety & Verification 2.0 model calls
out:

- `grok-install-cli/src/grok_install/safety/rules.py` +
  `scanner.py` — the CLI's `grok-install scan` subcommand
  backend. Most mature implementation; sibling of
  `core/`, `deploy/`, `integrations/`, `runtime/`.
- `grok-build-bridge/_patterns.py` — static regex layer,
  one half of the bridge's "dual-layer safety" (the other
  half is the LLM audit in `xai_client.py`).
- `awesome-grok-agents/scripts/scan_template.py` — the
  gallery's CI-time scanner. §2 #12 (covered in an earlier
  Session-2 draft in this pass) removes this one by routing
  through the real CLI instead.

`grok-agent-orchestra` also plans to implement a safety layer
once bootstrapped (§2 #17); without this extraction, the
orchestra would make it *four* parallel implementations — a
degradation `audits/10-grok-agent-orchestra.md §9 row 5`
explicitly calls out as a failure mode to pre-empt.

The drift risk is concrete. Today, the three implementations are
"probably close" to each other — no one has systematically
diffed them. As the ecosystem evolves, each implementation drifts
against whichever axis its own repo cares about most (the CLI
cares about install-time scanning; the bridge cares about LLM
audit context; the gallery cares about CI speed). Nothing in the
ecosystem's current process flags the divergence.

The fix is extraction: one package, one source module, three (or
four) consumers. §2 #5 provides the behavioural contract (the
rubric's seven normative axes); this rec ships the code that
implements that contract. After both land:

- The rubric defines *what* a profile means.
- The shared package is *how* it's enforced.
- Consumers call into the package rather than re-implementing.

That's the only configuration in which UNV-4 ("safety surfaces
drifting apart unobserved") closes structurally rather than
situationally.
