# PROGRESS

Living log of what shipped and why. Most recent entries first.

## 2026-04-23 — Phase 3 §1: cli-runner

**Shipped** a single-invocation entry point that turns a Python case
file into a verdict doc, closing the loop between Phase-2 config /
evals / telemetry and a CI-runnable command.

* **`frok.cli.run`** — `frok run <case-file>` wires
  `load_default_config(file=…, profile=…)` → builds the full stack
  via the Phase-2 builders → executes the case set through
  `EvalRunner` → prints (or writes) `EvalReport.to_markdown()`.
  Flags: `-c/--config`, `-p/--profile`, `-o/--output`,
  `--summary-json`, `--fail-on-regression`.
* **Case-file conventions.** A `.py` file must expose either
  `CASES: list[EvalCase]` (plain list) or
  `build_cases(config) -> list[EvalCase]` (parameterised by the
  resolved `FrokConfig`). Optional `make_client(config, sink) ->
  GrokClient` lets CI wire a stub transport; without it the default
  factory uses `frok.clients.transports.urllib_transport` + the
  config's `telemetry.sink` fan-out (`MultiSink(in_memory,
  config_sink)` so scorers keep their per-case InMemorySink while
  operators still get JsonlSink captures when configured).
* **`frok.clients.transports.urllib_transport`** — a stdlib-only
  `Transport` that runs `urllib.request` under `asyncio.to_thread`.
  Zero deps, modest throughput, good enough for a CLI and CI. Swap
  in httpx/aiohttp behind the Protocol when volume arrives.
* **Entry points** — `python -m frok` via `src/frok/__main__.py`
  and a console script (`[project.scripts] frok = "frok.cli:main"`).

**Verification.** `python3 -m pytest -q` → 193 passed in 0.41s (12
new). Tests cover: CASES-list + `build_cases(config)` paths,
`make_client` override, missing case-file / missing CASES / empty
CASES errors, `--fail-on-regression` exit-code behaviour on pass +
fail, `-o` writing Markdown to a nested path (and suppressing
stdout), `--summary-json` shape, default factory raising when
`client.api_key` is unconfigured, and the argparse shape.

**Decisions / trade-offs.**
* Case files are Python, not YAML/TOML. Python gives direct access
  to `EvalCase`, `Scorer`, and `GrokMessage` without a mini-DSL;
  `build_cases(config)` is the escape hatch when cases need to
  parameterise themselves.
* `ConfigError` and `CliError` are both caught at `main()` boundary
  and printed as ``frok: error: <msg>`` so operators get a single
  consistent failure surface regardless of whether the problem is
  config shape, missing case file, or api-key.
* The default factory fans out per-case InMemorySink ⊕
  ``telemetry.sink`` via `MultiSink`. Scorers still get their
  hermetic in-memory view; operators still get persistent capture
  when they want it. One flag, two observers.

**Next suggested action:** `Extend Phase 3 with \`frok trace
inspect <jsonl>\`: a sibling subcommand that loads a JsonlSink
capture via \`read_jsonl\`, reconstructs the trace tree, and prints
a summary (per-span durations, error hot-spots, top tool
invocations). Closes the telemetry <-> eval loop for post-hoc
regression triage.`

## 2026-04-23 — §2 #9 config-loader

**Shipped** `frok.config`: a typed, layered config surface that's the
single place the rest of the stack reads runtime settings from.

* **`FrokConfig`** (`schema.py`) — one top-level dataclass with
  sub-dataclasses per concern: `ClientConfig`, `SafetyConfig`,
  `TelemetryConfig`, `MemoryConfig`, `MultimodalConfig`. No logic,
  just shape. A `SECTIONS` map is exposed so the loader can
  enumerate fields programmatically.
* **`load_config(file=, env=, cli=, profile=)`** (`loader.py`) —
  deterministic precedence: defaults < file < env < CLI. File is
  JSON (always) or TOML (stdlib `tomllib`, 3.11+) detected by
  extension. Env vars are `FROK_<SECTION>_<FIELD>` with per-field
  type coercion (including `tuple[str, ...]` from comma lists). CLI
  accepts either a nested dict or a flat dict keyed by
  ``"section.field"``; `None` values are ignored so forwarding
  `vars(argparse.Namespace())` Just Works.
