import json

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.evals import (
    AnswerAbsent,
    AnswerContains,
    EvalCase,
    EvalRunner,
    NoErrors,
    NoSafetyBlocks,
    TokensWithin,
    ToolCalled,
    ToolSequence,
)
from frok.telemetry import Tracer
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


# ---------------------------------------------------------------------------
# no-tools path
# ---------------------------------------------------------------------------
async def test_runner_chat_only_case_passes():
    transport = StubTransport([final_msg("The answer is 42.", prompt=11, completion=7)])
    case = EvalCase(
        name="arithmetic",
        messages=[GrokMessage("user", "what is 2+40?")],
        scorers=[
            AnswerContains("42"),
            AnswerAbsent("41"),
            NoErrors(),
            TokensWithin(50),
        ],
    )
    runner = EvalRunner(client_factory=_factory(transport))
    report = await runner.run([case])
    assert report.passed == 1 and report.failed == 0
    r = report.results[0]
    assert r.passed
    assert r.observation.total_tokens == 18
    assert [s.passed for s in r.scores] == [True, True, True, True]


async def test_runner_chat_only_case_fails_on_wrong_answer():
    transport = StubTransport([final_msg("It's 41, probably.")])
    case = EvalCase(
        name="bad-answer",
        messages=[GrokMessage("user", "what is 2+40?")],
        scorers=[AnswerContains("42"), AnswerAbsent("41")],
    )
    report = await EvalRunner(client_factory=_factory(transport)).run([case])
    r = report.results[0]
    assert not r.passed
    assert [s.name for s in r.failed_scores] == [
        "answer_contains['42']",
        "answer_absent['41']",
    ]


async def test_runner_records_run_error_when_client_raises():
    # Transport never hit because safety blocks on ingress.
    transport = StubTransport([])
    case = EvalCase(
        name="blocked",
        messages=[GrokMessage("user", "I can guarantee I am sentient.")],
        scorers=[NoSafetyBlocks(), AnswerContains("anything")],
    )
    report = await EvalRunner(client_factory=_factory(transport)).run([case])
    r = report.results[0]
    assert not r.passed
    assert r.observation.error is not None
    # Safety-block event is present on the chat span, so NoSafetyBlocks fires.
    assert any(s.name == "no_safety_blocks" and not s.passed for s in r.scores)


# ---------------------------------------------------------------------------
# tools path
# ---------------------------------------------------------------------------
async def test_runner_tool_case_covers_sequence_and_args():
    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    transport = StubTransport(
        [
            tool_call_msg([{"id": "c1", "name": "add", "args": {"a": 2, "b": 40}}]),
            final_msg("The answer is 42."),
        ]
    )
    case = EvalCase(
        name="tool-add",
        messages=[GrokMessage("user", "2+40?")],
        tools=[add],
        scorers=[
            AnswerContains("42"),
            ToolCalled("add", times=1),
            ToolSequence(("add",)),
            NoErrors(),
        ],
    )
    report = await EvalRunner(client_factory=_factory(transport)).run([case])
    r = report.results[0]
    assert r.passed, r.scores
    assert [i.name for i in r.observation.invocations] == ["add"]
    # Tool run produced a root tool.run span.
    assert r.observation.root_span is not None
    assert r.observation.root_span.name == "tool.run"


async def test_runner_handler_error_is_surfaced_not_fatal():
    @tool
    def boom() -> str:
        raise RuntimeError("nope")

    transport = StubTransport(
        [
            tool_call_msg([{"id": "c1", "name": "boom", "args": {}}]),
            final_msg("recovered"),
        ]
    )
    case = EvalCase(
        name="handler-error",
        messages=[GrokMessage("user", "go")],
        tools=[boom],
        scorers=[AnswerContains("recovered"), NoErrors()],
    )
    report = await EvalRunner(client_factory=_factory(transport)).run([case])
    r = report.results[0]
    # Answer is right but a span recorded the handler error → NoErrors fails.
    assert not r.passed
    names = [s.name for s in r.failed_scores]
    assert "no_errors" in names


# ---------------------------------------------------------------------------
# report rendering
# ---------------------------------------------------------------------------
async def test_report_markdown_and_summary_shape():
    transport = StubTransport(
        [final_msg("42"), final_msg("hello"), final_msg("goodbye")]
    )
    cases = [
        EvalCase(
            name="math",
            messages=[GrokMessage("user", "q1")],
            scorers=[AnswerContains("42")],
        ),
        EvalCase(
            name="greet",
            messages=[GrokMessage("user", "q2")],
            scorers=[AnswerContains("world")],  # will fail
        ),
        EvalCase(
            name="farewell",
            messages=[GrokMessage("user", "q3")],
            scorers=[AnswerContains("goodbye")],
        ),
    ]
    report = await EvalRunner(client_factory=_factory(transport)).run(cases)

    summary = report.to_summary()
    assert summary["passed"] == 2
    assert summary["failed"] == 1
    assert summary["total"] == 3
    assert {c["case"] for c in summary["cases"]} == {"math", "greet", "farewell"}

    md = report.to_markdown()
    assert "# Frok Eval Report" in md
    assert "| Case | Result" in md
    assert "PASS" in md and "FAIL" in md
    assert "## FAIL: greet" in md
