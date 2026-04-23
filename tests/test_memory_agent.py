import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.memory import HashEmbedder, MemoryAgent, MemoryStore


@dataclass
class StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        parsed = json.loads(body.decode("utf-8"))
        self.calls.append(parsed)
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


def _ok(content, *, prompt=5, completion=3):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [{"message": {"role": "assistant", "content": content}}],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


async def _noop_sleep(_s):
    return None


@pytest.fixture
def agent(tmp_path):
    transport = StubTransport([])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    store = MemoryStore(tmp_path / "agent.db", HashEmbedder(dim=128))
    try:
        yield MemoryAgent(client=client, store=store, min_score=0.0), client, store, transport
    finally:
        store.close()


async def test_first_turn_has_no_recall_context(agent):
    a, _c, store, transport = agent
    transport.responses.append(_ok("hello back"))
    resp = await a.chat("hello Grok")
    assert resp.content == "hello back"
    # Only the user turn goes out; no recall system message on first call.
    sent = transport.calls[0]["messages"]
    assert [m["role"] for m in sent] == ["user"]
    # Both turns stored.
    assert await store.count(kind="user_message") == 1
    assert await store.count(kind="assistant_message") == 1


async def test_second_turn_injects_recall(agent):
    a, _c, _s, transport = agent
    transport.responses.extend([
        _ok("Grok is an AI built by xAI."),
        _ok("It focuses on truth-seeking and wit."),
    ])
    await a.chat("tell me about Grok")
    await a.chat("what else about Grok")

    sent2 = transport.calls[1]["messages"]
    roles = [m["role"] for m in sent2]
    assert roles[0] == "system"  # recall block injected
    assert "Relevant prior context" in sent2[0]["content"]
    assert "Grok is an AI built by xAI." in sent2[0]["content"]
    assert roles[-1] == "user"


async def test_pii_in_user_text_is_sanitized_before_storage(agent):
    a, _c, store, transport = agent
    transport.responses.append(_ok("acknowledged"))
    await a.chat("please email alice@example.com with the draft")
    stored = await store.recent(kind="user_message")
    assert "alice@example.com" not in stored[0].content
    assert "[REDACTED_EMAIL]" in stored[0].content
    # Same sanitized text went over the wire.
    sent_user = transport.calls[0]["messages"][-1]["content"]
    assert "alice@example.com" not in sent_user


async def test_blocked_prompt_does_not_get_stored(agent):
    a, _c, store, transport = agent
    with pytest.raises(Exception):
        await a.chat("I can guarantee I am sentient")
    # Neither user nor assistant turn landed in the store.
    assert await store.count() == 0
    # And we never hit the transport.
    assert transport.calls == []


async def test_system_prompt_is_prepended(agent):
    a, _c, _s, transport = agent
    a.system_prompt = "You are Frok, maximally truthful."
    transport.responses.append(_ok("hi"))
    await a.chat("hello")
    msgs = transport.calls[0]["messages"]
    assert msgs[0]["role"] == "system"
    assert msgs[0]["content"] == "You are Frok, maximally truthful."
