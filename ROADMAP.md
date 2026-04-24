# Super AI Frok — Roadmap

Living document. Phases describe *intent*; individual items are implementable
units of work. Items keep stable numbers so commit messages and PROGRESS
entries can reference them unambiguously (e.g. "§2 #2 grok-client").

## Phase 1 — Foundations (complete when marked)
Not the focus of this branch. Reserved for environment / tooling bootstrap.

## Phase 2 — Frok core primitives
Goal: ship the smallest slice of the Super AI Frok core that a downstream
agent team can import: a safe, typed xAI/Grok client, an alignment-rules
engine, and an X-content ingestion helper. Everything else in the phase
builds on these three.

1. **grok-safety-rules** — Declarative rule engine enforcing xAI alignment
   values (truth-seeking, anti-sycophancy, no hallucinated capabilities,
   PII redaction). Exposed as a pre- and post-flight checker around any
   model call.
2. **grok-client** — Async client wrapping the xAI Chat Completions API
   with retries, streaming, tool-use, and cost accounting. Wired to the
   safety rules from #1 by default.
3. **persistent-memory** — Vector + episodic store for long-running agents.
   *Shipped 2026-04-23:* `frok.memory` (SQLite + pluggable `Embedder`),
   `MemoryAgent` wiring through `GrokClient`.
4. **tool-use-orchestrator** — Tool registry + dispatch for Grok-style
   function calling. *Shipped 2026-04-23:* `frok.tools` (Tool / @tool /
   ToolRegistry / ToolOrchestrator), zero-dep JSON Schema validator +
   signature inference, dry-run mode, full loop wired through
   `GrokClient.chat(tools=...)`.
5. **multimodal-adapter** — Vision/voice IO adapter surface.
   *Shipped 2026-04-23:* `frok.multimodal` (ImageRef / AudioRef
   path/bytes/URL factories, MultimodalAdapter + AdapterConfig,
   graceful descriptor fallbacks when vision/voice disabled).
   `GrokMessage.parts` threaded through safety pre-flight;
   `GrokClient.request_json` for non-chat endpoints.
6. **agent-team-runtime** — Lightweight multi-agent scheduler.
   *Shipped 2026-04-23:* `frok.team` (TeamRuntime + Role + Router +
   `pipeline_router` / `callback_router` / `loop_until`).
   `chat_role_from_client` wraps any `GrokClient` as a role; memory,
   tools, and multimodal wrappers compose by construction. Emits
   nested `team.run` / `team.hop` spans so §2 #8 evals can regress on
   team behaviour through the same `InMemorySink`.
7. **telemetry** — Structured logs, traces, and evals hook.
   *Shipped 2026-04-23:* `frok.telemetry` (Event + Null / InMemory /
   Jsonl / Multi sinks, `Tracer` with contextvar-scoped spans). Wired
   into `GrokClient.chat`, `MemoryStore.remember/recall/forget`, and
   `ToolOrchestrator.run` + per-invocation spans.
8. **eval-harness** — Regression + truthfulness scoring across model
   versions. *Shipped 2026-04-23:* `frok.evals` (EvalCase /
   Observation / Score / EvalRunner / EvalReport), 10 built-in
   scorers, baseline-trace diff against JsonlSink captures, Markdown
   verdict doc. `SpanHandle.fail()` added so caught tool-handler
   errors still regress the run.
9. **config-loader** — Layered config (env → file → CLI overrides).
   *Shipped 2026-04-23:* `frok.config` — typed `FrokConfig` with
   client / safety / telemetry / memory / multimodal sections; JSON +
   TOML files; profile sections merged on top; builders for every
   Phase-2 component keyed off the single config object.
