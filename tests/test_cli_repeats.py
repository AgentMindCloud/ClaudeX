"""Tests for ``frok run --repeat N`` + ``--seed S``."""

import json
import os
import random
from pathlib import Path

import pytest

from frok.cli import main
from frok.cli.run import apply_seed


# ---------------------------------------------------------------------------
# apply_seed helper
# ---------------------------------------------------------------------------
def test_apply_seed_sets_env_var_and_seeds_random(monkeypatch):
    monkeypatch.delenv("FROK_RUN_SEED", raising=False)
    assert apply_seed(1000, 3) == 1003
    assert os.environ["FROK_RUN_SEED"] == "1003"

    # Same effective seed produces the same random sequence.
    apply_seed(42, 0)
    a = random.random()
    apply_seed(42, 0)
    b = random.random()
    assert a == b


def test_apply_seed_shifts_per_repeat(monkeypatch):
    monkeypatch.delenv("FROK_RUN_SEED", raising=False)
    apply_seed(7, 0)
    first = random.random()
    apply_seed(7, 1)
    second = random.random()
    assert first != second


# ---------------------------------------------------------------------------
# case-file helpers for CLI tests
# ---------------------------------------------------------------------------
_CASE_FILE_N = '''
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


# Responses cycle: "42", "42", "wrong" → with --repeat 3 that's 2/3 pass rate.
_responses = [_final("42"), _final("42"), _final("wrong")]


def make_client(config, sink):
    # Each make_client call for a repeat peels one response.
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
        scorers=[AnswerContains("42")],
    ),
]
'''


def _write_flaky_case(tmp_path: Path) -> Path:
    path = tmp_path / "cases.py"
    path.write_text(_CASE_FILE_N, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# --repeat produces N results per case
# ---------------------------------------------------------------------------
def test_repeat_produces_n_results_per_case(tmp_path):
    case = _write_flaky_case(tmp_path)
    summary_path = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(case),
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
    # 3 individual results, 1 case, flaky (2/3 pass rate).
    assert data["total"] == 3
    assert data["total_cases"] == 1
    assert data["flaky_cases"] == 1
    assert data["case_pass_rates"]["flaky"] == 2 / 3


# ---------------------------------------------------------------------------
# markdown report shows aggregated pass rates
# ---------------------------------------------------------------------------
def test_repeat_markdown_shows_pass_rate_column(tmp_path, capsys):
    case = _write_flaky_case(tmp_path)
    assert main(["run", str(case), "--repeat", "3"]) == 0
    out = capsys.readouterr().out
    assert "Pass rate" in out
    assert "Cases passed:" in out
    # The flaky case shows up with a non-100% rate and FLAKY verdict.
    assert "FLAKY" in out
    assert "67%" in out or "66%" in out  # 2/3 ≈ 66.7%


# ---------------------------------------------------------------------------
# --fail-on-regression + flaky case
# ---------------------------------------------------------------------------
def test_fail_on_regression_fires_on_any_failed_repeat(tmp_path, capsys):
    case = _write_flaky_case(tmp_path)
    # Any failed repeat should flip the exit code under --fail-on-regression
    # (EvalReport.failed > 0).
    code = main(
        ["run", str(case), "--repeat", "3", "--fail-on-regression"]
    )
    assert code == 1


# ---------------------------------------------------------------------------
# --seed publishes FROK_RUN_SEED per-repeat before make_client runs
# ---------------------------------------------------------------------------
_SEED_OBSERVING_CASE = '''
import json
import os
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, Score
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
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("ok")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


# Scorer ALWAYS fails, carrying the observed FROK_RUN_SEED value in its
# name so the aggregated markdown's "Failed scorers" column surfaces every
# distinct seed the runner set.
def _scorer(case, obs):
    seed = os.environ.get("FROK_RUN_SEED", "unset")
    return Score(name=f"seed-{seed}", passed=False, detail=seed)


CASES = [
    EvalCase(
        name="seed-probe",
        messages=[GrokMessage("user", "q")],
        scorers=[_scorer],
    ),
]
'''


def test_seed_is_published_per_repeat(tmp_path):
    path = tmp_path / "cases.py"
    path.write_text(_SEED_OBSERVING_CASE, encoding="utf-8")
    report_md = tmp_path / "r.md"
    code = main(
        [
            "run",
            str(path),
            "--seed",
            "100",
            "--repeat",
            "3",
            "-o",
            str(report_md),
        ]
    )
    assert code == 0
    md = report_md.read_text(encoding="utf-8")
    # The aggregated "Failed scorers" column collects distinct scorer names
    # across every repeat, so all three effective seeds must appear.
    assert "seed-100" in md
    assert "seed-101" in md
    assert "seed-102" in md


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------
def test_repeat_zero_or_negative_is_cli_error(tmp_path, capsys):
    case = _write_flaky_case(tmp_path)
    assert main(["run", str(case), "--repeat", "0"]) == 2
    assert "--repeat must be >= 1" in capsys.readouterr().err


def test_repeat_gt_one_with_capture_baseline_is_cli_error(tmp_path, capsys):
    case = _write_flaky_case(tmp_path)
    code = main(
        [
            "run",
            str(case),
            "--repeat",
            "2",
            "--capture-baseline",
            str(tmp_path / "b"),
        ]
    )
    assert code == 2
    err = capsys.readouterr().err
    assert "--capture-baseline" in err
    assert "--repeat" in err


def test_default_repeat_is_one(tmp_path, capsys):
    # Sanity: running without --repeat yields the unchanged flat markdown.
    case = _write_flaky_case(tmp_path)
    assert main(["run", str(case)]) == 0
    out = capsys.readouterr().out
    assert "Pass rate" not in out  # flat format
    assert "PASS" in out
