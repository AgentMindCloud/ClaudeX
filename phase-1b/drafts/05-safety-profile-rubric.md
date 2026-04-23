# Publish a unified safety-profile rubric (strict / standard / permissive) with conformance tests

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #5 (`audits/99-recommendations.md`)
- **Target repo (primary — owner of the rubric artefact)**: AgentMindCloud/grok-yaml-standards
- **Target repos (consumers / conformance-test adopters)**: AgentMindCloud/awesome-grok-agents, AgentMindCloud/grok-install-cli, AgentMindCloud/grok-build-bridge, AgentMindCloud/grok-agent-orchestra
- **Filing strategy**: one coordination issue in `grok-yaml-standards` (primary — owner of the rubric); consumer-repo checklist rows inside the acceptance criteria. The user may optionally file short cross-reference issues in the four consumer repos once this primary lands, pointing at its `rubric-v1.md` path.
- **Risks closed**: partial UNV-3 (S3) — enables UNV-4 (S3) closure once consumers adopt. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 02 §9 row 3]`, `[→ 06 §9 row 1]`. Substantive cross-cut evidence in `audits/00-ecosystem-overview.md §6` (tripartite safety model, 6/4/0 distribution, three independent static-regex implementations).
- **Effort (§2)**: M — the rubric text itself is small; the conformance-test format + coordination across 4 consumer repos is what makes this M-effort.
- **Blocked by**: none
- **Unblocks**: §2 #1 (shared `grok-safety-rules` package), §2 #11 (permissive-profile exemplar), §2 #17 (`grok-agent-orchestra` bootstrap + Lucas behavioural contract)
- **Suggested labels**: `spec`, `safety`, `ecosystem`, `phase-1b`

---

## Context

The Grok ecosystem advertises a **tripartite safety model** —
`strict` / `standard` / `permissive` — across three repos that each
use the vocabulary but none of which publishes a machine-readable
rubric:

- `grok-install/SECURITY.md` defines "Enhanced Safety & Verification
  2.0" (pre-install file scan, minimum-keys, halt-on-anomaly,
  "Verified by Grok" badge) but leaves the three profile names
  undefined.
- `grok-yaml-standards/standards-overview.md` categorises the 12
  standards by security **level** (Low / Medium / High / Critical) —
  a separate axis that speaks about *what the standard touches*,
  not *how strict a consuming agent must be*. The strict/standard/
  permissive triplet is referenced in prose only.
- `grok-install-cli/src/grok_install/safety/` implements *some*
  ruleset under these names; whether it is a re-implementation of
  the `grok-security` schema or a divergent ruleset is undocumented
  (tracked as UNV-4, S3, in `audits/98-risk-register.md`).

The observable consequence is that the three profile names have no
behavioural contract. Concretely:

1. **The `awesome-grok-agents` gallery ships 6 strict, 4 standard,
   and 0 permissive templates** (source: `featured-agents.json`
   v1.0). There is no reference template for the loosest profile,
   so new adopters cannot calibrate what `permissive` should look
   like in practice. §2 #11 (add a permissive exemplar) is blocked
   on this rec; the exemplar cannot be honest without a rubric to
   point at.
2. **At least three independent static-regex implementations of
   "safety rules" live in the ecosystem** —
   `grok-install-cli/safety/rules.py`,
   `grok-build-bridge/_patterns.py`, and
   `awesome-grok-agents/scripts/scan_template.py` — with no shared
   source module. §2 #1 (extract a shared `grok-safety-rules`
   package) is blocked on this rec; a shared package needs a
   shared behavioural contract before extraction is meaningful.
3. **`grok-agent-orchestra`'s README advertises a "Lucas safety
   veto"** whose relationship to the three profiles is undefined
   (UNV-3, S3). §2 #17 (bootstrap the orchestra with a behavioural
   definition of the Lucas veto) is blocked on this rec.

This issue asks `grok-yaml-standards` to publish the rubric as a
versioned artefact (`rubric-v1.md` + machine-readable companion),
then ships a conformance-test format that each of the four consumer
repos can run in CI to prove its claimed profile mapping matches
the rubric. The rubric is the contract; the conformance tests are
what give it teeth.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**Where the vocabulary appears today**

| Repo | Artefact | What it says | What is missing |
|------|----------|--------------|-----------------|
| `grok-install` | `SECURITY.md` — "Enhanced Safety & Verification 2.0" | Defines the overall safety stance (pre-install scan, halt-on-anomaly, "Verified by Grok" badge). | No definition of the three profile names. |
| `grok-yaml-standards` | `standards-overview.md` | Categorises the 12 standards by security **level** (Low / Medium / High / Critical). | Level ≠ profile. No rubric for strict / standard / permissive. |
| `grok-yaml-standards` | `grok-security/` | Operational catalogue entry for the security standard. | Does not enumerate profile semantics. |
| `grok-install-cli` | `src/grok_install/safety/rules.py`, `scanner.py` | Implements *a* ruleset used by `grok-install scan`. | Not documented whether it re-implements `grok-security` or diverges (UNV-4). |
| `awesome-grok-agents` | `featured-agents.json` v1.0 | Declares one of `strict` / `standard` / `permissive` per template. | **6 strict / 4 standard / 0 permissive** — no permissive exemplar. |
| `grok-build-bridge` | `_patterns.py` + LLM audit in `xai_client.py` | Implements its own dual-layer safety scan. | Parallel re-implementation of "safety rules" vocabulary. |
| `grok-agent-orchestra` | README | Advertises "Lucas safety veto". | No source defines Lucas or its relationship to the three profiles (UNV-3). |

*Sources: `audits/00-ecosystem-overview.md §6.1`, `§6.2`, `§6.3`;
`audits/01-grok-install.md §6`; `audits/02-grok-yaml-standards.md
§6`; `audits/03-grok-install-cli.md §6, §10`; `audits/06-awesome-
grok-agents.md §6, §11 row 3`; `audits/09-grok-build-bridge.md §6`;
`audits/10-grok-agent-orchestra.md §10`.*

**Risk register** — `audits/98-risk-register.md`:

- **UNV-3** (S3, L-med, `needs-info`): "'Lucas safety veto'
  (advertised on `grok-agent-orchestra`): no source defines what
  Lucas is, what veto authority it carries, or how it interacts
  with the strict / standard / permissive profiles. Branding
  without a behavioural contract."
- **UNV-4** (S3, L-med, `needs-info`): "Whether `grok-install-cli`'s
  safety rules are a re-implementation of the `grok-yaml-standards/
  grok-security` schema or a divergent ruleset is not stated —
  risks two safety surfaces drifting apart unobserved."

**Why `grok-yaml-standards` is the right home for the rubric.**
The repo already owns `standards-overview.md` (the ecosystem's
most authoritative cross-standard table) and
`version-reconciliation.md` (which established the "12 standards"
count against competing 8- and 14-counts — audit 02 §4). Publishing
the safety-profile rubric alongside those artefacts keeps the
ecosystem's single-source-of-truth discipline intact. The four
consumer repos already import this repo's schemas; adding a rubric
file is additive.
