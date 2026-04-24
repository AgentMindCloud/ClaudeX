"""``frok run <case-file>`` — single-invocation eval regression runner.

Wires `load_default_config` → builds the full Phase-2 stack → loads an
`EvalCase` set from a user-supplied Python file → runs the set through
`EvalRunner` → prints (or writes) `EvalReport.to_markdown()`.

Case-file conventions (checked in order):
  * ``build_cases(config: FrokConfig) -> list[EvalCase]`` — preferred;
    the config is passed in so cases can parameterise themselves.
  * ``CASES: list[EvalCase]`` — plain list, no parameters.
Either must be present; otherwise we fail fast.

Optional in the case file:
  * ``make_client(config: FrokConfig, sink: InMemorySink) -> GrokClient``
    — overrides the default client factory. Use this in CI so the eval
    runner talks to a stub transport instead of real xAI.
"""

from __future__ import annotations

import argparse
import asyncio
import fnmatch
import importlib.util
import json
import os
import random
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from ..clients.grok import GrokClient
from ..clients.transports import urllib_streaming_transport, urllib_transport
from ..config import (
    FrokConfig,
    build_client,
    build_telemetry_sink,
    load_default_config,
)
from ..evals import EvalCase, EvalResult, EvalReport, EvalRunner
from ..telemetry import (
    InMemorySink,
    JsonlSink,
    MultiSink,
    NullSink,
    Tracer,
    with_added_sink,
)
from .common import CliError


ClientFactory = Callable[[InMemorySink], GrokClient]


# ---------------------------------------------------------------------------
# case-file loading
# ---------------------------------------------------------------------------
@dataclass
class LoadedCaseFile:
    cases: list[EvalCase]
    client_factory: ClientFactory


def _load_case_module(path: Path) -> Any:
    if not path.exists():
        raise CliError(f"case file not found: {path}")
    module_name = f"frok_case_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise CliError(f"cannot import case file: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # pragma: no cover — bubbled up for the caller
        raise CliError(f"error while importing {path}: {exc}") from exc
    return mod


def _default_client_factory(config: FrokConfig) -> ClientFactory:
    """Factory: per-case InMemorySink + optional fan-out to configured sink."""

    def make(sink: InMemorySink) -> GrokClient:
        config_sink = build_telemetry_sink(config)
        if isinstance(config_sink, NullSink):
            tracer = Tracer(sink=sink)
        else:
            tracer = Tracer(sink=MultiSink(sink, config_sink))
        return build_client(
            config,
            transport=urllib_transport,
            streaming_transport=urllib_streaming_transport,
            tracer=tracer,
        )

    return make


def load_case_file(path: Path, config: FrokConfig) -> LoadedCaseFile:
    mod = _load_case_module(path)

    if hasattr(mod, "build_cases"):
        cases = list(mod.build_cases(config))
    elif hasattr(mod, "CASES"):
        cases = list(mod.CASES)
    else:
        raise CliError(
            f"{path} must define `CASES` or `build_cases(config)`"
        )
    if not cases:
        raise CliError(f"{path} produced zero eval cases")

    if hasattr(mod, "make_client"):
        user_factory = mod.make_client

        def factory(sink: InMemorySink) -> GrokClient:
            return user_factory(config, sink)

    else:
        factory = _default_client_factory(config)

    return LoadedCaseFile(cases=cases, client_factory=factory)


# ---------------------------------------------------------------------------
# pattern-based filtering (--filter / --exclude)
# ---------------------------------------------------------------------------
# Patterns default to fnmatch globs. Prefix with ``re:`` for a regex.
_REGEX_PREFIX = "re:"


def _compile_pattern(raw: str) -> tuple[str, Any]:
    if raw.startswith(_REGEX_PREFIX):
        body = raw[len(_REGEX_PREFIX):]
        try:
            return ("regex", re.compile(body))
        except re.error as exc:
            raise CliError(f"invalid regex in pattern {raw!r}: {exc}")
    return ("glob", raw)


