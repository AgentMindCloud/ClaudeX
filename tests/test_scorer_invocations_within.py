"""Tests for the ``InvocationsWithin`` scorer."""

import pytest

from frok.clients.grok import GrokResponse
from frok.evals import InvocationsWithin, Observation
from frok.tools.orchestrator import ToolInvocation


def _inv(name: str, **args) -> ToolInvocation:
    return ToolInvocation(call_id="c", name=name, arguments=dict(args), result="r")


def _obs(*invocations: ToolInvocation) -> Observation:
    return Observation(
        final_response=GrokResponse(model="grok-4", content="", raw={}),
        messages=[],
        invocations=list(invocations),
        events=[],
    )


# ---------------------------------------------------------------------------
# pass / fail
# ---------------------------------------------------------------------------
def test_passes_when_count_below_ceiling():
    score = InvocationsWithin(max_count=5)(
        None, _obs(_inv("a"), _inv("b"), _inv("c"))
    )
    assert score.passed is True
    assert score.measure == 3


def test_passes_at_exactly_the_ceiling():
    # "within" is inclusive — at-limit should pass.
    score = InvocationsWithin(max_count=2)(None, _obs(_inv("a"), _inv("b")))
    assert score.passed is True


def test_fails_over_ceiling_surfaces_both_values_in_detail():
    score = InvocationsWithin(max_count=2)(
        None, _obs(_inv("a"), _inv("b"), _inv("c"), _inv("d"))
    )
    assert score.passed is False
    assert "4" in score.detail
    assert "2" in score.detail
    assert "invocations" in score.detail
    assert score.measure == 4


# ---------------------------------------------------------------------------
# edge: zero invocations
# ---------------------------------------------------------------------------
def test_zero_invocations_passes_any_non_negative_threshold():
    score = InvocationsWithin(max_count=0)(None, _obs())
    assert score.passed is True
    assert score.measure == 0


def test_no_tools_case_passes():
    # No tools -> no invocations -> always under any non-negative cap.
    score = InvocationsWithin(max_count=3)(None, _obs())
    assert score.passed is True


def test_count_counts_every_invocation_regardless_of_tool():
    # Same tool invoked three times counts as 3.
    score = InvocationsWithin(max_count=2)(
        None, _obs(_inv("add"), _inv("add"), _inv("add"))
    )
    assert score.passed is False
    assert score.measure == 3


# ---------------------------------------------------------------------------
# scorer name
# ---------------------------------------------------------------------------
def test_scorer_name_includes_max_count():
    score = InvocationsWithin(max_count=7)(None, _obs())
    assert "invocations_within" in score.name
    assert "7" in score.name