* **Profiles** — a config file may declare `[profiles.NAME]` blocks;
  when a profile is selected (explicit arg → CLI → env
  `FROK_PROFILE` → file's own `profile = "..."`), that section is
  deep-merged on top of the base. Dev / prod swap is one flag.
* **Builders** (`builders.py`) — `build_safety_ruleset`,
  `build_telemetry_sink`, `build_tracer`, `build_client`,
  `build_memory_store`, `build_multimodal_adapter`. Each consumes
  `FrokConfig` + optional overrides, validates required fields
  (e.g. `client.api_key`, `telemetry.path` for jsonl), and returns
  the live component. Downstream code keeps taking narrow types —
  nothing else needs to know `FrokConfig` exists.
* **`load_default_config(**overrides)`** — the ergonomic wrapper that
  sources `os.environ` + optional `FROK_CONFIG_FILE` + explicit
  overrides. `load_config()` with all `None` args stays hermetic for
  tests.

**Verification.** `python3 -m pytest -q` → 181 passed in 0.38s (33
new). Tests cover defaults, env coercion across every type, JSON +
TOML file loading, nested + flat CLI overrides, file-vs-env-vs-CLI
precedence, profile merging via arg and env, unknown-section /
unknown-field / bad-shape errors, and per-builder wiring (safety
rule exclusion, sink construction, memory disabled-by-default,
explicit tracer override, end-to-end full-stack build from one
config).

**Decisions / trade-offs.**
* Opted against auto-reading `~/.frok/config.toml`. `load_config()`
  is inert without explicit args; `load_default_config()` is the
  "do the thing" entry point. Splitting them keeps tests hermetic
  without an env-scrubbing harness.
* Memory defaults to `enabled=False`. Forcing opt-in keeps
  first-time callers from accidentally writing a SQLite file into
  their working directory.
* Unknown sections / fields *fail loudly* at load time rather than
  being silently ignored — typos in config are the single biggest
  "huh, why isn't X working" time-sink I've seen, and we have the
  schema so we may as well police it.

**Next suggested action:** `Continue Phase 3 with a CLI runner that
wires load_default_config into a \`frok run <case-file>\` entry
point driving the §2 #8 eval harness, so a single invocation loads
config -> builds client/memory/adapter -> runs a case set -> prints
the markdown verdict doc.`

## 2026-04-23 — §2 #6 agent-team-runtime

**Shipped** `frok.team`: a deliberately small multi-agent scheduler
that composes every Phase-2 wrapper (`MemoryAgent`,
`MultimodalAdapter`, `ToolOrchestrator`, bare `GrokClient`) as a
named `Role` inside one transcript-driven loop.

* **`TeamMessage`** — frozen `(from_, to, content, meta, step)`; the
  only data type that flows through the system.
* **`Role`** — name + an async `respond(transcript) -> str`. The
  runtime passes each role only the messages addressed to it (or
  `to="all"`) so roles don't have to filter.
* **`TeamRuntime.run(initial)`** — loops until the router returns
  `None` (clean termination → `to="user"` on the final message) or
  `max_hops` trips (raises `TeamError`). Each hop is wrapped in a
  `team.hop` span nested under a `team.run` span; both share a
  `trace_id` and carry `hops` / `terminated` so evals can regress on
  the team tree alongside `grok.chat` / `tool.invoke` children.
* **Routers** — three built-ins:
  * `pipeline_router(["researcher", "writer", "editor"])` — fixed
    linear pipeline, terminates after the last role.
  * `callback_router(fn)` — identity passthrough for hand-written
    supervisors.
  * `loop_until(predicate, next_=..., max_rounds=...)` — keep
    dispatching to `next_` until either the predicate matches on the
    reply or the per-sender round cap is hit.
* **Role adapters** — `chat_role_from_client(name, client, system=...)`
  flattens the transcript into alternating `assistant` / `user`
  turns with `[sender->recipient]` prefixes so the model can see the
  hand-off. `echo_role(name)` is the deterministic test fixture.

**Verification.** `python3 -m pytest -q` → 148 passed in 0.31s (12
new). Tests cover single-role termination, unknown-role guard,
pipeline walking, supervisor-style branching, `loop_until` predicate
and round-cap paths, `max_hops` error + span metadata, per-role
transcript filtering, and a composition test that runs two
`GrokClient`-backed roles and asserts the telemetry tree
(`team.run` → `team.hop` → `grok.chat`) reconstructs under one
`trace_id`.

**Decisions / trade-offs.**
* Replies are routed **directly** to the next role (not via a
  supervisor indirection) so every role's filtered transcript
  includes its predecessor's hand-off. A terminal reply is addressed
  to `"user"` — the caller.
* The probe `TeamMessage` passed to the router has `to=""`; it's the
  router's job to decide. This keeps the router signature from
  depending on prior routing state.
* No DSL for inter-role protocols. Roles are async callables,
  routers are async callables, transcripts are lists. If a team
  needs custom protocol logic it lives in user code, not the
  runtime.

**Next suggested action:** `Continue Phase 2 with §2 #9 config-loader:
a layered config loader (env vars -> file -> CLI overrides) that
produces a single typed \`FrokConfig\` object, wires the default
\`GrokClient\` / \`MemoryStore\` / \`MultimodalAdapter\` / tracer
instances from it, and makes it trivial to swap dev vs production
profiles without touching call sites.`

## 2026-04-23 — §2 #5 multimodal-adapter

**Shipped** `frok.multimodal`: a typed image + audio IO surface that
routes through `GrokClient` (so safety + telemetry + retries come
along for free) and falls back to short text descriptors when a
modality is disabled.

* **`frok.multimodal.encoding`** — MIME tables for the image formats
  Grok actually accepts (png / jpeg / gif / webp / bmp / tiff) and
  audio formats (wav / mp3 / m4a / flac / ogg / opus / webm), plus a
  `to_data_url()` helper + base64 encoder. Zero deps.
* **`ImageRef` / `AudioRef`** — frozen dataclasses with three
  consistent factories each: `from_path`, `from_bytes`, `from_url`.
  `to_content_part()` emits the OpenAI-compatible chat content part
  (URLs stay as URLs, bytes/paths become `data:` URLs). Audio has a
  sibling `to_transcribe_payload()` for the voice endpoint.
  `describe()` gives a short text fallback (`alt_text` first, then
  URL / path / bytes summary).
* **`MultimodalAdapter`** — wraps a `GrokClient`. Public API:
  * `describe_image(image, prompt=...)` — one-shot vision chat.
  * `chat([parts...])` — mixed text + images + audio.
  * `transcribe_audio(audio)` — routes to a configurable endpoint
    (default `/audio/transcriptions`) via the new
    `GrokClient.request_json()` helper; returns descriptor when voice
    is disabled so callers always get *something*.
  * `AdapterConfig` toggles vision / voice, configurable fallback
    prefixes, transcribe path, voice model. Default is
    vision-enabled, voice-disabled.
* **`GrokMessage.parts`** — new optional `tuple[dict, ...]` carrying
  OpenAI-style content parts. When set, safety pre-flight rewrites
  only `{"type": "text"}` parts and leaves image / audio parts
  untouched. The payload emits the parts list as `content`. Safety
  blocks on any text part short-circuit before the network.
* **`GrokClient.request_json(path, payload)`** — public POST for
  non-chat endpoints (audio / embeddings / …). Bypasses chat safety
  but inherits retries, auth, and the tracer (`grok.request` span).

**Verification.** `python3 -m pytest -q` → 136 passed in 0.37s (25
new). Tests cover MIME/format detection, three-way ref factories,
data-URL round-trips, vision-enabled + vision-disabled fallback,
voice-enabled endpoint routing (base64 + model name + path), voice-
disabled descriptor path, safety rewriting text parts while leaving
image parts alone, and block-before-network on unsafe text parts.

**Decisions / trade-offs.**
* Adapter builds exactly one user message carrying a list of content
  parts. Multi-turn multimodal chats are still one `client.chat`
  call each — no hidden state in the adapter.
* Audio transcription currently expects a JSON endpoint returning
  `{"text": "..."}`. If a real xAI voice endpoint takes multipart,
  `GrokClient.request_json` is the narrow hook to swap (or add a
  sibling `request_multipart`). Tests pin the JSON shape so the swap
  is observable.
* Fallback descriptors are surfaced as plain text parts, not system
  prompts, so they flow with the user's other text in order — a
  vision-disabled model still sees the image in the "right place"
  relative to the prompt.

**Next suggested action:** `Continue Phase 2 with §2 #6 agent-team-
runtime: a lightweight multi-agent scheduler that composes multiple
MemoryAgent / MultimodalAdapter / ToolOrchestrator instances as named
roles, routes messages between them, and reports a run trace through
the telemetry sink so §2 #8 evals can regress the team's behaviour.`

## 2026-04-23 — §2 #8 eval-harness

**Shipped** `frok.evals`: declarative cases, composable scorers, a
runner that re-plays through any `GrokClient`, and a baseline-trace
differ that diffs captured `JsonlSink` runs against live candidates.

* **`frok.evals.case`** — `EvalCase` (messages, tools, scorers,
  optional baseline path, max-steps, dry-run), `Observation`
  (final response + invocations + full event stream + aggregates like
  `total_tokens` / `total_latency_ms` / `tool_call_order`), `Score`
  (ok / fail factories), `EvalResult`, `EvalReport` with
  `to_summary()` and `to_markdown()` verdict rendering.
* **`frok.evals.scorers`** — 10 composable, pure-function scorers:
  * truthfulness: `AnswerContains`, `AnswerMatches`, `AnswerAbsent`,
    `NoSafetyBlocks`
  * tool-behavior: `ToolCalled` (with count), `ToolNotCalled`,
    `ToolArgsSubset`, `ToolSequence` (prefix match)
  * perf / trace: `TokensWithin`, `NoErrors` (covers both run-level
    exceptions and any errored span)
* **`frok.evals.runner.EvalRunner`** — factory-per-case pattern
  (`(sink) -> GrokClient`) so each case gets a fresh `InMemorySink`
  and independent state. Uses `ToolOrchestrator` when the case
  declares tools, otherwise a single `client.chat` call. Runner
  swallows exceptions into `Observation.error` so one bad case
  doesn't abort the report.
* **`frok.evals.baseline`** — `diff_against_baseline(obs, path)`
  reads a `JsonlSink` capture with `telemetry.read_jsonl`, compares
  the tool-call order, token totals, and error count, and marks
  `regressed=True` on tool-sequence divergence or new errors (token
  deltas alone do not regress). The runner escalates
  `regressed=True` to an overall case failure.
* **Tracer tweak** — `SpanHandle.fail(reason)` lets callers mark a
  span as errored without re-raising. Wired through the tool
  orchestrator's caught-exception paths so "model recovers from a
  handler exception" still surfaces to `NoErrors` as a regression.

**Verification.** `python3 -m pytest -q` → 111 passed in 0.34s (21
new). The runner tests exercise both paths (chat-only + tools),
handler-error recovery, and the full Markdown-report shape.

**Decisions / trade-offs.**
* Scorers are *pure callables*, not a class hierarchy — keeps
  composition trivial (`scorers=[AnswerContains("42"),
  ToolCalled("add")]`) and sidesteps registration overhead.
* Baseline regressions check structural behaviour (tool order +
  errors), not tokens. Token deltas are reported for visibility but
  a longer answer shouldn't fail a regression test when the answer
  is still right.
* No case-file format yet (YAML/TOML) — cases are Python values.
  Fine for §2 #8 scope; a format loader is a cheap follow-up once
  real cases accumulate.

**Next suggested action:** `Continue Phase 2 with §2 #5 multimodal-
adapter: a typed IO surface that accepts images (path / bytes /
URL) and audio, routes them to Grok's vision + voice endpoints
through the GrokClient transport, and falls back to a text
description when a modality is unsupported.`

## 2026-04-23 — §2 #7 telemetry

**Shipped** `frok.telemetry` and wired it into every Phase-2 producer so
§2 #8 evals can regress on structured traces.

* **`frok.telemetry.sink`** — canonical `Event` dataclass (`ts`,
  `trace_id`, `span_id`, `parent_span_id`, `kind`, `name`,
  `duration_ms`, `data`, `error`) plus four sinks:
  * `NullSink` — default; tracers fast-path around it so the
    zero-consumer case is free.
  * `InMemorySink` — collects events with `find` / `spans` / `errors`
    query helpers; the shape the eval harness will consume.
  * `JsonlSink` — append-only newline-delimited JSON, thread-safe, with
    a `read_jsonl()` replay helper.
  * `MultiSink` — fan-out across several sinks.
* **`frok.telemetry.tracer`** — `Tracer.span(name, **attrs)` is an async
  context manager that emits `span.start` + `span.end` and records
  parent/child through `contextvars`. Exceptions are captured on the
  span as `error` and re-raised. A `SpanHandle.set(**kwargs)` lets
  producers attach measurements (tokens, hit-count, …) once known. The
  `NullSink` fast-path short-circuits all allocation when no consumer
  is attached.
* **Wiring** (all backwards-compatible — defaults keep the null tracer):
  * `GrokClient.chat` → `grok.chat` span with `model`,
    `message_count`, `has_tools`, `prompt_tokens`, `completion_tokens`,
    `total_tokens`, `tool_calls`, `finish_reason`, `safety_findings`,
    plus a `safety_blocked` attr on ingress/egress blocks.
  * `MemoryStore.remember/recall/forget` → `memory.remember`,
    `memory.recall` (with `candidates` / `hit_count`), `memory.forget`.
  * `ToolOrchestrator` → root `tool.run` span wrapping the loop and
    a nested `tool.invoke` per call (`tool`, `call_id`, `dry_run`,
    `error_kind`, `result_len`). Nested spans inherit `trace_id` so
    a full run reconstructs as a single tree.

**Verification.** `python3 -m pytest -q` → 90 passed in 0.40s (18 new).
Integration tests pin the event shape + nesting contract so §2 #8 can
rely on it.

**Decisions / trade-offs.**
* Clock + id generator are injectable on `Tracer` — tests want
  determinism; production gets `time.time` + `secrets.token_hex(8)`.
* No sampling / batching yet. `JsonlSink` flushes on every event; if it
  becomes a bottleneck we can add buffering behind the same interface
  without touching producers.
* Span data is deliberately small (ints, floats, short strings) so it
  can survive JSON round-trips. No message bodies / tool args are
  emitted — PII already leaks into logs faster than people think.

**Next suggested action:** `Continue Phase 2 with §2 #8 eval-harness:
a deterministic replay/diff runner that re-plays a captured JsonlSink
trace through a candidate model/client, scores truthfulness +
tool-behavior regressions, and produces a compact verdict doc.`

## 2026-04-23 — §2 #4 tool-use-orchestrator

**Shipped** `frok.tools` + tool-use plumbing on `GrokClient`.

* **`GrokClient` / `GrokMessage` / `GrokResponse` extension**
  * New `ToolCall` dataclass (`id`, `name`, `arguments` as a JSON string).
  * `GrokMessage` carries optional `tool_calls` + `tool_call_id`; its
    payload emits `content: null` alongside `tool_calls` as the xAI /
    OpenAI spec expects for assistant turns.
  * `GrokResponse` exposes `tool_calls` and `finish_reason`. Safety
    pre-flight now preserves `tool_calls` + `tool_call_id` across its
    rebuild (fix caught by tests).
* **`frok.tools.schema`** — zero-dep Draft-07 subset validator (type,
  enum, required, additionalProperties, items, min/max, length) plus a
  `infer_schema(fn)` that turns a Python signature into a JSON Schema —
  handles `Optional`, PEP-604 `A | B`, `Literal`, `Enum`, `list[T]`,
  `dict`, and defaults.
* **`frok.tools.registry`** — `Tool`, a `@tool` decorator (param/no-param
  forms), and `ToolRegistry` with `.spec()` (OpenAI-compatible) and
  `.dispatch(name, args, dry_run=...)` that validates args, awaits
  async handlers, stringifies structured results, and honours
  `side_effects=False` / a custom `dry_run_handler`.
* **`frok.tools.orchestrator`** — `ToolOrchestrator` runs the full loop
  against `GrokClient`: send → if `tool_calls` → dispatch each → append
  assistant + tool messages → repeat until `finish_reason != tool_calls`
  or `max_steps`. Bad-arg / unknown-tool / handler-raised errors are
  surfaced *back to the model* as tool-message content so it can
  recover rather than crashing the run.

**Verification.** `python3 -m pytest -q` → 72 passed in 0.22s (30 new).

**Decisions / trade-offs.**
* Parallel `tool_calls` in one turn execute sequentially on purpose —
  deterministic ordering matters more than latency at this stage, and
  `asyncio.gather` is a one-line swap when it doesn't.
* Dry-run policy is per-tool: side-effectful tools stub to a predictable
  `[dry-run] name({args})` string unless they provide a `dry_run_handler`;
  read-only tools (`side_effects=False`) run for real. This lets the
  loop still make forward progress under dry-run.
* Schema inference stays permissive on unknown annotations (empty
  schema) rather than failing import-time — a broken annotation
  shouldn't break registration.

**Next suggested action:** `Continue Phase 2 with §2 #7 telemetry — a
pluggable structured-log / trace sink that every GrokClient.chat,
MemoryStore op, and ToolOrchestrator invocation can emit to, so #8
evals can regress on runs later.`

## 2026-04-23 — §2 #3 persistent-memory

**Shipped** `frok.memory` on top of Phase 2 #1/#2.

* **`Embedder` protocol + `HashEmbedder`** (`memory/embedder.py`)
  * Deterministic feature-hashing fallback (blake2b → signed bucket),
    L2-normalised. Zero deps, zero network — lets tests and offline
    smoke runs produce meaningful cosine distances without a real
    embedding provider. `Embedder` is a `@runtime_checkable` Protocol so
    real xAI/Voyage/OpenAI embedders drop in.
* **`MemoryStore`** (`memory/store.py`)
  * SQLite-backed, embeddings stored as packed float32 BLOBs alongside
    rows. Cosine similarity computed in Python — adequate for the
    small-agent case; swap to sqlite-vss / ANN behind the same surface
    when §2 #7 telemetry shows it's needed.
  * API: `remember`, `remember_many`, `forget`, `recall` (k, kind, time
    window, min-score), `recent`, `count`. Persists across reopen.
* **`MemoryAgent`** (`memory/agent.py`)
  * Wraps `GrokClient`. Each turn: sanitise user text via the client's
    ruleset, recall top-k similar memories, inject them as a system
    message, send to Grok, then store both turns (sanitised user +
    assistant + usage metadata). PII-blocked prompts never reach the
    store or the network.

**Verification.** `python3 -m pytest -q` → 42 passed in 0.22s (18 new).

**Decisions / trade-offs.**
* Kept a single long-lived SQLite connection per `MemoryStore`. Simpler
  and fine for single-agent use; a pool is trivial to add later.
* Default recall `min_score=0.1` in `MemoryAgent` — filters out the
  near-orthogonal junk the hash embedder produces on unrelated text.
  Real embedders will want a different threshold; it's a field on the
  agent.
* Chose to sanitise user text **before** recall so prompt-injection and
  PII shapes don't influence the recalled context either.

**Next suggested action:** `Continue Phase 2 with §2 #4 tool-use-
orchestrator: a Tool registry + dispatch layer that plugs into
GrokClient.chat(tools=...) and routes the model's function calls to
typed handlers, with schema validation and a dry-run mode.`

## 2026-04-23 — Phase 2 kickoff (branch `claude/super-ai-frok-phase-2-bWvah`)

**Shipped** §2 items #1, #2, #10 as a usable first slice of the Super AI
Frok core.

* **§2 #1 grok-safety-rules** (`src/frok/safety/rules.py`)
  * Declarative rule engine. Four built-ins: anti-sycophancy (REWRITE),
    no-overclaim (BLOCK), PII redaction for email/phone/SSN (REWRITE),
    prompt-injection (WARN).
  * `SafetyRuleSet.apply()` applies non-overlapping rewrites right-to-left
    so spans stay valid, and preserves original text on BLOCK.
* **§2 #2 grok-client** (`src/frok/clients/grok.py`)
  * Async `GrokClient` for xAI `/chat/completions`. Transport is a protocol
    (no hard httpx/aiohttp dependency) so it's trivially testable.
  * Exponential backoff + jitter on 429/5xx; 4xx other than 429 raise
    immediately. Lifetime prompt/completion token totals are tracked.
  * Pre-flight runs the ruleset over every inbound message; post-flight
    runs it over the model output. Callers can opt out with an empty
    ruleset.
* **§2 #10 content** (`src/frok/content/x_post.py`)
  * `normalize_post()` accepts X API v2 payloads (with or without
    `includes`) and loose scrape dicts, falling back to text extraction
    when `entities` is missing.
  * `thread_from_posts()` union-finds on `reply_to_id` + `conversation_id`
    and returns chronologically-sorted threads.
  * Media refs are deterministically ordered by `media_key`.

**Interpretation note.** The kickoff prompt referenced "§2 #10's content"
without a pre-existing ROADMAP. I interpreted #10 as X-platform content
ingestion because it's the most mission-aligned reading ("X real-time data
agents"). `ROADMAP.md` §2 #10 is marked as a chosen interpretation — if a
different #10 was intended, the module is self-contained and easy to
rename or replace.

**Verification.** `python3 -m pytest -q` → 24 passed in 0.08s.

**Decisions / trade-offs.**
* Kept zero runtime dependencies. Transport is injected; a production
  httpx adapter is a ~10-line follow-up, not a core concern.
* Safety rules are heuristic and deterministic by design — auditable
  first, classifier-augmented later (§2 #7 telemetry + §2 #8 evals).
* `XPost` is frozen so it's safe to hand across agent-team boundaries
  once §2 #6 lands.

**Next suggested action:** `Continue Phase 2 with §2 #3 persistent-memory
(episodic + vector store) backed by SQLite + a pluggable embedder, wired
through the grok-client for long-running agent context.`

## 2026-04-23 — repo bootstrap
Initial commit of master instructions and empty progress/changelog.
