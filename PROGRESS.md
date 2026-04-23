# PROGRESS

Living log of what shipped and why. Most recent entries first.

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
