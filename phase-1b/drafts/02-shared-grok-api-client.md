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

## Acceptance criteria

Three parts. Part A is the package skeleton + ownership
decisions + release pipeline. Part B is the feature surface
(what the package must actually do). Part C is the
consumer-adoption sequencing. The issue closes when v0.1.0
ships to PyPI and the first two consumers (CLI + bridge)
have adopted it on `main`.

### Part A — Package shape + ownership

- [ ] **Pick the package home.** Same two-option pattern §2
      #1 uses. Decide once, cite the §2 #1 decision; whichever
      landed there should land here.

      **A1 — Extract from `grok-install-cli` as a sibling
      top-level package.** A new `src/grok_client/` alongside
      `src/grok_install/`, published as a separate PyPI
      distribution. CLI depends on it.

      **A2 — Create a new dedicated repo.**
      `AgentMindCloud/grok-client`. Extract the Python logic;
      publish from there; CLI + bridge + other consumers
      depend on it.

      Default recommendation: **A2**. Ownership boundary
      rationale carries over from §2 #1: the shared client
      has ≥3 Python consumers across repos; separate repo
      governance is cleaner than CLI-centric review cadence.
      If §2 #1 chose A2, follow suit for consistency. If §2
      #1 chose A1 (in-repo extraction), this rec can still
      choose A2 — the two decisions are not forced to match,
      but reviewers should note the divergence explicitly.

- [ ] **Package naming**:
      - Distribution (PyPI): `grok-client`.
      - Import: `grok_client`.
      - Avoid `grok-sdk` (that name belongs to xAI's own SDK
        and colliding with it is confusing).

- [ ] **Scope: Python-first, JS-second-or-never.** The two
      JS implementations (`grok-install`/browser,
      `x-platform-toolkit`/inlined) are out of scope for
      v0.1.0. Document this in the README as a **deliberate
      choice**, not an oversight. Two honest paths for JS:
      - **JS-never**: browser-flavoured Grok invocations stay
        per-repo; the toolkit's inlined client is a constraint
        of the single-file-HTML format the toolkit ships. A
        shared JS package would need a build step those tools
        don't have.
      - **JS-later**: if/when a need emerges, extract a
        sibling `grok-client-js` package. Out of scope for
        this rec; captured in README roadmap.

- [ ] **Pin library deps.** Runtime: `xai-sdk` pinned at
      exact version (this is the point — the whole ecosystem
      pins here). `httpx` pinned. `pydantic>=2,<3`. No other
      runtime deps. Dev deps follow §2 #18's CI-template
      discipline.

- [ ] **Ship v0.1.0 to PyPI** via Trusted Publisher config
      (same pattern §2 #7 Part A establishes for
      `grok-install-cli`). Tag `v0.1.0`. GitHub Release with
      generated notes.

- [ ] **License**: Apache-2.0 (ecosystem convention
      post-v1.2.0).

