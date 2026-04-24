"""Tests for ``frok run --timeout-s``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_timeout_default_none():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.timeout_s is None


def test_parser_timeout_accepts_float():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py", "--timeout-s", "2.5"])
    assert ns.timeout_s == 2.5


def test_parser_timeout_accepts_zero():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py", "--timeout-s", "0"])
    assert ns.timeout_s == 0.0


# ---------------------------------------------------------------------------
# case-file fixtures
# ---------------------------------------------------------------------------
_FAST_CASE_FILE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("ok")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="fast",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


_SLOW_CASE_FILE = '''
import asyncio
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains, NoErrors
from frok.telemetry import Tracer


async def _slow_transport(*, method, url, headers, body, timeout):
    await asyncio.sleep(5.0)  # longer than any test timeout
    payload = {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": "late"},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
    return 200, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_slow_transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="slow",
        messages=[GrokMessage("user", "q")],
        scorers=[NoErrors()],
    ),
]
'''


# Two cases: one with its own timeout_s already set, one without.
_MIXED_CASE_FILE = '''
import asyncio
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, NoErrors
from frok.telemetry import Tracer


async def _slow_transport(*, method, url, headers, body, timeout):
    await asyncio.sleep(5.0)
    return 200, {}, b"{}"


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_slow_transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


# First case has its own (tight) timeout_s; second inherits --timeout-s.
CASES = [
    EvalCase(
        name="own-timeout",
        messages=[GrokMessage("user", "q")],
        scorers=[NoErrors()],
        timeout_s=0.02,
    ),
    EvalCase(
        name="inherits-cli",
        messages=[GrokMessage("user", "q")],
        scorers=[NoErrors()],
    ),
]
'''


def _write(tmp_path: Path, body: str, name: str = "cases.py") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# no flag: existing behaviour unchanged
# ---------------------------------------------------------------------------
def test_no_timeout_flag_leaves_cases_untouched(tmp_path):
    path = _write(tmp_path, _FAST_CASE_FILE)
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    # No timeout field surfaced on a non-repeating run; case passes normally.


# ---------------------------------------------------------------------------
# flag fires: slow case with --timeout-s N fails via TimeoutError
# ---------------------------------------------------------------------------
def test_flag_fills_timeout_for_unconfigured_cases(tmp_path):
    path = _write(tmp_path, _SLOW_CASE_FILE)
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--timeout-s",
            "0.05",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0  # default exit 0 on failure
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["failed"] == 1
    assert "TimeoutError" in (data["cases"][0]["error"] or "")
    assert "0.05" in (data["cases"][0]["error"] or "")


# ---------------------------------------------------------------------------
# per-case override wins over the CLI default
# ---------------------------------------------------------------------------
def test_per_case_timeout_wins_over_cli_default(tmp_path):
    path = _write(tmp_path, _MIXED_CASE_FILE)
    summary = tmp_path / "s.json"
    # --timeout-s 5.0 would be generous, but the own-timeout case has
    # timeout_s=0.02 already — so that case should still fail with its own
    # tighter limit while the second case fails on the CLI default.
    code = main(
        [
            "run",
            str(path),
            "--timeout-s",
            "0.10",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    # Find each case.
    own = next(c for c in data["cases"] if c["case"] == "own-timeout")
    inh = next(c for c in data["cases"] if c["case"] == "inherits-cli")
    # own case used its own tight value.
    assert "timeout_s=0.02" in own["error"]
    # inherited case used the CLI default.
    assert "timeout_s=0.1" in inh["error"]


# ---------------------------------------------------------------------------
# zero CLI timeout short-circuits
# ---------------------------------------------------------------------------
def test_zero_timeout_short_circuits_every_case(tmp_path):
    path = _write(tmp_path, _FAST_CASE_FILE)
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--timeout-s",
            "0",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["failed"] == 1
    assert "TimeoutError" in (data["cases"][0]["error"] or "")


# ---------------------------------------------------------------------------
# --fail-on-regression surfaces timeout failures
# ---------------------------------------------------------------------------
def test_fail_on_regression_returns_1_when_timeout_fires(tmp_path):
    path = _write(tmp_path, _SLOW_CASE_FILE)
    code = main(
        [
            "run",
            str(path),
            "--timeout-s",
            "0.05",
            "--fail-on-regression",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 1


# ---------------------------------------------------------------------------
# negative value is a CliError
# ---------------------------------------------------------------------------
def test_negative_timeout_is_cli_error(tmp_path, capsys):
    path = _write(tmp_path, _FAST_CASE_FILE)
    code = main(["run", str(path), "--timeout-s", "-1"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--timeout-s must be >= 0" in err
