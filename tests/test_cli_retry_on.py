"""Tests for ``frok run --retry-on PATTERN``.

Verifies the retry loop narrows to matching case names while
non-matches run exactly once even when --retry is set.
"""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_retry_on_default_empty():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.retry_on == []


def test_parser_retry_on_is_repeatable():
    parser = build_parser()
    ns = parser.parse_args(
        ["run", "cases.py", "--retry-on", "flaky-*", "--retry-on", "re:^net-"]
    )
    assert ns.retry_on == ["flaky-*", "re:^net-"]


# ---------------------------------------------------------------------------
# fixtures — two cases, both always fail. Counter file records each attempt,
# prefixed by case name, so tests can assert attempts per case.
# ---------------------------------------------------------------------------
_TWO_CASE_FILE = '''
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


def _bump(name):
    p = Path(os.environ["FROK_RETRY_ON_COUNTER"])
    with p.open("a", encoding="utf-8") as fh:
        fh.write(name + "\\n")


@dataclass
class _StubTransport:
    name: str
    responses: list

    async def __call__(self, *, method, url, headers, body, timeout):
        _bump(self.name)
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


# Per-client module-level state: each case gets its own name-stamped
# response list. make_client peels one per build.
_by_case = {
    "flaky-net": [_final("nope")] * 10,
    "deterministic": [_final("nope")] * 10,
}


def make_client(config, sink):
    # Infer case by inspecting the pending responses — the runner builds
    # one client per case per attempt, but doesn't pass the case name.
    # We work around that by consuming the next response from whichever
    # list still has one reserved.
    # Simplest approach: use FROK_CURRENT_CASE, set by pytest wrapper.
    name = os.environ.get("FROK_CURRENT_CASE", "")
    if not name:
        # Fallback: round-robin between non-empty lists.
        for k, v in _by_case.items():
            if v:
                name = k
                break
    resp = _by_case[name].pop(0)
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport(name=name, responses=[resp]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


# Two cases. Both always fail the scorer (wants "ok"; response is "nope").
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


# The name-inference in _TWO_CASE_FILE is brittle; a cleaner approach uses
# `build_cases` + a closure-captured counter mapping case → transport. But
# the existing `make_client(config, sink)` API doesn't get the case. Simpler
# approach: use separate case files when we need per-case control, and for
# --retry-on tests use a single case + assert attempts via summary.
_SINGLE_FLAKY_TEMPLATE = '''
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list

    async def __call__(self, *, method, url, headers, body, timeout):
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


_responses_a = [_final(t) for t in __RESPONSES_A__]
_responses_b = [_final(t) for t in __RESPONSES_B__]


