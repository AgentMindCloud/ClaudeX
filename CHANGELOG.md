# Changelog

All notable changes. Format loosely follows Keep a Changelog.

## [0.39.0] — 2026-04-23
### Added
- `frok.evals.LatencyDeltaWithin(max_ms)` — second baseline-
  aware scorer, mirroring `TokenDeltaWithin` but on root-span
  `duration_ms`. Symmetric; construction rejects negative
  `max_ms`; `max_ms=0` is exact-parity.
- `diff_event_streams` output gained three keys:
  `{a_label}_latency_ms`, `{b_label}_latency_ms`,
  `latency_delta_ms`. Backwards-compatible — existing key
  assertions unchanged.
- Shared private `_load_baseline_diff` helper keeps the two
  baseline-aware scorers in lockstep on error paths.
- Tests: 21 new (5 diff-field + 16 scorer); 616 total.

## [0.38.0] — 2026-04-23
### Added
- `frok.evals.TokenDeltaWithin(max_delta)` — first baseline-
  aware scorer. Loads `case.baseline` via `read_jsonl`, reuses
  `diff_event_streams` from `frok.evals.baseline`, fails when
  `abs(observed_tokens - baseline_tokens) > max_delta`.
  Symmetric (catches runaway-long and bail-early answers);
  failure detail surfaces baseline + observed + signed delta;
  measure carries the signed delta for trend-scanning.
- Construction rejects negative `max_delta`; `max_delta=0`
  is allowed as exact-parity.
- Tests: 16 new (construction, no-baseline, missing-file,
  under / at / over threshold both directions, runner
  integration); 595 total.

## [0.37.0] — 2026-04-23
### Added
- `frok.evals.AnswerLength(min_chars=None, max_chars=None)`
  scorer — shape gate complementing content-based scorers.
  At least one bound required; construction validates
  non-negative bounds and `min <= max`. Scorer name reflects
  the active bounds (`>=N`, `<=M`, or `>=N,<=M`); measure
  carries the observed length.
- Tests: 17 new (4 construction errors + all three bound
  modes + bounds edges + no-final-response + name formatting
  + measure); 579 total.

## [0.36.0] — 2026-04-23
### Added
- `frok.evals.InvocationsWithin(max_count)` scorer — asserts
  the total number of tool invocations on a case stays at or
  below the threshold. Aggregate "don't loop forever" cap
  complementing `ToolCalled(..., times=N)`'s per-tool exact
  count. Inclusive at-limit; zero-invocations edge passes any
  non-negative threshold.
- Tests: 7 new (pass / fail / edge / name format); 562 total.

## [0.35.0] — 2026-04-23
### Added
- `frok.evals.LatencyWithin(max_ms)` scorer — asserts the
  case's root-span `duration_ms` stays within a threshold.
  Complements `TokensWithin` (cost ceiling) with a wall-clock
  ceiling. Inclusive at-limit comparison; zero-latency fallback
  when a run errors before a root span closes.
- Tests: 7 new (pass / fail / edge paths + scorer-name format);
  555 total.

## [0.34.0] — 2026-04-23
### Added
- `frok.evals.ToolArgsMatch(name, regex, field=None, flags=0)` —
  regex-based tool-argument scorer. Complements
  `ToolArgsSubset` (exact equality) with `re.search`-style
  fuzzy matching. `field=None` matches against the
  JSON-serialised args; a pinned field matches against
  `str(args[field])`. Invalid regex fails cleanly; measure
  carries the matched haystack.
- Tests: 14 new (field vs whole-args, non-string values,
  multi-invocation semantics, flags, anchored patterns,
  invalid regex, scorer name formatting); 548 total.

## [0.33.0] — 2026-04-23
### Added
- `frok.evals.ResponseModelIs(expected)` scorer — asserts
  `GrokResponse.model == expected`. Complements
  `EvalCase.model=…` (which pins the request) by pinning the
  response, catching silent provider-side model swaps. Missing
  final response / empty-string model / mismatch all fail with
  a triage-friendly detail; measure carries the actual model
  string.
- Tests: 7 new (unit + runner-integration); 534 total.

## [0.32.0] — 2026-04-23
### Added
- `GrokClient.chat(..., model=)` and
  `chat_stream(..., model=)` — per-call model override.
  Precedence: explicit kwarg > `client.model`.
- `ToolOrchestrator.model` field passes through on every turn.
- `EvalCase.model` — flows through the runner on both
  no-tools and tools paths (streaming and non-stream).
- `grok.chat` / `grok.chat_stream` telemetry spans report the
  effective model (kwarg-override or client default).
