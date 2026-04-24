"""Tests for the ``LatencyWithin`` scorer."""

import pytest

from frok.clients.grok import GrokResponse
from frok.evals import LatencyWithin, Observation
from frok.telemetry import SPAN_END, Event


def _root_span(duration_ms: float) -> Event:
    return Event(
        ts=1000.0,
        trace_id="t1",
        span_id="r1",
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=duration_ms,
        data={},
    )


def _obs(duration_ms: float | None, *, error: str | None = None) -> Observation:
    events = [_root_span(duration_ms)] if duration_ms is not None else []
    return Observation(
        final_response=GrokResponse(model="grok-4", content="", raw={}),
        messages=[],
        invocations=[],
        events=events,
        error=error,
    )


# ---------------------------------------------------------------------------
# pass / fail
# ---------------------------------------------------------------------------
def test_passes_when_latency_below_ceiling():
    score = LatencyWithin(max_ms=100.0)(None, _obs(50.0))
    assert score.passed is True
    assert score.measure == 50.0


def test_passes_at_exactly_the_ceiling():
    # "within" is inclusive — at-limit should pass.
    score = LatencyWithin(max_ms=100.0)(None, _obs(100.0))
    assert score.passed is True


def test_fails_over_ceiling_surfaces_both_values_in_detail():
    score = LatencyWithin(max_ms=100.0)(None, _obs(240.3))
    assert score.passed is False
    assert "240.3" in score.detail
    assert "100" in score.detail
    assert "ms" in score.detail
    assert score.measure == 240.3


# ---------------------------------------------------------------------------
# missing root span → zero latency → always passes non-negative threshold
# ---------------------------------------------------------------------------
def test_missing_root_span_reports_zero_and_passes():
    score = LatencyWithin(max_ms=0.0)(None, _obs(None))
    assert score.passed is True
    assert score.measure == 0.0


def test_missing_root_span_still_fails_a_negative_ceiling():
    # Pathological, but documents the contract: the scorer compares
    # observation.total_latency_ms (0.0 when no root) against max_ms.
    score = LatencyWithin(max_ms=-1.0)(None, _obs(None))
    assert score.passed is False


# ---------------------------------------------------------------------------
# run-errored observation still reports zero latency
# ---------------------------------------------------------------------------
def test_run_error_without_root_span_passes():
    # The right signal for a failed run is NoErrors — LatencyWithin
    # doesn't second-guess it.
    score = LatencyWithin(max_ms=10.0)(
        None, _obs(None, error="RuntimeError: boom")
    )
    assert score.passed is True


# ---------------------------------------------------------------------------
# scorer name
# ---------------------------------------------------------------------------
def test_scorer_name_includes_max_ms():
    score = LatencyWithin(max_ms=250.0)(None, _obs(100.0))
    assert "latency_within" in score.name
    assert "250" in score.name
