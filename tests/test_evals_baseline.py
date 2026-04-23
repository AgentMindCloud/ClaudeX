import pytest

from frok.clients import GrokClient, GrokMessage
from frok.evals import (
    AnswerContains,
    EvalCase,
    EvalRunner,
    diff_against_baseline,
)
from frok.telemetry import JsonlSink, Tracer
from frok.tools import tool

from tests._eval_fixtures import StubTransport, final_msg, noop_sleep, tool_call_msg


def _factory(transport):
    def make(sink):
        return GrokClient(
            api_key="k",
            transport=transport,
            sleep=noop_sleep,
            tracer=Tracer(sink=sink),
        )

    return make


async def _capture_baseline(tmp_path, transport, case) -> str:
    """Run a case with a JsonlSink to produce a baseline trace file."""
    path = tmp_path / "baseline.jsonl"
    with JsonlSink(path) as sink:
        client = GrokClient(
            api_key="k", transport=transport, sleep=noop_sleep, tracer=Tracer(sink=sink)
        )

        def factory(_inmem_sink):
            return client  # reuse the same jsonl-sinked client

        runner = EvalRunner(client_factory=factory)
        await runner.run([case])
    return str(path)


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def _replay_transport():
    return StubTransport(
        [
            tool_call_msg([{"id": "c1", "name": "add", "args": {"a": 2, "b": 40}}]),
            final_msg("42", prompt=5, completion=1),
        ]
    )


async def test_baseline_match_no_regression(tmp_path):
    case = EvalCase(
        name="add",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[AnswerContains("42")],
    )
    baseline_path = await _capture_baseline(tmp_path, _replay_transport(), case)

    case_with_baseline = EvalCase(
        name="add",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[AnswerContains("42")],
        baseline=baseline_path,
    )
    report = await EvalRunner(client_factory=_factory(_replay_transport())).run(
        [case_with_baseline]
    )
    r = report.results[0]
    assert r.passed
    diff = r.baseline_diff
    assert diff is not None
    assert diff["tool_order_match"] is True
    assert diff["baseline_tools"] == diff["observed_tools"] == ["add"]
    assert diff["token_delta"] == 0
    assert diff["new_errors"] == 0
    assert diff["regressed"] is False


async def test_baseline_regresses_when_tool_order_diverges(tmp_path):
    """Baseline calls `add`; candidate doesn't call it — that's a regression."""
    baseline_case = EvalCase(
        name="add",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[AnswerContains("42")],
    )
    baseline_path = await _capture_baseline(
        tmp_path, _replay_transport(), baseline_case
    )

    # Candidate answers directly without calling the tool.
    candidate_transport = StubTransport([final_msg("42")])
    candidate_case = EvalCase(
        name="add",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[AnswerContains("42")],
        baseline=baseline_path,
    )
    report = await EvalRunner(client_factory=_factory(candidate_transport)).run(
        [candidate_case]
    )
    r = report.results[0]
    # Scorers pass, but baseline regresses on tool order → case fails overall.
    assert all(s.passed for s in r.scores)
    assert not r.passed
    assert r.baseline_diff["tool_order_match"] is False
    assert r.baseline_diff["regressed"] is True
    assert r.baseline_diff["baseline_tools"] == ["add"]
    assert r.baseline_diff["observed_tools"] == []


async def test_baseline_token_delta_alone_does_not_regress(tmp_path):
    baseline_case = EvalCase(
        name="chat",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hello")],
    )
    baseline_path = await _capture_baseline(
        tmp_path, StubTransport([final_msg("hello", prompt=5, completion=2)]), baseline_case
    )

    # Candidate uses *more* tokens for the same answer.
    heavier_transport = StubTransport([final_msg("hello", prompt=50, completion=20)])
    candidate_case = EvalCase(
        name="chat",
        messages=[GrokMessage("user", "hi")],
        scorers=[AnswerContains("hello")],
        baseline=baseline_path,
    )
    report = await EvalRunner(client_factory=_factory(heavier_transport)).run(
        [candidate_case]
    )
    r = report.results[0]
    assert r.passed
    assert r.baseline_diff["token_delta"] == 63
    assert r.baseline_diff["regressed"] is False


async def test_diff_against_missing_file_raises(tmp_path):
    from frok.evals import Observation

    with pytest.raises(FileNotFoundError):
        diff_against_baseline(
            Observation(final_response=None, messages=[], invocations=[], events=[]),
            tmp_path / "does-not-exist.jsonl",
        )
