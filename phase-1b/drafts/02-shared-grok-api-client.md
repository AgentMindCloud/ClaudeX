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

## Context

Four repos in the Grok ecosystem independently implement a Grok
API client. None of them share code. Each carries its own
auth flow, retry policy, streaming handler, rate-limit
bookkeeping, and SDK-version pin. When the Grok API surface
moves — a new model ID, a revised streaming chunk format, a
tightened rate-limit header — four separate patches need to
land, and the inevitable asymmetric-landing is the drift this
rec targets.

`audits/00-ecosystem-overview.md §9.A` calls this "the highest
cross-ecosystem leverage in the recommendations pile". The
reasoning is straightforward:

- **Auth.** xAI API keys, org headers, bearer tokens — every
  caller needs the same handling. Today each implementation
  re-derives it.
- **Retries.** Transient 5xx, rate-limit 429 backoff,
  streaming-connection restart — a shared retry policy lets
  the whole ecosystem adopt improvements in one PR.
- **Streaming.** `xai-sdk` emits server-sent-events; chunk
  decoding, tool-call deltas, finish-reason handling are all
  non-trivial. Four parallel decoders means four silent bugs.
- **Rate limiting.** `X-RateLimit-Remaining` / `Retry-After`
  interpretation varies by endpoint and by SDK version.
  Encoding that in one place is the only way it stays
  correct.
- **SDK-version pin.** `xai-sdk` drifts; a bridge pinned to
  Grok-4.20 is not the same as a CLI pinned to whatever
  `xai>=0.1.0` resolves to on install day (audit 09 §9 row 3).
  A shared package is the natural pin point.

The fix is extraction: one package, one source module, one
SDK-version pin, consumed by every Python-calling repo. The
two JS-flavoured implementations (`grok-install`'s browser
invocation + `x-platform-toolkit`'s inlined JS client) are a
separate axis — Part A discusses whether to extract a sibling
JS package now, later, or never.

This rec's relationship to §2 #1 (shared `grok-safety-rules`)
is parallel: same extraction pattern, different subject
matter. The ownership-boundary argument that recommended a
new repo for §2 #1 (A2 in that draft) applies here too. If
one of the two lands first, the other inherits the repo
pattern; if both land in the same pass, coordinate naming
(`grok-safety-rules` + `grok-client` — consistent dash-
separated names under the AgentMindCloud org).

L-effort honestly. This is an SDK-shape design + 4-consumer
migration, not a one-weekend extraction. Budget 4–8 focused
weeks of work. The draft's Parts A / B / C split the work so
partial landings are possible (Part A ships the package
skeleton; Part B ships feature parity with the current
implementations; Part C adopts in each consumer).