- Tests: 13 new (chat + chat_stream + orchestrator + EvalCase
  + span attrs + response-fallback); 527 total.

## [0.31.0] — 2026-04-23
### Added
- `GrokClient.chat(..., tool_choice=)` and
  `chat_stream(..., tool_choice=)` — first-class kwargs for
  the OpenAI/xAI tool-choice field. Accepts strings
  (`"auto"` / `"none"` / `"required"`) or a dict
  (`{"type": "function", "function": {"name": "X"}}`).
- `GrokClient.tool_choice` — client-level default. Precedence:
  explicit kwarg > client default > omit.
- `ClientConfig.tool_choice` config knob, env
  `FROK_CLIENT_TOOL_CHOICE`; flows through `build_client`.
- `EvalCase.tool_choice` — runner forwards into
  `ToolOrchestrator(tool_choice=…)`.
- Render layer handles dict-shaped `tool_choice`: TOML inline
  tables (round-trips through `tomllib`) and JSON-encoded env
  values.
- Tests: 21 new (GrokClient + chat_stream + orchestrator +
  EvalCase + config + render); 514 total.

### Changed
- `ToolOrchestrator` now passes `tool_choice` via the explicit
  `chat()` / `chat_stream()` kwarg instead of folding it into
  `extra`. Request body shape unchanged.

## [0.30.0] — 2026-04-23
### Added
- `ToolOrchestrator.run(stream_sink=callable)` — streams chat
  turns via `chat_stream` when the client has a
  `streaming_transport`, forwarding content deltas to the sink
  and emitting a `>>> turn N` marker per iteration. Falls back
  to non-stream `chat` when no streaming_transport is set.
- `tool.run` telemetry span gained a `streamed` attr
  (True / False).
- `EvalRunner._execute` now forwards `stream_sink` to the tool
  orchestrator instead of dropping it silently — `frok run
  --stream` on a tools-enabled case now gives live feedback.
- Tests: 7 new (orchestrator-level library tests + an end-to-end
  CLI test proving the tools path streams); 493 total.

## [0.29.0] — 2026-04-23
### Added
- `frok run --stream` — forward content deltas to stderr live
  (per-case `>>> <name>` header + raw tokens). The final
  `GrokResponse` still flows to scorers / report / baseline
  diff. Cases with tools silently fall back to the non-stream
  path. Incompatible with `--jobs > 1`.
- `EvalRunner.run_case(..., stream_sink=callable)` threads a
  per-delta callback; no-tools path uses `client.chat_stream`,
  tools path ignores it (for now).
- `build_client(..., streaming_transport=)` kwarg; default
  factory now wires `urllib_streaming_transport` so
  `--transport real` + `--stream` works out-of-the-box.
- Tests: 8 new (parser, deltas + header to stderr, scorers see
  final, tools fallback, `--jobs` guard, missing-streaming-
  transport as case error); 486 total.

## [0.28.0] — 2026-04-23
### Added
- `GrokClient.chat_stream(messages, …)` — async generator yielding
  `StreamChunk`s from an SSE stream. Pre-flight safety on
  messages, live deltas, post-flight safety on the assembled
  content. Streamed tool-call deltas reassemble as `ToolCall`s
  on the final chunk. Emits a `grok.chat_stream` telemetry span.
- `StreamingTransport` protocol + `StreamChunk` dataclass +
  `urllib_streaming_transport` stdlib implementation
  (line-by-line via `asyncio.to_thread`).
- `streaming_transport` field on `GrokClient`.
- Tests: 19 new (SSE parser, tool-call merger, chat_stream
  happy-path + safety + error paths + telemetry); 478 total.

## [0.27.0] — 2026-04-23
### Added
- `frok init --transport {stub,real}` — choose the generated
  `cases/smoke.py` transport. `stub` (default) runs with no
  credentials; `real` wires `urllib_transport` + reads
  `FROK_CLIENT_API_KEY` from the environment. Next-steps block
  prints the right on-ramp for each.
- `frok.cli.init._TRANSPORT_TEMPLATES` map + `_SMOKE_CASE_REAL`
  template.
- Tests: 11 new (parser, template contents, next-steps
  switching, run-without-api_key error, stubbed-urllib live
  green-path, example composition); 459 total.

## [0.26.0] — 2026-04-23
### Changed
- Root `frok --help` now opens with a mission-statement line and
  an explicit "onboarding triple" callout (`init`, `doctor`,
  `run`). Epilog lists every everyday operation as a copy-
  pasteable one-liner + a `frok version` pointer for bug
  reports. Multi-line layout preserved via
  `RawDescriptionHelpFormatter`.