def make_client(config, sink):
    # Drain the first case's responses first, then the second's.
    src = _responses_a if _responses_a else _responses_b
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([src.pop(0)]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="__NAME_A__",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
    EvalCase(
        name="__NAME_B__",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


def _two_cases(
    tmp_path: Path,
    *,
    name_a: str = "flaky-net",
    name_b: str = "deterministic",
    responses_a: list[str],
    responses_b: list[str],
) -> Path:
    body = (
        _SINGLE_FLAKY_TEMPLATE
        .replace("__NAME_A__", name_a)
        .replace("__NAME_B__", name_b)
        .replace(
            "__RESPONSES_A__",
            "[" + ", ".join(repr(r) for r in responses_a) + "]",
        )
        .replace(
            "__RESPONSES_B__",
            "[" + ", ".join(repr(r) for r in responses_b) + "]",
        )
    )
    path = tmp_path / "cases.py"
    path.write_text(body, encoding="utf-8")
    return path


def _run(tmp_path: Path, case_file: Path, *extra: str) -> dict:
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
    assert code == 0
    return json.loads(summary.read_text(encoding="utf-8"))


def _case(data: dict, name: str) -> dict:
    return next(c for c in data["cases"] if c["case"] == name)


# ---------------------------------------------------------------------------
# happy path: --retry-on narrows the retry budget
# ---------------------------------------------------------------------------
def test_retry_on_narrows_to_matching_case(tmp_path):
    # flaky-net gets attempts=3 (1 + retry 2); deterministic runs once.
    path = _two_cases(
        tmp_path,
        responses_a=["nope", "nope", "nope"],
        responses_b=["nope"],
    )
    data = _run(tmp_path, path, "--retry", "2", "--retry-on", "flaky-*")
    assert _case(data, "flaky-net")["attempts"] == 3
    assert _case(data, "deterministic").get("attempts") is None


def test_retry_on_no_match_runs_everyone_once(tmp_path):
    # --retry-on "flaky-*" matches neither case, so both run exactly once.
    path = _two_cases(
        tmp_path,
        name_a="alpha",
        name_b="beta",
        responses_a=["nope"],
        responses_b=["nope"],
    )
    data = _run(tmp_path, path, "--retry", "3", "--retry-on", "flaky-*")
    assert _case(data, "alpha").get("attempts") is None
    assert _case(data, "beta").get("attempts") is None
    # No retries happened at all; _has_retries stays False in summary.
    assert "total_attempts" not in data


def test_retry_on_regex_prefix(tmp_path):
    # Regex: retry only cases whose names start with "net-".
    path = _two_cases(
        tmp_path,
        name_a="net-timeout",
        name_b="math-correctness",
        responses_a=["nope", "nope"],
        responses_b=["nope"],
    )
    data = _run(tmp_path, path, "--retry", "1", "--retry-on", "re:^net-")
    assert _case(data, "net-timeout")["attempts"] == 2
    assert _case(data, "math-correctness").get("attempts") is None


def test_retry_on_repeatable_any_match_wins(tmp_path):
    # Two patterns, each matches one case — both should be retried.
    path = _two_cases(
        tmp_path,
        name_a="flaky-net",
        name_b="flaky-llm",
        responses_a=["nope", "nope"],
        responses_b=["nope", "nope"],
    )
    data = _run(
        tmp_path,
        path,
        "--retry",
        "1",
        "--retry-on",
        "flaky-net",
        "--retry-on",
        "flaky-llm",
    )
    assert _case(data, "flaky-net")["attempts"] == 2
    assert _case(data, "flaky-llm")["attempts"] == 2


def test_retry_on_pass_first_attempt_no_retry_consumed(tmp_path):
    # Matched case passes on first try → attempts stays 1 (omitted).
    path = _two_cases(
        tmp_path,
        responses_a=["ok"],
        responses_b=["nope"],
    )
    data = _run(tmp_path, path, "--retry", "3", "--retry-on", "flaky-*")
    assert _case(data, "flaky-net").get("attempts") is None
    assert _case(data, "deterministic").get("attempts") is None


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------
def test_retry_on_without_retry_is_cli_error(tmp_path, capsys):
    path = _two_cases(
        tmp_path,
        responses_a=["nope"],
        responses_b=["nope"],
    )
    code = main(["run", str(path), "--retry-on", "flaky-*"])
    assert code == 2
    err = capsys.readouterr().err
    assert "--retry-on requires --retry > 0" in err


def test_retry_on_with_retry_zero_is_cli_error(tmp_path, capsys):
    path = _two_cases(
        tmp_path,
        responses_a=["nope"],
        responses_b=["nope"],
    )
    code = main(
        ["run", str(path), "--retry", "0", "--retry-on", "flaky-*"]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "--retry-on requires --retry > 0" in err


def test_retry_on_invalid_regex_is_cli_error(tmp_path, capsys):
    path = _two_cases(
        tmp_path,
        responses_a=["nope"],
        responses_b=["nope"],
    )
    code = main(
        ["run", str(path), "--retry", "1", "--retry-on", "re:[invalid"]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "invalid regex" in err


# ---------------------------------------------------------------------------
# interop: composes with --fail-on-regression and --filter
# ---------------------------------------------------------------------------
def test_retry_on_fail_on_regression_exhausts(tmp_path):
    # Matched case exhausts retries → exit 1 under --fail-on-regression.
    path = _two_cases(
        tmp_path,
        responses_a=["nope", "nope"],
        responses_b=["nope"],
    )
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "1",
            "--retry-on",
            "flaky-*",
            "--fail-on-regression",
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 1


def test_retry_on_composes_with_filter(tmp_path):
    # --filter keeps both cases; --retry-on only retries flaky-net.
    path = _two_cases(
        tmp_path,
        responses_a=["nope", "nope"],
        responses_b=["nope"],
    )
    data = _run(
        tmp_path,
        path,
        "--retry",
        "1",
        "--retry-on",
        "flaky-*",
        "--filter",
        "*",
    )
    assert _case(data, "flaky-net")["attempts"] == 2
    assert _case(data, "deterministic").get("attempts") is None
