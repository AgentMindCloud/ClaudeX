"""Tests for ``frok run --jobs N`` (parallel case execution)."""

import asyncio
import json
from pathlib import Path

import pytest

from frok.cli import main


_MULTI_CASE_FILE = '''
import asyncio
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)
    delay: float = 0.0

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        if self.delay:
            await asyncio.sleep(self.delay)
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {"message": {"role": "assistant", "content": text},
                 "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        },
    )


def make_client(config, sink):
    # Every case answers "42" on a single stubbed call.
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("42")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(name=f"case-{i:02d}",
             messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("42")])
    for i in range(6)
]
'''


def _write_cases(tmp_path: Path, body: str = _MULTI_CASE_FILE) -> Path:
    path = tmp_path / "cases.py"
    path.write_text(body, encoding="utf-8")
    return path


def _summary(tmp_path: Path, *extra: str) -> dict:
    case = _write_cases(tmp_path)
    summary_path = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(case),
            "-o",
            str(tmp_path / "r.md"),
            "--summary-json",
            str(summary_path),
            *extra,
        ]
    )
    assert code == 0, summary_path
    return json.loads(summary_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# defaults + serial compatibility
# ---------------------------------------------------------------------------
def test_jobs_defaults_to_one_and_preserves_case_order(tmp_path):
    data = _summary(tmp_path)
    names = [c["case"] for c in data["cases"]]
    assert names == [f"case-{i:02d}" for i in range(6)]
    assert data["passed"] == 6


def test_explicit_jobs_one_matches_default(tmp_path):
    data = _summary(tmp_path, "--jobs", "1")
    names = [c["case"] for c in data["cases"]]
    assert names == [f"case-{i:02d}" for i in range(6)]


# ---------------------------------------------------------------------------
# parallel execution preserves ordering
# ---------------------------------------------------------------------------
def test_jobs_gt_one_preserves_case_order(tmp_path):
    data = _summary(tmp_path, "--jobs", "4")
    names = [c["case"] for c in data["cases"]]
    assert names == [f"case-{i:02d}" for i in range(6)]
    assert data["total"] == 6
    assert data["passed"] == 6


def test_jobs_with_repeats_multiplies_total(tmp_path):
    # 6 cases * 3 repeats = 18 runs; all still pass (stub always says "42").
    # Each case has its own stub; make_client is called per-run so we need
    # one response per call — already set up. But --repeat 3 means each case
    # gets called 3 times and the stub only has 1 response. Let's add more.
    body = _MULTI_CASE_FILE.replace(
        "_StubTransport([_final(\"42\")])",
        "_StubTransport([_final(\"42\") for _ in range(1)])",
    )
    # Since make_client is called fresh per-run, the stub only ever needs
    # one response per call — good. We just need to ensure make_client
    # builds a fresh transport. Already does.
    _write_cases(tmp_path, body)
    summary_path = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(tmp_path / "cases.py"),
            "--jobs",
            "3",
            "--repeat",
            "3",
            "-o",
            str(tmp_path / "r.md"),
            "--summary-json",
            str(summary_path),
        ]
    )
    assert code == 0
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["total"] == 18
    assert data["total_cases"] == 6
    assert data["passed_cases"] == 6


def test_jobs_with_capture_baseline_writes_all_files(tmp_path):
    case = _write_cases(tmp_path)
    baseline_dir = tmp_path / "b"
    assert (
        main(
            [
                "run",
                str(case),
                "--jobs",
                "4",
                "--capture-baseline",
                str(baseline_dir),
            ]
        )
        == 0
    )
    files = sorted(p.name for p in baseline_dir.iterdir())
    assert files == [f"case-{i:02d}.jsonl" for i in range(6)]


# ---------------------------------------------------------------------------
# clamping to cpu_count
# ---------------------------------------------------------------------------
def test_jobs_silently_clamps_to_cpu_count(tmp_path, monkeypatch):
    monkeypatch.setattr("frok.cli.run.os.cpu_count", lambda: 2)
    # Requesting 1000 should still succeed — clamped to 2 under the hood.
    data = _summary(tmp_path, "--jobs", "1000")
    assert data["total"] == 6


def test_jobs_handles_cpu_count_returning_none(tmp_path, monkeypatch):
    monkeypatch.setattr("frok.cli.run.os.cpu_count", lambda: None)
    data = _summary(tmp_path, "--jobs", "4")
    assert data["total"] == 6


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_jobs_zero_is_cli_error(tmp_path, capsys):
    case = _write_cases(tmp_path)
    assert main(["run", str(case), "--jobs", "0"]) == 2
    assert "--jobs must be >= 1" in capsys.readouterr().err


def test_seed_with_jobs_gt_one_is_cli_error(tmp_path, capsys):
    case = _write_cases(tmp_path)
    assert (
        main(["run", str(case), "--jobs", "2", "--seed", "42"]) == 2
    )
    err = capsys.readouterr().err
    assert "--seed" in err and "--jobs" in err


def test_seed_with_jobs_one_is_allowed(tmp_path):
    case = _write_cases(tmp_path)
    assert main(["run", str(case), "--jobs", "1", "--seed", "42"]) == 0


# ---------------------------------------------------------------------------
# parallelism actually lets tasks interleave (not a strict test, but a smoke)
# ---------------------------------------------------------------------------
def test_parallel_run_completes_without_deadlocking(tmp_path):
    # Stubs use asyncio.sleep in a test to make interleaving observable,
    # but we just assert the run completes in reasonable time with jobs>1.
    data = _summary(tmp_path, "--jobs", "3")
    assert data["total"] == 6
