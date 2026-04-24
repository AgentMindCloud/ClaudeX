"""Tests for ``EvalCase.timeout_s`` + runner wait_for wrapping."""

import asyncio
import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.evals import (
    AnswerContains,
    EvalCase,
    EvalRunner,
    NoErrors,
)
from frok.telemetry import Tracer


# ---------------------------------------------------------------------------
# shared stubs
# ---------------------------------------------------------------------------
@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


def _slow_transport(delay_s: float):
    async def transport(*, method, url, headers, body, timeout):
        await asyncio.sleep(delay_s)
        payload = {
            "model": "grok-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": "slow"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }
        return 200, {}, json.dumps(payload).encode("utf-8")

    return transport


async def _noop_sleep(_s):
    return None


def _ok(text="hi"):
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
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        },
    )


def _factory(transport):
    def make(sink):
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(sink=sink),
        )

    return make


# ---------------------------------------------------------------------------
# default (no timeout): no wait_for, existing behaviour preserved
# ---------------------------------------------------------------------------
async def test_default_case_has_no_timeout_wrapping():
    case = EvalCase(
        name="untimed",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hi")],
    )
    assert case.timeout_s is None
    transport = _StubTransport([_ok("hi there")])
    result = await EvalRunner(client_factory=_factory(transport)).run_case(case)
    assert result.passed
    assert result.observation.error is None


# ---------------------------------------------------------------------------
# generous timeout: run completes well under the cap
# ---------------------------------------------------------------------------
async def test_generous_timeout_still_passes():
    case = EvalCase(
        name="generous",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hi")],
        timeout_s=5.0,
    )
    transport = _StubTransport([_ok("hi there")])
    result = await EvalRunner(client_factory=_factory(transport)).run_case(case)
    assert result.passed
    assert result.observation.error is None


# ---------------------------------------------------------------------------
# tiny timeout + slow transport → TimeoutError observation.error
# ---------------------------------------------------------------------------
async def test_tiny_timeout_surfaces_timeout_error():
    case = EvalCase(
        name="too-slow",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hi")],
        timeout_s=0.05,
    )
    # Transport would take 2s; timeout at 50ms fires first.
    result = await EvalRunner(
        client_factory=_factory(_slow_transport(2.0))
    ).run_case(case)
    assert not result.passed
    assert result.observation.final_response is None
    assert result.observation.error is not None
    assert "TimeoutError" in result.observation.error
    assert "0.05" in result.observation.error


# ---------------------------------------------------------------------------
# timeout + scorers: NoErrors / content-based scorers see the error
# ---------------------------------------------------------------------------
async def test_timeout_causes_noerrors_to_fail():
    case = EvalCase(
        name="timeout-ne",
        messages=[GrokMessage("user", "hi")],
        scorers=[NoErrors()],
        timeout_s=0.05,
    )
    result = await EvalRunner(
        client_factory=_factory(_slow_transport(2.0))
    ).run_case(case)
    assert not result.passed
    failed = [s for s in result.scores if not s.passed]
    assert any(s.name == "no_errors" for s in failed)
    # NoErrors surfaces the run-level error in its detail.
    ne = next(s for s in failed if s.name == "no_errors")
    assert "TimeoutError" in ne.detail


async def test_timeout_causes_answer_scorers_to_see_empty_answer():
    case = EvalCase(
        name="timeout-content",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("anything")],
        timeout_s=0.05,
    )
    result = await EvalRunner(
        client_factory=_factory(_slow_transport(2.0))
    ).run_case(case)
    assert not result.passed
    # AnswerContains fails because obs.answer is "" when final_response is None.
    failed = [s for s in result.scores if not s.passed]
    assert len(failed) == 1


# ---------------------------------------------------------------------------
# preserves partial events (grok.chat span was opened before the cancel)
# ---------------------------------------------------------------------------
async def test_timeout_preserves_partial_events_from_sink():
    case = EvalCase(
        name="partial-events",
        messages=[GrokMessage("user", "hi")],
        scorers=[],
        timeout_s=0.05,
    )
    result = await EvalRunner(
        client_factory=_factory(_slow_transport(2.0))
    ).run_case(case)
    # The grok.chat span opened (start) and then closed during cancellation
    # unwinding, so the sink caught at least a span.start + span.end pair.
    events = result.observation.events
    names = {e.name for e in events}
    assert "grok.chat" in names
    # And the closing span has an error recorded (cancellation / timeout).
    span_ends = [e for e in events if e.kind == "span.end" and e.name == "grok.chat"]
    assert len(span_ends) == 1
    assert span_ends[0].error is not None


# ---------------------------------------------------------------------------
# timeout composes with repeats: each repeat gets its own timeout budget
# ---------------------------------------------------------------------------
async def test_timeout_applied_per_repeat_not_per_suite():
    case = EvalCase(
        name="per-repeat",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hi")],
        timeout_s=5.0,
    )
    # Two fast responses, one per repeat — cumulative time << 5s each.
    transport = _StubTransport([_ok("hi"), _ok("hi")])
    report = await EvalRunner(client_factory=_factory(transport)).run(
        [case], repeats=2
    )
    # Both repeats complete normally.
    assert all(r.passed for r in report.results)
    assert len(report.results) == 2


# ---------------------------------------------------------------------------
# zero / negative timeout behaviour
# ---------------------------------------------------------------------------
async def test_zero_timeout_fires_immediately():
    # asyncio.wait_for with 0 raises TimeoutError immediately (the
    # coroutine may not even start). This is the correct contract —
    # operators asking for "0 seconds" are saying "don't run at all".
    case = EvalCase(
        name="zero",
        messages=[GrokMessage("user", "hi")],
        scorers=[NoErrors()],
        timeout_s=0.0,
    )
    transport = _StubTransport([_ok("hi")])
    result = await EvalRunner(client_factory=_factory(transport)).run_case(case)
    assert not result.passed
    assert "TimeoutError" in (result.observation.error or "")
