"""Tests for ``frok run --retry-on-error REGEX``.

Verifies that the retry loop only retries failures whose
observation.error matches at least one regex. Scorer-only
failures (no observation.error) are never retried.
"""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_retry_on_error_default_empty():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.retry_on_error == []


def test_parser_retry_on_error_repeatable():
    parser = build_parser()
    ns = parser.parse_args(
        ["run", "cases.py", "--retry-on-error", "429", "--retry-on-error", "^Runtime"]
    )
    assert ns.retry_on_error == ["429", "^Runtime"]


# ---------------------------------------------------------------------------
# case-file templates
#
# (A) Transport that raises a named exception on first N calls then returns
#     a successful response. Produces observation.error of the form
#     "RuntimeError: <message>".
# (B) Transport that always succeeds but with a wrong answer so the scorer
#     fails (no observation.error).
# ---------------------------------------------------------------------------
_ERROR_RETRY_TEMPLATE = '''
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


# Module-level sequence of (kind, payload):
#   ("err", msg) → transport raises RuntimeError(msg)
#   ("ok", text) → transport returns a _final(text) response
_script = __SCRIPT__


@dataclass
class _StubTransport:
    async def __call__(self, *, method, url, headers, body, timeout):
        kind, payload = _script.pop(0)
        if kind == "err":
            raise RuntimeError(payload)
        status, body = _final(payload)
        return status, {}, json.dumps(body).encode("utf-8")


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


def _script(tmp_path: Path, events: list[tuple[str, str]]) -> Path:
    body = _ERROR_RETRY_TEMPLATE.replace(
        "__SCRIPT__", repr(list(events))
    )
    path = tmp_path / "cases.py"
    path.write_text(body, encoding="utf-8")
    return path


def _run(tmp_path: Path, case_file: Path, *extra: str) -> tuple[int, dict]:
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(case_file),
            *extra,
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    return code, json.loads(summary.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# matching error → retry happens
# ---------------------------------------------------------------------------
def test_matching_error_is_retried(tmp_path):
    # First two calls raise "429 Too Many Requests"; third succeeds.
    path = _script(
        tmp_path,
        [("err", "429 Too Many Requests"), ("err", "429 again"), ("ok", "ok")],
    )
    code, data = _run(tmp_path, path, "--retry", "3", "--retry-on-error", "429")
    assert code == 0
    assert data["passed"] == 1
    assert data["cases"][0]["attempts"] == 3
    assert data["cases"][0]["retry_budget"] == 4


# ---------------------------------------------------------------------------
# non-matching error → no retry
# ---------------------------------------------------------------------------
def test_non_matching_error_is_not_retried(tmp_path):
    # Error is "ValueError" but pattern matches only "429".
    path = _script(tmp_path, [("err", "ValueError: bad arg")])
    code, data = _run(
        tmp_path, path, "--retry", "3", "--retry-on-error", "429"
    )
    assert code == 0  # default exit 0 on failure
    assert data["failed"] == 1
    # Exactly one attempt — the error didn't match the pattern.
    assert data["cases"][0].get("attempts") is None  # omitted when 1
    assert data["cases"][0]["retry_budget"] == 4
    assert data["total_attempts"] == 1
    assert data["total_budget"] == 4


# ---------------------------------------------------------------------------
# scorer-only failure (no observation.error) → no retry
# ---------------------------------------------------------------------------
def test_scorer_failure_not_retried_under_error_filter(tmp_path):
    # Transport always succeeds but with wrong content — scorer fails.
    # observation.error is None, so --retry-on-error can never match.
    # Script is longer than the retry budget so we'd see many attempts
    # if the filter were broken.
    path = _script(tmp_path, [("ok", "wrong")] * 10)
    code, data = _run(
        tmp_path, path, "--retry", "5", "--retry-on-error", ".*"
    )
    assert code == 0
    assert data["failed"] == 1
    # Single attempt: no observation error to match against.
    assert data["cases"][0].get("attempts") is None


# ---------------------------------------------------------------------------
# multiple regex patterns — any match wins
# ---------------------------------------------------------------------------
def test_multiple_patterns_any_match_wins(tmp_path):
    # First error matches second pattern; second call succeeds.
    path = _script(
        tmp_path,
        [("err", "ConnectionResetError: peer closed"), ("ok", "ok")],
    )
    code, data = _run(
        tmp_path,
        path,
        "--retry",
        "2",
        "--retry-on-error",
        "429",
        "--retry-on-error",
        "ConnectionReset",
    )
    assert code == 0
    assert data["passed"] == 1
    assert data["cases"][0]["attempts"] == 2


# ---------------------------------------------------------------------------
# timeout still short-circuits (even when pattern matches "TimeoutError")
# ---------------------------------------------------------------------------
_SLOW_TEMPLATE = '''
import asyncio

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


