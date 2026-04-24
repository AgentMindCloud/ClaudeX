"""Tests for ``frok run --retry N``."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_retry_default_zero():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.retry == 0


def test_parser_retry_accepts_int():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py", "--retry", "3"])
    assert ns.retry == 3


# ---------------------------------------------------------------------------
# case-file fixtures
#
# Each case file writes one byte to `FROK_RETRY_COUNTER` (a path in tmp_path)
# per transport call so tests can count how many attempts the runner made.
# ---------------------------------------------------------------------------
_PASS_FIRST_CASE_FILE = '''
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


def _bump():
    p = Path(os.environ["FROK_RETRY_COUNTER"])
    with p.open("a", encoding="utf-8") as fh:
        fh.write(".")


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        _bump()
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
    # Always passes — single "ok" response per client build.
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("ok")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="always-passes",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


# A "flaky" case file that cycles through responses. Module-level `_responses`
# persists across repeated `make_client` calls within one run (importlib loads
# the module once per run_cmd). Tests point `_responses` at whatever scenario
# they want by patching the `RESPONSES` constant via a preamble.
_FLAKY_TEMPLATE = '''
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


def _bump():
    p = Path(os.environ["FROK_RETRY_COUNTER"])
    with p.open("a", encoding="utf-8") as fh:
        fh.write(".")


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        _bump()
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


# Module-level so the list shrinks across make_client invocations.
_responses = [_final(t) for t in __RESPONSES__]


def make_client(config, sink):
    # Peel one response per attempt; a fresh transport per client build.
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_responses.pop(0)]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="flaky",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


_SLOW_CASE_FILE = '''
import asyncio
import json
import os
from pathlib import Path

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains, NoErrors
from frok.telemetry import Tracer


def _bump():
    p = Path(os.environ["FROK_RETRY_COUNTER"])
    with p.open("a", encoding="utf-8") as fh:
        fh.write(".")


async def _slow_transport(*, method, url, headers, body, timeout):
    _bump()
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


CASES = [
    EvalCase(
        name="slow",
        messages=[GrokMessage("user", "q")],
        scorers=[NoErrors()],
    ),
]
'''


def _write(tmp_path: Path, body: str, name: str = "cases.py") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def _flaky(tmp_path: Path, responses: list[str]) -> Path:
    """Materialise the flaky-case template with the given response texts."""
    pyreps = "[" + ", ".join(repr(r) for r in responses) + "]"
    body = _FLAKY_TEMPLATE.replace("__RESPONSES__", pyreps)
    return _write(tmp_path, body)


@pytest.fixture
def counter(tmp_path, monkeypatch):
    path = tmp_path / "counter.txt"
    monkeypatch.setenv("FROK_RETRY_COUNTER", str(path))
    return path


def _count(counter: Path) -> int:
    return len(counter.read_text(encoding="utf-8")) if counter.exists() else 0


# ---------------------------------------------------------------------------
# default: retry=0 → a failing case runs exactly once
# ---------------------------------------------------------------------------
def test_default_retry_zero_runs_once(tmp_path, counter):
    # Case always fails (scorer wants "ok", response is "nope").
    path = _flaky(tmp_path, ["nope"])
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
    assert data["failed"] == 1
    assert _count(counter) == 1


# ---------------------------------------------------------------------------
# first attempt passes → no retry consumed
# ---------------------------------------------------------------------------
def test_pass_first_attempt_no_retry(tmp_path, counter):
    path = _write(tmp_path, _PASS_FIRST_CASE_FILE)
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "3",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    assert _count(counter) == 1


# ---------------------------------------------------------------------------
# fail-then-succeed → retry flips the verdict to PASS
# ---------------------------------------------------------------------------
def test_fail_then_succeed_passes(tmp_path, counter):
    # Two fails, then an "ok": with --retry 2 the final attempt wins.
    path = _flaky(tmp_path, ["nope", "still-nope", "ok"])
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    assert _count(counter) == 3


# ---------------------------------------------------------------------------
# exhausted retries → case still FAILs, counter == retry+1
# ---------------------------------------------------------------------------
def test_always_fail_exhausts_retries(tmp_path, counter):
    path = _flaky(tmp_path, ["nope", "nope", "nope"])
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0  # default exit 0 on failure
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["failed"] == 1
    assert _count(counter) == 3  # 1 attempt + 2 retries


# ---------------------------------------------------------------------------
# TimeoutError is NOT retried (by design — case-level cap)
# ---------------------------------------------------------------------------
def test_timeout_not_retried(tmp_path, counter):
    path = _write(tmp_path, _SLOW_CASE_FILE)
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--timeout-s",
            "0.05",
            "--retry",
            "5",
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
    # Exactly one attempt: timeouts short-circuit the retry loop.
    assert _count(counter) == 1


# ---------------------------------------------------------------------------
# --fail-on-regression interop
# ---------------------------------------------------------------------------
def test_fail_on_regression_exhausts_retries_returns_1(tmp_path, counter):
    path = _flaky(tmp_path, ["nope", "nope"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "1",
            "--fail-on-regression",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 1
    assert _count(counter) == 2


def test_fail_on_regression_eventual_pass_returns_0(tmp_path, counter):
    path = _flaky(tmp_path, ["nope", "ok"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "1",
            "--fail-on-regression",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    assert _count(counter) == 2


# ---------------------------------------------------------------------------
# negative --retry is a CliError
# ---------------------------------------------------------------------------
def test_negative_retry_is_cli_error(tmp_path, counter, capsys):
    path = _write(tmp_path, _PASS_FIRST_CASE_FILE)
    code = main(["run", str(path), "--retry", "-1"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--retry must be >= 0" in err


# ---------------------------------------------------------------------------
# --retry > 0 + --capture-baseline is rejected
# ---------------------------------------------------------------------------
def test_retry_with_capture_baseline_is_cli_error(tmp_path, counter, capsys):
    path = _write(tmp_path, _PASS_FIRST_CASE_FILE)
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "1",
            "--capture-baseline",
            str(tmp_path / "baselines"),
        ]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "--capture-baseline is incompatible with --retry > 0" in err


def test_retry_zero_with_capture_baseline_is_fine(tmp_path, counter):
    # Explicit --retry 0 should NOT conflict with --capture-baseline.
    path = _write(tmp_path, _PASS_FIRST_CASE_FILE)
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "0",
            "--capture-baseline",
            str(tmp_path / "baselines"),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    assert (tmp_path / "baselines" / "always-passes.jsonl").exists()
