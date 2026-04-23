# Changelog

All notable changes. Format loosely follows Keep a Changelog.

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
