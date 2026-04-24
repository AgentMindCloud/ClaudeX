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
import importlib.util
import json
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ..clients.grok import GrokClient
from ..clients.transports import urllib_transport
from ..config import (
    FrokConfig,
    build_client,
    build_telemetry_sink,
    load_default_config,
)
from ..evals import EvalCase, EvalReport, EvalRunner
from ..telemetry import InMemorySink, MultiSink, NullSink, Tracer
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
# run command
# ---------------------------------------------------------------------------
async def run_cmd(args: argparse.Namespace) -> int:
    try:
        config = load_default_config(file=args.config, profile=args.profile)
    except Exception as exc:
        raise CliError(f"config load failed: {exc}") from exc

    loaded = load_case_file(args.case_file, config)
    runner = EvalRunner(client_factory=loaded.client_factory)
    report: EvalReport = await runner.run(loaded.cases)

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
    run.set_defaults(fn=run_cmd)
