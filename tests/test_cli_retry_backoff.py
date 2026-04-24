"""Tests for ``frok run --retry-backoff`` + ``--retry-backoff-jitter``.

Patches the module-level ``_retry_sleep`` seam so tests record sleep
durations without actually waiting.
"""

import asyncio
import json
import random
from pathlib import Path

import pytest

from frok.cli import build_parser, main
from frok.cli import run as run_mod


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_backoff_defaults():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.retry_backoff == 0
    assert ns.retry_backoff_jitter == 0.0


def test_parser_backoff_accepts_values():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "run",
            "cases.py",
            "--retry-backoff",
            "250",
            "--retry-backoff-jitter",
            "0.5",
        ]
    )
    assert ns.retry_backoff == 250
    assert ns.retry_backoff_jitter == 0.5


# ---------------------------------------------------------------------------
# _apply_retry_backoff — unit-level
# ---------------------------------------------------------------------------
def test_apply_backoff_sleeps_ms_to_seconds(monkeypatch):
    calls: list[float] = []

    async def fake_sleep(s: float) -> None:
        calls.append(s)

    monkeypatch.setattr(run_mod, "_retry_sleep", fake_sleep)
    asyncio.get_event_loop_policy()  # ensure loop fixture isn't needed
    asyncio.run(run_mod._apply_retry_backoff(250, 0.0))
    assert calls == [0.25]


def test_apply_backoff_noop_when_ms_zero(monkeypatch):
    calls: list[float] = []

    async def fake_sleep(s: float) -> None:
        calls.append(s)

    monkeypatch.setattr(run_mod, "_retry_sleep", fake_sleep)
    asyncio.run(run_mod._apply_retry_backoff(0, 0.0))
    asyncio.run(run_mod._apply_retry_backoff(-5, 0.0))
    assert calls == []


def test_apply_backoff_jitter_range(monkeypatch):
    calls: list[float] = []

    async def fake_sleep(s: float) -> None:
        calls.append(s)

    monkeypatch.setattr(run_mod, "_retry_sleep", fake_sleep)
    # Seed random so uniform is deterministic — check bounds.
    random.seed(0)
    for _ in range(50):
        asyncio.run(run_mod._apply_retry_backoff(1000, 0.5))
    # With jitter 0.5 and ms 1000 → sleep seconds ∈ [0.5, 1.5].
    assert all(0.5 <= s <= 1.5 for s in calls)
    # Variance check — not every sample the same.
    assert len(set(round(s, 3) for s in calls)) > 1


# ---------------------------------------------------------------------------
# case-file fixture: fails on N-1 calls, succeeds on Nth
# ---------------------------------------------------------------------------
_FLAKY_TEMPLATE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


_responses = [_final(t) for t in __RESPONSES__]


@dataclass
class _StubTransport:
    async def __call__(self, *, method, url, headers, body, timeout):
        status, payload = _responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport(),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="target",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


def _flaky(tmp_path: Path, responses: list[str]) -> Path:
    body = _FLAKY_TEMPLATE.replace(
        "__RESPONSES__", "[" + ", ".join(repr(r) for r in responses) + "]"
    )
    path = tmp_path / "cases.py"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.fixture
def recorded_sleeps(monkeypatch):
    calls: list[float] = []

    async def fake_sleep(s: float) -> None:
        calls.append(s)

    monkeypatch.setattr(run_mod, "_retry_sleep", fake_sleep)
    return calls


# ---------------------------------------------------------------------------
# happy path: N-1 sleeps for N attempts
# ---------------------------------------------------------------------------
def test_backoff_sleeps_between_retries(tmp_path, recorded_sleeps):
    # 3 attempts (one initial + two retries) → 2 sleeps.
    path = _flaky(tmp_path, ["nope", "nope", "ok"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--retry-backoff",
            "100",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    # Two sleeps recorded, each 0.1s (100ms).
    assert recorded_sleeps == [0.1, 0.1]


def test_backoff_skipped_when_first_attempt_passes(tmp_path, recorded_sleeps):
    path = _flaky(tmp_path, ["ok"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "3",
            "--retry-backoff",
            "100",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    # Zero sleeps — passed on first attempt.
    assert recorded_sleeps == []


def test_backoff_not_after_final_failed_attempt(tmp_path, recorded_sleeps):
    # 3 attempts all fail → only 2 sleeps (no sleep after the last attempt).
    path = _flaky(tmp_path, ["nope", "nope", "nope"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--retry-backoff",
            "100",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0  # fail without --fail-on-regression
    assert len(recorded_sleeps) == 2


# ---------------------------------------------------------------------------
# jitter: end-to-end via deterministic random.seed
# ---------------------------------------------------------------------------
def test_backoff_jitter_uses_random_uniform(tmp_path, recorded_sleeps):
    # Two retries → two sleeps. With jitter 0.5 and base 1000ms, each sleep
    # is in [0.5, 1.5] seconds (not the base 1.0).
    path = _flaky(tmp_path, ["nope", "nope", "ok"])
    random.seed(0)
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--retry-backoff",
            "1000",
            "--retry-backoff-jitter",
            "0.5",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    assert len(recorded_sleeps) == 2
    assert all(0.5 <= s <= 1.5 for s in recorded_sleeps)


# ---------------------------------------------------------------------------
# interop: no sleep when retry-on-error filter stops the loop early
# ---------------------------------------------------------------------------
def test_no_backoff_when_error_filter_stops_loop(tmp_path, recorded_sleeps):
    # Error doesn't match pattern → loop breaks on first failure → no sleep.
    script = '''
import json
from dataclasses import dataclass

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    async def __call__(self, *, method, url, headers, body, timeout):
        raise RuntimeError("ValueError: bad arg")


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport(),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="target",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''
    path = tmp_path / "cases.py"
    path.write_text(script, encoding="utf-8")
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "3",
            "--retry-backoff",
            "500",
            "--retry-on-error",
            "429",  # won't match "ValueError"
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    # Single attempt, single failure, pattern miss → no sleep.
    assert recorded_sleeps == []


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def test_negative_backoff_is_cli_error(tmp_path, capsys):
    path = _flaky(tmp_path, ["ok"])
    code = main(["run", str(path), "--retry-backoff", "-5"])
    assert code == 2
    assert "--retry-backoff must be >= 0" in capsys.readouterr().err


def test_jitter_out_of_range_is_cli_error(tmp_path, capsys):
    path = _flaky(tmp_path, ["ok"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "1",
            "--retry-backoff",
            "100",
            "--retry-backoff-jitter",
            "1.5",
        ]
    )
    assert code == 2
    assert (
        "--retry-backoff-jitter must be between 0 and 1"
        in capsys.readouterr().err
    )


def test_jitter_without_backoff_is_cli_error(tmp_path, capsys):
    path = _flaky(tmp_path, ["ok"])
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "1",
            "--retry-backoff-jitter",
            "0.5",
        ]
    )
    assert code == 2
    assert (
        "--retry-backoff-jitter requires --retry-backoff > 0"
        in capsys.readouterr().err
    )


def test_backoff_without_retry_is_cli_error(tmp_path, capsys):
    path = _flaky(tmp_path, ["ok"])
    code = main(
        ["run", str(path), "--retry-backoff", "100"]
    )
    assert code == 2
    assert "--retry-backoff requires --retry > 0" in capsys.readouterr().err