def _pattern_matches(compiled: tuple[str, Any], name: str) -> bool:
    kind, pattern = compiled
    if kind == "glob":
        return fnmatch.fnmatchcase(name, pattern)
    return bool(pattern.search(name))


def filter_cases(
    cases: Sequence[EvalCase],
    *,
    includes: Sequence[str] = (),
    excludes: Sequence[str] = (),
) -> list[EvalCase]:
    """Return the subset of ``cases`` that matches any include and no
    exclude. With no includes, every case is considered a match."""
    inc = [_compile_pattern(p) for p in includes]
    exc = [_compile_pattern(p) for p in excludes]
    out: list[EvalCase] = []
    for case in cases:
        if inc and not any(_pattern_matches(c, case.name) for c in inc):
            continue
        if any(_pattern_matches(c, case.name) for c in exc):
            continue
        out.append(case)
    return out


# ---------------------------------------------------------------------------
# baseline capture / injection helpers
# ---------------------------------------------------------------------------
_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def case_slug(name: str) -> str:
    """Filename-safe slug derived from an EvalCase name."""
    s = _SLUG_RE.sub("_", name).strip("_")
    return s or "case"


def _check_unique_slugs(cases: list[EvalCase]) -> dict[str, str]:
    """Return case-name → slug. Raise if two cases would collide."""
    slugs: dict[str, str] = {}
    used: dict[str, str] = {}
    for case in cases:
        s = case_slug(case.name)
        if s in used:
            raise CliError(
                f"cases {used[s]!r} and {case.name!r} both slug to "
                f"{s!r}; baseline filenames would collide"
            )
        used[s] = case.name
        slugs[case.name] = s
    return slugs


def _attach_baselines(
    cases: list[EvalCase], directory: Path
) -> list[EvalCase]:
    """Set `case.baseline` on any case whose matching capture file exists."""
    slugs = _check_unique_slugs(cases)
    for case in cases:
        if case.baseline is not None:
            continue
        candidate = directory / f"{slugs[case.name]}.jsonl"
        if candidate.exists():
            case.baseline = candidate
    return cases


def _wrap_factory_with_extra_sink(
    factory: ClientFactory, extra: "JsonlSink"
) -> ClientFactory:
    def wrapped(sink: InMemorySink) -> GrokClient:
        client = factory(sink)
        client.tracer = with_added_sink(client.tracer, extra)
        return client

    return wrapped


