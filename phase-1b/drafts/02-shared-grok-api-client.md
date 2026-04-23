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

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**The four parallel implementations** —
`audits/00-ecosystem-overview.md §9.A` (verbatim):

| # | Client | Language | Location | Consumed by |
|---|--------|----------|----------|-------------|
| 1 | Browser Grok invocation | HTML/JS | `grok-install/index.html`, `my-agents.html` | End users visiting the spec repo pages [→ 01, §2] |
| 2 | `grok-install-cli` (optional `xai` extra) | Python | `grok-install-cli/src/grok_install/` (entry via `runtime/` + `integrations/`) | Action, templates, downstream CLIs [→ 03, §2, §3] |
| 3 | `grok-build-bridge/xai_client.py` | Python | `grok_build_bridge/xai_client.py` | The bridge's runtime + LLM-based safety audit [→ 09, §2, §6] |
| 4 | `x-platform-toolkit/shared/grok-client/` | JavaScript | Inlined per-tool into each `index.html` | The 8 Live single-file tools [→ 11, §3] |

Summary sentence (also verbatim): *"None of the four share
code. Auth flows, error shapes, retry/rate-limit policy, and
SDK-version drift are implemented four times over."*

**Per-implementation anchors**:
- **Implementation 1** — `audits/01-grok-install.md §2`: the
  spec repo's user-facing pages invoke Grok directly for the
  live playground + "my agents" UI.
- **Implementation 2** — `audits/03-grok-install-cli.md §2, §3`:
  Python package layout `src/grok_install/{core,deploy,
  integrations,runtime,safety}/`. Integration + runtime
  subpackages are where Grok calls happen; `xai` is listed as
  an optional extra in `pyproject.toml`.
- **Implementation 3** — `audits/09-grok-build-bridge.md §2, §6`:
  `xai_client.py` handles Grok API traffic for both the
  bridge runtime and the LLM-audit safety layer. Pinned to
  `grok-4.20` at audit time; SDK pin is loose (audit 09 §9
  row 3 calls this out as a risk).
- **Implementation 4** — `audits/11-x-platform-toolkit.md §3`:
  shared JS is "inlined per-tool into each `index.html`" —
  8 single-file HTML tools, each carrying its own copy.

**§2-row-vs-§9.A discrepancy** (flagged honestly):
`audits/99-recommendations.md §2 #2`'s "Affected repos"
column lists **grok-install-cli, grok-build-bridge,
grok-agents-marketplace, awesome-grok-agents**. This
disagrees with the §9.A implementation list (which names
`grok-install` and `x-platform-toolkit` instead of
`grok-agents-marketplace` and `awesome-grok-agents`).

Best reading: §2 #2's "Affected repos" enumerates *likely
consumers after extraction* rather than *current parallel
implementations*. The two JS implementations
(`grok-install`'s browser invocation and
`x-platform-toolkit`'s inlined JS) are language-incompatible
with a Python-flavoured shared-package extraction and were
probably deferred out of §2's headline list. Meanwhile,
`awesome-grok-agents` (Python scripts) and
`grok-agents-marketplace` (Node/Next.js client-side) could
both consume the shared client over time.

This draft treats the §9.A list as the **authoritative
current-state ground truth** and §2 #2's list as the
**future-consumer aspiration**. Part C (consumer adoption
sequencing) enumerates both sets explicitly and makes the
language-boundary concrete.

(Same pattern the §2 #18 draft used when it flagged its own
audit-citation inconsistency. Preserve literal §2 citations;
add substantive ones alongside; don't invent new
cross-refs.)

**Relevant ecosystem coordination points**:
- `xai-sdk` version pin — currently per-implementation;
  shared client pins once.
- `grok-4.20` model ID — bridge hard-codes it in
  `xai_client.py`; shared client parameterises.
- Error shapes — `xai-sdk` raises specific exception types;
  each implementation handles them differently today.
- Streaming — SSE decode + tool-call delta handling is the
  place most per-implementation bugs live.

**Risk register**: no direct row. `audits/98-risk-register.md`
catalogues 29 risks; the four-clients drift was classed as
a cross-cutting concern (`00-ecosystem-overview.md §9.A`)
rather than a standalone risk. Closing this rec preempts
future SEC/SUP-category risks (e.g. "one implementation ships
a retry-storm fix; three others still have the bug" →
SEC-2-adjacent).

**Related §2 cross-refs**:
- §2 #1 (shared `grok-safety-rules`) — parallel extraction
  pattern. If #1's "new repo (A2)" option lands, follow the
  same org convention here.
- §2 #12 (replace `awesome-grok-agents` stub with real CLI)
  — §12 already routes that repo's validation through the
  CLI; once §12 lands, `awesome-grok-agents` transitively
  consumes this shared client via the CLI. No additional
  work there.
- §2 #17 (`grok-agent-orchestra` bootstrap) — §17's draft
  flags that the orchestra may pin `httpx` directly for
  Grok calls if this shared client isn't shipped by
  orchestra-bootstrap time. Two ecosystems of coordination:
  this rec ships the client; §17 adopts it when available.
- §2 #7 (`grok-install-cli` tagged releases + Trusted
  Publisher) — this rec's release pipeline follows the same
  pattern (Trusted Publisher to PyPI, SemVer tags).
