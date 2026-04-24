# PROGRESS

Living log of what shipped and why. Most recent entries first.

## 2026-04-24 — Phase 5 §16: cli-retry

**Shipped** ``frok run --retry N`` — a per-case retry loop that
re-runs failing cases up to N times and accepts the case if
*any* attempt wins. The mirror opposite of `--repeat` in intent:
`--repeat` surfaces flake, `--retry` absorbs it.

* **CLI flag** (`frok/cli/run.py`) — int, default 0,
  `metavar="N"`. `args.retry < 0` → `CliError`. `args.retry > 0`
  combined with `--capture-baseline` → `CliError` (retries
  would overwrite the previous attempt's captured JSONL, same
  shape of failure as the `--repeat > 1 + --capture-baseline`
  guard).
* **Retry loop** — wrapped inside `_run_unit` right around the
  existing `runner.run_case` call. A `for _ in range(args.retry
  + 1):` loop retains `retry=0`'s "run once" baseline. Breaks
  at the first `result.passed`. Also breaks when the
  observation error starts with `"TimeoutError"` — timeouts are
  a case-level cap (§14), not flakiness, and retrying them
  would undo the operator's explicit budget.
* **Composes with `--repeat`** by contrast. `--repeat N` runs
  every attempt and reports each as its own result (pass-rate
  aggregation surfaces flake). `--retry N` collapses the
  attempts into one verdict (pass-on-any, no new EvalResult per
  attempt). Both flags together work: each repeat gets its own
  retry budget.
* **Composes with `--fail-on-regression`** too — exhausted
  retries still leave the case FAIL, so CI gates exactly as
  you'd expect.

