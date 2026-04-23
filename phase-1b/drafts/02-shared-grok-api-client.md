# Extract a shared Grok API client consumed by every Grok-calling repo

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #2 (`audits/99-recommendations.md`)
- **Target repo (primary)**: AgentMindCloud/grok-install-cli *(primary — owns the most mature Python Grok client surface in the ecosystem; extraction happens here first or yields a new sibling repo)*. Alternative: a new `AgentMindCloud/grok-client` repo — recommended (A2) in Part A for the same ownership-boundary reasons §2 #1 cites.
- **Current parallel implementations (per `audits/00-ecosystem-overview.md §9.A` — 4 repos, not 4 consumers)**:
  1. `grok-install/index.html` + `my-agents.html` — browser JS (end users visiting the spec repo).
  2. `grok-install-cli/src/grok_install/` — Python (via `runtime/` + `integrations/` subpackages).
  3. `grok-build-bridge/xai_client.py` — Python.
  4. `x-platform-toolkit/shared/grok-client/` — JavaScript (inlined per-tool into single-file HTML tools).
- **Consumer repos (adoption follow-ups, per §2 #2's "Affected repos" column)**: grok-install-cli, grok-build-bridge, grok-agents-marketplace, awesome-grok-agents. Note: this list disagrees with the §9.A-implementation list above — see §Evidence for the honest reconciliation.
- **Filing strategy**: coordination issue in `grok-install-cli` (or in the new repo if A2 is chosen). Consumer-repo adoption follow-ups open only **after** the shared-client v0.1.0 release ships.
- **Risks closed**: none directly in `audits/98-risk-register.md` — §2 #2 cites only "drift identified in 00 §9.A" rather than a SEC/SUP/GOV/VER/DOC/UNV row. The drift is real (four implementations, four auth flows, four retry policies) but was catalogued as a cross-cutting concern, not a risk row. Closing it still reduces the surface for future SEC/SUP-category risks.
- **Source audits**: `[→ 00 §9.A]`. Supporting per-implementation sources: `[→ 01 §2]`, `[→ 03 §2, §3]`, `[→ 09 §2, §6]`, `[→ 11 §3]`.
- **Effort (§2)**: L — extraction is M; packaging + 4-consumer adoption + auth/retry/streaming/rate-limit feature parity is what pushes this to L. This draft spec'es the **issue**, not the implementation; the implementation ships across multiple PRs over 4–8 weeks.
- **Blocked by (§2)**: none — this is one of only two §2 recs with no `Blocked by` entry that also has no speculative-draft prerequisites in this repo. Pure non-speculative draft.
- **Suggested labels**: `extraction`, `shared-library`, `grok-api`, `ecosystem`, `phase-1b`

---
