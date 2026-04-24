"""Composition tests: team runtime wrapping a real GrokClient."""

import json
from dataclasses import dataclass, field

from frok.clients import GrokClient
from frok.team import (
    TeamMessage,
    TeamRuntime,
    chat_role_from_client,
    pipeline_router,
)
from frok.telemetry import InMemorySink, Tracer


@dataclass
class StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _chat_ok(text, *, prompt=4, completion=2):
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


async def test_two_grok_backed_roles_share_trace_and_run_in_order():
    sink = InMemorySink()
    tracer = Tracer(sink=sink)
    transport = StubTransport([
        _chat_ok("researcher notes: xAI ships truth"),
        _chat_ok("writer draft: xAI ships truth, with wit"),
    ])
    client = GrokClient(
        api_key="k", transport=transport, sleep=_noop_sleep, tracer=tracer
    )

    researcher = chat_role_from_client(
        "researcher", client, system="Gather facts about xAI."
    )
    writer = chat_role_from_client(
        "writer", client, system="Turn facts into a tight tagline."
    )

    runtime = TeamRuntime(
        roles={"researcher": researcher, "writer": writer},
        router=pipeline_router(["researcher", "writer"]),
        tracer=tracer,
    )
    run = await runtime.run(
        TeamMessage(from_="user", to="researcher", content="what does xAI do?")
    )

    assert run.hops == 2
    assert run.final.from_ == "writer"
    assert "wit" in run.final.content

    # Writer's request includes the researcher's reply as a `user` turn, with
    # the [sender->recipient] prefix so the model sees the hand-off.
    writer_call = transport.calls[1]["messages"]
    as_texts = " ".join(m["content"] for m in writer_call)
    assert "[researcher->writer] researcher notes:" in as_texts

    # Telemetry tree: team.run -> team.hop -> grok.chat, all one trace.
    team_run = sink.spans(name="team.run")[0]
    hops = sink.spans(name="team.hop")
    chats = sink.spans(name="grok.chat")
    assert len(hops) == 2
    assert len(chats) == 2
    assert team_run.parent_span_id is None
    for h in hops:
        assert h.parent_span_id == team_run.span_id
        assert h.trace_id == team_run.trace_id
    for c in chats:
        assert c.trace_id == team_run.trace_id
        # chat spans nest under the hop that produced them
        assert c.parent_span_id in {h.span_id for h in hops}
