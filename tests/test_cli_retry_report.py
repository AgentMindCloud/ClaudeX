"""Tests for ``frok run --retry-report PATH``.

Verifies the per-case per-attempt timeline JSON shape.
"""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main
from frok.cli import run as run_mod


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_retry_report_default_none():
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py"])
    assert ns.retry_report is None


def test_parser_retry_report_accepts_path(tmp_path):
    parser = build_parser()
    ns = parser.parse_args(["run", "cases.py", "--retry-report", str(tmp_path / "r.json")])
    assert ns.retry_report == tmp_path / "r.json"


# ---------------------------------------------------------------------------
# case-file fixture
# ---------------------------------------------------------------------------
_SCRIPT_TEMPLATE = '''
import json
from dataclasses import dataclass

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


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


def _script_case(tmp_path: Path, events: list[tuple[str, str]]) -> Path:
    body = _SCRIPT_TEMPLATE.replace("__SCRIPT__", repr(list(events)))
    path = tmp_path / "cases.py"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.fixture
def patched_sleep(monkeypatch):
    async def fake_sleep(_s):
        return None

    monkeypatch.setattr(run_mod, "_retry_sleep", fake_sleep)


# ---------------------------------------------------------------------------
# single-attempt pass → timeline has one entry
# ---------------------------------------------------------------------------
def test_single_attempt_pass_timeline(tmp_path):
    path = _script_case(tmp_path, [("ok", "ok")])
    report = tmp_path / "retry.json"
    code = main(
        [
            "run",
            str(path),
            "--retry-report",
            str(report),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["cases"] == [
        {
            "case": "target",
            "repeat": 0,
            "attempts": [
                {
                    "attempt": 1,
                    "passed": True,
                    "error": None,
                    "sleep_before_ms": 0.0,
                }
            ],
            "retry_budget": 1,
            "passed": True,
        }
    ]


# ---------------------------------------------------------------------------
# multi-attempt with error + final pass → entries reflect each try
# ---------------------------------------------------------------------------
def test_multi_attempt_timeline_captures_each_error(tmp_path, patched_sleep):
    path = _script_case(
        tmp_path,
        [
            ("err", "429 Too Many Requests"),
            ("err", "429 again"),
            ("ok", "ok"),
        ],
    )
    report = tmp_path / "retry.json"
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "3",
            "--retry-backoff",
            "250",
            "--retry-report",
            str(report),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    case = data["cases"][0]
    assert case["case"] == "target"
    assert case["repeat"] == 0
    assert case["retry_budget"] == 4
    assert case["passed"] is True

    attempts = case["attempts"]
    assert len(attempts) == 3
    # First attempt: no backoff, carries the error.
    assert attempts[0] == {
        "attempt": 1,
        "passed": False,
        "error": "RuntimeError: 429 Too Many Requests",
        "sleep_before_ms": 0.0,
    }
    # Second and third attempts: backoff kicks in.
    assert attempts[1]["attempt"] == 2
    assert attempts[1]["passed"] is False
    assert attempts[1]["error"] == "RuntimeError: 429 again"
    assert attempts[1]["sleep_before_ms"] == 250.0
    assert attempts[2]["attempt"] == 3
    assert attempts[2]["passed"] is True
    assert attempts[2]["error"] is None
    assert attempts[2]["sleep_before_ms"] == 250.0


# ---------------------------------------------------------------------------
# exhausted retries → all attempts logged, all failing
# ---------------------------------------------------------------------------
def test_exhausted_retries_logs_every_attempt(tmp_path, patched_sleep):
    path = _script_case(
        tmp_path,
        [
            ("err", "boom"),
            ("err", "boom"),
            ("err", "boom"),
        ],
    )
    report = tmp_path / "retry.json"
    code = main(
        [
            "run",
            str(path),
            "--retry",
            "2",
            "--retry-report",
            str(report),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0  # no --fail-on-regression
    data = json.loads(report.read_text(encoding="utf-8"))
    case = data["cases"][0]
    assert case["passed"] is False
    assert case["retry_budget"] == 3
    assert len(case["attempts"]) == 3
    assert all(a["passed"] is False for a in case["attempts"])
    assert all(a["error"] == "RuntimeError: boom" for a in case["attempts"])


# ---------------------------------------------------------------------------
# no flag → no file written
# ---------------------------------------------------------------------------
def test_no_flag_writes_no_file(tmp_path):
    path = _script_case(tmp_path, [("ok", "ok")])
    # A file at the would-be path must NOT exist after the run.
    report = tmp_path / "retry.json"
    code = main(["run", str(path), "-o", str(tmp_path / "r.md")])
    assert code == 0
    assert not report.exists()


# ---------------------------------------------------------------------------
# parent directory is created when missing
# ---------------------------------------------------------------------------
def test_retry_report_creates_parent_dir(tmp_path):
    path = _script_case(tmp_path, [("ok", "ok")])
    report = tmp_path / "deep" / "nested" / "retry.json"
    code = main(
        [
            "run",
            str(path),
            "--retry-report",
            str(report),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    assert report.exists()
    assert json.loads(report.read_text(encoding="utf-8"))["cases"]


# ---------------------------------------------------------------------------
# --repeat + multi-case — every (case, repeat) gets an entry in order
# ---------------------------------------------------------------------------
_MULTI_CASE_FILE = '''
import json
from dataclasses import dataclass

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


def _final(text):
    return (200, {"model": "grok-4", "choices": [
        {"message": {"role": "assistant", "content": text},
         "finish_reason": "stop"}
    ], "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


@dataclass
class _StubTransport:
    async def __call__(self, *, method, url, headers, body, timeout):
        status, payload = _final("ok")
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
        name="alpha",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
    EvalCase(
        name="beta",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("ok")],
    ),
]
'''


def test_retry_report_multi_case_multi_repeat(tmp_path):
    path = tmp_path / "cases.py"
    path.write_text(_MULTI_CASE_FILE, encoding="utf-8")
    report = tmp_path / "retry.json"
    code = main(
        [
            "run",
            str(path),
            "--repeat",
            "2",
            "--retry-report",
            str(report),
            "-o",
            str(tmp_path / "r.md"),
        ]
    )
    assert code == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    # Submission order: (alpha, 0), (alpha, 1), (beta, 0), (beta, 1).
    cases = data["cases"]
    assert [(c["case"], c["repeat"]) for c in cases] == [
        ("alpha", 0),
        ("alpha", 1),
        ("beta", 0),
        ("beta", 1),
    ]
    # Each (case, repeat) has exactly one attempt entry — all pass on first try.
    assert all(len(c["attempts"]) == 1 for c in cases)
    assert all(c["attempts"][0]["passed"] is True for c in cases)