CASES = [
    EvalCase(
        name="slow",
        messages=[GrokMessage("user", "q")],
        scorers=[NoErrors()],
    ),
]
'''


def test_timeout_short_circuits_even_when_error_pattern_matches(tmp_path):
    # Timeout still wins: operator's case-level cap is by design.
    path = tmp_path / "slow.py"
    path.write_text(_SLOW_TEMPLATE, encoding="utf-8")
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--timeout-s",
            "0.05",
            "--retry",
            "5",
            "--retry-on-error",
            "TimeoutError",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    # One attempt: timeout short-circuits before the error filter kicks in.
    assert data["cases"][0].get("attempts") is None


# ---------------------------------------------------------------------------
# --retry-on composes with --retry-on-error (AND semantics)
# ---------------------------------------------------------------------------
_TWO_CASE_TEMPLATE = '''
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


# Separate scripts per case (drained in order).
_script_a = __SCRIPT_A__
_script_b = __SCRIPT_B__


@dataclass
class _StubTransport:
    script: list

    async def __call__(self, *, method, url, headers, body, timeout):
        kind, payload = self.script.pop(0)
        if kind == "err":
            raise RuntimeError(payload)
        status, body = _final(payload)
        return status, {}, json.dumps(body).encode("utf-8")


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    # Drain case a's script first, then case b's.
    script = _script_a if _script_a else _script_b
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport(script=script),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="flaky-net",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
    EvalCase(
        name="deterministic",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


def test_retry_on_and_retry_on_error_compose_AND(tmp_path):
    # flaky-net: matches --retry-on "flaky-*" AND --retry-on-error "429" →
    # should retry.
    # deterministic: doesn't match --retry-on → no retry even if error
    # would match.
    path = tmp_path / "cases.py"
    body = (
        _TWO_CASE_TEMPLATE
        .replace(
            "__SCRIPT_A__",
            repr([("err", "429 Too Many Requests"), ("ok", "ok")]),
        )
        .replace(
            "__SCRIPT_B__",
            repr([("err", "429 Too Many Requests")]),
        )
    )
    path.write_text(body, encoding="utf-8")
    summary = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--retry-on",
            "flaky-*",
            "--retry-on-error",
            "429",
            "--summary-json",
            str(summary),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(summary.read_text(encoding="utf-8"))
    flaky = next(c for c in data["cases"] if c["case"] == "flaky-net")
    deter = next(c for c in data["cases"] if c["case"] == "deterministic")
    assert flaky["attempts"] == 2
    assert flaky["passed"] is True
    # deterministic didn't match --retry-on → budget=1 → single attempt.
    assert deter.get("attempts") is None
    assert deter.get("retry_budget") is None
    assert deter["passed"] is False


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def test_retry_on_error_without_retry_is_cli_error(tmp_path, capsys):
    path = _script(tmp_path, [("ok", "ok")])
    code = main(["run", str(path), "--retry-on-error", "429"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--retry-on-error requires --retry > 0" in err


def test_retry_on_error_invalid_regex_is_cli_error(tmp_path, capsys):
    path = _script(tmp_path, [("ok", "ok")])
    code = main(
        ["run", str(path), "--retry", "1", "--retry-on-error", "[invalid"]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "invalid regex in --retry-on-error" in err
