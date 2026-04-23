from datetime import datetime

from frok.clients.grok import GrokResponse
from frok.evals import (
    AnswerAbsent,
    AnswerContains,
    AnswerMatches,
    NoErrors,
    NoSafetyBlocks,
    Observation,
    TokensWithin,
    ToolArgsSubset,
    ToolCalled,
    ToolNotCalled,
    ToolSequence,
)
from frok.telemetry import SPAN_END, Event
from frok.tools.orchestrator import ToolInvocation


def _chat_span(*, total_tokens=10, error=None, safety_blocked=None, duration_ms=4.0):
    data = {"total_tokens": total_tokens}
    if safety_blocked is not None:
        data["safety_blocked"] = safety_blocked
    return Event(
        ts=0.0,
        trace_id="t",
        span_id="s",
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=duration_ms,
        data=data,
        error=error,
    )


def _obs(
    *,
    answer="",
    invocations=None,
    events=None,
    error=None,
):
    resp = GrokResponse(model="grok-4", content=answer, raw={}) if answer != "" else GrokResponse(model="grok-4", content="", raw={})
    if answer == "" and error is None:
        resp = None  # simulate "run failed"
    return Observation(
        final_response=resp,
        messages=[],
        invocations=list(invocations or []),
        events=list(events or []),
        error=error,
    )


# ---------------------------------------------------------------------------
# answer scorers
# ---------------------------------------------------------------------------
def test_answer_contains_case_insensitive_by_default():
    obs = _obs(answer="The answer is 42.")
    s = AnswerContains("FORTY-TWO")
    assert s(None, obs).passed is False
    s2 = AnswerContains("42")
    assert s2(None, obs).passed is True


def test_answer_contains_case_sensitive_opt_in():
    obs = _obs(answer="Hello")
    assert AnswerContains("hello", case_sensitive=True)(None, obs).passed is False
    assert AnswerContains("Hello", case_sensitive=True)(None, obs).passed is True


def test_answer_matches_regex():
    obs = _obs(answer="price is $3.14 per unit")
    assert AnswerMatches(r"\$\d+\.\d+")(None, obs).passed is True
    assert AnswerMatches(r"^free$")(None, obs).passed is False


def test_answer_absent_blocks_known_wrong_answer():
    obs = _obs(answer="The answer is probably 41.")
    s = AnswerAbsent("41")
    assert s(None, obs).passed is False
    assert AnswerAbsent("43")(None, obs).passed is True


def test_no_safety_blocks_reads_chat_spans():
    clean = _obs(events=[_chat_span()])
    blocked = _obs(events=[_chat_span(safety_blocked="prompt")])
    assert NoSafetyBlocks()(None, clean).passed is True
    res = NoSafetyBlocks()(None, blocked)
    assert res.passed is False
    assert "prompt" in res.detail


# ---------------------------------------------------------------------------
# tool scorers
# ---------------------------------------------------------------------------
def _inv(name, **args):
    return ToolInvocation(call_id="c", name=name, arguments=dict(args), result="r")


def test_tool_called_and_counts():
    obs = _obs(invocations=[_inv("add"), _inv("add"), _inv("search")])
    assert ToolCalled("add")(None, obs).passed is True
    assert ToolCalled("add", times=2)(None, obs).passed is True
    s = ToolCalled("add", times=1)(None, obs)
    assert s.passed is False and s.measure == 2
    assert ToolCalled("missing")(None, obs).passed is False


def test_tool_not_called_is_regression_guard():
    obs = _obs(invocations=[_inv("search")])
    assert ToolNotCalled("send_email")(None, obs).passed is True
    assert ToolNotCalled("search")(None, obs).passed is False


def test_tool_args_subset():
    obs = _obs(invocations=[_inv("add", a=1, b=2), _inv("add", a=3, b=4)])
    assert ToolArgsSubset("add", {"a": 3})(None, obs).passed is True
    assert ToolArgsSubset("add", {"a": 9})(None, obs).passed is False
    assert ToolArgsSubset("missing", {})(None, obs).passed is False


def test_tool_sequence_matches_prefix():
    obs = _obs(invocations=[_inv("a"), _inv("b"), _inv("c")])
    assert ToolSequence(("a", "b"))(None, obs).passed is True
    assert ToolSequence(("a", "c"))(None, obs).passed is False


# ---------------------------------------------------------------------------
# perf / trace
# ---------------------------------------------------------------------------
def test_tokens_within_budget():
    obs = _obs(events=[_chat_span(total_tokens=80), _chat_span(total_tokens=20)])
    assert TokensWithin(100)(None, obs).passed is True
    assert TokensWithin(99)(None, obs).passed is False


def test_no_errors_covers_run_and_spans():
    clean = _obs(events=[_chat_span()])
    with_span_err = _obs(events=[_chat_span(error="boom")])
    with_run_err = _obs(events=[_chat_span()], error="FooError: bar")
    assert NoErrors()(None, clean).passed is True
    assert NoErrors()(None, with_span_err).passed is False
    assert NoErrors()(None, with_run_err).passed is False