- [ ] **Repo governance** (if A2): seed with `README.md`,
      `LICENSE`, `CHANGELOG.md`, `SECURITY.md` (points at
      `grok-install/SECURITY.md`), `CONTRIBUTING.md`,
      `.github/CODEOWNERS`, `.github/workflows/ci.yml`
      (adopt §2 #18's CI template from day one, same as §2
      #17's bootstrap pattern).

- [ ] **Test discipline**: `pytest --cov-fail-under=85` +
      `mypy` strict + matrix over Python 3.10/3.11/3.12
      (matches §2 #18 template).
      Include a **recorded-cassette** test suite that pins
      SDK behaviour without hitting the live API on every
      CI run. Use `vcrpy` or a hand-rolled fixture pattern;
      either works. Live-API tests gated behind an
      `XAI_API_KEY` secret + an opt-in workflow.

- [ ] **Maintainer roster**: name at least two maintainers
      in `CODEOWNERS`. Shared libraries consumed by 3+ repos
      with one maintainer are governance debt; make it
      visible.

### Part B — Feature surface (v0.1.0 = current-implementation parity)

v0.1.0 covers exactly what the two Python implementations
(`grok-install-cli` via `runtime/` + `integrations/` and
`grok-build-bridge/xai_client.py`) currently do — no new
features. Parity, not ambition. Extensions land post-v0.1.0
as each consumer's needs surface.

Indicative public API (finalised in the v0.1.0 PR):

```python
from grok_client import (
    GrokClient,              # primary entry
    AsyncGrokClient,         # asyncio variant
    ClientConfig,            # auth + retry + rate-limit config
    Message,                 # dataclass: role, content, tool_calls
    ToolDecl,                # dataclass: tool function schema
    StreamChunk,             # dataclass: delta / usage / finish_reason
    GrokAPIError,            # base exception
    RateLimitError,          # 429 with Retry-After semantics
    AuthError,               # 401 / 403
    ServerError,             # 5xx (retryable)
    TimeoutError,            # client-side timeouts
)
```

- [ ] **Auth**:
      - `ClientConfig(api_key, org_id?, base_url?)` —
        `api_key` sourced from env `XAI_API_KEY` by default;
        explicit arg wins; missing both raises `AuthError`
        at client init, not on first call.
      - Bearer header + org header (if set) injected
        uniformly.
      - Never echo the key to logs; `repr(ClientConfig)`
        masks it.

- [ ] **Retries**:
      - Default policy: **3 retries**, exponential backoff
        with jitter, retry on 429 (honouring `Retry-After`),
        500, 502, 503, 504, and `TimeoutError`. No retry on
        auth or 4xx-other (bad request, not-found).
      - Configurable via `ClientConfig(retry=RetryPolicy(
        max_retries=3, backoff_base=0.5, max_backoff=30))`.
      - Observable: each retry emits a structured log line
        (`event=retry attempt=N reason=...`). Callers can
        intercept via `logging`.

- [ ] **Streaming**:
      - `chat(stream=True)` returns an iterator (or async
        iterator) of `StreamChunk`.
      - Chunks carry `delta` (new content), `tool_call_delta`
        (partial tool-call JSON), `usage` (on final chunk),
        and `finish_reason`.
      - Decode is the one place the ecosystem has silently
        diverged today — pin the SSE handling here and every
        consumer inherits correctness.

- [ ] **Rate limiting**:
      - Parse `X-RateLimit-Remaining` + `X-RateLimit-Reset`
        on every response; expose via
        `client.last_rate_limit` for callers that want to
        self-throttle.
      - Automatic pre-emptive slow-down when
        `remaining / window < threshold` (off by default;
        opt-in via `ClientConfig`).
      - `RateLimitError` carries the `retry_after` seconds
        value from the `Retry-After` header so the retry
        policy consumes it correctly.

- [ ] **Tool calling**:
      - `ToolDecl` matches the SDK's function-schema shape.
      - `Message.tool_calls` is a list of tool invocations
        the model requested; each has `id`, `name`,
        `arguments` (parsed JSON).
      - Helpers: `ToolDecl.from_callable(fn)` introspects a
        Python function's signature to emit the schema —
        reduces per-consumer boilerplate.

- [ ] **Structured output (optional, v0.1.0)**:
      - `chat(response_format={"type": "json_schema", ...})`
        passthrough to the SDK.
      - Result returned as `dict`; callers can validate via
        `pydantic` or `jsonschema` per preference.

- [ ] **SDK-version pin**:
      - `xai-sdk == <exact>` pin in this package's
        `pyproject.toml`. Bumping the SDK is a deliberate
        PR here; consumers inherit via version-bumping this
        package.
      - Document the SDK pin philosophy in `README.md`: this
        package is the ecosystem's SDK pin point; consumers
        should NOT pin `xai-sdk` directly.

- [ ] **Non-goals for v0.1.0** (documented in README):
      - Caching / memoisation of completions.
      - Automatic batching of requests.
      - Cost tracking.
      - Prompt templating / chain composition (that's
        agent-framework territory; see §2 #17 for the
        orchestra repo).
      - JS / TypeScript port (see Part A JS-later path).

- [ ] **Model-ID handling**:
      - Models are passed as strings
        (`GrokClient.chat(model="grok-4.20", ...)`); no
        enum gatekeeping in v0.1.0. The ecosystem's single
        hard-coded pin today (`grok-4.20` in
        `grok-build-bridge/xai_client.py`) moves to
        consumer-side config, not into this package.
      - Helpful but non-gating: `grok_client.MODELS`
        constant listing known model IDs for discoverability.
        Consumers can pass arbitrary strings; this package
        does not validate.

### Part C — Consumer adoption sequencing

Each consumer gets its own follow-up PR (or linked issue +
PR) filed **after** `grok-client` v0.1.0 ships to PyPI. Do
NOT pre-file the follow-ups — Part B's API shape may shift
during v0.1.0 review.

Consumer sets:

**Python consumers (current implementations — §9.A rows 2, 3):**

- [ ] **Consumer 1 — `grok-install-cli`**: refactor
      `src/grok_install/{runtime,integrations}/` Grok-calling
      surface to be thin wrappers around `grok_client`.
      Drop per-module retry/auth/streaming logic; import from
      `grok_client`. Keep the CLI's subcommand surface
      unchanged; only the implementation moves. **First
      adopter** because this repo has the most mature
      Python client implementation today; porting it first
      validates that `grok_client`'s API covers real-world
      needs.

- [ ] **Consumer 2 — `grok-build-bridge`**: refactor
      `xai_client.py` to be a thin wrapper around
      `grok_client`. The LLM-audit safety layer in
      `xai_client.py` is the subtlest consumer (it does
      structured-output decoding from Grok); if the bridge
      ports cleanly, the API covers every realistic case.
      Drop the hard-coded `grok-4.20` model ID — move to
      bridge-side config. **Second adopter** for the same
      "most divergent implementation" reason §2 #1 gave.

**Python consumers (future — §2 #2's "Affected repos" aspiration):**

- [ ] **Consumer 3 — `awesome-grok-agents`**: the gallery's
      Python scripts (`validate_template.py`,
      `mock_run_template.py` — see audit 06 §5) don't call
      Grok today; they validate templates. Once §2 #12
      lands (replace stub with real CLI), the gallery
      transitively consumes `grok_client` via the CLI. No
      direct dependency in `awesome-grok-agents` — flag in
      Notes so this is explicit.

- [ ] **Consumer 4 — `grok-agents-marketplace`**: Next.js /
      TypeScript. Does not consume this Python package. If
      the marketplace develops server-side Python Grok calls
      in the future (e.g. a background-job worker), it will
      consume `grok_client` at that time. Not a v0.1.0
      consumer; flag in Notes.

**JS implementations (current but out of scope):**

- [ ] **`grok-install` browser invocation (§9.A row 1)**:
      NOT a v0.1.0 consumer. Browser-side Grok calls stay
      per-repo until/unless a JS port lands (Part A's
      JS-later path).

- [ ] **`x-platform-toolkit` inlined JS (§9.A row 4)**: NOT
      a v0.1.0 consumer. The single-file-HTML tools have no
      build step; a shared JS package would need one. Out
      of scope.

**Cross-cut verification after Python consumers land:**

- [ ] **Behavioural regression check**: build a shared
      cassette test fixture (5–10 realistic Grok API
      exchanges: chat, streaming, tool-calling,
      rate-limit-hit, auth-fail) and run it against both the
      pre-refactor and post-refactor implementations in CLI
      + bridge. Zero observable difference in output is the
      pass criterion. Any divergence found: either a bug in
      `grok_client` (fix) or a per-implementation quirk the
      consumer was silently relying on (surface explicitly
      in `grok_client` issue tracker).

- [ ] **SDK-version floor check**: after both CLI + bridge
      adopt, the ecosystem has **one** `xai-sdk` pin. Audit
      each repo's lockfile / `pyproject.toml` to confirm
      `xai-sdk` appears only as a transitive through
      `grok-client`. Any direct pin is a bug.

- [ ] **Document the adoption rollout** in a follow-up
      issue or ADR (`grok-client/docs/adr/0002-…`): which
      consumer adopted when, what quirks surfaced, what was
      upstream into `grok_client` as a result. Useful history
      for when §2 #11's permissive exemplar or §2 #17's
      orchestra bootstrap later adopts.

- [ ] **Per-consumer CHANGELOG entries**. Each consumer's
      CHANGELOG `[Unreleased]` cites the `grok-client`
      version adopted and flags any behavioural diff visible
      in the cassette suite. Mirrors §2 #1's adoption
      discipline.

## Notes

- **L-effort sizing honesty.** Auth / retries / streaming /
  rate-limit are each non-trivial. Tool calling + structured
  output add weeks. Consumer-side migration (refactor + diff
  the cassette suite + land in a consumer release) is weeks
  more. Budget 4–8 focused weeks for v0.1.0 + both Python
  consumers adopting. Splitting into PRs per Part (A: skeleton,
  B: feature, C: consumers) is encouraged; partial landings
  are still value-positive.

- **Relationship to §2 #1 (`grok-safety-rules`).** Parallel
  extraction pattern. The two packages are independent but
  the ownership-boundary decisions (A1 vs. A2) should agree
  for ecosystem consistency. If §1 ships A2 (new repo)
  first, §2 should follow. Naming: `grok-safety-rules` +
  `grok-client` is the consistent dash-separated pair.

- **Relationship to §2 #7 (`grok-install-cli` tagged releases).**
  §7 establishes the ecosystem's Trusted-Publisher pattern
  for PyPI. This rec adopts the same pattern. If §7 lands
  first, copy the workflow verbatim. If this rec lands first,
  §7's draft can reference this rec's workflow as the
  template.

- **Relationship to §2 #17 (orchestra bootstrap).** §17's
  Part A lists this shared client as a day-one dependency
  (falling back to `httpx` if `grok-client` isn't shipped
  at bootstrap time). The two recs are independent; both
  shipping is cheaper in aggregate than either alone.

- **Relationship to §2 #12 (replace stub).** §12's v0.1.0
  closes the stub/real-CLI gap in `awesome-grok-agents`.
  Once §12 lands, the gallery transitively consumes
  `grok-client` via the CLI. No direct dependency in
  `awesome-grok-agents`; no action needed there for this
  rec.

- **JS port is a real question, not a deferral-forever.**
  If/when `grok-install`'s browser playground grows beyond
  its current shape, or `x-platform-toolkit` tools are
  rewritten with a build step, a sibling `grok-client-js`
  package (same feature surface, TypeScript, published to
  npm) is the honest answer. README's "Scope: Python-first,
  JS-second-or-never" section documents this so it's not
  forgotten.

- **Model-ID churn discipline.** xAI's model catalogue moves
  (Grok-4.20, Grok-4.25, …). This package does NOT hard-code
  model IDs (deliberate — audit 09 §9 row 3 calls out the
  bridge's current hard-coded `grok-4.20` as a risk).
  Consumer-side config is the right place for the pin. The
  `grok_client.MODELS` constant is discoverability only.

- **Out of scope here.**
  - A TypeScript port (captured in "JS-later" path above).
  - Prompt templating / chain composition (agent-framework
    territory; see §2 #17).
  - Cost tracking (separate concern; may pair with §2 #17's
    orchestra telemetry).
  - xAI-SDK-version auto-bumping (Renovate handles the pin
    update; this package decides when to land it).
  - HTTP-transport alternatives (`httpx` is the chosen
    backend; `requests` or `aiohttp` ports are not v0.1.0).

- **Filing strategy.** Coordination issue in
  `grok-install-cli` (if A1) or first issue on the new
  `grok-client` repo (if A2). Consumer adoption follow-ups
  (Part C) open only after v0.1.0 ships. Pattern identical
  to §2 #1's filing strategy.

- **Non-speculative draft.** Unlike Session 2 drafts, this
  one is NOT gated on an in-repo prerequisite. All
  source-audit data lives in Phase 1A. Filing this upstream
  does not wait on anything in `phase-1b/drafts/`.

