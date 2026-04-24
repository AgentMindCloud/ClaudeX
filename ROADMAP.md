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
10. **invocations-ceiling** — `InvocationsWithin(max_count)`
    asserts `len(obs.invocations) <= max_count`. Aggregate
    "don't loop forever" cap across every tool, complementing
    `ToolCalled(..., times=N)`'s per-tool exact count. Catches
    prompt regressions that start over-calling tools without
    needing one scorer per tool. *Shipped 2026-04-23.*
11. **answer-length** — `AnswerLength(min_chars=None,
    max_chars=None)` asserts the assembled response length
    falls within a range. Complements `AnswerContains` /
    `AnswerMatches` (content) with a shape gate. At least one
    bound required; inclusive comparisons; construction
    validates `min <= max` and non-negative bounds.
    *Shipped 2026-04-23.*
12. **token-delta** — `TokenDeltaWithin(max_delta)` reads
    `case.baseline`, diffs baseline vs observed token totals,
    and fails when `abs(delta) > max_delta`. Symmetric
    (catches both runaway-long and bail-early answers);
    failure detail surfaces baseline + observed + signed
    delta; measure carries the signed delta for trend-
    scanning. *Shipped 2026-04-23.*
13. **latency-delta** — `LatencyDeltaWithin(max_ms)` mirrors
    `TokenDeltaWithin` but on root-span `duration_ms`, via a
    new `latency_delta_ms` key on `diff_event_streams`.
    Completes the baseline-drift gate: cost + wall-clock
    now both assertable in one scorer stack. Shared
    `_load_baseline_diff` helper keeps the two scorers in
    lockstep. *Shipped 2026-04-23.*
14. **case-timeout** — `EvalCase.timeout_s` wraps each case in
    `asyncio.wait_for`. On timeout the case fails with a
    clean `TimeoutError` observation.error; partial events
    captured up to the cancellation point are preserved on
    the sink. Catches truly-stuck cases that `LatencyWithin`
    can only gate on AFTER the run completes.
    *Shipped 2026-04-23.*
15. **cli-timeout-default** — `frok run --timeout-s SECONDS`
    sets a default timeout on every case whose own
    `EvalCase.timeout_s` is None. Per-case values always win;
    negative values error; 0 short-circuits unconfigured
    cases. Mirrors the `--use-baseline` "fill from CLI"
    pattern so operators get suite-wide defaults without
    editing every case file. *Shipped 2026-04-23.*
