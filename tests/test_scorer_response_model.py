"""Tests for the ``ResponseModelIs`` scorer."""

import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.clients.grok import GrokResponse
from frok.evals import (
    AnswerContains,
    EvalCase,
    EvalRunner,
    Observation,
    ResponseModelIs,
)
from frok.telemetry import Tracer


# ---------------------------------------------------------------------------
# unit-level: scorer behavior against hand-built Observations
# ---------------------------------------------------------------------------
def _obs(*, model: str | None, error: str | None = None) -> Observation:
    if model is None and error is None:
        return Observation(
            final_response=None,
            messages=[],
            invocations=[],
            events=[],
        )
    return Observation(
        final_response=(
            GrokResponse(model=model or "", content="", raw={})
            if model is not None
            else None
        ),
        messages=[],
        invocations=[],
        events=[],
        error=error,
    )


def test_passes_when_response_model_matches_expected():
    score = ResponseModelIs("grok-4")(None, _obs(model="grok-4"))
    assert score.passed is True
    assert score.measure == "grok-4"


def test_fails_on_mismatch_surfaces_both_values_in_detail():
    score = ResponseModelIs("grok-4-fast")(None, _obs(model="grok-4"))
    assert score.passed is False
    # Both expected + actual visible for triage.
    assert "'grok-4-fast'" in score.detail
    assert "'grok-4'" in score.detail
    assert score.measure == "grok-4"


def test_fails_when_final_response_is_none():
    score = ResponseModelIs("grok-4")(None, _obs(model=None))
    assert score.passed is False
    assert "no final response" in score.detail
    assert score.measure is None


def test_fails_on_empty_model_string():
    # Server returned an empty model field — treat as mismatch, not pass.
    score = ResponseModelIs("grok-4")(None, _obs(model=""))
    assert score.passed is False


def test_scorer_name_reflects_expected_value():
    score = ResponseModelIs("grok-4-fast")(None, _obs(model="grok-4"))
    assert "response_model_is[" in score.name
    assert "grok-4-fast" in score.name


# ---------------------------------------------------------------------------
# integration: scorer runs inside EvalRunner with an overriding EvalCase.model
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


def _ok(text, *, model):
    return (
        200,
        {
            "model": model,
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        },
    )


async def test_scorer_passes_when_server_honours_pinned_model():
    transport = _StubTransport([_ok("ok", model="grok-4-fast")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            model="grok-4",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="pinned",
        messages=[GrokMessage("user", "hi")],
        model="grok-4-fast",
        scorers=[AnswerContains("ok"), ResponseModelIs("grok-4-fast")],
    )
    result = await EvalRunner(client_factory=factory).run_case(case)
    assert result.passed


async def test_scorer_fails_on_silent_provider_model_swap():
    # Request goes out with model=grok-4-fast but the server echoes a
    # different model — precisely what the scorer is meant to catch.
    transport = _StubTransport([_ok("ok", model="grok-4-STALE")])

    def factory(_sink):
        return GrokClient(
            api_key="k",
            model="grok-4",
            transport=transport,
            sleep=_noop_sleep,
            tracer=Tracer(),
        )

    case = EvalCase(
        name="silent-swap",
        messages=[GrokMessage("user", "hi")],
        model="grok-4-fast",
        scorers=[ResponseModelIs("grok-4-fast")],
    )
    result = await EvalRunner(client_factory=factory).run_case(case)
    assert not result.passed
    failed = [s for s in result.scores if not s.passed]
    assert len(failed) == 1
    assert "'grok-4-STALE'" in failed[0].detail
