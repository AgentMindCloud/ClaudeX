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
6. **agent-team-runtime** — Lightweight multi-agent scheduler.
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
10. **content** — X-platform content ingestion: normalises posts, threads,
    and media references into a canonical record the other modules can
    reason over. (Interpretation chosen on this branch; see PROGRESS.md.
    Narrow to rename if a different #10 was intended.)

## Phase 3+ (sketch)
Super-intelligence scaffolding, X-native production agents, alignment red-
teaming, distributed inference — detailed once Phase 2 #1/#2/#10 are green.
