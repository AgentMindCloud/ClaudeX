"""Frok CLI entry point."""

from __future__ import annotations

import argparse
import asyncio
import sys

from ..config import ConfigError
from .common import CliError
from .config import register as _register_config
from .config import show_cmd
from .doctor import doctor_cmd
from .doctor import register as _register_doctor
from .eval import diff_cmd, summarize_cmd
from .eval import register as _register_eval
from .init import init_cmd
from .init import register as _register_init
from .version import version_cmd
from .version import register as _register_version
from .retry import diff_cmd as retry_diff_cmd
from .retry import register as _register_retry
from .retry import summarize_cmd as retry_summarize_cmd
from .run import (
    ClientFactory,
    LoadedCaseFile,
    load_case_file,
    run_cmd,
)
from .run import register as _register_run
from .trace import inspect_cmd
from .trace import register as _register_trace

__all__ = [
    "CliError",
    "ClientFactory",
    "LoadedCaseFile",
    "build_parser",
    "diff_cmd",
    "doctor_cmd",
    "init_cmd",
    "inspect_cmd",
    "load_case_file",
    "main",
    "retry_diff_cmd",
    "retry_summarize_cmd",
    "run_cmd",
    "show_cmd",
    "summarize_cmd",
    "version_cmd",
]


_DESCRIPTION = (
    "Super AI Frok — LLM eval regressions, telemetry, and agent "
    "orchestration for the xAI/Grok ecosystem.\n"
    "\n"
    "Getting started (the onboarding triple):\n"
    "  frok init       scaffold a runnable project skeleton\n"
    "  frok doctor     verify your config, safety, and client setup\n"
    "  frok run FILE   execute an eval case set, print the verdict"
)


_EPILOG = (
    "Quick start:\n"
    "  frok init && frok run cases/smoke.py\n"
    "\n"
    "Everyday operations:\n"
    "  frok config show           inspect the resolved FrokConfig\n"
    "  frok run --list            preview cases a run would hit\n"
    "  frok trace inspect FILE    summarize a JsonlSink capture\n"
    "  frok eval diff A B         diff two captures side-by-side\n"
    "  frok eval summarize DIR    roll up a baseline directory\n"
    "  frok retry diff A B        diff two --retry-report JSONs\n"
    "  frok retry summarize DIR   trend-view a series of retry reports\n"
    "\n"
    "Reporting bugs: include the output of `frok version`."
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="frok",
        description=_DESCRIPTION,
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)
    # Ordered for help-output UX: onboarding triple first, then everyday
    # operations, then the triage primitive last.
    _register_init(sub)
    _register_doctor(sub)
    _register_run(sub)
    _register_config(sub)
    _register_eval(sub)
    _register_trace(sub)
    _register_retry(sub)
    _register_version(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return asyncio.run(args.fn(args))
    except (CliError, ConfigError) as exc:
        print(f"frok: error: {exc}", file=sys.stderr)
        return 2
