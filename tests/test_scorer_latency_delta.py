"""Tests for the ``LatencyDeltaWithin`` scorer."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.clients.grok import GrokResponse
from frok.evals import (
    AnswerContains,
    EvalCase,
    EvalRunner,
    LatencyDeltaWithin,
    Observation,
)
from frok.telemetry import SPAN_END, Event, JsonlSink, Tracer


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _root_span(duration_ms: float) -> Event:
    return Event(
        ts=1000.0,
        trace_id="t1",
        span_id="r1",
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=duration_ms,
        data={"total_tokens": 5},
    )


def _obs(duration_ms: float) -> Observation:
    return Observation(
        final_response=GrokResponse(model="grok-4", content="ok", raw={}),
        messages=[],
        invocations=[],
        events=[_root_span(duration_ms)],
    )


def _write_baseline(path: Path, duration_ms: float) -> Path:
    with JsonlSink(path) as sink:
        sink.emit(_root_span(duration_ms))
    return path


def _case_with_baseline(baseline: Path | None) -> EvalCase:
    return EvalCase(
        name="stub",
        messages=[GrokMessage("user", "hi")],
        baseline=baseline,
    )


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------
def test_rejects_negative_max_ms():
    with pytest.raises(ValueError, match="max_ms must be >= 0"):
        LatencyDeltaWithin(max_ms=-1.0)


def test_zero_max_ms_allowed_as_exact_parity():
    assert LatencyDeltaWithin(max_ms=0.0).max_ms == 0.0


# ---------------------------------------------------------------------------
# no baseline attached → fails cleanly
# ---------------------------------------------------------------------------
def test_fails_cleanly_when_no_baseline_attached():
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(None), _obs(50.0)
    )
    assert score.passed is False
    assert "no baseline" in score.detail


def test_fails_cleanly_when_baseline_file_missing(tmp_path):
    case = _case_with_baseline(tmp_path / "does-not-exist.jsonl")
    score = LatencyDeltaWithin(max_ms=10.0)(case, _obs(50.0))
    assert score.passed is False
    assert "baseline file not found" in score.detail


# ---------------------------------------------------------------------------
# delta under threshold → passes (both directions)
# ---------------------------------------------------------------------------
def test_zero_delta_passes(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=50.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(50.0)
    )
    assert score.passed is True
    assert score.measure == 0.0


def test_small_positive_delta_passes(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=100.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(108.0)
    )
    assert score.passed is True
    assert score.measure == pytest.approx(8.0)


def test_small_negative_delta_passes(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=100.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(92.0)
    )
    assert score.passed is True
    assert score.measure == pytest.approx(-8.0)


def test_at_threshold_positive_passes_inclusive(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=100.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(110.0)
    )
    assert score.passed is True


def test_at_threshold_negative_passes_inclusive(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=100.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(90.0)
    )
    assert score.passed is True


# ---------------------------------------------------------------------------
# delta over threshold → fails (both directions)
# ---------------------------------------------------------------------------
def test_over_threshold_positive_fails(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=100.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(175.5)
    )
    assert score.passed is False
    assert "+75.5" in score.detail
    assert "±10" in score.detail
    assert "baseline=100" in score.detail
    assert "observed=175" in score.detail
    assert score.measure == pytest.approx(75.5)


def test_over_threshold_negative_fails(tmp_path):
    # Bail-early signal: observed dropped sharply below baseline.
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=500.0)
    score = LatencyDeltaWithin(max_ms=10.0)(
        _case_with_baseline(baseline), _obs(50.0)
    )
    assert score.passed is False
    assert "-450.0" in score.detail
    assert score.measure == pytest.approx(-450.0)


def test_max_ms_zero_enforces_exact_parity(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=50.0)
    assert LatencyDeltaWithin(max_ms=0.0)(
        _case_with_baseline(baseline), _obs(50.0)
    ).passed is True
    assert LatencyDeltaWithin(max_ms=0.0)(
        _case_with_baseline(baseline), _obs(50.1)
    ).passed is False


# ---------------------------------------------------------------------------
# scorer name + measure
# ---------------------------------------------------------------------------
def test_scorer_name_includes_max_ms(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=50.0)
    score = LatencyDeltaWithin(max_ms=42.0)(
        _case_with_baseline(baseline), _obs(50.0)
    )
    assert score.name == "latency_delta_within[42.0]"


def test_measure_signed_delta_direction_preserved(tmp_path):
    baseline = _write_baseline(tmp_path / "b.jsonl", duration_ms=100.0)
    scorer = LatencyDeltaWithin(max_ms=1000.0)
    assert scorer(_case_with_baseline(baseline), _obs(120.0)).measure == pytest.approx(20.0)
    assert scorer(_case_with_baseline(baseline), _obs(80.0)).measure == pytest.approx(-20.0)


# ---------------------------------------------------------------------------
# runner integration
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


def _ok(text, *, prompt=5, completion=3):
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


async def test_runner_integration_passes_when_latency_parity(tmp_path):
    # Deterministic clock: each tick returns +0.005 s, so grok.chat span
    # ends up ~5 ms — matching the baseline.
    import itertools
    counter = itertools.count()

    def clock() -> float:
        return 0.005 * next(counter)

    baseline = _write_baseline(tmp_path / "baseline.jsonl", duration_ms=5.0)
    transport = _StubTransport([_ok("hi")])

    def factory(sink):
        from frok.telemetry import Tracer
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(sink=sink, clock=clock),
        )

    case = EvalCase(
        name="latency-parity",
        messages=[GrokMessage("user", "hi")],
        baseline=baseline,
        scorers=[
            AnswerContains("hi"),
            LatencyDeltaWithin(max_ms=5.0),  # generous cap for wall-clock noise
        ],
    )
    result = await EvalRunner(client_factory=factory).run_case(case)
    # Deterministic clock makes duration exactly 5 ms; baseline is 5 ms →
    # delta 0 → passes regardless of wall-clock noise.
    assert result.passed, [s for s in result.scores if not s.passed]


async def test_runner_integration_fails_on_latency_drift(tmp_path):
    import itertools
    # Per-span timing: start=0.0, end=1.0 s → duration 1000 ms (>> baseline).
    stamps = iter([0.0, 1.0])

    def clock() -> float:
        return next(stamps)

    baseline = _write_baseline(tmp_path / "baseline.jsonl", duration_ms=10.0)
    transport = _StubTransport([_ok("hi")])

    def factory(sink):
        from frok.telemetry import Tracer
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(sink=sink, clock=clock),
        )

    case = EvalCase(
        name="latency-drift",
        messages=[GrokMessage("user", "hi")],
        baseline=baseline,
        scorers=[LatencyDeltaWithin(max_ms=100.0)],
    )
    result = await EvalRunner(client_factory=factory).run_case(case)
    assert not result.passed
    failed = [s for s in result.scores if not s.passed]
    assert len(failed) == 1
    # Delta = 1000 - 10 = 990 ms.
    assert "+990.0" in failed[0].detail