**Verification.** `python3 -m pytest -q` → 645 passed in 2.69s
(12 new). Tests cover: parser default 0, parser accepts int,
retry=0 runs once, pass-first-attempt consumes no retry,
fail-then-succeed flips verdict to PASS, always-fail exhausts
`retry+1` attempts, `--timeout-s` + `--retry 5` runs exactly
once (timeout short-circuit), `--fail-on-regression` returns 1
when retries exhaust and 0 on eventual pass, `--retry -1`
errors with "`--retry must be >= 0`", `--retry 1 +
--capture-baseline` errors, `--retry 0 + --capture-baseline` is
fine (explicit-zero doesn't trigger the guard).

**Decisions / trade-offs.**
* Kept retries out of `EvalRunner` itself — the runner's
  contract is "one case → one EvalResult". Retry is a
  higher-level operator knob, identical to `--repeat`, which
  also lives in the CLI. Keeping it in the CLI means library
  users get a stable `run_case` without retry semantics leaking
  through.
* Chose pass-on-any over "all-must-pass". Opposite semantics
  exist (`--repeat` + manual aggregation) and a scorer can
  always assert `InvocationsWithin` / `LatencyWithin` on the
  winning run. The common operator need here is flake
  absorption, not quorum.
* Timeouts skip the retry loop. `TimeoutError` is semantically
  "operator's explicit cap was exceeded" — retrying it silently
  turns a 30s cap into a 90s cap without the operator asking.
  Flakiness is a property of the network/model/seed; case-level
  timeout is a property of the operator's intent.
* `--capture-baseline` conflict follows the exact shape of the
  existing `--repeat > 1` guard: both would overwrite per-case
  `<slug>.jsonl` files. Explicit `--retry 0` is allowed through
  (mirrors "no retry requested, no conflict").
* `--retry` is orthogonal to `--jobs`. The retry loop runs
  within a unit's semaphore hold, so concurrency bounds still
  apply and parallel retries don't oversubscribe CPU.
* No exponential backoff / sleep between retries. Cases run
  against user-controlled transports (stubs, memoised clients,
  live xAI). A fixed-sleep retry is wrong for all three; if a
  case wants its own backoff it can layer it in the transport.
  Keeping the loop tight also makes `--retry` cheap for pure-
  stub CI suites.

**Next suggested action:** `Extend Phase 5 §17 with an
\`EvalResult.attempts\` field surfacing how many retry attempts
each case consumed, plumbing it through \`to_summary()\` and
the report markdown so flaky cases are visible in the verdict
doc even when \`--retry\` successfully masks their failure.
Catches \"this case passes in CI but only on attempt 3/3\"
regressions before they become full failures.`

## 2026-04-23 — Phase 5 §15: cli-timeout-default

**Shipped** ``frok run --timeout-s SECONDS`` — a suite-wide
default for `EvalCase.timeout_s`, filled in per case where the
case itself hasn't opted out. Operators who want "no case
should ever take more than 30s" can now set it once at the
command line instead of editing every case file.

* **CLI flag** (`frok/cli/run.py`) — registered as a float
  with `metavar="SECONDS"`. Default is `None` (no fill).
* **Runner fill** — after `load_case_file` + `--use-baseline`,
  if `args.timeout_s is not None`, iterate `loaded.cases` and
  set `case.timeout_s = args.timeout_s` for any case whose
  own value is `None`. Per-case overrides win by construction.
* **Validation** — negative `--timeout-s` raises `CliError`
  ("`--timeout-s must be >= 0`", exit 2). Zero is allowed —
  `asyncio.wait_for(0)` short-circuits every unconfigured case
  before it runs, which is a legitimate "pre-flight check the
  loader, skip execution" move. Per-case `timeout_s=0` already
  has the same semantics (§14).

**Verification.** `python3 -m pytest -q` → 633 passed in 2.58s
(9 new). Tests cover: parser default `None`, parser accepts
float + zero, no-flag leaves cases untouched (existing
behaviour preserved), `--timeout-s 0.05` on a 5s-sleep
transport fires the timeout with both marker + configured
value in `observation.error`, mixed-case file with one
`timeout_s=0.02` + one None + `--timeout-s 0.10` honours both
boundaries simultaneously, `--timeout-s 0` short-circuits,
`--fail-on-regression` returns 1 on a timeout case,
`--timeout-s -1` is a `CliError`.

**Decisions / trade-offs.**
* Fill at the runner layer, not on the EvalCase directly at
  load time. Cases authored in the file are the source of
  truth for their own `timeout_s`; the CLI is a fallback for
  un-opinionated cases. Filling only the `None` slots keeps
  that layering clean.
* Negative is a hard error. Existing flags (`--repeat`,
  `--jobs`) follow the same rule; zero is a valid edge-case
  for "don't actually execute" but negatives are always bugs.
* Mirrors `--use-baseline` semantics. That flag fills
  `case.baseline` for cases whose own is None; this fills
  `case.timeout_s` for cases whose own is None. Consistent
  precedence ladder, consistent operator mental model.
* No validation that `--timeout-s` is above some floor
  (e.g. "not less than 1ms"). Unit tests often need sub-
  millisecond timeouts to exercise the error path
  deterministically, and operators trying `--timeout-s 0.0001`
  on a live call will see the same `TimeoutError` the case-
  level setting produces — the failure is already clean.

**Next suggested action:** `Extend Phase 5 §16 with a
\`frok run --retry N\` flag wiring \`asyncio\` retry loops
around each case: on a failing case (not a timeout — those
are by design), re-run up to N times and mark the case passed
if any attempt succeeds. Useful for shaking out genuinely
flaky cases from regressions. Combines cleanly with
\`--repeat\` (which runs N times and reports every outcome)
by contrast — retry stops at the first win.`

## 2026-04-23 — Phase 5 §14: case-timeout

**Shipped** ``EvalCase.timeout_s`` — a hard wall-clock cap per
case, enforced by the runner via ``asyncio.wait_for``. Closes a
real operational gap: ``LatencyWithin`` / ``LatencyDeltaWithin``
only assert after the case completes; a case that's *actually*
stuck hangs the suite until the operator ctrl-C's. Setting
``timeout_s`` turns that into a clean case-level failure.

* **`EvalCase.timeout_s: float | None = None`** — default
  None preserves existing behaviour (no wait_for wrapping);
  any positive value caps the case's runtime.
* **Runner enforcement** — `EvalRunner.run_case` wraps the
  `_execute` coroutine in `asyncio.wait_for(..., timeout_s)`
  when set. On timeout, Python cancels the underlying task;
  cancellation unwinds through every open `async with` span
  (so spans close with errors marked), `asyncio.wait_for`
  translates to a `TimeoutError`, and the runner builds a
  clean Observation with `error="TimeoutError: case
  exceeded timeout_s=N.N"`.
* **Partial events preserved** — the InMemorySink the
  runner passes into the factory catches span events as they
  close during unwinding. The timeout-produced Observation
  carries those partial events, so trace-inspect / scorer
  post-mortems aren't left empty.
* **Composition** — timeout applies per case per repeat, not
  per suite. `--repeat 5 timeout_s=10.0` gives each of the
  five runs its own 10s budget; a slow repeat doesn't eat
  budget from the others.

**Verification.** `python3 -m pytest -q` → 624 passed in 2.43s
(8 new). Tests cover: default `timeout_s=None` preserves the
no-wait behaviour, generous timeout + fast transport still
passes, tiny timeout (50ms) + slow transport (2s) surfaces
`TimeoutError` + the configured value in `observation.error`,
`NoErrors` scorer fires on the timeout error (with
`TimeoutError` in its detail), content scorers see an empty
answer when `final_response is None`, partial `grok.chat`
span events survive on the sink with their `error` field
populated from cancellation unwinding, per-repeat budget
composes correctly with `--repeat`, and `timeout_s=0.0` fires
immediately (correct contract — "don't run at all").

**Decisions / trade-offs.**
* Wrap `_execute`, not scorers. Scorers are assertion
  machinery; timing them would tangle "the model took
  forever" with "my Python scorer is slow". The timeout
  gates the chat/tool work; scorers run post-hoc on
  whatever partial observation the runner salvaged.
* Partial events preserved rather than emptied. A
  cancelled run is often the most interesting one to
  inspect (which span hung?); keeping the sink's events
  means `trace inspect` works on timeout failures too.
* `asyncio.TimeoutError` not `asyncio.CancelledError`.
  `wait_for` already translates the cancel to a TimeoutError
  under the hood; the runner just catches the translated
  form, keeping the `Observation.error` message
  operator-readable.
* `timeout_s=0.0` fires immediately by design. Python's
  `wait_for(..., 0)` raises before scheduling the
  coroutine, so the case never runs. An operator explicitly
  passing 0 is saying "short-circuit this case" — that's a
  feature, not a bug. Documented.
* Timeout wraps a single coroutine per repeat, not the
  whole suite. `--repeat 5 timeout_s=10.0` → 50s max across
  the five; gating the whole suite at once would punish
  slower repeats that are still within budget individually.

**Next suggested action:** `Extend Phase 5 §15 with a
\`frok run --timeout-s N\` CLI flag: set a default
\`timeout_s\` on every loaded case whose own \`timeout_s\` is
None. Mirrors how \`--use-baseline\` fills in
\`case.baseline\` — operators get a suite-wide default
without editing every case file, while per-case
overrides still win.`

## 2026-04-23 — Phase 5 §13: latency-delta

**Shipped** ``LatencyDeltaWithin(max_ms)`` — the wall-clock
twin of §12's ``TokenDeltaWithin``. Operators regression-testing
a prompt change now have one scorer stack that asserts both
"tokens didn't drift by more than N" and "wall-clock didn't
drift by more than M", both anchored to the same captured
baseline.

* **`diff_event_streams` extension** — added a
  ``_root_duration_ms(events)`` helper matching
  ``Observation.total_latency_ms`` semantics (first root span's
  `duration_ms`), plus three new keys on the diff dict:
  ``{a_label}_latency_ms``, ``{b_label}_latency_ms``,
  ``latency_delta_ms``. Existing callers and tests aren't
  affected — they check specific keys, not shape equality.
* **`LatencyDeltaWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring ``TokenDeltaWithin`` line-for-line.
  `__post_init__` rejects negative `max_ms`; zero is allowed as
  exact-parity.
* **Shared baseline loader** — pulled out a private
  ``_load_baseline_diff(case, sname, obs)`` helper that both
  baseline-aware scorers call. Returns a `Score` on error
  paths (no baseline attached / missing file / unreadable) or
  the diff dict on success. Keeps the two scorers from
  drifting on error messages.
* **Failure detail** surfaces baseline + observed + signed
  delta, same shape as the token scorer; ``measure`` carries
  the signed latency delta as a float.

**Verification.** `python3 -m pytest -q` → 616 passed in 1.45s
(21 new). Library tests cover the five new diff-field paths
(identical streams → zero latency delta, root span only (nested
spans don't contribute), signed delta direction preserved,
custom labels rename the keys, missing root span → 0.0), plus
16 scorer tests mirroring ``TokenDeltaWithin``'s coverage:
construction rejects negative / zero allowed, no-baseline +
missing-file fail cleanly, zero delta passes, small positive +
small negative deltas pass, inclusive at-threshold in both
directions, over-threshold positive + negative both fail with
baseline + observed + signed delta in detail, ``max_ms=0``
enforces exact parity, scorer name reflects the cap, measure
preserves direction. Two integration tests use a deterministic
clock injected into `Tracer(clock=...)` so wall-clock noise
doesn't flake: the parity case passes, the drift case fails
with ``+990.0`` in the detail.

**Decisions / trade-offs.**
* Extended `diff_event_streams` rather than duplicating the
  root-span lookup in the scorer. One canonical helper keeps
  the live-vs-captured differ and the scorer in lockstep —
  exactly the parity ``diff_against_baseline`` already
  delegates through.
* Root-span duration, not sum-of-all-spans. Matches
  ``Observation.total_latency_ms`` semantics so a case's
  runtime wall-clock and the captured baseline compare
  apples-to-apples.
* Symmetric `abs(delta_ms)` gate. A sudden latency collapse
  is as much a regression signal as a latency spike (usually
  means the model bailed early); operators who want one-sided
  can layer a future variant.
* Shared `_load_baseline_diff` helper is module-private.
  Public API is the two scorer classes; operators don't need
  to know they share plumbing.
* Integration tests inject a deterministic `Tracer(clock=)`
  rather than relying on `asyncio.sleep` timing. Wall-clock
  tests on CI are flaky; synthetic clocks are the way.

**Next suggested action:** `Extend Phase 5 §14 with an
\`EvalCase.timeout_s\` field + runner enforcement:
asyncio.wait_for wraps each case execution, failing the case
with a clean \`TimeoutError\` observation.error when it
exceeds timeout_s. Closes the gap that today's
LatencyWithin / LatencyDeltaWithin close only after the run
completes — a truly-stuck case hangs the whole suite until
the operator hits Ctrl+C.`

## 2026-04-23 — Phase 5 §12: token-delta

**Shipped** ``TokenDeltaWithin(max_delta)`` — the first
baseline-aware scorer. Reads ``case.baseline``, diffs baseline
vs observed token totals, fails when ``abs(delta) > max_delta``.
The existing baseline differ already reports the delta but never
gated CI on it; this scorer closes that loop for operators who
want "token cost shouldn't move by more than N between captured
baselines".

* **`TokenDeltaWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass. `__post_init__` rejects negative `max_delta`;
  zero is allowed as "tokens must match baseline exactly".
* **Baseline loading** — when `case.baseline` is None, fails
  cleanly with a message pointing at how to attach one
  (``case.baseline=`` or CLI ``--use-baseline``). When the
  file is missing, fails with the exact path. Both error
  paths are test-covered.
* **Symmetric by design** — ``abs(delta)`` comparison catches
  prompt changes that doubled tokens (positive delta) *and*
  changes that collapsed the answer to a one-liner (negative
  delta, often signalling the model bailed). Operators who
  only care about one direction can layer a future
  one-sided variant.
* **Delta diff reuses the existing core** — ``diff_event_streams``
  from `frok.evals.baseline` is imported at module top; no
  duplication between this scorer and the single-observation
  baseline differ already powering `EvalCase.baseline_diff`.
* **Failure detail** surfaces baseline tokens, observed
  tokens, and the signed delta — triage can tell at a glance
  which direction drifted. ``measure`` carries the signed
  delta (positive = observed used more) for aggregated
  trend-scanning.

**Verification.** `python3 -m pytest -q` → 595 passed in 1.54s
(16 new). Tests cover: construction rejects negative
`max_delta`, zero `max_delta` is allowed, no-baseline case
fails cleanly with guidance, missing-baseline-file fails with
the exact path, zero delta passes, small positive + small
negative deltas pass under threshold, inclusive at-threshold
in both directions, over-threshold positive + negative both
fail with baseline + observed + signed delta in detail,
``max_delta=0`` enforces exact parity, scorer name includes
the configured cap, and `measure` carries the signed delta
direction. Two integration tests wire the scorer through
`EvalRunner` end-to-end: the parity case passes, the drift
case (10 token baseline vs 100 token observed) fails with
``+90`` in the detail.

**Decisions / trade-offs.**
* Symmetric ``abs(delta)`` gate, not asymmetric `max_increase`
  / `max_decrease`. A one-liner bail is a real regression signal;
  treating positive and negative drift as equally suspect
  reflects that. YAGNI for the asymmetric form.
* Scorer loads the baseline file itself rather than relying on
  the runner's `baseline_diff`. `baseline_diff` is populated
  *after* scorers run (it's an `EvalResult` field), so a scorer
  that wanted to read it would need a runner refactor. Loading
  via `read_jsonl` keeps the scorer self-contained.
* `max_delta=0` is allowed as "exact parity". A case that's
  genuinely deterministic (`--seed` + stub transport) should
  trip on *any* token drift; forcing a positive minimum would
  rule that out.
* No separate "tokens drifted" telemetry event emitted. The
  eval report already surfaces the scorer's failure; adding
  a telemetry fire-and-forget would be double-reporting.

**Next suggested action:** `Extend Phase 5 §13 with
\`LatencyDeltaWithin(max_ms)\`: mirrors TokenDeltaWithin but
on root-span duration. Closes the second half of the
baseline-drift gate — operators regression-testing a prompt
change care about wall-clock impact as much as token cost,
and today there's no one-shot "tokens + latency both within
5% of baseline" assertion pair.`

## 2026-04-23 — Phase 5 §11: answer-length

**Shipped** ``AnswerLength(min_chars=None, max_chars=None)`` —
the shape gate complementing ``AnswerContains`` / ``AnswerMatches``
(content). Catches prompt regressions that start producing
one-word replies (set ``min_chars``) or runaway prompts that
emit long preambles before the actual answer (set ``max_chars``).

* **`AnswerLength`** (`frok/evals/scorers.py`) — frozen
  dataclass. Reads ``len(obs.answer)`` (which returns "" when
  no final response, so length 0 — consistent with the rest of
  the scorer family).
* **Construction validation** — ``__post_init__`` raises
  `ValueError` for the four malformed cases:
    * both bounds None (nothing to assert)
    * negative ``min_chars``
    * negative ``max_chars``
    * ``min_chars > max_chars`` (contradictory)
  ``min_chars == max_chars`` is allowed as "exact length".
* **Scorer name** dynamically reflects active bounds:
  ``answer_length[>=5]`` for min-only, ``answer_length[<=100]``
  for max-only, ``answer_length[>=3,<=10]`` for both. Aggregate
  reports can grep on exact / asymmetric / two-sided variants.
* **Measure** carries the observed length whether pass or
  fail — useful when post-hoc scanning runs to spot trends
  (e.g. "the 95p answer length crept from 80 to 150 chars
  over the last 20 baselines").

**Verification.** `python3 -m pytest -q` → 579 passed in 1.75s
(17 new). Tests cover: all four construction-error branches,
``min == max`` allowed as exact-length, min-only passes at/above
+ fails below, max-only passes at/below + fails above, both
bounds' closed-range pass + below-min + above-max fail paths,
empty answer (``obs.final_response is None``) correctly reports
length 0, scorer name formatting for min-only / max-only /
both, and measure always carries the observed length.

**Decisions / trade-offs.**
* Character-based, not token-based. Operators who need token
  ceilings layer ``TokensWithin`` alongside; a character
  gate doesn't need a tokenizer dependency and works
  identically across models.
* At-least-one-bound required at construction, not at call
  time. Fails fast when the case file loads, not on every
  invocation that silently asserts nothing.
* Empty answer (no final response) has length 0 — same
  contract the rest of the scorer family uses. Cases that
  need to fail on "no response at all" pair this with
  ``NoErrors``.
* ``min_chars == max_chars`` is allowed. An operator asserting
  a specific-length response (e.g. "yes/no answer") is a
  legitimate use; rejecting equality would force them to
  write two inequality scorers.

**Next suggested action:** `Extend Phase 5 §12 with a
\`TokenDeltaWithin(max_tokens, baseline=None)\` scorer: when a
baseline capture is attached (via \`case.baseline\`), assert
the token delta between observed and baseline runs stays
within a threshold. The existing baseline differ reports the
delta but never gates CI on it; this scorer lets operators
catch a prompt change that quietly doubled tokens without
diverging tool order (which would trip the existing
regressed=True flag).`

## 2026-04-23 — Phase 5 §10: invocations-ceiling

**Shipped** ``InvocationsWithin(max_count)`` — the aggregate
"don't loop forever" cap. `ToolCalled(..., times=N)` pins
per-tool counts; this scorer pins the total across every tool,
so a prompt regression that starts over-calling an arbitrary
tool surfaces without one scorer per tool.

* **`InvocationsWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring `LatencyWithin` / `TokensWithin` shape.
  Reads ``len(obs.invocations)`` — every tool call the
  orchestrator actually dispatched, regardless of which tool.
  Inclusive at-limit comparison; failure detail surfaces both
  actual and ceiling; measure carries the actual count.
* **Edge cases** — zero invocations passes any non-negative
  threshold (no-tools cases, blocked-before-tools cases, run-
  errored cases all report ``len([]) == 0``). Same-tool
  repeated invocations count as separate entries, which is the
  right behaviour for a "loop cap" assertion.
* **Exports** — added to `frok.evals.__all__` alphabetically.

**Verification.** `python3 -m pytest -q` → 562 passed in 1.65s
(7 new). Tests cover: pass under the ceiling with `measure`
populated, inclusive at-limit passes, over-ceiling fails with
both values in detail, zero invocations passes any non-
negative threshold, no-tools case passes any cap,
same-tool-repeated correctly counts each invocation, and the
scorer name includes the configured ``max_count`` for
aggregated reports to grep on.

**Decisions / trade-offs.**
* Aggregate across every tool, not per-tool. The per-tool
  variant is already ``ToolCalled(name, times=N)``. This is
  the "don't loop forever" cap; enumerating every tool's
  count would bury the real signal.
* Same-tool repeated invocations each count as one. A case
  that legitimately calls ``search`` three times can set
  ``max_count=3``; a case that calls it twice on purpose
  then blows up to 15 on a prompt regression will fire the
  scorer.
* No matching ``min_count`` ("at least N calls"). Operators
  who want "tool was called at least once" use
  ``ToolCalled(name)``; "at least N across any tool" hasn't
  come up. YAGNI.
* Zero-invocations path passes by default. A case that
  failed before any tool dispatch has a real signal
  (``NoErrors``, missing final response); double-tapping via
  an invocation-cap assertion would bury it.

**Next suggested action:** `Extend Phase 5 §11 with an
\`AnswerLength(min_chars=None, max_chars=None)\` scorer:
assert the assembled response length falls within a range.
Today's scorers assert answer CONTENT (\`AnswerContains\`,
\`AnswerMatches\`) but never answer LENGTH. A prompt
regression that starts producing one-word replies — or a
runaway prompt that emits 4000 tokens of preamble before the
actual answer — would both slip through the current scorer
set without a dedicated length gate.`

## 2026-04-23 — Phase 5 §9: latency-ceiling

**Shipped** ``LatencyWithin(max_ms)`` — the wall-clock gate that
pairs with ``TokensWithin`` (cost). CI runs now have a cheap way
to catch a prompt or tool-use pattern that quietly doubled
latency after a model swap.

* **`LatencyWithin`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring ``TokensWithin``'s shape. Reads
  ``obs.total_latency_ms`` (the root span's ``duration_ms``).
  Inclusive comparison: at-limit passes, strictly-over fails.
  Failure detail surfaces both the actual and the ceiling;
  ``measure`` carries the observed duration for aggregate
  reports.
* **Zero-latency fallback** — a run that errors before a root
  span closes reports 0.0 ms from the underlying `Observation`
  helper. The scorer passes any non-negative threshold in that
  case: the right signal for a failed run is ``NoErrors``, not
  a latency assertion. Documented in the scorer docstring.
* **Exports** — added to `frok.evals.__all__` so case-file
  authors can ``from frok.evals import LatencyWithin``.

**Verification.** `python3 -m pytest -q` → 555 passed in 1.68s
(7 new). Tests cover: pass under the ceiling with measure
populated, inclusive at-limit passes, over-limit fails with
both values in detail, missing root span → zero latency →
passes a non-negative threshold, missing root span + a
negative ceiling (pathological, but documents the compare),
run-error observation still passes (not the scorer's job),
and the scorer name includes the configured ``max_ms`` for
aggregated reports to grep on.

**Decisions / trade-offs.**
* Read from the observation's ``total_latency_ms``, not
  wall-clock time measured by the scorer. Cases run under
  repeats / parallel jobs / streaming — the only honest
  duration is what the root span recorded.
* Inclusive at-limit. An operator setting ``max_ms=500``
  usually means "at most 500 ms", not "strictly less than
  500 ms". Mirrors ``TokensWithin``.
* Zero-latency fallback passes by default. Failed runs
  already fail through the scorer stack (no final response,
  ``NoErrors`` trips, etc.); having latency-ceiling double-
  tap would bury the real failure under a misleading one.
* No separate ``min_ms`` (latency floor). We haven't seen a
  real need for "assert the model took at least N ms"; add
  if and when it comes up. YAGNI.

**Next suggested action:** `Extend Phase 5 §10 with an
\`InvocationsWithin(max_count)\` scorer: assert the total
number of tool invocations on a case stays below a threshold.
Complements \`ToolCalled(..., times=N)\` (per-tool exact count)
with an aggregate "don't loop forever" cap. Catches a prompt
regression that starts over-calling tools without having to
enumerate them in a scorer per tool.`

## 2026-04-23 — Phase 5 §8: tool-args-regex

**Shipped** ``ToolArgsMatch(name, regex, field=None, flags=0)`` —
the fuzzy counterpart to ``ToolArgsSubset``'s exact-equality
check. Operators can now assert "the tool call's query field
contains the user's question verbatim" without hand-writing a
scorer per case.

* **`ToolArgsMatch`** (`frok/evals/scorers.py`) — frozen
  dataclass. Two modes:
  * ``field=None`` — matches against ``json.dumps(args,
    sort_keys=True, default=str)``. Useful for "something
    anywhere in the args" assertions; sorted keys mean a
    regex can safely anchor on layout.
  * ``field="<key>"`` — matches against ``str(args[field])``.
    Missing keys surface as ``<missing>`` in the failure
    detail rather than silently skipping.
* **Matching semantics** — ``re.search`` (partial, like the
  existing ``AnswerMatches``); operators anchor with
  ``^``/``$`` when they want exact match. ``flags`` passes
  through so ``re.IGNORECASE`` etc. work.
* **Error handling** — invalid regex patterns fail the
  scorer with ``"invalid regex 'pat': <re.error>"`` rather
  than raising out of the runner. Matches the pattern used
  everywhere else in the codebase (e.g. `--filter re:...`).
* **Scorer name** — ``tool_args_match[<tool>:<field>]`` when
  a field is pinned, ``tool_args_match[<tool>]`` otherwise.
  Aggregate reports can grep by tool, field, or both.
* **Measure** — on success, the haystack that matched
  (JSON string or field value). Useful when post-hoc diffing
  runs.

**Verification.** `python3 -m pytest -q` → 548 passed in 1.57s
(14 new). Tests cover every branch: field-specific match /
fail / missing-field-placeholder, non-string values
stringified before regex (ints, lists), whole-args matching
anywhere in the JSON, sort-keys behaviour lets a regex anchor
on layout, tool-not-invoked fails cleanly, multi-invocation
semantics (any single match wins, no-match lists everything
seen), ``re.IGNORECASE`` via flags, anchored regex via
``re.search`` + ``^/$``, invalid regex degrades to a clean
fail, and scorer-name formatting covers both field-pinned and
whole-args modes.

**Decisions / trade-offs.**
* Field OR whole-args, not both. An operator who needs
  "any of two fields" can write two scorers; keeping the API
  one-argument-at-a-time keeps the signature readable.
* Measure carries the full haystack on pass, not just the
  matched substring. Easier for aggregated reports to surface
  "what the model actually sent"; the regex caller already
  has the pattern.
* Non-string args (ints, lists, dicts) are ``str()``'d before
  regex. Catches "the model called this with a numeric id
  ending in 42" without forcing the operator to JSON-encode
  the field by hand. The full-args mode JSON-encodes instead,
  which is the right choice when the shape matters.
* Invalid regex fails the scorer, doesn't raise. Every other
  user-facing regex in the codebase (CLI ``--filter re:...``,
  ``AnswerMatches``) follows this rule; cases shouldn't be
  able to crash the runner with a typo.

**Next suggested action:** `Extend Phase 5 §9 with a
\`LatencyWithin(max_ms)\` scorer: assert the case's root-span
duration_ms stays below a threshold. Complements
\`TokensWithin\` (cost ceiling) with a wall-clock ceiling for
CI — cheap way to catch a prompt or tool-use pattern that
quietly doubled latency on a model swap.`

## 2026-04-23 — Phase 5 §7: response-model-scorer

**Shipped** ``ResponseModelIs(expected)`` — completes the
model-regression loop. ``EvalCase.model`` (§6) pins the
*request*; this scorer pins the *response*. Together they catch
silent provider-side swaps that a request-only assertion would
miss.

* **`ResponseModelIs`** (`frok/evals/scorers.py`) — frozen
  dataclass mirroring every other scorer shape.
  `obs.final_response` None → clean ``Score.fail`` ("no final
  response — run failed before a model could be reported");
  mismatch → fail with both expected + actual in the detail;
  empty-string model is treated as a mismatch, not a pass.
  `measure` carries the actual model string so aggregated
  reports can surface which model actually served.
* **Export** — added to `frok.evals` public `__all__` so
  case-file authors can ``from frok.evals import
  ResponseModelIs``.

**Verification.** `python3 -m pytest -q` → 534 passed in 1.48s (7
new). Unit tests cover match (passes, measure carries value),
mismatch surfaces both values in detail + measure, missing
final-response fails cleanly, empty-string model is a
mismatch, and the generated scorer name includes the expected
value (grepped by aggregated reports). Integration tests run
the scorer through ``EvalRunner`` end-to-end: a case with
``model="grok-4-fast"`` + ``ResponseModelIs("grok-4-fast")``
passes when the server honours the pin, fails when the server
silently echoes ``grok-4-STALE`` — exactly the silent-swap
scenario the scorer was written for.

**Decisions / trade-offs.**
* Named `ResponseModelIs`, not `AnswerMatchesModel`. The
  suggestion in the prior §'s "next action" used the looser
  phrasing; renaming here for parity with `ToolCalled` /
  `NoErrors` / `ResponseModelIs` reads as "predicate about
  the response's model". Scorer names are API; getting them
  right matters.
* Strict string equality, no fuzzy matching. A "starts-with"
  or regex variant can layer on later if operators need to
  pin a model family (e.g. ``grok-4*``); today's need is
  exact-version regression.
* Empty-string model fails rather than passing on string
  equality with ``""`` (if expected happened to be empty).
  A server that returned no model isn't honouring the pin
  by accident — fail loudly.
* No special-case for no-tools vs tools paths. The scorer
  reads ``obs.final_response.model``; both paths populate
  that identically, so one implementation handles both.

**Next suggested action:** `Extend Phase 5 §8 with a
\`ToolArgsMatch(name, regex=...)\` scorer: assert that at
least one invocation of tool \`name\` has arguments matching
a regex (or a JSON-schema predicate). The existing
\`ToolArgsSubset\` only checks exact key/value matches;
regex / schema unlocks fuzzier assertions like "the query
string contains the user's question verbatim" without the
operator hand-writing a scorer per case.`

## 2026-04-23 — Phase 5 §6: model-override

**Shipped** per-call model overrides. Case authors can now pin a
specific model per `EvalCase` without scaffolding a second client
— the thing you need when regression-testing a model-version
upgrade (grok-4 → grok-4-fast, etc.).

* **`GrokClient`**
  * ``chat(..., model=...)`` and ``chat_stream(..., model=...)``
    accept an explicit override. Precedence:
    ``model kwarg > self.model``. Unlike ``tool_choice`` there
    is no "omit" path — a model is always on the wire.
  * ``effective_model = model or self.model`` computed once per
    call and used for the payload, the ``grok.chat`` /
    ``grok.chat_stream`` span attr, and the fallback used when
    the server's response omits the ``model`` field.
* **`ToolOrchestrator.model`** — new field, defaults to
  ``None`` (defer to ``client.model``). Passed to both
  ``chat()`` (non-stream path) and ``_streamed_turn``'s
  ``chat_stream()`` call, so every turn of a multi-turn tool
  run uses the same model.
* **`EvalCase.model`** — new optional field. The runner wires
  ``case.model`` into the orchestrator (tools path) and into
  both ``chat()`` / ``chat_stream()`` calls (no-tools path,
  streaming or not). ``None`` defers to the client default.

**Verification.** `python3 -m pytest -q` → 527 passed in 1.55s (13
new). Tests cover: ``chat`` without kwarg uses ``client.model``,
kwarg overrides, server response with no ``model`` field falls
back to ``effective_model`` (not ``client.model``), same three
paths for ``chat_stream``, ``grok.chat`` and ``grok.chat_stream``
span attrs report the effective model, orchestrator's ``model``
flows through *every* turn of a multi-turn run, orchestrator
defaults to ``client.model`` without override, ``EvalCase.model``
reaches the wire on no-tools / tools / streaming paths, and
``EvalCase.model=None`` correctly defers to ``client.model``.

**Decisions / trade-offs.**
* Two-level precedence (explicit > client), not three like
  ``tool_choice``. A model must always be on the wire, so there
  is no "omit the key" tier; the client default is the floor.
* ``EvalCase.model = None`` defers to the client default. We
  could have defaulted to ``"grok-4"`` and let ``None`` mean
  "use newest", but that couples the schema to a specific
  model name. Deferring to ``client.model`` keeps the case
  portable across client configurations.
* Span attr reflects the *effective* model, not the request or
  response. If a case overrides to ``grok-4-fast`` the span
  says ``grok-4-fast`` even if the server returns something
  odd. Post-hoc trace inspection needs the effective
  declaration, not the server echo.
* ``ToolOrchestrator.model`` is a field rather than a per-run
  argument. The orchestrator is already constructed per-case
  in the runner; adding one more constructor kwarg is lower-
  ceremony than threading it through ``run()``.
* ``EvalCase.model`` is a plain ``str | None``; the case-file
  API stays simple. When richer model-routing is needed (per-
  turn swaps, fallback chains), it can layer on via a custom
  ``make_client`` or a future ``frok.models`` module without
  breaking this surface.

**Next suggested action:** `Extend Phase 5 §7 with
\`AnswerMatchesModel(expected)\` scorer: asserts the
assembled GrokResponse.model equals the expected string.
Complements \`EvalCase.model=...\` by proving the right model
actually served the request (guards against silent mid-flight
model swaps on the provider side). Small but exactly the kind
of assertion a model-upgrade regression test needs.`

## 2026-04-23 — Phase 5 §5: tool-choice

**Shipped** a first-class ``tool_choice`` surface so cases can
assert the model *will* / *won't* / *must use tool X* rather than
hoping `"auto"` does the right thing. The orchestrator
hard-coded ``"auto"`` until today; lifting it to an explicit
kwarg unlocks pinned-behaviour tests.

* **`GrokClient`**
  * New ``tool_choice: str | dict | None = None`` field — the
    client-level default; ``None`` omits the key from the
    payload entirely.
  * ``chat(..., tool_choice=...)`` and
    ``chat_stream(..., tool_choice=...)`` accept an explicit
    kwarg. Precedence: explicit kwarg > client-level default >
    omit. Value flows to the top-level ``tool_choice`` field of
    the request body (same JSON shape xAI/OpenAI already
    consumes).
* **Config**
  * ``ClientConfig.tool_choice: str | dict | None`` plumbs
    through ``build_client`` → ``GrokClient.tool_choice``. Env
    ``FROK_CLIENT_TOOL_CHOICE=required`` works; dict-shaped
    values come through file (JSON / TOML) or CLI overrides.
  * ``to_toml`` emits dicts as TOML inline tables
    (``tool_choice = {type = "function", function = {name =
    "add"}}``) which ``tomllib`` round-trips cleanly.
  * ``to_env`` JSON-encodes dict values so the output is
    shell-injectable: ``FROK_CLIENT_TOOL_CHOICE={"type":...}``.
  * ``to_json`` was already dict-friendly; no change needed.
  * The unset-value render path still prints
    ``# tool_choice  (unset)`` in TOML.
* **`ToolOrchestrator`**
  * Switched to passing ``tool_choice`` via the new explicit
    kwarg instead of stuffing it into ``extra``. Cleaner;
    ``_streamed_turn`` also uses the explicit kwarg.
  * Default remains ``"auto"``.
* **`EvalCase.tool_choice`** — cases can pin behaviour without
  a custom client. The runner forwards
  ``case.tool_choice`` into ``ToolOrchestrator(tool_choice=…)``;
  ``None`` falls back to the orchestrator's ``"auto"``. No-tools
  cases ignore it (the orchestrator isn't engaged).

**Verification.** `python3 -m pytest -q` → 514 passed in 1.56s (21
new). Tests cover: ``chat`` omits the key by default, explicit
kwarg passes through, client-default applies when kwarg absent,
explicit wins over client default (including dict-shaped), same
three paths for ``chat_stream``, orchestrator forwards its
``tool_choice`` on *every* turn (not just the first), the default
is ``"auto"``, EvalCase string + dict values reach the wire via
the runner, config defaults to ``None``, env sets a string,
file accepts a dict, ``build_client`` propagates, render for all
three formats + inline-table TOML + JSON-in-env + the unset
comment.

**Decisions / trade-offs.**
* Three-level precedence (explicit > client > omit). "Omit"
  means the server picks, which is the right default for
  free-form chats; the client-level override is a convenient
  middle ground for config profiles (e.g. "force no tools in
  prod"), and the explicit kwarg is per-call surgery.
* Dropped the "stuff into extra" trick. Two paths to the same
  field are a smell; one typed kwarg makes the intent visible
  in every call site and in the spans.
* `EvalCase.tool_choice` defaults to ``None`` (fall back to
  orchestrator's ``"auto"``), not ``"auto"`` directly. Keeps
  the runner aware of "user didn't opt in"; a future global
  eval-harness config could apply a different default without
  having to parse out ``"auto"``.
* Render layer now handles dicts natively. We committed to
  supporting non-string `tool_choice` values; the
  ``config show`` output would otherwise stringify them into
  garbage. Inline-table TOML is the cleanest representation
  for our shallow nested schemas.
* Env-var JSON encoding is a compromise. Operators who want a
  dict via env need ``FROK_CLIENT_TOOL_CHOICE='{"type":...}'``,
  which is ugly but unambiguous; string values like
  ``"none"`` / ``"required"`` stay plain.

**Next suggested action:** `Extend Phase 5 §6 with
GrokClient.chat(..., model=...): allow per-call model overrides
so EvalCase authors can pin a specific model for a case
(regression-testing a model upgrade without scaffolding two
whole clients). Same precedence ladder as tool_choice —
explicit kwarg > client.model > no override — and surface on
EvalCase.model.`

## 2026-04-23 — Phase 5 §4: stream-tools

**Shipped** streaming through the `ToolOrchestrator` loop. `frok
run --stream` on a tools-enabled case now gives live feedback for
every chat turn instead of silently falling back.

* **`ToolOrchestrator.run(stream_sink=...)`** — new kwarg. Each
  loop iteration checks ``self.client.streaming_transport``:
  * **Available.** Issues `chat_stream` for the turn, forwards
    content deltas to the sink, and emits a ``\n>>> turn N\n``
    marker before each call. Final answer streams token-by-
    token; earlier tool-call turns are marker-only (their SSE
    payload has no content).
  * **Missing.** Falls back to non-stream `chat` silently —
    same behaviour callers already relied on. Preserves the
    "pass stream_sink unconditionally" contract.
* **Runner wiring** — `EvalRunner._execute` now forwards
  `stream_sink` into `orch.run(..., stream_sink=...)` instead of
  dropping it on the tools path. The "tools always silently
  fall back" comment disappears.
* **Telemetry** — `tool.run` span gains a ``streamed`` attr
  (True when the orchestrator used `chat_stream`, else False).
  Operators grepping the JsonlSink can now spot which runs
  streamed without replaying.
* **Helper extracted** — `ToolOrchestrator._streamed_turn`
  consumes `chat_stream`, forwards deltas, returns the final
  `GrokResponse`. Keeps the loop body readable and fails loudly
  (`ToolError`) if the stream ends before a final chunk
  arrives.

**Verification.** `python3 -m pytest -q` → 493 passed in 1.55s (7
new). Library tests cover: two-turn stream emits per-turn
markers + final-answer deltas in the right order + both turns
sent `stream=true`, fallback when `streaming_transport` is
missing (non-stream transport serves both turns, sink stays
empty), backward-compat path where `stream_sink` is None
continues to use `chat()` even when `streaming_transport`
exists, `tool.run.streamed` attr is True under streaming and
False without it, and short-stream (no explicit `[DONE]`) still
produces a clean final. CLI test
``test_stream_flows_through_tool_orchestrator_when_streaming_transport_set``
closes the end-to-end loop: a case with `tools=[add]` +
`streaming_transport` + `--stream` actually emits the turn
markers + streamed final answer via `frok run`.

**Decisions / trade-offs.**
* Per-turn markers (``>>> turn N``) rather than silent
  streaming. Tool-use cases have natural turn boundaries; the
  marker gives operators something to anchor on when scanning
  live output.
* Marker printed even for tool-call turns that produce no text
  content. Without it, the operator would see "nothing" for
  the first N-1 turns — indistinguishable from a hung process.
* Streaming capability is detected via `streaming_transport`
  presence, not a separate flag. One knob per concept;
  operators who configure a streaming transport implicitly
  opt into per-turn streaming.
* Telemetry gets a `streamed=bool` attr rather than a
  separate span name. Eval-harness scorers and trace-inspect
  renderers can already filter on span data; splitting the
  span into `tool.run.streamed` vs `tool.run.chat` would
  fragment the trace tree for no payoff.
* Kept the orchestrator non-stream path untouched when
  `stream_sink is None`. Existing callers (and the 74 tests
  covering them) continue to exercise the same code they did.

**Next suggested action:** `Extend Phase 5 §5 with
GrokClient.chat(..., tool_choice=) and a matching config knob:
expose "force call tool X" / "forbid tool use" semantics so
cases can assert that the model either uses a specific tool or
stays free-form. The orchestrator currently hard-codes
tool_choice="auto" — graduating it to a configurable argument
unlocks tests that pin tool-selection behaviour.`

## 2026-04-23 — Phase 5 §3: stream-cli

**Shipped** ``frok run --stream`` — live progress at the CLI. Long
answers no longer look hung; operators see tokens as the model
produces them while the `EvalReport` and scorers still get the
same assembled `GrokResponse` they did before.

* **`EvalRunner.run_case(..., stream_sink=callable)`** threads a
  per-delta callback into `_execute`. No tools: the runner uses
  ``client.chat_stream`` and forwards each content delta to
  `stream_sink` as it arrives, finalising into the same
  `GrokResponse` shape the non-stream path produces. Tools
  present: silently falls back to the non-stream orchestrator
  loop so callers can pass `stream_sink` unconditionally.
* **`build_client`** learned a `streaming_transport` kwarg; the
  `_default_client_factory` wires
  ``frok.clients.transports.urllib_streaming_transport`` so
  `--transport real` + `--stream` works out of the box.
* **`frok run --stream`** CLI flag
  * Per-case stderr header: ``\n>>> <case-name>\n``; each delta
    flushes to stderr raw; a trailing newline separates the
    stream from the report.
  * Incompatible with ``--jobs > 1`` — raises `CliError`.
    Interleaved stderr from concurrent tasks would be useless;
    operators who want both should use ``--summary-json`` and
    parse the machine-readable output instead.
  * Compatible with ``--repeat`` (serial stream per repeat),
    ``--capture-baseline``, ``--use-baseline``,
    ``--fail-on-regression``.

**Verification.** `python3 -m pytest -q` → 486 passed in 1.52s (8
new). Tests cover: argparse default + flag recognition,
``--stream`` writes the per-case header + every delta to stderr
(stub streaming transport scripts "Hello", ", ", "stream!"),
scorers still see the assembled final (case passes under
``--fail-on-regression``), tools-enabled case silently falls back
(header still prints, no deltas, non-stream transport fires),
``--stream`` + ``--jobs 2`` rejected with a specific error,
``--stream --jobs 1`` allowed, and a case whose `make_client`
omits `streaming_transport` surfaces the client's "no
streaming_transport" error as a case-level failure (not a CLI
crash).

**Decisions / trade-offs.**
* Output lands on stderr, not stdout. The Markdown report is
  stdout's job; streaming deltas are operator feedback that
  should survive pipes redirecting stdout.
* Tools-enabled cases silently fall back rather than streaming
  through the orchestrator loop. Each orchestrator iteration
  is its own chat call with its own streamed deltas —
  merging those into a coherent single-case display would need
  per-iteration headers / markers, which is design-work we
  haven't done yet. Fall-back keeps the flag usable now.
* ``--jobs > 1`` is a hard error, not a soft one. We could have
  serialised the stderr writes with a lock, but the result
  would be a jumble of "case A token / case B token" that
  nobody could read. Two concurrent cases can still run under
  ``--jobs 2`` — they just can't both stream.
* `streaming_transport` kwarg on `build_client` rather than a
  second factory. One config, one builder; the extra parameter
  defaults to None so existing callers are unchanged.
* Newline after every stream. The Markdown report starts on a
  fresh line regardless of whether the last delta ended with
  one.

**Next suggested action:** `Extend Phase 5 §4 with streaming
through the ToolOrchestrator loop: when --stream is set on a
tools-enabled case, yield deltas from each chat turn prefixed
with a per-turn marker (e.g. >>> turn 1, >>> turn 2), so tool-
use runs get the same live feedback as no-tools runs. Removes the
current silent fallback.`

## 2026-04-23 — Phase 5 §2: streaming

**Shipped** ``GrokClient.chat_stream`` — an async generator that
yields ``StreamChunk``s as SSE data arrives. Today's ``chat``
waits for the whole response; streaming unlocks live progress
indicators in the CLI and cuts apparent latency on long answers.

* **`StreamingTransport` protocol** (`frok/clients/grok.py`) —
  one-call shape returning ``(status, headers,
  AsyncIterator[bytes])``. Consistent with the existing
  `Transport` contract; callers await once, then iterate.
* **`StreamChunk(delta, tool_calls, finish_reason, is_final,
  response)`** frozen dataclass. Non-final chunks carry
  incremental text; the final chunk has ``is_final=True`` +
  ``response`` = the assembled `GrokResponse` (post-flight
  safety applied).
* **`GrokClient.chat_stream(messages, …)`**
  * Pre-flight safety runs on every inbound message (same shape
    as `chat`); a blocked prompt raises before any network call.
  * POST carries ``stream: true`` + an ``Accept: text/event-
    stream`` header; SSE chunks are parsed line-by-line via a
    module-level ``_iter_sse_events`` helper that tolerates
    blank / comment lines and malformed JSON.
  * Content deltas are yielded live as ``StreamChunk(delta=…)``.
    Tool-call deltas are accumulated via
    ``_merge_tool_call_delta`` and materialised as ``ToolCall``s
    on the final chunk.
  * After the stream ends (either ``[DONE]`` sentinel or
    connection close), post-flight safety runs on the
    accumulated content. If blocked, the generator raises
    ``GrokError`` instead of yielding the final chunk — the
    deltas already emitted are the caller's problem to redact;
    the contract is documented.
  * Emits a ``grok.chat_stream`` telemetry span with ``model``,
    ``message_count``, ``chunks``, ``content_chars``,
    ``tool_calls``, ``finish_reason``, and safety counts.
  * Shared pre-flight logic extracted into ``_preflight`` so
    `chat` and `chat_stream` can't drift on safety semantics.
* **`urllib_streaming_transport`** (`frok/clients/transports.py`)
  — stdlib streaming transport. Line-by-line read via
  ``asyncio.to_thread`` so the event loop isn't blocked; swap in
  httpx/aiohttp when production volume arrives. Handles 4xx/5xx
  by returning the status + a one-shot body iterator so
  `chat_stream` can surface a meaningful `HttpError`.

**Verification.** `python3 -m pytest -q` → 478 passed in 1.49s (19
new). Library tests cover `_iter_sse_events` (happy-path JSON,
``[DONE]`` sentinel, non-data/blank/comment lines, malformed-JSON
tolerance), `_merge_tool_call_delta` (fragment assembly, index
growth), and `chat_stream`: deltas yielded in order + request
body carries ``stream: true`` + ``Accept: text/event-stream``,
stream without ``[DONE]`` sentinel still produces a final chunk,
pre-flight blocks unsafe prompts before any network hit, PII
rewrites on prompts reach the wire, post-flight blocks unsafe
accumulated content (deltas already emitted), empty ruleset
skips safety, missing streaming_transport / empty messages / 4xx
all error correctly, tool-call deltas reassemble across fragments
and land as `ToolCall` on the final chunk, telemetry span carries
the expected attrs + records ``safety_blocked`` on a prompt
block.

**Decisions / trade-offs.**
* Post-flight safety runs *after* the stream completes, not
  chunk-by-chunk. Partial-text regex matching would be
  unreliable (a rule that fires on ``"guarantee"`` would miss a
  stream that yields ``"guar"`` + ``"antee"``); waiting for the
  full content is the honest contract.
* Live deltas are the caller's responsibility to redact when
  safety blocks the final. A CLI that renders live tokens
  should clear its buffer on `GrokError` rather than trust
  what it already drew — documented in the method docstring.
* New `StreamingTransport` protocol rather than overloading the
  existing `Transport`. Different return shape, different
  consumer pattern; muddling them would cost more than a second
  protocol type.
* Shared `_preflight` helper rather than duplicating the safety
  loop. The stream branch and the non-stream branch can't
  silently diverge on what counts as a blocked prompt.
* Ships with a stdlib streaming transport because the lack of
  one would be the first blocker for any real use. Throughput
  is modest (thread-hop per line); good-enough for a CLI live-
  progress display; operators with volume swap in httpx.

**Next suggested action:** `Extend Phase 5 §3 with \`frok run
--stream\`: flip the runner to use \`chat_stream\` + print each
delta to stderr as it arrives, so a live \`frok run cases/\*\`
gives operators a progress indicator. Cases still assemble a
normal \`EvalReport\` (stream finalises into the same
\`GrokResponse\`), so scorers and baseline diffs remain
untouched. Closes the "why does my long answer look hung?" UX
gap.`

## 2026-04-23 — Phase 5 §1: init-transport

**Shipped** ``frok init --transport {stub,real}`` — the "how do
I flip from stub to real?" gap-closer. Every example's docstring
previously told operators to swap the transport by hand; now
there's a flag that produces a ready-to-run live template.

* **New template** — ``_SMOKE_CASE_REAL`` is a ~20-line
  module: a single ``EvalCase`` with loose scorers
  (``AnswerMatches(r"\S")``, ``NoErrors()``), no ``make_client``,
  no ``_StubTransport``. The runner's default factory picks it up
  and wires ``frok.clients.transports.urllib_transport`` +
  whatever `FrokConfig.client` carries, so the only thing the
  operator needs to set is ``FROK_CLIENT_API_KEY``.
* **`_TRANSPORT_TEMPLATES`** map — ``stub`` → existing
  scripted-fake template; ``real`` → the live template. Keeps
  argparse's ``choices=`` list and the template lookup in one
  place.
* **Next-steps message is conditional**. Stub path still says
  "no API key is required yet"; real path walks the operator
  through setting ``FROK_CLIENT_API_KEY`` → running ``frok
  doctor`` → running the case for real.
* **Composition preserved**. ``--transport real --example
  tools`` still scaffolds the stub-backed ``cases/tools.py``;
  only the *smoke* case gets swapped. The examples rely on
  scripted tool-call sequences / canned descriptions that the
  real model can't be asked to reproduce deterministically.

**Verification.** `python3 -m pytest -q` → 459 passed in 1.56s (11
new). Tests cover: argparse default + real + bogus rejection,
stub default preserves every previously-asserted marker
(``_StubTransport`` / ``make_client`` / ``api_key="stub"``) and
the "no API key is required" next-steps line, real-template
content (no stub markers, FROK_CLIENT_API_KEY surfaced in the
docstring, module parses via ``ast.parse``, loose scorers
present), real template's next-steps block mentions
FROK_CLIENT_API_KEY + ``frok doctor``, real case errors with
exit 2 on a missing api_key (surfaced as ``ConfigError``), real
case runs green end-to-end when ``urllib_transport`` is
monkey-patched to a stub and an api_key is set (exercising the
exact default-factory code path), and real + ``--example``
composes correctly (smoke swapped, example stubs intact).

**Decisions / trade-offs.**
* Only the smoke case gets a real-transport variant. Examples
  script specific tool calls; the live model can't be promised
  to emit exactly those, and a "real" example that sometimes
  fails would undermine the first-impression principle the
  examples were written for.
* Loose scorers on the real smoke case (``\S`` regex). The point
  is "the call succeeded and the model said something"; tight
  assertions would force every operator to tune them per model
  on the first run.
* Default stays ``stub``. Backwards compatibility with the §1
  scaffold + zero surprise on a first-time ``frok init`` with
  no flags.
* Test for live-path uses a monkey-patched ``urllib_transport``
  imported into ``frok.cli.run``'s namespace. Production code
  paths are exercised end-to-end except for the wire itself —
  which is exactly the boundary a unit test should cut at.

Phase 5 opens with real-integration scaffolding; the remaining
§s can focus on the actual xAI API contract (streaming, tool-
choice hints, model-version swapping) now that the flip-to-real
path is a flag rather than a manual edit.

**Next suggested action:** `Extend Phase 5 with streaming support
in GrokClient: \`chat_stream(messages, …)\` yields content tokens
as they arrive over the wire, honoring the same safety / telemetry
hooks as \`chat()\`. Today a live run waits for the whole response;
streaming unlocks live progress indicators in the CLI and shorter
apparent latency on long answers.`

## 2026-04-23 — Phase 4 §6: help-polish

**Shipped** the root `frok --help` rewrite. First-time operators
who type `frok --help` now see what to do, not just a list of
subcommand names.

* **Description** names the "onboarding triple" (`init`,
  `doctor`, `run`) alongside a one-line mission statement. This
  block prints BEFORE the subcommand table so readers don't have
  to guess which three verbs to try first.
* **Epilog** lists the everyday operations (`config show`, `run
  --list`, `trace inspect`, `eval diff`, `eval summarize`) as
  copy-pasteable one-liners plus a "Reporting bugs: include the
  output of `frok version`" pointer.
* **Subcommand order** reshuffled for help-output UX: init →
  doctor → run → config → eval → trace → version. Argparse
  displays subparsers in registration order; the previous order
  was chronological by feature development, which is exactly
  backwards from what an operator wants to read.
* **`RawDescriptionHelpFormatter`** preserves the multi-line
  description + epilog layout. Default `HelpFormatter` collapses
  newlines, which would have reduced the block to one paragraph.
* **No external URLs** in the epilog. `CLAUDE.md` guidance says
  never to emit URLs we're not certain of, so the help points at
  local commands and files rather than a README link.

**Verification.** `python3 -m pytest -q` → 448 passed in 1.40s (9
new). Tests lock in: description names the ecosystem + onboarding
triple, epilog includes the quick-start and everyday-ops blocks
and the bug-report pointer, the raw formatter is the one actually
wired (preventing a silent regression to collapsed whitespace),
subcommand listing starts with the onboarding triple and ends
with `version`, and the parser still requires a subcommand when
none is passed.

**Decisions / trade-offs.**
* Onboarding triple before alphabetical. Operators read the
  listing top-down; the first three names should be the ones
  they should type first.
* Epilog is text, not a table. A table reads well in tabular
  data but not as "here are some useful commands"; a plain
  two-column text block composes with every terminal and pipe.
* Pointer at `frok version` for bug reports rather than an
  issue-tracker URL. We don't publish that URL from this tree,
  and the command is the thing triage actually needs.
* Formatter choice is tested. Defaulting back to
  `HelpFormatter` silently would undo the layout without any
  functional breakage — exactly the kind of regression that
  asymptotically costs you users.

Phase 4 is now closed at the onboarding layer. Next up is Phase
5-ish work: real-integration scaffolding (`urllib_transport` swap
recipes, end-to-end live smoke harness, multi-repo release
plumbing).

**Next suggested action:** `Begin Phase 5 with \`frok init
--transport real\`: when set, the generated cases/smoke.py swaps
the stub transport for \`urllib_transport\` + a config-driven
api_key check, so operators graduating past the stub get a
ready-to-run live template instead of hand-editing the file.
Closes the "how do I flip from stub to real?" gap surfaced by
every example's docstring.`

## 2026-04-23 — Phase 4 §5: version

**Shipped** ``frok version`` — the triage primitive. Prints the
installed frok version, the Python it's running on, and the
platform string. Small but load-bearing: every bug report starts
with "what version?", and this answers it with one command.

* **`VersionInfo`** dataclass + `collect_version_info()` helper in
  `frok/cli/version.py`. Pulls `frok.__version__`,
  `platform.python_version()`, `platform.platform(aliased=True)`.
* **Output modes**:
  * default — ``frok 0.24.0 (Python 3.11.15, Linux-6.18.5-x86_64-with-glibc2.39)``
    on one line, pipe-friendly and eye-friendly.
  * ``--short`` — just the frok version
    (``$(frok version --short)`` is shell-usable).
  * ``--json`` — ``{"frok": …, "python": …, "platform": …}``.
* **Flag precedence**: ``--short`` wins over ``--json`` when both
  are passed. ``--short`` is the most specific ask and scripting
  users pass it for a reason.

**Verification.** `python3 -m pytest -q` → 439 passed in 1.33s (8
new). Tests cover: argparse defaults + flag recognition,
`VersionInfo` matches `frok.__version__` / runtime values, default
one-line shape + regex-verified Python version, ``--short`` emits
only the version string, ``--json`` is parseable + complete,
``--short`` + ``--json`` both set → short wins (not JSON), exit
code 0 across all three modes.

**Decisions / trade-offs.**
* ``--short`` wins over ``--json`` silently. Erroring on the
  combination would be strictly-correct but unhelpful; the
  interpretation is obvious.
* ``platform(aliased=True)`` rather than `system()` alone. Bug
  triage wants the glibc / kernel / arch string, not just
  "Linux".
* No ``--verbose`` mode that dumps site-packages, interpreter
  path, etc. YAGNI — operators who need that run the one-liner
  directly.

**Next suggested action:** `Wrap Phase 4 with a \`frok --help\`
polish pass: a root-level description line pointing operators at
\`frok init\` / \`frok doctor\` / \`frok run\` as the onboarding
triple, plus a short epilog linking the README. Small but makes
the first \`frok\` invocation self-explanatory instead of just
listing subcommands.`

## 2026-04-23 — Phase 4 §4: doctor

**Shipped** ``frok doctor`` — the "does my setup actually work?"
preflight. Loads the resolved `FrokConfig` (same env + file +
profile merging the real run uses), runs one check per Phase-2
subsystem, and reports a PASS / FAIL / SKIP line for each.

* **`Check(name, status, detail)`** dataclass; ``PASS`` / ``FAIL`` /
  ``SKIP`` constants used everywhere for consistent filtering.
* **Library-level checks** (`frok/cli/doctor.py`)
  * ``check_config`` — reports the resolved profile + source.
  * ``check_safety`` — builds the ruleset and reports active /
    disabled rule counts.
  * ``check_telemetry`` — builds the configured sink, then closes
    it. `jsonl` without a path fails here.
  * ``check_memory`` — SKIP when disabled; otherwise builds the
    store, does a `remember → recall → forget` round-trip, and
    reports ok. Fails loudly on unsupported embedders or I/O
    errors.
  * ``check_multimodal`` — reports vision/voice toggle state.
  * ``check_client_live`` — skipped without ``client.api_key`` or
    with ``--no-live``; otherwise fires a real
    ``client.chat([GrokMessage("user", "ping")])`` through
    ``urllib_transport`` and reports token usage + model.
    Transport is injectable for tests.
* **`frok doctor` CLI** — wraps `_collect_checks` + `render_markdown`
  (default) / `render_json` (``--json``). Flags: ``-c/--config``,
  ``-p/--profile``, ``-o/--output``, ``--json``, ``--no-live``,
  ``--fail-on-skip``. Exit codes: 1 on any FAIL, 1 on any SKIP
  under ``--fail-on-skip``, else 0. Config load failure surfaces
  as ``CliError`` (exit 2) — same shape as the rest of the
  Phase-3 family.

**Verification.** `python3 -m pytest -q` → 431 passed in 1.32s (26
new). Library tests cover each check (config source reporting,
safety rule counting + disabled-rule surfacing, telemetry null /
jsonl-missing-path / jsonl-valid-path, memory skip / round-trip /
unsupported embedder, multimodal toggle reflection, client-live
skip-without-api-key / skip-under-no-live / pass-with-stub /
fail-on-500) and the renderers (markdown section presence + total
line, JSON shape + round-trip). CLI tests cover argparse shape +
defaults, happy-path markdown, ``--json`` parseability, ``-o``
file write, ``--fail-on-skip`` exit 1 when anything skips,
telemetry-failure producing exit 1, ``--no-live`` skipping
client-live even with an api_key present, config-load failure
surfacing as CliError, and an explicit ``-c`` flag reaching the
config check.

**Decisions / trade-offs.**
* Live chat hits the real API by default when an api_key is
  present. The alternative — opt-in with `--live` — would
  silently SKIP the check that most operators actually want
  when they run doctor. ``--no-live`` is the escape hatch for
  offline / CI-without-secret cases.
* Memory check does a full remember → recall → forget cycle
  rather than just opening the DB. Catches embedder
  misconfigurations and WAL-mode surprises that a pure
  open-and-close wouldn't.
* ``--fail-on-skip`` opt-in. A SKIP almost always means "not
  configured yet, but not broken" — the default exit code
  should keep that honest. Operators enforcing a fully
  configured stack in CI get the strict mode with one flag.
* Transport is injectable on ``check_client_live`` but not on
  the other checks. Memory and telemetry are covered by the
  Phase-2 tests; what we need to isolate here is the network
  call.

**Next suggested action:** `Extend Phase 4 with \`frok version\`:
print the installed package version (from \`frok.__version__\`) and
the Python runtime it's running on (platform.python_version()).
Small but essential for bug reports — the first thing any triage
asks is "what version?"`

## 2026-04-23 — Phase 4 §3: init-list-examples

**Shipped** ``frok init --list-examples`` — a discoverability flag
that prints every available ``--example`` name alongside its
one-line description, so operators can explore the scaffold
catalog without reading the source. Mirrors the ``frok run
--list`` pattern that already closes the "what am I about to run?"
gap; this closes the "what could I scaffold?" gap.

* **`_example_summary(src)`** (``frok/cli/init.py``) — parses a
  template's module-level docstring via ``ast.get_docstring`` and
  returns the first non-empty line. Syntax errors / missing
  docstrings degrade to an empty string rather than raising — a
  broken template shouldn't prevent `--list-examples` from
  surfacing the names.
* **`format_examples_list()`** — sorts the examples alphabetically,
  computes a shared left-column width based on the longest name,
  and returns a two-column text block terminated by a trailing
  newline. Pipe-friendly out of the box (``frok init
  --list-examples | cut -d' ' -f1`` gives just the names).
* **CLI short-circuit** — ``--list-examples`` branches off at the
  top of ``init_cmd`` before any existence check or directory
  creation. ``--example`` / ``--force`` / ``path`` are ignored
  when ``--list-examples`` is set; no files are ever written.

**Verification.** `python3 -m pytest -q` → 405 passed in 1.18s (12
new). Tests cover: argparse shape (default False + flag
recognition), every example name appears in output, descriptions
match each template's docstring first line, output is
alphabetically sorted, `_example_summary` handles a syntax error
and a docstring-less module gracefully, CLI output matches
``format_examples_list()``, no files are written under any
combination of flags, and an existing ``CLAUDE.md`` in the target
directory is preserved verbatim (proves the short-circuit
precedes every write path).

**Decisions / trade-offs.**
* ``ast.get_docstring`` rather than regex splicing. The templates
  are real Python; parsing them is the right tool and costs
  nothing at run time (this flag is rare).
* Two-column text, no table-drawing chars or colors. Fits
  anywhere (CI logs, terminals without unicode, files), and is
  trivial to pipe through ``awk``/``cut``.
* Alphabetical sort rather than insertion order. Stable + obvious
  from the CLI output; operators don't have to guess the
  canonical order.
* ``--list-examples`` ignores the rest of the flags rather than
  erroring on unknown combinations. A preview flag shouldn't be
  strict about what else the operator typed — they're discovering
  the space, not committing to an action.

**Next suggested action:** `Extend Phase 4 with \`frok doctor\`:
a preflight health check that loads the resolved config, attempts
a tiny \`client.chat(...)\` through \`urllib_transport\` if
\`client.api_key\` is set (otherwise skips), verifies
\`MemoryStore\` can open + write to \`memory.path\` when
\`memory.enabled\`, and reports a concise pass/fail per subsystem.
Gives new users a definitive "your setup works" signal before
their first real run.`

## 2026-04-23 — Phase 4 §2: init-examples

**Shipped** ``frok init --example {tools,multimodal,memory}`` — a
repeatable flag that adds working reference cases alongside the
basic smoke scaffold. Each example runs green out of the box,
demonstrates one major Phase-2 surface, and carries a "production
swap" docstring pointing at the real transport/store choices.

* **`cases/tools.py`** — `@tool def add(a,b)` + a stub transport
  scripted for one tool call + one final answer; scorers:
  `AnswerContains("42")`, `ToolCalled("add", times=1)`,
  `NoErrors()`. Proves the ToolOrchestrator drives the loop
  end-to-end.
* **`cases/multimodal.py`** — a `GrokMessage` with `parts=(text,
  image_url)` built via `ImageRef.from_bytes(...).to_content_part()`
  and a stub that returns a canned description. The case runs
  without vision creds and shows the exact wire shape Grok
  expects for image messages.
* **`cases/memory.py`** — shared ``MemoryStore(":memory:",
  HashEmbedder(dim=64))`` exposed as two typed tools
  (``remember(text)``, ``recall(query, k)``). Stub scripts a
  remember → recall → final-answer sequence; ToolCalled + answer
  scorers confirm the model exercised both paths. Demonstrates
  the typical "memory as tools" pattern.
* **CLI wiring** — `--example NAME` is an `action="append"` with
  `choices=sorted(EXAMPLE_TEMPLATES)`. Unknown values are
  rejected by argparse before any I/O. `init_cmd` composes
  `TEMPLATES | {f"cases/{n}.py": EXAMPLE_TEMPLATES[n]}` so every
  existence check and ``--force`` guarantee from §1 applies to
  the example files too.

**Verification.** `python3 -m pytest -q` → 393 passed in 1.20s (16
new). Tests cover: argparse accepting known names and rejecting
unknown ones, default `--example` list is empty, no-flag scaffold
matches §1 exactly, each of the three examples scaffolds its
file, multi-flag composition, existence-abort on a pre-existing
example file, ``--force`` overwrite, each example running green
under ``frok run --fail-on-regression`` (parametrized over all
three), a tools-specific check that `ToolCalled` actually passed
(proves the orchestrator fired), a multimodal check that the
content parts hit the wire via direct import + runner, and a
memory check that both `remember` and `recall` were invoked.

**Decisions / trade-offs.**
* Examples live as template constants in `frok/cli/init.py`
  alongside the base templates — same zero-ceremony pattern from
  §1. Edits are Python commits.
* Each example uses a stub transport rather than
  ``urllib_transport``. The docstring calls out the swap; green
  runs out of the box matter more than "realistic" network
  behaviour.
* Memory example uses `:memory:` SQLite + a module-level shared
  store. The state survives the whole (case, run) and dies when
  the module is GCed. Production users swap to a file path;
  that's one line.
* Multimodal example builds parts directly in the `GrokMessage`
  rather than spinning up a `MultimodalAdapter`. The adapter is
  showcased implicitly via `ImageRef.to_content_part()`; going
  through the adapter would have required its own chat
  invocation wrapper, which doesn't map cleanly to an
  `EvalCase`. The example's docstring points at the adapter for
  production use.
* ``--example`` uses argparse `choices=` for validation rather
  than a post-hoc `CliError`. Tightens the bad-input path with
  less code.

**Next suggested action:** `Extend Phase 4 with \`frok init
--list-examples\`: print the available \`--example\` names along
with each one's docstring first line, so operators can
discover what's available without reading the source. Closes
the "what examples do I have?" discoverability gap parallel to
\`frok run --list\` closing the "what cases am I about to run?"
gap.`

## 2026-04-23 — Phase 4 §1: init-scaffold

**Shipped** ``frok init [PATH]`` — the onboarding command that
closes the "okay how do I actually start using this" gap.
Writes four files; the generated project runs end-to-end with no
further setup because the smoke case uses a stub transport.

* **Templates** (`frok/cli/init.py`, inline constants)
  * ``CLAUDE.md`` — project-scoped instructions linking the
    operator to the key subcommands and the baseline workflow.
  * ``frok.toml`` — every `FrokConfig` section populated, with a
    ``[profiles.prod.telemetry]`` override showing how profile
    merging works.
  * ``cases/smoke.py`` — one `EvalCase` + a ``make_client`` that
    returns a `GrokClient` wired to a stub transport. Replacing
    the transport with `urllib_transport` is the documented next
    step.
  * ``.github/workflows/frok.yml`` — PR-gating workflow using
    ``--fail-on-regression`` + an artifact upload, with a
    commented-out baseline-capture job on `main`.
* **`frok init`** — abort-if-any-exists by default
  (``CliError`` listing the offending files); ``--force`` to
  overwrite. Directories are `mkdir -p`'d. Writes a Next-steps
  block to stdout so the operator sees the three commands they
  should run next. ``path`` defaults to ``.``.

**Verification.** `python3 -m pytest -q` → 377 passed in 1.10s (14
new). Tests cover: argparse shape + default path, full-scaffold
write, nested path creation, existing-files abort + file
preservation, `--force` overwrite behaviour, generated
``frok.toml`` loading via `load_config` (base + `prod` profile),
``tomllib.loads`` round-trip of the template, the generated
smoke case running green via `frok run --fail-on-regression`,
``frok run --list`` over the generated case, the generated
``CLAUDE.md`` and workflow containing their promised references,
and an all-or-nothing guarantee (a partial existing tree doesn't
get half-scaffolded).

**Decisions / trade-offs.**
* Templates live as inline string constants rather than package-
  data files. No MANIFEST / package_data / importlib.resources
  ceremony; edits to the templates are an ordinary Python
  commit.
* The smoke case uses a stub transport, not real xAI. ``frok
  init && frok run cases/smoke.py`` passing out-of-the-box is
  the single best signal that the install works.
* Abort-if-any-exists is stricter than "skip if exists" — a
  partial scaffold is more confusing than a loud ``--force``
  requirement.
* The workflow comments out the baseline-capture job. It's a
  real pattern but requires a decision about where baselines
  live; better to enable it consciously than have a workflow
  fail on the first run because a secret's unset.

**Next suggested action:** `Extend Phase 4 with \`frok init
--example tools\` / \`--example multimodal\` / \`--example
memory\`: the basic smoke scaffold plus a second case file
showcasing the ToolOrchestrator / MultimodalAdapter / MemoryAgent
respectively. Closes the "great, now how do I wire up more of the
stack?" gap with working, runnable reference cases.`

## 2026-04-23 — Phase 3 §11: parallel-jobs

**Shipped** ``frok run --jobs N`` — concurrent case execution
under an `asyncio.Semaphore`. Default stays serial (N=1), so
every existing test and operator muscle-memory run is unchanged.
With N>1, up to N (case, repeat) units run at once; results come
back in submission order so the `EvalReport` always reflects the
case file's ordering regardless of which unit finished first.

* **Unified unit coroutine** in `run_cmd`: each
  `(case, repeat_idx)` pair maps to a task that acquires the
  shared semaphore, applies the seed (if any), runs through
  `EvalRunner.run_case`, and closes its JsonlSink in ``finally``.
  All tasks are created up front and driven by one
  ``asyncio.gather``; the order of the resulting list mirrors the
  order of creation.
* **Clamp to `os.cpu_count()`**: `jobs = min(args.jobs, cpu_cap)`.
  Requesting 1000 workers silently becomes whatever the box can
  actually run. `cpu_count()` returning `None` falls back to 1.
* **Mutual-exclusion guards**:
  * `--seed` + `--jobs > 1` raises `CliError`. Python's `random`
    state is process-global; parallel tasks would step on each
    other's seeding and no "determinism" would survive.
  * `--jobs 0` (and negative) raises at the CLI layer, same
    shape as the existing `--repeat` guard.
  * `--capture-baseline` still works with `--jobs > 1` — each
    case owns its own `<slug>.jsonl`; no collisions because
    `--repeat > 1` was already excluded.

**Verification.** `python3 -m pytest -q` → 363 passed in 0.97s (11
new). Tests cover: defaults (--jobs 1 == no flag), explicit serial
matches default, --jobs 4 preserves case order across 6 cases,
--jobs 3 with --repeat 3 produces 18 runs (6 cases × 3 repeats),
--jobs 4 with --capture-baseline writes all per-case JSONL files,
silent clamping to a monkey-patched `os.cpu_count() == 2`,
`cpu_count() is None` fallback, --jobs 0 / negative errors, --seed
+ --jobs > 1 errors, --seed + --jobs 1 still works, and a smoke
test that a parallel run completes without deadlocking.

**Decisions / trade-offs.**
* Semaphore over task pool. `asyncio.Semaphore(jobs)` is the
  simplest primitive that gets "at most N in flight" right. No
  need for a worker pool; `gather` collects everything.
* Submission-order, not completion-order, results. The Markdown
  report reads top-to-bottom the way the case file is authored.
* Seed + jobs are mutually exclusive rather than partially
  compatible. Any scheme that tried to serialise just the
  seed-touching work would either reintroduce global ordering
  (defeating --jobs) or fragment the abstraction. Explicit
  error is cleaner.
* Clamp is silent. Operators who want to know actually ran `K`
  workers can check the system's `os.cpu_count()` — surfacing it
  on every invocation would spam CI logs.

**Next suggested action:** `Begin Phase 4 with \`frok init\`:
scaffold a new project — create a CLAUDE.md stub, a minimal
case file, a \`frok.toml\` config template, and a
\`.github/workflows/frok.yml\` snippet demonstrating capture /
diff / fail-on-regression. Closes the "okay how do I actually
start using this" gap for new users.`

## 2026-04-23 — Phase 3 §10: repeat-runs

**Shipped** ``frok run --repeat N --seed S`` — executes each case
N times with a deterministic seed so operators can cleanly
separate "the case regressed" from "the scorer is flaky". The
``EvalReport`` aggregates by case name with a pass rate; any case
in (0, 1) is surfaced as `FLAKY` distinctly from `FAIL`.

* **`EvalResult`** grew optional ``repeat`` (0-based index) and
  ``repeats`` (total) fields. Defaults (0/1) preserve the existing
  shape; `to_summary()` only surfaces the new fields when
  ``repeats > 1``.
* **`EvalReport`** now exposes ``by_case`` / ``case_pass_rates``
  / ``total_cases`` / ``passed_cases`` / ``flaky_cases`` /
  ``failed_cases``. The Markdown renderer has two paths:
  * flat (existing) when every case has ``repeats == 1`` — no
    downstream test asserting on the current shape had to change.
  * aggregated when any case has ``repeats > 1`` — one row per
    case with a pass-rate column, a FLAKY/FAIL/PASS verdict, and
    the per-repeat failure list below for non-all-passing cases.
    The failure list uses scorer-name union across repeats.
* **`EvalRunner.run(cases, *, repeats=1)`** / ``run_case(case, *,
  repeat, repeats)`` — runner loops repeats internally when
  invoked via ``run`` and accepts explicit positions via
  ``run_case`` so the CLI can stamp them.
* **CLI `--repeat N` / `--seed S`** (`frok/cli/run.py`)
  * ``--repeat`` validates ``>= 1`` at the CLI layer.
  * ``apply_seed(seed, repeat_index)`` calls ``random.seed(seed +
    repeat_index)`` and publishes ``FROK_RUN_SEED`` per repeat
    before `make_client` runs, so a case file's stub transport
    can read the env var and react deterministically.
  * ``--repeat > 1`` + ``--capture-baseline`` raises ``CliError``
    — the per-case JSONL filenames would collide. Operators are
    directed to capture once and use ``--use-baseline`` on
    subsequent repeat runs.

**Verification.** `python3 -m pytest -q` → 352 passed in 0.90s (17
new). Library tests cover default repeat fields, flat-format
preservation on single-repeat runs, ``by_case`` grouping,
``case_pass_rates`` across flaky + all-pass + all-fail cases,
aggregated-markdown column presence + FLAKY verdict + per-repeat
detail, summary shape for both single- and multi-repeat runs.
CLI tests cover the ``apply_seed`` helper (env var + `random`
determinism + per-repeat shift), end-to-end ``--repeat 3``
flaky-case production (2/3 pass), aggregated markdown column +
FLAKY surfacing, ``--fail-on-regression`` flipping exit on any
failed repeat, ``--seed`` publishing ``FROK_RUN_SEED`` before
``make_client`` (verified through the aggregated Failed-scorers
column), and both error paths (``--repeat 0`` and
``--repeat > 1`` + ``--capture-baseline``).

**Decisions / trade-offs.**
* Aggregate Markdown only when ``repeats > 1``. The existing flat
  table is optimized for single-run output; changing it globally
  would break operator muscle memory and churn test assertions.
* Seed is ``S + repeat_index``, not ``S``. Two repeats of the
  same case need distinct stochastic paths, otherwise a flaky
  case would appear deterministic.
* ``FROK_RUN_SEED`` env var rather than a constructor argument.
  Case-file ``make_client`` functions don't have a stable
  contract for receiving runner-internal state; an env var is
  the Unix-native escape hatch.
* ``--repeat > 1`` + ``--capture-baseline`` fails loudly rather
  than silently overwriting the JSONL. If operators want a
  repeat-with-capture flow, they can capture the first repeat
  manually or use ``--use-baseline`` against a one-shot capture.

**Next suggested action:** `Extend Phase 3 with the final CI-
ergonomics flag \`frok run --jobs N\`: run cases in parallel
across N workers (respecting --repeat so each case gets its N
repeats, but different cases can interleave). Default stays
serial (N=1). Caps at os.cpu_count(). Closes the "my eval suite
takes forever" complaint without compromising determinism — each
case's output is still collected in the same EvalReport order.`

## 2026-04-23 — Phase 3 §9: eval-dirdiff

**Shipped** ``frok eval summarize <a> --diff-against <b>`` — the
one-shot "did this PR regress any of my captured baselines?"
command. Two directories of `<slug>.jsonl` captures, one report,
CI-gateable.

* **Library** (`frok/evals/baseline.py`)
  * ``CaseDiff`` — one matched pair (name, a_path, b_path, and
    the ``diff_event_streams`` payload). ``.regressed`` mirrors
    the payload.
  * ``DirectoryDiff`` — matched list + ``only_in_a`` /
    ``only_in_b`` slug sets + ``regressed_cases`` +
    ``regressed`` rollup. The rollup flips on either a matched-
    case regression *or* slug divergence — operators opting into
    ``--diff-against`` probably want to know about both.
  * ``diff_directories(a, b)`` walks each side via `<dir>/*.jsonl`
    (sorted, empty captures silently skipped) and diffs each
    matched pair through the shared ``diff_event_streams`` core.
  * ``directory_diff_to_markdown`` / ``_to_json`` renderers;
    Markdown hides Only-in / Regression-details sections when
    they'd be empty.
* **CLI** (`frok/cli/eval.py`)
  * `frok eval summarize <DIR>` gained ``--diff-against <DIR>``
    that short-circuits the single-dir rollup into directory-
    diff mode.
  * Companion ``--fail-on-regression`` flag (distinct from the
    existing ``--fail-on-errors`` which remains in single-dir
    mode). Missing / not-a-directory `--diff-against` targets
    raise ``CliError`` via a shared ``_require_dir`` helper.

**Verification.** `python3 -m pytest -q` → 335 passed in 0.87s (19
new). Library tests cover identical directories, added /
removed slugs, tool-order regression, token-only delta not
regressing, new-error regression, empty-capture skipping, missing-
directory errors, Markdown section presence + hiding on clean
diffs, and JSON round-trip. CLI tests cover argparse shape, clean
exit-0 under ``--fail-on-regression``, tool-order divergence
flipping exit to 1, slug divergence flagged in both JSON and
Markdown, token-only delta staying clean, ``-o`` file write,
missing / not-a-dir ``--diff-against`` errors, and — crucially —
that the single-dir path still works unchanged when
``--diff-against`` is absent.

**Decisions / trade-offs.**
* Reused ``summarize`` as the subcommand verb rather than adding
  a new one. The flag cleanly toggles modes, help output shows
  both, and operators don't have to memorise a second command
  name.
* Slug divergence is treated as a regression by default. A case
  silently appearing or disappearing between runs is almost
  always a bug to investigate; the operator can still post-
  process the JSON if they disagree.
* Matching is by exact slug (file stem). Fuzzy matching across
  renames is out of scope — if a case got renamed, the operator
  explicitly handles that via the list the CLI surfaces in
  ``only_in_a`` / ``only_in_b``.
* Per-case regression details section only renders for the
  cases that actually regressed. Markdown stays tight when the
  PR is clean; the info is there when it isn't.

**Next suggested action:** `Extend Phase 3 with \`frok run
--repeat N\` + \`--seed S\`: execute each case N times with a
deterministic seed so flaky-scorer investigations can quickly
separate "the case regressed" from "the case is inherently
non-deterministic". The repeat aggregate becomes a pass-rate in
the EvalReport; the seed lets CI re-stage the same run
identically.`

## 2026-04-23 — Phase 3 §8: eval-summarize

**Shipped** ``frok eval summarize <dir>`` — a directory-wide
rollup over a bag of `JsonlSink` captures. Closes the last
discoverability gap: today operators could `trace inspect` one
file or `eval diff` two; now they can point at a
``--capture-baseline`` directory and get one report.

* **`frok.telemetry.analysis`** (extension)
  * ``CaseSummary`` — per-capture rollup: name (file stem),
    path, span count, total tokens (from `grok.chat`), error
    count, duration (sum of root spans), tool counts, errored
    tool counts.
  * ``DirectorySummary`` — cases + aggregate properties
    (``total_spans`` / ``total_tokens`` / ``total_errors`` /
    ``tool_counts`` / ``errored_tool_counts``) and leader
    methods (``slowest(n)`` / ``heaviest_tokens(n)`` /
    ``most_errors(n)``).
  * ``summarize_directory(dir)`` walks ``<dir>/*.jsonl`` in
    sorted order, skipping empty captures; raises
    ``NotADirectoryError`` if the path isn't a directory.
  * ``dir_summary_to_markdown`` + ``dir_summary_to_json``
    renderers. Markdown hides leader sections that'd be empty
    (no errored tools, no errored cases) so a clean run's report
    stays tight.
* **`frok eval summarize <dir>`** (`frok/cli/eval.py`)
  * Flags: `-o/--output`, `--json`, `--top N` (default 5),
    `--fail-on-errors` for CI. Missing / not-a-dir / empty
    directory all raise ``CliError`` (exit 2); full traces in
    empty JSONL files are silently skipped so a partial capture
    doesn't tank the whole report.
  * Lives under the existing `eval` subparser alongside
    `eval diff`.

**Verification.** `python3 -m pytest -q` → 316 passed in 0.89s (24
new). Library tests cover the directory walker (sorted order,
non-jsonl files ignored, missing dir errors, empty captures
skipped); CaseSummary field correctness (token aggregation, chat+
tool error counting, tool/errored tool counts, root-span duration
summation with nested children excluded); DirectorySummary
aggregates (tool merging, errored-tool merging, slowest/heaviest/
most-errors leader ordering); renderers (all section headers
present, empty leader sections hidden, JSON round-trips). CLI
tests cover argparse shape, Markdown + JSON outputs, `-o` writes
+ stdout suppression, `--top` caps leader rows but not per-case
rollup, `--fail-on-errors` flips the exit code, error paths
(missing dir, not-a-directory, empty directory), and an end-to-
end interop test that pipes a `frok run --capture-baseline` run
directly into `frok eval summarize` and asserts both case names
appear.

**Decisions / trade-offs.**
* Directory walker silently skips empty JSONL files rather than
  erroring — a half-written capture from a crashed run
  shouldn't prevent the operator from summarising the 99 that
  succeeded.
* `--top` caps only the leader tables, not the per-case rollup.
  A dashboard for 200 cases should list all 200 but highlight
  the top-N on each dimension.
* Errored-tool and errored-case sections are hidden on clean
  runs. Operators who scroll a perfectly-green report shouldn't
  be made to stare at empty "## Tools with errors" headers.
* Directory aggregation reuses the single-capture `summarize`
  helper so the two entry points can't drift on what counts as
  a tool invocation, a token, or an error.

**Next suggested action:** `Extend Phase 3 with \`frok eval
summarize --diff-against <dir>\`: two directories, each a set of
\`<slug>.jsonl\` captures; surface per-case diffs (tokens,
tool-order, errors) where the slugs match, and flag slugs that
appear in one side but not the other. Makes it a one-shot "did
the PR regress any of my captured baselines?" command.`

## 2026-04-23 — Phase 3 §7: eval-diff

**Shipped** ``frok eval diff <a.jsonl> <b.jsonl>`` — symmetric
two-capture comparison for A/B testing prompt / model / config
changes. Complements the single-capture ``trace inspect`` and the
per-case ``--use-baseline`` with a general two-sided diff that
lives outside a live run.

* **Library refactor** (`frok/evals/baseline.py`)
  * Extracted the comparison core into
    ``diff_event_streams(a_events, b_events, *, a_label, b_label)``.
    Returns tool-order match, per-side tools / tokens / errors /
    span counts, deltas (`token_delta`, `span_delta`), and a
    ``regressed`` verdict (tool-order divergence or new errors in
    ``b``). Labels parameterise the dict keys.
  * ``diff_against_baseline(obs, path)`` now delegates to the
    above with legacy labels ``"baseline"``/``"observed"`` —
    existing `EvalRunner` consumers and every previously-shipped
    assertion key are preserved.
  * Added ``diff_to_markdown(diff, *, a_label, b_label, a_path,
    b_path)`` for a compact verdict rendering with tool-order /
    tokens / errors sections.
* **`frok eval diff` CLI** (`frok/cli/eval.py`)
  * `a` is the reference ("before"), `b` is the candidate
    ("after"). Missing / empty / malformed captures raise
    `CliError` (exit 2), matching `trace inspect`'s semantics.
  * Flags: `-o/--output`, `--json`, `--fail-on-regression`.
    JSON output includes `a_path` / `b_path` so downstream
    tooling has everything it needs in one payload.

**Verification.** `python3 -m pytest -q` → 292 passed in 0.73s (19
new). Tests cover: `diff_event_streams` across identical, tool-
order divergence, token-delta-only (no regression), new errors in
``b`` (regression), fewer errors in ``b`` (floor at zero), custom
label key-rename, span-count delta; `diff_to_markdown` sections +
signed token delta; CLI argparse shape, identical captures clean
exit, divergence regresses under `--fail-on-regression`, clean
diff stays 0, `--json` parseable with paths, `-o` writes file and
suppresses stdout, and all three error paths (missing / empty /
malformed).

**Decisions / trade-offs.**
* One pure-function helper shared between "live vs captured" and
  "captured vs captured" paths — same matcher, same semantics, so
  the two tools can't drift on what counts as a regression.
* `a` and `b` labels in the general helper, `baseline` /
  `observed` in the back-compat wrapper. Downstream code reading
  either set of keys keeps working.
* Token deltas reported but don't flip ``regressed``. Longer
  correct answers shouldn't fail CI; tool-order and errors are
  the trust-relevant signals.
* The CLI preserves exit-code semantics across the Phase-3
  family: ``--fail-on-regression`` → 1 on divergence; CliError
  → 2 on operator mistakes; 0 otherwise.

**Next suggested action:** `Extend Phase 3 with \`frok eval
summarize <dir>\`: walk a baseline directory, run \`trace
inspect\` across every \`<slug>.jsonl\` in it, and emit an
aggregated Markdown (or JSON) report — per-case span-count /
token / error rollups plus cross-case leaders (slowest cases,
most-errored tools). Closes the last gap: today operators can
inspect one capture or diff two, but there's no "scan my whole
baseline folder" command.`

## 2026-04-23 — Phase 3 §6: list-preview

**Shipped** ``frok run --list`` — an early-exit preview that prints
the resolved case names (after ``--filter`` / ``--exclude``) one per
line and returns without constructing a client or running any
case. Completes the discoverability loop alongside ``config show``
and ``trace inspect``.

* **`run_cmd` short-circuit**: after filter application, if
  ``--list`` is set, print names and ``return 0`` — before any
  ``build_client`` / ``JsonlSink`` / ``runner.run_case`` work. No
  api_key is required, no capture files are written.
* **Output format**: one case name per line with a trailing
  newline. Pipe-friendly by construction
  (``frok run cases.py --list | grep safety``).
* **Flags reused**: ``-o/--output`` writes to a file (parents are
  `mkdir -p`-ed) and suppresses stdout; ``--filter`` / ``--exclude``
  apply normally.

**Verification.** `python3 -m pytest -q` → 273 passed in 0.62s (10
new). Tests cover: basic output + ordering, filter / exclude /
regex-prefix interop, zero-match still errors (filters apply
before the list branch), ``-o`` writes file + blanks stdout, the
empty stub transport is NOT called under ``--list``, api-key-free
case files still list fine, and ``--list --capture-baseline``
writes nothing since the loop never runs.

**Decisions / trade-offs.**
* Minimal format: just names. Richer previews (scorer / tool
  counts, baseline status) can be bolted on via a future
  ``--list --format=table`` without breaking the simple
  lines-on-stdout contract.
* ``--list`` runs AFTER filter application but BEFORE client
  construction — so the printed list is exactly what a non-list
  invocation would execute, giving operators a faithful preview.
* Zero-match still errors (exit 2) under ``--list``. Operators
  using ``--list`` to sanity-check filters should get the same
  feedback they'd get on a real run; silent empty output would be
  a worse experience than the "no cases matched" message that
  lists available names.

**Next suggested action:** `Extend Phase 3 with \`frok eval diff
<a.jsonl> <b.jsonl>\`: diff two JsonlSink captures side-by-side
(tool-call order, token delta, new errors, span count) and print
a compact report. Complements \`trace inspect\` (single capture)
and \`--use-baseline\` (per-case diff) with a general two-capture
comparison for A/B testing prompt / model / config changes.`

## 2026-04-23 — Phase 3 §5: case-filter

**Shipped** ``frok run --filter <pattern>`` / ``--exclude <pattern>``
so CI and local iteration can re-run a subset of cases without
editing the case file to comment cases out.

* **`frok.cli.run.filter_cases(cases, *, includes, excludes)`** —
  pure-function helper. A case is kept when (includes empty OR any
  include matches) AND no exclude matches.
* **Pattern syntax**: fnmatch glob by default (``safety-*``),
  `re:` prefix for a Python regex (``re:^tool-``). Glob comparison
  is case-sensitive (`fnmatchcase`); regex uses `re.search` so
  partial matches work the same way people expect from `grep`.
* **Flags** (repeatable, union semantics):
  * `--filter PATTERN` — keep matches.
  * `--exclude PATTERN` — drop matches. Exclude wins over filter.
* **Error paths**:
  * Invalid regex → ``frok: error: invalid regex in pattern
    're:[': …``, exit 2.
  * Zero matches → ``frok: error: no cases matched the filters
    (filter=…, exclude=…); available: [names…]``, exit 2. Surfacing
    the full case-name list makes typos self-diagnosing.
* **Interop.** Filters compose with `--capture-baseline` so only the
  filtered cases produce capture files; with `--use-baseline` so
  selective re-runs still regress against the recorded baseline.

**Verification.** `python3 -m pytest -q` → 263 passed in 0.58s (16
new). Tests cover: every library-level matcher (no filters, glob,
multi-glob union, case-sensitivity, `re:` prefix, partial regex
via search, exclude-only, filter+exclude intersect, invalid
regex); CLI paths (single glob, regex prefix, exclude, filter +
exclude, zero-match error with case list surfaced, invalid regex
error); and a `--filter` + `--capture-baseline` interop test
confirming only filtered cases produce capture files.

**Decisions / trade-offs.**
* Prefix-based syntax (`re:`) rather than a second flag. Keeps one
  consistent knob for both `--filter` and `--exclude`, matches the
  user's example syntax, and `re:` collisions with real case names
  are implausible.
* Glob is the default because most filter invocations are "give me
  every safety-* case"; regex is the escape hatch for anchoring
  (`re:^tool-`) or boundary-sensitive matches.
* Zero matches is a hard error rather than a silent pass. A filter
  that accidentally removes every case almost always means a typo;
  we'd rather flag it than emit an empty report.

**Next suggested action:** `Extend Phase 3 with \`frok run --list\`:
print the resolved case names (after config + filter application)
and exit, so operators can preview what a given invocation would
run before committing to the full execution. Completes the
discoverability loop alongside \`config show\` and \`trace
inspect\`.`

## 2026-04-23 — Phase 3 §4: baseline-capture

**Shipped** the missing piece of the baseline-regression loop:
``frok run --capture-baseline <dir>`` records per-case telemetry
JSONL; ``--use-baseline <dir>`` auto-attaches those files as each
case's baseline on subsequent runs. The §2 #8 differ then fires
automatically and a regression (tool-order divergence or new
errors) turns the exit code red under ``--fail-on-regression``.

* **`Tracer.with_added_sink(tracer, extra)`**
  (`frok/telemetry/tracer.py`) — returns a new tracer whose sink
  fans out to the original plus ``extra``. `NullSink` is collapsed
  away; `MultiSink` is extended; anything else is wrapped. `clock`
  and `id_gen` are preserved so deterministic-clock tests survive.
* **`--capture-baseline <DIR>`** (`frok/cli/run.py`)
  * Slugs each case name (`[^A-Za-z0-9._-]+` → `_`, fallback
    `"case"`), rejects slug collisions within a single run, and
    creates `<DIR>/<slug>.jsonl` via a `JsonlSink` layered onto the
    client's tracer with `with_added_sink`.
  * Runs cases one at a time (`runner.run_case`) so each capture
    closes cleanly. Doesn't change the observed report.
* **`--use-baseline <DIR>`** — iterates cases, and for any case
  without an explicit `baseline=`, sets `case.baseline =
  DIR/<slug>.jsonl` when that file exists. Missing captures leave
  the case alone; non-directory paths are `CliError`.
* The two flags compose: first-run captures; subsequent run with
  `--use-baseline <same-dir>` diffs automatically. Regressed
  cases still propagate through `--fail-on-regression`.

**Verification.** `python3 -m pytest -q` → 247 passed in 0.54s (13
new). Tests cover `case_slug` across safe / symbol-heavy / empty
inputs, `with_added_sink` under `NullSink` / plain / `MultiSink`
bases with `clock`/`id_gen` preservation, per-case file creation
at nested paths, slug-based collision rejection, normal-report
output isn't disturbed by capture, `--use-baseline` attachment
behaviour (match, no-match, non-directory), and the full
capture-then-use round-trip catching an answer regression via
`--fail-on-regression`.

**Decisions / trade-offs.**
* Baseline file per *case*, not per *run*. The §2 #8 differ takes
  one baseline path per case, so sharding by case name keeps the
  existing contract.
* Case slug is the filename; collisions within one run are an
  error because the second capture would silently overwrite the
  first. Explicit is better than a confusing partial capture.
* `--capture-baseline` and `--use-baseline` can point to the same
  directory simultaneously; the user is explicitly opting into
  "diff against the baseline I'm recording this run", which is a
  valid "smoke test the capture itself" use case. We don't block
  it.
* The per-case JsonlSink is layered via `with_added_sink` instead
  of modifying the factory signature — means case-file authors'
  `make_client(config, sink)` contract is untouched, and any
  existing MultiSink fan-out from config's `telemetry.sink` is
  preserved.

**Next suggested action:** `Extend Phase 3 with \`frok run
--filter=<pattern>\`: filter the case list by glob or regex before
execution, so CI jobs can re-run only the cases that failed last
time (e.g. \`frok run cases.py --filter="safety-*"\` or \`--filter
"^tool-"\`). Keeps local iteration fast without editing case files
to comment cases out.`

## 2026-04-23 — Phase 3 §3: config-show

**Shipped** ``frok config show [--format=toml|json|env]`` — renders
the resolved `FrokConfig` after file + env + CLI + profile merging,
so operators can sanity-check which settings actually got applied
before running anything. Closes the config <-> runtime loop the
same way `trace inspect` closes the telemetry <-> eval loop.

* **`frok.config.render`** — three pure functions producing
  strings: `to_toml`, `to_json`, `to_env`. All three serialise the
  same `_as_plain_dict` so the three formats agree on content.
  `SENSITIVE_FIELDS = {("client", "api_key")}` drives masking; last
  four characters preserved, rest replaced with ``****``. Unset
  (``None``) values survive the round-trip:
    * JSON: native `null`
    * TOML: commented-out key with `(unset)` marker (TOML has no null)
    * env: `# FROK_<SECTION>_<FIELD>=` comment line
* **`frok config show`** (`frok/cli/config.py`)
  * Loads config via `load_default_config(file=args.config,
    profile=args.profile)`, applies the selected renderer, writes
    stdout or `-o/--output`.
  * `--reveal` flips sensitive values plain; default is masked.
  * Config load failures surface as `CliError` → ``frok: error:
    config load failed: …`` → exit 2, same as `run` and
    `trace inspect`.

**Verification.** `python3 -m pytest -q` → 234 passed in 0.48s (18
new). Tests cover every renderer (shape + masking + reveal + short-
key handling + special-char escaping in TOML + dotenv-shape env
keys), TOML round-trip through stdlib `tomllib`, and the CLI paths
(default toml, `--format=json` parsability, env matches loader
keys, `-c/-p` pickup including profile merging, `-o` writes file +
suppresses stdout, missing-config-file error).

**Decisions / trade-offs.**
* Minimal in-house TOML emitter rather than a third-party dep —
  the schema is fixed and flat, no heroics needed. Round-trip via
  `tomllib` is asserted in the test suite.
* No `--set key=val` on `config show` — if operators want to try
  overrides they can prepend env vars or pass `-c` to a tweaked
  file. The command's job is *showing* what's resolved, not
  mutating it.
* Masking is opt-out (`--reveal`) rather than opt-in. Accidental
  copy-paste of an api_key into a paste buffer is worse than the
  mild annoyance of re-running with `--reveal`.

**Next suggested action:** `Extend Phase 3 with \`frok run
--capture-baseline <path>\`: run a case set and write the captured
telemetry to \`<path>\` as a JsonlSink, so the next run can diff
against it via EvalCase.baseline automatically. Closes the
baseline-capture loop — today operators have to set
\`telemetry.sink=jsonl\` + \`telemetry.path=...\` by hand to feed
§2 #8's baseline differ.`

## 2026-04-23 — Phase 3 §2: trace-inspect

**Shipped** a library-level trace analysis surface plus the
``frok trace inspect <jsonl>`` CLI — post-hoc regression triage off
a `JsonlSink` capture without rebuilding the agent stack.

* **`frok.telemetry.analysis`**
  * `build_tree(events) -> list[TraceNode]` — reconstructs the
    parent/child tree from `span.end` events; children sorted by
    start time; orphaned parents (capture truncation, filtering)
    surface as roots rather than being dropped.
  * `summarize(events) -> TraceSummary` — per-name stats
    (count, total / mean / p50 / p95 / max ms, error_count), errored
    span list (ordered by start_ts), and top-tool aggregates
    (`tool.invoke` spans grouped by `data["tool"]`, sorted by count
    then total-ms, `errors` column). Empty-input safe.
  * `summary_to_markdown` / `render_tree` / `summary_to_json` for
    the three output formats the CLI emits.
* **`frok trace inspect <jsonl>`** (`frok/cli/trace.py`)
  * Reads a JsonlSink capture via `read_jsonl`, summarises, and
    prints. Flags: `-o/--output`, `--tree`, `--json`, `--top N`.
  * Catches malformed JSONL and empty files as `CliError` so the
    operator sees ``frok: error: ...`` not a stack trace.
* **CLI refactor.** `frok/cli/__init__.py` now owns the top-level
  parser and `main()`; `run.py` and `trace.py` each export a
  `register(sub)` helper. Adding a third subcommand is one more
  `register` call — no growing God function.

**Verification.** `python3 -m pytest -q` → 216 passed in 0.46s (23
new). Tests cover tree nesting + orphan handling, per-name stat
aggregation (mean / percentile / error-count), tool ranking (count
tiebreak by total_ms), empty-input safety, JSON round-trip, tree +
markdown rendering, and CLI paths: help shape, md / json / tree /
output-file output, `--top` capping, missing / empty / malformed
input errors.

**Decisions / trade-offs.**
* Token / latency deltas between two trace captures live in
  `frok.evals.baseline.diff_against_baseline`; the inspect
  subcommand stays single-capture and focused on "where did the
  time and errors go in *this* run?".
* Renderers are pure functions producing strings so operators can
  pipe the output into mail / Slack / `jq` without a plugin system.
* JSON output uses the same shape the Python API returns from
  `summary_to_json`, so downstream scripts and the CLI agree on one
  schema.

**Next suggested action:** `Extend Phase 3 with \`frok config show
[--format=toml|json|env]\`: render the resolved FrokConfig (after
file+env+CLI+profile merging) so operators can sanity-check which
settings actually got applied before running anything. Closes the
config <-> runtime loop the same way trace inspect closes the
telemetry <-> eval loop.`

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
