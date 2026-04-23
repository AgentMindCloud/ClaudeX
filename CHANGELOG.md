# Changelog

All notable changes. Format loosely follows Keep a Changelog.

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
