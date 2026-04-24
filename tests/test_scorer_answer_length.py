"""Tests for the ``AnswerLength`` scorer."""

import pytest

from frok.clients.grok import GrokResponse
from frok.evals import AnswerLength, Observation


def _obs(answer: str = "") -> Observation:
    return Observation(
        final_response=GrokResponse(model="grok-4", content=answer, raw={})
        if answer is not None
        else None,
        messages=[],
        invocations=[],
        events=[],
    )


def _obs_no_response() -> Observation:
    return Observation(
        final_response=None,
        messages=[],
        invocations=[],
        events=[],
    )


# ---------------------------------------------------------------------------
# construction validation
# ---------------------------------------------------------------------------
def test_requires_at_least_one_bound():
    with pytest.raises(ValueError, match="at least one"):
        AnswerLength()


def test_rejects_negative_min():
    with pytest.raises(ValueError, match="min_chars must be >= 0"):
        AnswerLength(min_chars=-1)


def test_rejects_negative_max():
    with pytest.raises(ValueError, match="max_chars must be >= 0"):
        AnswerLength(max_chars=-1)


def test_rejects_min_greater_than_max():
    with pytest.raises(ValueError, match="min_chars .* > max_chars"):
        AnswerLength(min_chars=10, max_chars=5)


def test_min_equal_to_max_allowed_as_exact_length():
    # Pinning an exact length is a legitimate assertion.
    scorer = AnswerLength(min_chars=3, max_chars=3)
    assert scorer(None, _obs("abc")).passed is True
    assert scorer(None, _obs("ab")).passed is False
    assert scorer(None, _obs("abcd")).passed is False


# ---------------------------------------------------------------------------
# min-only
# ---------------------------------------------------------------------------
def test_min_only_passes_at_and_above():
    scorer = AnswerLength(min_chars=5)
    assert scorer(None, _obs("hello")).passed is True
    assert scorer(None, _obs("hello world")).passed is True


def test_min_only_fails_below_with_both_values_in_detail():
    scorer = AnswerLength(min_chars=5)
    score = scorer(None, _obs("hi"))
    assert score.passed is False
    assert "length 2" in score.detail
    assert "min 5" in score.detail
    assert score.measure == 2


# ---------------------------------------------------------------------------
# max-only
# ---------------------------------------------------------------------------
def test_max_only_passes_at_and_below():
    scorer = AnswerLength(max_chars=5)
    assert scorer(None, _obs("")).passed is True
    assert scorer(None, _obs("hi")).passed is True
    assert scorer(None, _obs("hello")).passed is True


def test_max_only_fails_above_with_both_values_in_detail():
    scorer = AnswerLength(max_chars=5)
    score = scorer(None, _obs("hello world"))
    assert score.passed is False
    assert "length 11" in score.detail
    assert "max 5" in score.detail
    assert score.measure == 11


# ---------------------------------------------------------------------------
# both bounds: closed range
# ---------------------------------------------------------------------------
def test_both_bounds_passes_in_range():
    scorer = AnswerLength(min_chars=3, max_chars=10)
    assert scorer(None, _obs("abc")).passed is True
    assert scorer(None, _obs("abcdef")).passed is True
    assert scorer(None, _obs("abcdefghij")).passed is True


def test_both_bounds_fail_below_min():
    scorer = AnswerLength(min_chars=3, max_chars=10)
    score = scorer(None, _obs("ab"))
    assert score.passed is False
    assert "< min 3" in score.detail


def test_both_bounds_fail_above_max():
    scorer = AnswerLength(min_chars=3, max_chars=10)
    score = scorer(None, _obs("abcdefghijk"))
    assert score.passed is False
    assert "> max 10" in score.detail


# ---------------------------------------------------------------------------
# edge: missing final response
# ---------------------------------------------------------------------------
def test_no_final_response_treated_as_empty_string():
    # obs.answer is "" when final_response is None; min-based scorers
    # correctly fail and max-only correctly passes.
    assert AnswerLength(max_chars=10)(None, _obs_no_response()).passed is True
    fail = AnswerLength(min_chars=1)(None, _obs_no_response())
    assert fail.passed is False
    assert fail.measure == 0


# ---------------------------------------------------------------------------
# scorer name reflects active bounds
# ---------------------------------------------------------------------------
def test_scorer_name_min_only():
    score = AnswerLength(min_chars=5)(None, _obs("hello"))
    assert score.name == "answer_length[>=5]"


def test_scorer_name_max_only():
    score = AnswerLength(max_chars=100)(None, _obs("hi"))
    assert score.name == "answer_length[<=100]"


def test_scorer_name_both_bounds():
    score = AnswerLength(min_chars=3, max_chars=10)(None, _obs("hello"))
    assert score.name == "answer_length[>=3,<=10]"


# ---------------------------------------------------------------------------
# measure carries the observed length whether pass or fail
# ---------------------------------------------------------------------------
def test_measure_always_carries_observed_length():
    scorer = AnswerLength(min_chars=3, max_chars=10)
    assert scorer(None, _obs("abc")).measure == 3
    assert scorer(None, _obs("a" * 100)).measure == 100
    assert scorer(None, _obs("")).measure == 0