16. **cli-retry** — `frok run --retry N` re-runs a failing
    case up to N times and marks it PASS if any attempt wins.
    Timeouts short-circuit the loop (case-level caps are by
    design, not flakiness). Contrasts with `--repeat` which
    runs every attempt and reports each outcome. Rejects
    `--retry < 0` and `--retry > 0` + `--capture-baseline`
    (retries would overwrite the previous attempt's JSONL).
    Shakes genuinely flaky cases out of regression runs
    without masking hard failures. *Shipped 2026-04-24.*
17. **attempts-field** — `EvalResult.attempts` records how
    many runner invocations produced the result; the CLI
    retry loop bumps it via `dataclasses.replace` on exit.
    `to_summary()` omits the field when 1 (clean baseline);
    `EvalReport._has_retries` drives an Attempts column in
    flat + aggregated markdown plus `total_attempts` and
    `retried_cases` in the summary. Surfaces "this case
    passes in CI but only on attempt 3/3" before retries
    silently mask it into a full failure.
    *Shipped 2026-04-24.*
18. **retry-on-pattern** — `frok run --retry-on PATTERN`
    narrows `--retry`'s budget to cases whose names match
    any pattern (glob by default; `re:` prefix for regex;
    repeatable — any match wins). Non-matches always run
    exactly once, even under `--retry > 0`. Rejects
    `--retry-on` without `--retry > 0` (no budget to spend)
    and invalid regexes. Composes with `--filter`,
    `--fail-on-regression`, and `--timeout-s`. Useful when a
    handful of cases depend on flaky external services and
    a blanket `--retry` would mask real regressions
    elsewhere. *Shipped 2026-04-24.*
19. **retry-budget** — `EvalResult.retry_budget` records
    the attempt allowance allocated to each result; the
    markdown report's Attempts column becomes
    `Attempts/Budget` (e.g. "3/5") and the summary line
    reads "used A of B attempts". Caught-it-late retries
    still mask into PASS but surface as "used most of the
    budget" — a softer flakiness signal than the binary
    retried/not-retried flag. Summary grows `total_budget`
    alongside `total_attempts` when any case was retry-
    eligible. *Shipped 2026-04-24.*
20. **retry-on-error** — `frok run --retry-on-error REGEX`
    narrows `--retry` to failures whose
    `observation.error` matches REGEX (Python `re.search`
    semantics; repeatable — any match wins). Scorer-only
    failures (no observation error) are never retried under
    this flag — they're almost always real regressions.
    Timeouts still short-circuit as always. Composes with
    `--retry-on`: both gates must match (case-name AND
    error-shape) for a retry to be eligible. Rejects
    `--retry-on-error` without `--retry > 0` and invalid
    regexes. *Shipped 2026-04-24.*
21. **retry-backoff** — `frok run --retry-backoff MS`
    sleeps MS milliseconds before each retry (default 0 =
    no sleep); `--retry-backoff-jitter FRACTION` (in [0,
    1]) applies symmetric jitter via
    `random.uniform(1 - F, 1 + F) * MS`. Sleep goes BEFORE
    each retry, never after the final attempt, and is
    skipped entirely on early breaks (pass, timeout,
    error-filter miss). Mainly against rate-limited APIs
    where immediate retries hit the same limit again.
    Rejects negative backoff, jitter outside [0, 1],
    jitter without backoff, and backoff without
    `--retry > 0`. *Shipped 2026-04-24.*
22. **retry-report** — `frok run --retry-report PATH`
    writes a per-case per-attempt timeline JSON with
    `{attempt, passed, error, sleep_before_ms}` records
    plus the case's `retry_budget` and terminal `passed`
    verdict. Lets CI diff retry behaviour across runs and
    catch creeping flake ("attempts grew from 2 to 5 on
    three cases") before the budget-relative summary
    would flag it. Always written when the flag is set,
    regardless of `--retry` value; parent dir created if
    missing. *Shipped 2026-04-24.*
23. **retry-diff** — `frok retry diff A B` loads two
    retry-report JSONs, matches `(case, repeat)` pairs,
    and surfaces attempts drift, error-shape changes,
    and newly-failing / newly-passing cases. Regression
    heuristic: attempts grew, newly failing, error
    drifted between two non-null strings, or a new
    failing case appeared in B. `--fail-on-regression`
    gates CI; `--json` emits structured output;
    `--a-label` / `--b-label` rename the columns in
    markdown. *Shipped 2026-04-24.*
24. **retry-summarize** — `frok retry summarize DIR`
    walks `DIR/*.json` retry-reports (lexicographic
    filename ordering — `YYYY-MM-DD.json` sorts
    chronologically for free), matches entries by
    `(case, repeat)`, and classifies each case's attempt
    trend: `flat` / `growing` (monotonic non-decreasing
    with at least one rise) / `shrinking` / `mixed`
    (real flake). Cases missing from early reports show
    `None` slots. `--fail-on-growing` gates CI on the
    creeping-flake pattern; `--json` emits structured
    output. Complements §23's pairwise diff with a
    longitudinal view. *Shipped 2026-04-24.*
25. **retry-show** — `frok retry show PATH` pretty-
    prints a single retry-report JSON as markdown:
    summary bloc plus per-case attempt tables for
    retried OR failing cases. Single-attempt passes
    collapse to a bulleted "Clean passes" list so the
    output stays scannable when most of the suite is
    green. `--fail-on-failure` gates CI when any case
    failed; `--json` passes through the raw payload.
    Completes the retry-report toolkit: produces (§22),
    diff (§23), summarize (§24), show (§25).
    *Shipped 2026-04-24.*
26. **retry-show-compare** — `frok retry show PATH
    --compare-to PATH2` enriches the single-report
    triage view with inline pairwise comparison: per-
    case headers gain "(was N/M, PASS/FAIL)" suffixes
    (or "(NEW — not in previous)"), the summary bloc
    grows a Comparison section with grew/shrank/newly-
    failing/newly-passing counts, and an "Only in
    previous" section lists vanished cases. Reuses
    §23's `diff_retry_reports` internally. Markdown-
    only — `--json` passes through the primary verbatim
    (structured diff data is `retry diff`'s job).
    *Shipped 2026-04-24.*

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
