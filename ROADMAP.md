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
9. *Sketch:* `frok serve` (long-running agent), distributed
   inference, X-native production agents, alignment red-teaming.
