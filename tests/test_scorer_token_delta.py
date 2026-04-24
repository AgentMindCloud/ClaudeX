"""Tests for the ``TokenDeltaWithin`` scorer."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.clients.grok import GrokResponse
from frok.evals import AnswerContains, EvalCase, EvalRunner, Observation, TokenDeltaWithin
from frok.telemetry import SPAN_END, Event, JsonlSink, Tracer


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _chat_span(tokens: int) -> Event:
    return Event(
        ts=1000.0,
        trace_id="t1",
        span_id="c1",
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=5.0,
        data={"total_tokens": tokens},
    )


def _obs(tokens: int) -> Observation:
    return Observation(
        final_response=GrokResponse(model="grok-4", content="ok", raw={}),
        messages=[],
        invocations=[],
        events=[_chat_span(tokens)],
    )


def _write_baseline(path: Path, tokens: int) -> Path:
    with JsonlSink(path) as sink:
        sink.emit(_chat_span(tokens))
    return path


def _case_with_baseline(baseline: Path | None = None) -> EvalCase:
    return EvalCase(
        name="stub",
        messages=[GrokMessage("user", "hi")],
        baseline=baseline,
    )


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------
def test_rejects_negative_max_delta():
    with pytest.raises(ValueError, match="max_delta must be >= 0"):
        TokenDeltaWithin(max_delta=-1)


def test_zero_max_delta_allowed_as_exact_parity():
    # max_delta=0 means "tokens must match baseline exactly".
    assert TokenDeltaWithin(max_delta=0).max_delta == 0


# ---------------------------------------------------------------------------
# no baseline attached → fails cleanly
# ---------------------------------------------------------------------------
def test_fails_cleanly_when_no_baseline_attached():
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline=None), _obs(50)
    )
    assert score.passed is False
    assert "no baseline" in score.detail


def test_fails_cleanly_when_baseline_file_missing(tmp_path):
    case = _case_with_baseline(baseline=tmp_path / "does-not-exist.jsonl")
    score = TokenDeltaWithin(max_delta=10)(case, _obs(50))
    assert score.passed is False
    assert "baseline file not found" in score.detail


# ---------------------------------------------------------------------------
# delta under threshold → passes (both directions)
# ---------------------------------------------------------------------------
def test_zero_delta_passes(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(50)
    )
    assert score.passed is True
    assert score.measure == 0


def test_small_positive_delta_passes(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(55)
    )
    assert score.passed is True
    assert score.measure == 5


def test_small_negative_delta_passes(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(45)
    )
    assert score.passed is True
    assert score.measure == -5


def test_at_threshold_positive_passes_inclusive(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(60)
    )
    assert score.passed is True


def test_at_threshold_negative_passes_inclusive(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(40)
    )
    assert score.passed is True


# ---------------------------------------------------------------------------
# delta over threshold → fails (both directions)
# ---------------------------------------------------------------------------
def test_over_threshold_positive_fails(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(75)
    )
    assert score.passed is False
    assert "+25" in score.detail
    assert "±10" in score.detail
    # Baseline + observed values surfaced for triage.
    assert "baseline=50" in score.detail
    assert "observed=75" in score.detail
    assert score.measure == 25


def test_over_threshold_negative_fails(tmp_path):
    # Caught bail-early bugs: observed collapsed to far fewer tokens.
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=100)
    score = TokenDeltaWithin(max_delta=10)(
        _case_with_baseline(baseline), _obs(20)
    )
    assert score.passed is False
    assert "-80" in score.detail
    assert score.measure == -80


def test_max_delta_zero_enforces_exact_parity(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    # Any delta at all fails.
    score = TokenDeltaWithin(max_delta=0)(
        _case_with_baseline(baseline), _obs(51)
    )
    assert score.passed is False
    # Exact match still passes.
    assert TokenDeltaWithin(max_delta=0)(
        _case_with_baseline(baseline), _obs(50)
    ).passed is True


# ---------------------------------------------------------------------------
# scorer name reflects the configured cap
# ---------------------------------------------------------------------------
def test_scorer_name_includes_max_delta(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    score = TokenDeltaWithin(max_delta=42)(
        _case_with_baseline(baseline), _obs(50)
    )
    assert score.name == "token_delta_within[42]"


# ---------------------------------------------------------------------------
# measure carries signed delta for trend-scanning
# ---------------------------------------------------------------------------
def test_measure_signed_delta_direction_preserved(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", tokens=50)
    # Going up is +, going down is -.
    assert TokenDeltaWithin(max_delta=100)(
        _case_with_baseline(baseline), _obs(60)
    ).measure == 10
    assert TokenDeltaWithin(max_delta=100)(
        _case_with_baseline(baseline), _obs(40)
    ).measure == -10


# ---------------------------------------------------------------------------
# runner integration: scorer runs end-to-end under EvalRunner
# ---------------------------------------------------------------------------
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


def _ok(text, *, prompt, completion):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


async def test_runner_integration_passes_when_tokens_parity(tmp_path):
    # Record a baseline that captures total_tokens=10 on a grok.chat span.
    baseline = _write_baseline(tmp_path / "baseline.jsonl", tokens=10)

    transport = _StubTransport([_ok("hi", prompt=7, completion=3)])

    def factory(sink):
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(sink=sink),
        )

    case = EvalCase(
        name="drift",
        messages=[GrokMessage("user", "hi")],
        baseline=baseline,
        scorers=[
            AnswerContains("hi"),
            TokenDeltaWithin(max_delta=5),
        ],
    )
    result = await EvalRunner(client_factory=factory).run_case(case)
    assert result.passed, [s for s in result.scores if not s.passed]


async def test_runner_integration_fails_on_token_drift(tmp_path):
    baseline = _write_baseline(tmp_path / "baseline.jsonl", tokens=10)
    transport = _StubTransport([_ok("hi", prompt=50, completion=50)])  # 100 tokens

    def factory(sink):
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(sink=sink),
        )

    case = EvalCase(
        name="drift",
        messages=[GrokMessage("user", "hi")],
        baseline=baseline,
        scorers=[TokenDeltaWithin(max_delta=5)],
    )
    result = await EvalRunner(client_factory=factory).run_case(case)
    assert not result.passed
    failed = [s for s in result.scores if not s.passed]
    assert len(failed) == 1
    assert "+90" in failed[0].detail