# ---------------------------------------------------------------------------
# --repeat / --seed helpers
# ---------------------------------------------------------------------------
def apply_seed(seed: int, repeat_index: int) -> int:
    """Seed Python's `random` and publish ``FROK_RUN_SEED`` for stubs."""
    effective = seed + repeat_index
    random.seed(effective)
    os.environ["FROK_RUN_SEED"] = str(effective)
    return effective


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------
async def run_cmd(args: argparse.Namespace) -> int:
    try:
        config = load_default_config(file=args.config, profile=args.profile)
    except Exception as exc:
        raise CliError(f"config load failed: {exc}") from exc

    loaded = load_case_file(args.case_file, config)

    if args.filter or args.exclude:
        original = list(loaded.cases)
        loaded.cases = filter_cases(
            original, includes=args.filter, excludes=args.exclude
        )
        if not loaded.cases:
            raise CliError(
                "no cases matched the filters "
                f"(filter={list(args.filter)!r}, exclude={list(args.exclude)!r}); "
                f"available: {[c.name for c in original]!r}"
            )

    if args.list:
        # Preview-only: print resolved case names (after --filter/--exclude)
        # and exit. No client is constructed, no case runs.
        out_text = "\n".join(case.name for case in loaded.cases) + "\n"
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out_text, encoding="utf-8")
        else:
            sys.stdout.write(out_text)
        return 0

    if args.use_baseline is not None:
        if not args.use_baseline.is_dir():
            raise CliError(
                f"--use-baseline path is not a directory: {args.use_baseline}"
            )
        _attach_baselines(loaded.cases, args.use_baseline)

    if args.timeout_s is not None:
        if args.timeout_s < 0:
            raise CliError(
                f"--timeout-s must be >= 0, got {args.timeout_s}"
            )
        for case in loaded.cases:
            # Per-case EvalCase.timeout_s always wins over the CLI default.
            if case.timeout_s is None:
                case.timeout_s = args.timeout_s

    if args.repeat < 1:
        raise CliError(f"--repeat must be >= 1, got {args.repeat}")
    if args.jobs < 1:
        raise CliError(f"--jobs must be >= 1, got {args.jobs}")
    if args.seed is not None and args.jobs > 1:
        raise CliError(
            "--seed cannot be combined with --jobs > 1 "
            "(Python's random state is process-global and can't be "
            "isolated across parallel tasks); keep --jobs 1 when seeding"
        )
    if args.stream and args.jobs > 1:
        raise CliError(
            "--stream cannot be combined with --jobs > 1 "
            "(stderr deltas from concurrent cases would interleave "
            "unreadably); keep --jobs 1 when streaming"
        )

    cpu_cap = os.cpu_count() or 1
    jobs = min(args.jobs, cpu_cap)

    capture_dir: Path | None = args.capture_baseline
    if capture_dir is not None:
        if args.repeat > 1:
            raise CliError(
                "--capture-baseline is incompatible with --repeat > 1 "
                "(would overwrite per-case JSONL files); capture once "
                "with --repeat 1, then --use-baseline on subsequent runs"
            )
        capture_dir.mkdir(parents=True, exist_ok=True)
        slugs = _check_unique_slugs(loaded.cases)
    else:
        slugs = {}

    # One unit = one (case, repeat) coroutine. A Semaphore caps concurrency
    # to `jobs`. Results come back from `asyncio.gather` in submission order
    # so the EvalReport preserves case order regardless of completion order.
    semaphore = asyncio.Semaphore(jobs)

    def _stream_sink_for(case: EvalCase) -> Callable[[str], None] | None:
        if not args.stream:
            return None
        sys.stderr.write(f"\n>>> {case.name}\n")
        sys.stderr.flush()

        def _write(delta: str) -> None:
            sys.stderr.write(delta)
            sys.stderr.flush()

        return _write

    async def _run_unit(
        case: EvalCase,
        repeat_idx: int,
        jsonl: JsonlSink | None,
        factory: ClientFactory,
    ) -> EvalResult:
        try:
            async with semaphore:
                if args.seed is not None:
                    apply_seed(args.seed, repeat_idx)
                runner = EvalRunner(client_factory=factory)
                sink = _stream_sink_for(case)
                result = await runner.run_case(
                    case,
                    repeat=repeat_idx,
                    repeats=args.repeat,
                    stream_sink=sink,
                )
                if sink is not None:
                    # Newline after the last delta so the report doesn't run
                    # onto the same line as the streamed answer.
                    sys.stderr.write("\n")
                    sys.stderr.flush()
                return result
        finally:
            if jsonl is not None:
                jsonl.close()

    tasks: list[asyncio.Task[EvalResult]] = []
    for case in loaded.cases:
        for repeat_idx in range(args.repeat):
            jsonl: JsonlSink | None = None
            factory = loaded.client_factory
            if capture_dir is not None:
                jsonl = JsonlSink(capture_dir / f"{slugs[case.name]}.jsonl")
                factory = _wrap_factory_with_extra_sink(factory, jsonl)
            tasks.append(
                asyncio.create_task(_run_unit(case, repeat_idx, jsonl, factory))
            )

    results: list[EvalResult] = list(await asyncio.gather(*tasks))

    report = EvalReport(results=results)

    md = report.to_markdown()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(md, encoding="utf-8")
    else:
        print(md)

    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(
            json.dumps(report.to_summary(), indent=2, default=str),
            encoding="utf-8",
        )

    if args.fail_on_regression and report.failed > 0:
        return 1
    return 0


