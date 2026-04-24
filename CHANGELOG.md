# Changelog

All notable changes. Format loosely follows Keep a Changelog.

## [0.11.0] — 2026-04-23
### Added
- `frok.telemetry.analysis` — `build_tree(events)`, `summarize(events)`
  returning per-name stats + errored spans + top-tool aggregates, plus
  `summary_to_markdown` / `render_tree` / `summary_to_json` renderers.
- `frok trace inspect <jsonl>` subcommand — loads a `JsonlSink`
  capture, summarises it, and prints Markdown (or JSON via `--json`,
  or Markdown+tree via `--tree`). Flags: `-o/--output`, `--top`.
- Tests: 23 new (analysis functions + CLI paths); 216 total.

### Changed
- CLI refactor: top-level parser + `main()` now live in
  `frok.cli.__init__`; each subcommand module exports a
  `register(sub)` helper. `CliError` moved to `frok.cli.common`.
  Public imports (`CliError`, `build_parser`, `main`, `run_cmd`,
  `load_case_file`) unchanged.

## [0.10.0] — 2026-04-23
### Added
- `frok.cli` — `frok run <case-file>` entry point. Wires
  `load_default_config` → full-stack build → `EvalRunner` → prints
  `EvalReport.to_markdown()`. Flags: `-c/--config`, `-p/--profile`,
  `-o/--output`, `--summary-json`, `--fail-on-regression`.
- Case-file conventions: `CASES: list[EvalCase]` or
  `build_cases(config) -> list[EvalCase]`, plus optional
  `make_client(config, sink) -> GrokClient`.
- `frok.clients.transports.urllib_transport` — stdlib-only default
  `Transport` (urllib + asyncio.to_thread).
- Console script (`frok`) and `python -m frok` entry points.
- Tests: 12 new (CLI loader, exit codes, output paths, parser).
  193 total.

