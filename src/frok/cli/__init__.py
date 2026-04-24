"""Frok CLI entry point."""

from __future__ import annotations

import argparse
import asyncio
import sys

from ..config import ConfigError
from .common import CliError
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
    "inspect_cmd",
    "load_case_file",
    "main",
    "run_cmd",
]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="frok", description="Super AI Frok CLI")
    sub = p.add_subparsers(dest="command", required=True)
    _register_run(sub)
    _register_trace(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return asyncio.run(args.fn(args))
    except (CliError, ConfigError) as exc:
        print(f"frok: error: {exc}", file=sys.stderr)
        return 2