# ---------------------------------------------------------------------------
# parser registration (called from frok.cli.__init__.build_parser)
# ---------------------------------------------------------------------------
def register(sub: "argparse._SubParsersAction") -> None:
    run = sub.add_parser(
        "run",
        help="Run an eval case file and print the verdict doc.",
        description=(
            "Load config -> build the full Phase-2 stack -> execute an "
            "EvalCase set -> print EvalReport.to_markdown()."
        ),
    )
    run.add_argument(
        "case_file",
        type=Path,
        help="path to a .py file exposing CASES or build_cases(config)",
    )
    run.add_argument("-c", "--config", type=Path, help="explicit config file path")
    run.add_argument("-p", "--profile", help="profile name to select")
    run.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write markdown verdict to this file instead of stdout",
    )
    run.add_argument(
        "--summary-json",
        type=Path,
        help="also write the summary dict as JSON to this path",
    )
    run.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="exit non-zero when any case fails; default: always 0",
    )
    run.add_argument(
        "--repeat",
        type=int,
        default=1,
        metavar="N",
        help=(
            "run each case N times (default 1). With N>1, the report "
            "aggregates by case and shows pass rate. Flaky cases (0 < "
            "rate < 1) are surfaced separately."
        ),
    )
    run.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="S",
        help=(
            "deterministic seed; applied as `random.seed(S + repeat)` and "
            "published as FROK_RUN_SEED per repeat so stubs can pick it up"
        ),
    )
    run.add_argument(
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help=(
            "run up to N cases concurrently (default 1 = serial). Silently "
            "clamped to os.cpu_count(). Results are still collected in case "
            "order. Incompatible with --seed because `random`'s state is "
            "process-global."
        ),
    )
    run.add_argument(
        "--stream",
        action="store_true",
        help=(
            "stream model deltas to stderr as they arrive (per-case header "
            "+ live tokens). Cases with tools fall back to non-stream "
            "silently. Requires a streaming_transport on the client (the "
            "default factory wires urllib_streaming_transport). "
            "Incompatible with --jobs > 1 (interleaved output)."
        ),
    )
    run.add_argument(
        "--list",
        action="store_true",
        help=(
            "print resolved case names (after --filter/--exclude) and exit; "
            "no client is constructed and no cases run"
        ),
    )
    run.add_argument(
        "--filter",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "keep only cases whose name matches PATTERN. Glob by default "
            "(e.g. 'safety-*'); prefix with 're:' for a Python regex "
            "(e.g. 're:^tool-'). Repeatable — any match wins."
        ),
    )
    run.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="drop cases whose name matches PATTERN (same syntax as --filter).",
    )
    run.add_argument(
        "--capture-baseline",
        type=Path,
        metavar="DIR",
        help=(
            "capture per-case telemetry to DIR/<case-slug>.jsonl; subsequent "
            "runs can pass --use-baseline DIR to regress against it"
        ),
    )
    run.add_argument(
        "--use-baseline",
        type=Path,
        metavar="DIR",
        help=(
            "attach DIR/<case-slug>.jsonl as each case's baseline when the "
            "file exists; cases with an explicit `baseline=` are untouched"
        ),
    )
    run.add_argument(
        "--timeout-s",
        type=float,
        default=None,
        metavar="SECONDS",
        help=(
            "default wall-clock timeout (seconds) applied to every case "
            "whose own EvalCase.timeout_s is None. Per-case overrides "
            "always win. SECONDS=0 short-circuits every unconfigured "
            "case (asyncio.wait_for(0) fires before the coroutine runs)."
        ),
    )
    run.set_defaults(fn=run_cmd)
