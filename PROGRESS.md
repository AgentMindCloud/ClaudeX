# PROGRESS

Living log of what shipped and why. Most recent entries first.

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