## [0.9.0] — 2026-04-23
### Added
- `frok.config` — typed `FrokConfig` with client / safety / telemetry
  / memory / multimodal sections; `load_config(file=, env=, cli=,
  profile=)` with deterministic layered precedence; JSON + TOML file
  support; `FROK_<SECTION>_<FIELD>` env mapping; nested + flat-dotted
  CLI overrides; profile-section merging; `load_default_config()`
  ergonomic wrapper. (§2 #9)
- Builders: `build_safety_ruleset`, `build_telemetry_sink`,
  `build_tracer`, `build_client`, `build_memory_store`,
  `build_multimodal_adapter` — one per component, each keyed off the
  single `FrokConfig`.
- Tests: 33 new (loader + builders); 181 total.

## [0.8.0] — 2026-04-23
### Added
- `frok.team` — `TeamRuntime` multi-agent scheduler with `Role` +
  `Router` primitives, three built-in routers (`pipeline_router`,
  `callback_router`, `loop_until`), and a `chat_role_from_client`
  helper that wraps any `GrokClient` as a role. Emits nested
  `team.run` / `team.hop` telemetry spans. (§2 #6)
- Tests: 12 new (routing, telemetry nesting, max-hops, role
  filtering, `GrokClient` composition); 148 total.

## [0.7.0] — 2026-04-23
### Added
- `frok.multimodal` — `ImageRef` + `AudioRef` with `from_path` /
  `from_bytes` / `from_url` factories, MIME & format detection,
  `to_content_part()` and `to_transcribe_payload()`, plus a
  `MultimodalAdapter` that wraps `GrokClient` and routes images
  through chat + audio through a configurable transcribe endpoint.
  `AdapterConfig` controls vision / voice toggles and fallback
  descriptors. (§2 #5)
- `GrokMessage.parts` — optional OpenAI-compatible multimodal content
  parts. Safety pre-flight rewrites only `type: text` parts; image /
  audio parts pass through. Block-before-network behaviour preserved.
- `GrokClient.request_json(path, payload)` — public POST helper for
  non-chat endpoints (emits its own `grok.request` telemetry span).
- Tests: 25 new (encoding, refs, adapter vision + voice paths, safety
  interaction, fallbacks); 136 total.

## [0.6.0] — 2026-04-23
### Added
- `frok.evals` — declarative `EvalCase`s, 10 built-in scorers
  (`AnswerContains`, `AnswerMatches`, `AnswerAbsent`, `NoSafetyBlocks`,
  `ToolCalled`, `ToolNotCalled`, `ToolArgsSubset`, `ToolSequence`,
  `TokensWithin`, `NoErrors`), an `EvalRunner` with a per-case
  `(sink) -> GrokClient` factory, and `EvalReport.to_markdown()` /
  `.to_summary()` verdict rendering. (§2 #8)
- `frok.evals.diff_against_baseline` — reads a captured `JsonlSink`
  trace and diffs tool-call order, token deltas, and error counts
  against a live `Observation`. (§2 #8)
- `SpanHandle.fail(reason)` on `frok.telemetry.Tracer` so caught-but-
  regressed work (e.g. a tool handler that raised) still shows up on
  the end span's `error` field.
- Tests: 21 new (scorers, runner, baseline diff); 111 total.

## [0.5.0] — 2026-04-23
### Added
- `frok.telemetry` — `Event` dataclass + four pluggable sinks
  (`NullSink`, `InMemorySink`, `JsonlSink`, `MultiSink`) and a
  contextvar-scoped `Tracer` with async `span()` context manager.
  `read_jsonl()` replay helper. (§2 #7)
- `GrokClient`, `MemoryStore`, and `ToolOrchestrator` now accept an
  optional `tracer` and emit structured spans:
  * `grok.chat` with token / safety / finish-reason attrs
  * `memory.remember` / `memory.recall` / `memory.forget`
  * `tool.run` wrapping nested `tool.invoke` spans; all share a
    trace_id so a full run reconstructs as one tree.
- Tests: 18 new (sinks, tracer semantics, cross-component integration);
  90 total.

## [0.4.0] — 2026-04-23
### Added
- `frok.tools` — JSON Schema validator + signature inference, `@tool`
  decorator, `ToolRegistry` with `.spec()` / `.dispatch()`, and
  `ToolOrchestrator` driving the full model → tool-call → result loop
  through `GrokClient`. Dry-run mode per-tool. (§2 #4)
- `GrokClient` now handles the tool-use wire format: `ToolCall`
  dataclass, `tool_calls` / `tool_call_id` on `GrokMessage`,
  `tool_calls` / `finish_reason` on `GrokResponse`.
- Tests: 30 new (schema, registry, orchestrator); 72 total.

### Fixed
- Safety pre-flight rebuild in `GrokClient.chat` no longer drops
  `tool_calls` / `tool_call_id` off messages mid-loop.

## [0.3.0] — 2026-04-23
### Added
- `frok.memory` — SQLite-backed `MemoryStore` with pluggable `Embedder`
  protocol and a zero-dep `HashEmbedder` fallback. (§2 #3)
- `frok.memory.MemoryAgent` wrapping `GrokClient`: sanitised recall,
  injected-context chat, automatic exchange storage. (§2 #3)
- Tests: embedder determinism + ranking, store recall / filters /
  persistence, agent recall-injection and PII-sanitisation. 42 total.

## [0.2.0] — 2026-04-23
### Added
- ROADMAP.md documenting Phase 2 (#1–#10).
- `frok.safety` — declarative alignment-rule engine with built-ins for
  anti-sycophancy, overclaim blocking, PII redaction, and prompt-injection
  detection. (§2 #1)
- `frok.clients.GrokClient` — async xAI `/chat/completions` client with
  injected transport, exponential-backoff retries, usage accounting, and
  pre/post-flight safety guarding. (§2 #2)
- `frok.content` — X-platform post normaliser (`normalize_post`) and
  thread reconstructor (`thread_from_posts`). (§2 #10)
- `pyproject.toml`, src/ layout, and a pytest suite (24 tests).