- Subcommand display order reshuffled for help-output UX: init →
  doctor → run → config → eval → trace → version.
- Tests: 9 new (description, epilog, formatter, ordering,
  regression guards); 448 total.

## [0.25.0] — 2026-04-23
### Added
- `frok version` — print frok + Python + platform versions.
  Default: `frok X.Y.Z (Python A.B.C, <platform>)`. Flags:
  `--short` (just the frok version), `--json` (all three fields).
  `--short` wins over `--json`.
- `frok.cli.version.VersionInfo` dataclass +
  `collect_version_info()` helper.
- Tests: 8 new (parser, helper, each output mode, flag
  precedence); 439 total.

## [0.24.0] — 2026-04-23
### Added
- `frok doctor` preflight health check. Loads the resolved config
  and runs one Check per Phase-2 subsystem (config, safety,
  telemetry, memory, multimodal, live client.chat). Flags:
  `-c/--config`, `-p/--profile`, `-o/--output`, `--json`,
  `--no-live`, `--fail-on-skip`. Exit 1 on any FAIL (or any SKIP
  under `--fail-on-skip`).
- `frok.cli.doctor.Check` dataclass, `PASS`/`FAIL`/`SKIP`
  constants, library-level `check_*` helpers, `render_markdown` /
  `render_json` renderers.
- Tests: 26 new (library + CLI paths); 431 total.