10. **content** — X-platform content ingestion: normalises posts, threads,
    and media references into a canonical record the other modules can
    reason over. (Interpretation chosen on this branch; see PROGRESS.md.
    Narrow to rename if a different #10 was intended.)

## Phase 5 — Real-integration polish
1. **init-transport** — `frok init --transport {stub,real}`
   switches the generated `cases/smoke.py` between the stub
   (default, runs with no api_key) and a `urllib_transport`-backed
   live template that reads `FROK_CLIENT_API_KEY` from the
   environment. Next-steps message is conditional on the
   transport. *Shipped 2026-04-23.*
2. **streaming** — `GrokClient.chat_stream(messages, …)` is an
   async generator yielding `StreamChunk`s as SSE data arrives.
   Safety pre-flight runs on messages; deltas are yielded live;
   a final chunk carries the assembled `GrokResponse` after
   post-flight safety. Tool-call deltas are reassembled.
   Telemetry: `grok.chat_stream` span. Ships with a stdlib
   `urllib_streaming_transport`. *Shipped 2026-04-23.*
3. **stream-cli** — `frok run --stream` forwards each content
   delta to stderr live with a `>>> <case-name>` header while
   the final `GrokResponse` still flows to the scorers and
   report. Tools-enabled cases silently fall back; default
   factory wires `urllib_streaming_transport` so `--transport
   real` + `--stream` works out-of-the-box. Incompatible with
   `--jobs > 1` (interleaved stderr). *Shipped 2026-04-23.*
4. **stream-tools** — `ToolOrchestrator.run(stream_sink=...)`
   now honours streaming when the client has a
   `streaming_transport`. Each chat turn gets a `>>> turn N`
   marker; text deltas flow live while tool-call deltas stay
   silent. The previous silent fallback is gone for
   streaming-capable clients; it survives for clients without a
   streaming transport so callers can pass `stream_sink`
   unconditionally. *Shipped 2026-04-23.*
5. **tool-choice** — `GrokClient.chat(..., tool_choice=)` +
   `chat_stream(..., tool_choice=)` now accept an explicit
   kwarg, with `GrokClient.tool_choice` as the client-level
   default. Explicit > client default > omit. `ClientConfig`
   grew a matching knob that flows through `build_client`;
   `EvalCase.tool_choice` plumbs through to the orchestrator so
   cases can assert forced / forbidden / specific-function
   selection. Render layer handles dict-shaped values via TOML
   inline tables and JSON-in-env. *Shipped 2026-04-23.*
6. **model-override** — `GrokClient.chat(..., model=)` +
   `chat_stream(..., model=)` accept a per-call override.
   Precedence: explicit > `client.model` (never omit — a model
   must be sent). `ToolOrchestrator.model` passes through on
   every turn; `EvalCase.model` flows through the runner on
   both no-tools and tools paths; `grok.chat` /
   `grok.chat_stream` spans report the effective model.
   *Shipped 2026-04-23.*
7. **response-model-scorer** — `ResponseModelIs(expected)`
   asserts the assembled `GrokResponse.model` equals the
   expected string. Complements `EvalCase.model=…` (which
   pins the *request*) by proving the *response* came from
   the expected model — catches silent mid-flight provider
   swaps. *Shipped 2026-04-23.*
8. **tool-args-regex** — `ToolArgsMatch(name, regex,
   field=None, flags=0)` asserts a regex matches either the
   JSON-serialised full args (field=None) or a specific
   argument's string form. `re.search` semantics; invalid
   regex fails cleanly; scorer name includes both tool + field
   for aggregate reports. *Shipped 2026-04-23.*
9. **latency-ceiling** — `LatencyWithin(max_ms)` asserts the
   case's root-span `duration_ms` stays within a threshold.
   Complements `TokensWithin` (cost ceiling) with a wall-clock
   ceiling for CI. Inclusive at-limit comparison; zero-latency
   fallback when a run errors before a root span closes.
   *Shipped 2026-04-23.*

## Phase 4 — Onboarding
1. **init-scaffold** — `frok init [PATH]` writes a minimal runnable
   skeleton: `CLAUDE.md`, `frok.toml` (with a prod profile),
   `cases/smoke.py` (stub transport so `frok run` passes with no
   api_key), and `.github/workflows/frok.yml` demoing the
   capture/diff loop. Aborts if any target exists unless `--force`.
   *Shipped 2026-04-23.*
2. **init-examples** — `frok init --example {tools,multimodal,memory}`
   (repeatable) adds dedicated case files demonstrating
   `ToolOrchestrator`, `MultimodalAdapter` (ImageRef + parts), and
   `MemoryStore`-backed tools. Each example is self-contained, runs
   green under `frok run`, and includes a "production swap" note
   pointing at real transport/store choices. *Shipped 2026-04-23.*
3. **init-list-examples** — `frok init --list-examples` prints a
   sorted, two-column roster of available `--example` names +
   one-line descriptions (parsed from each template's module
   docstring via `ast.get_docstring`). Early-exits before any I/O;
   short-circuits every other `init` flag.
   *Shipped 2026-04-23.*
4. **doctor** — `frok doctor` preflight health check. Runs one
   `Check` per major Phase-2 subsystem (config, safety, telemetry,
   memory, multimodal, live client.chat) and prints PASS / FAIL /
   SKIP. Live chat ping honours `client.api_key` + `--no-live`.
   Flags: `-c`, `-p`, `-o`, `--json`, `--no-live`, `--fail-on-skip`.
   *Shipped 2026-04-23.*
5. **version** — `frok version` prints `frok X.Y.Z (Python A.B.C,
   <platform>)`. `--short` emits only the frok version for shell
   use; `--json` emits `{frok, python, platform}`. The first
   question on any bug report, answered with one command.
   *Shipped 2026-04-23.*
6. **help-polish** — root parser description names the
   "onboarding triple" (init / doctor / run) and lists the
   everyday operations in the epilog. Subcommands now appear in
   discovery order (init → doctor → run → config → eval → trace →
   version) via a `RawDescriptionHelpFormatter`. *Shipped
   2026-04-23.*

## Phase 3 — Wiring + operations
1. **cli-runner** — `frok run <case-file>` entry point wiring
   `load_default_config` → full-stack build → `EvalRunner` →
   `EvalReport.to_markdown()`, with `--fail-on-regression` for CI.
   *Shipped 2026-04-23.* (stdlib-only `urllib_transport` as the
   default production transport.)
2. **trace-inspect** — `frok trace inspect <jsonl>` loads a
   `JsonlSink` capture, reconstructs the trace tree, and prints a
   summary of per-span durations, errors, and top tool invocations.
   *Shipped 2026-04-23.*
3. **config-show** — `frok config show [--format=toml|json|env]`
   renders the resolved `FrokConfig` (after file + env + CLI +
   profile merging) so operators can sanity-check what got applied
   before running anything. `client.api_key` masked by default;
   `--reveal` shows plain. *Shipped 2026-04-23.*
4. **baseline-capture** — `frok run --capture-baseline <dir>`
   writes per-case `<slug>.jsonl` captures; `--use-baseline <dir>`
   auto-attaches them to cases without a baseline so the next
   run diffs via §2 #8 automatically. *Shipped 2026-04-23.*
5. **case-filter** — `frok run --filter <pattern>` / `--exclude
   <pattern>` (glob by default; `re:` prefix for regex;
   repeatable). Zero matches is an explicit `CliError` that lists
   the available case names. Composes with `--capture-baseline` so
   CI can re-record only the cases being iterated on.
   *Shipped 2026-04-23.*
6. **list-preview** — `frok run --list` prints resolved case names
   (post-filter) one per line and exits without building a client
   or running any case. Short-circuits before api-key / capture /
   baseline logic. *Shipped 2026-04-23.*
7. **eval-diff** — `frok eval diff <a.jsonl> <b.jsonl>` diffs two
   captures (tool-order, token delta, new errors, span delta)
   with Markdown or JSON output. Symmetric two-file A/B
   comparison complementing `trace inspect` (single capture) and
   `--use-baseline` (per-case). *Shipped 2026-04-23.*
8. **eval-summarize** — `frok eval summarize <dir>` walks a
   directory of `<slug>.jsonl` captures (e.g. from
   `--capture-baseline`), rolls up per-case spans / tokens /
   errors / duration, and surfaces cross-case leaders (slowest,
   heaviest tokens, most errors, errored tools, top tools).
   Markdown or JSON; `--fail-on-errors` for CI gates.
   *Shipped 2026-04-23.*
9. **eval-dirdiff** — `frok eval summarize <a> --diff-against <b>`
   walks two capture directories, diffs each matched `<slug>.jsonl`
   pair, and flags slugs that appear in only one side. Markdown or
   JSON; `--fail-on-regression` gates CI on tool-order divergence,
   new errors, or slug drift. *Shipped 2026-04-23.*
10. **repeat-runs** — `frok run --repeat N --seed S` executes each
    case N times with a deterministic seed, aggregates the
    `EvalReport` into per-case pass rates, and flags flaky cases
    (0 < rate < 1) distinctly from hard failures. Seed is applied
    as ``random.seed(S + repeat_index)`` and published via the
    ``FROK_RUN_SEED`` env var so stubs can pick it up. Incompatible
    with `--capture-baseline` (prevents per-case file collisions).
    *Shipped 2026-04-23.*
11. **parallel-jobs** — `frok run --jobs N` runs up to N
    (case, repeat) units concurrently under an `asyncio.Semaphore`.
    Results come back in case order regardless of completion
    order. Silently clamped to `os.cpu_count()`. Incompatible
    with `--seed` because Python's `random` state is process-
    global. *Shipped 2026-04-23.*
12. *Sketch:* `frok serve` (long-running agent), distributed
    inference, X-native production agents, alignment red-teaming.