## [0.23.0] — 2026-04-23
### Added
- `frok init --list-examples` — print the available `--example`
  names with their one-line descriptions (parsed from each
  template's module docstring) and exit without writing anything.
  Output is alphabetically sorted, two-column, pipe-friendly.
- `frok.cli.init.format_examples_list()` and
  `frok.cli.init._example_summary(src)` helpers.
- Tests: 12 new (parser, helper, CLI, no-I/O guarantees); 405 total.

## [0.22.0] — 2026-04-23
### Added
- `frok init --example {tools,multimodal,memory}` (repeatable) —
  scaffold a reference case file for each named flavor alongside
  the basic smoke scaffold. Each example is self-contained, uses
  a stub transport, and runs green under `frok run`:
  * `cases/tools.py` — `@tool` + ToolOrchestrator loop
  * `cases/multimodal.py` — `GrokMessage.parts` with `ImageRef`
  * `cases/memory.py` — `MemoryStore` exposed as `remember` /
    `recall` tools
- `frok.cli.init.EXAMPLE_TEMPLATES` dict; unknown example names
  rejected by argparse.
- Tests: 16 new (parser, scaffold composition, each example
  running green, tool + multimodal + memory behaviour checks);
  393 total.

## [0.21.0] — 2026-04-23
### Added
- `frok init [PATH] [--force]` — scaffold a new Frok project.
  Writes `CLAUDE.md`, `frok.toml` (with prod profile),
  `cases/smoke.py` (stub transport so it runs out of the box),
  and `.github/workflows/frok.yml`. Aborts if any target exists
  unless `--force`; prints a Next-steps block.
- Tests: 14 new (scaffold + --force + validity of generated
  files); 377 total.

## [0.20.0] — 2026-04-23
### Added
- `frok run --jobs N` — run up to N (case, repeat) units
  concurrently under an `asyncio.Semaphore`. Default 1 (serial).
  Silently clamped to `os.cpu_count()`. Incompatible with
  `--seed` because Python's `random` state is process-global.
- Result order in the `EvalReport` mirrors case-file order
  regardless of completion order.
- Tests: 11 new (defaults, order preservation, capture interop,
  clamping, error paths); 363 total.

## [0.19.0] — 2026-04-23
### Added
- `frok run --repeat N --seed S` — execute each case N times with
  a deterministic seed (`random.seed(S + repeat_index)` +
  `FROK_RUN_SEED` env var). Aggregated report surfaces per-case
  pass rates and flags flaky cases (0 < rate < 1) distinctly from
  hard failures. `--repeat > 1` with `--capture-baseline` is
  rejected to prevent JSONL filename collisions.
- `EvalResult.repeat` / `.repeats` fields (default 0 / 1).
- `EvalReport.by_case`, `case_pass_rates`, `total_cases`,
  `passed_cases`, `flaky_cases`, `failed_cases` properties.
- `EvalReport.to_markdown()` picks an aggregated format with
  pass-rate column and `FLAKY` verdict when any case has
  `repeats > 1`; otherwise the existing flat format is preserved
  (zero change for single-run callers).
- `EvalRunner.run(cases, *, repeats=1)` +
  `run_case(case, *, repeat, repeats)`.
- `frok.cli.run.apply_seed(seed, repeat_index)` helper.
- Tests: 17 new (library + CLI paths); 352 total.

## [0.18.0] — 2026-04-23
### Added
- `frok eval summarize <A> --diff-against <B>` — walk two
  `<slug>.jsonl` directories, diff each matched pair, flag slugs
  that appear in only one side. Markdown or `--json`;
  `--fail-on-regression` gates CI on tool-order divergence, new
  errors, or slug drift.
- `frok.evals.CaseDiff` + `DirectoryDiff` dataclasses;
  `diff_directories(a, b)` walker;
  `directory_diff_to_markdown` / `directory_diff_to_json`
  renderers.
- Tests: 19 new (library + CLI paths); 335 total.

## [0.17.0] — 2026-04-23
### Added
- `frok eval summarize <DIR>` — walk a baseline directory, roll up
  per-case spans / tokens / errors / duration, surface cross-case
  leaders (slowest, heaviest tokens, most errors, errored tools,
  top tools). Markdown or `--json`; `--top N` caps leader rows;
  `--fail-on-errors` for CI gates.
- `frok.telemetry.CaseSummary` + `DirectorySummary` dataclasses
  with aggregate properties and `slowest` / `heaviest_tokens` /
  `most_errors` leader methods.
- `frok.telemetry.summarize_directory(dir)`,
  `dir_summary_to_markdown`, `dir_summary_to_json`.
- Tests: 24 new (library walker + aggregates + renderers; CLI
  paths + interop with `run --capture-baseline`); 316 total.

## [0.16.0] — 2026-04-23
### Added
- `frok eval diff <a.jsonl> <b.jsonl>` — diff two JsonlSink
  captures. Markdown or JSON output; `--fail-on-regression` flips
  exit code on tool-order divergence or new errors in `b`.
- `frok.evals.diff_event_streams(a, b, *, a_label, b_label)` —
  the shared comparison core (now also powers
  `diff_against_baseline`).
- `frok.evals.diff_to_markdown(diff, …)` — compact verdict render.
- Both helpers report `span_delta` alongside existing fields.
- Tests: 19 new (library + CLI paths); 292 total.

### Changed
- `diff_against_baseline` now delegates to
  `diff_event_streams`. Dict shape preserved (legacy keys
  `baseline_tools`, `observed_tools`, `token_delta`, etc.) plus
  two new: `baseline_spans`, `observed_spans`, `span_delta`.

## [0.15.0] — 2026-04-23
### Added
- `frok run --list` — preview-only mode. Prints resolved case names
  (after `--filter`/`--exclude`) one per line and exits without
  constructing a client or running any case. Honours `-o/--output`.
  No `client.api_key` required; no `--capture-baseline` files written.
- Tests: 10 new (basic output, filter interop, output flag,
  no-run contract, no-api-key path, capture interop); 273 total.

## [0.14.0] — 2026-04-23
### Added
- `frok run --filter <PATTERN>` / `--exclude <PATTERN>` — keep/drop
  cases by name. Fnmatch glob by default; `re:` prefix for regex;
  both flags repeatable. Zero matches is a `CliError` that lists
  every available case. Composes with `--capture-baseline` (only
  filtered cases produce capture files) and `--use-baseline`.
- `frok.cli.run.filter_cases(cases, *, includes, excludes)` —
  library-level helper exposing the same matcher.
- Tests: 16 new (matcher unit tests + CLI end-to-end + capture
  interop); 263 total.

## [0.13.0] — 2026-04-23
### Added
- `frok run --capture-baseline <DIR>` — writes per-case
  `<slug>.jsonl` telemetry captures by layering a `JsonlSink` onto
  the client's tracer.
- `frok run --use-baseline <DIR>` — auto-attaches
  `DIR/<slug>.jsonl` as each case's `baseline` when the file
  exists; cases with explicit `baseline=` are untouched.
- `frok.telemetry.with_added_sink(tracer, extra)` — return a new
  `Tracer` whose sink fans out to the original plus `extra`
  (collapses `NullSink`, extends `MultiSink`).
- `frok.cli.run.case_slug(name)` — filename-safe case-name slug.
- Tests: 13 new (slug, with_added_sink, capture / use / round-trip);
  247 total.

## [0.12.0] — 2026-04-23
### Added
- `frok.config.render` — `to_toml`, `to_json`, `to_env` renderers with
  sensitive-field masking (default) + `reveal=True` escape hatch.
- `frok config show [--format=toml|json|env] [-c FILE] [-p PROFILE]
  [-o PATH] [--reveal]` subcommand. Prints the resolved `FrokConfig`
  after file + env + CLI + profile merging.
- Tests: 18 new (renderers across all three formats + CLI paths);
  234 total.

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
