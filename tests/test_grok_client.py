import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokError, GrokMessage, HttpError
from frok.safety import SafetyRuleSet


@dataclass
class StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": json.loads(body.decode("utf-8")),
                "timeout": timeout,
            }
        )
        status, payload = self.responses.pop(0)
        raw = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload).encode()
        return status, {}, raw


async def _noop_sleep(_s: float) -> None:
    return None


def _ok(content: str, *, model: str = "grok-4", prompt=11, completion=7):
    return (
        200,
        {
            "model": model,
            "choices": [{"message": {"role": "assistant", "content": content}}],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


async def test_chat_happy_path_tracks_usage():
    transport = StubTransport([_ok("Grok thinks deeply.")])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    resp = await client.chat([GrokMessage("user", "What is truth?")])
    assert resp.content == "Grok thinks deeply."
    assert resp.total_tokens == 18
    assert client.prompt_tokens_total == 11
    assert client.completion_tokens_total == 7
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer k"
    assert transport.calls[0]["url"].endswith("/chat/completions")


async def test_chat_requires_messages():
    client = GrokClient(api_key="k", transport=StubTransport([]), sleep=_noop_sleep)
    with pytest.raises(GrokError):
        await client.chat([])


async def test_chat_blocks_on_prompt_safety():
    transport = StubTransport([])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    with pytest.raises(GrokError, match="prompt blocked"):
        await client.chat([GrokMessage("user", "I can guarantee I am sentient.")])
    assert transport.calls == []  # never hit the network


async def test_chat_rewrites_prompt_before_send():
    transport = StubTransport([_ok("ok")])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    await client.chat([GrokMessage("user", "ping alice@example.com")])
    sent = transport.calls[0]["body"]["messages"][0]["content"]
    assert "alice@example.com" not in sent
    assert "[REDACTED_EMAIL]" in sent


async def test_chat_rewrites_response_output():
    transport = StubTransport([_ok("Great question! Here is the answer.")])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    resp = await client.chat([GrokMessage("user", "hello")])
    assert "Great question" not in resp.content


async def test_retries_on_500_then_succeeds():
    transport = StubTransport(
        [
            (500, {"error": "boom"}),
            (503, {"error": "still boom"}),
            _ok("recovered"),
        ]
    )
    client = GrokClient(
        api_key="k", transport=transport, sleep=_noop_sleep, max_retries=3
    )
    resp = await client.chat([GrokMessage("user", "hello")])
    assert resp.content == "recovered"
    assert len(transport.calls) == 3


async def test_no_retry_on_400():
    transport = StubTransport([(400, {"error": "bad"})])
    client = GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)
    with pytest.raises(HttpError) as exc:
        await client.chat([GrokMessage("user", "hello")])
    assert exc.value.status == 400
    assert len(transport.calls) == 1


async def test_custom_empty_ruleset_skips_safety():
    transport = StubTransport([_ok("Great question!")])
    client = GrokClient(
        api_key="k",
        transport=transport,
        sleep=_noop_sleep,
        safety=SafetyRuleSet(rules=()),
    )
    resp = await client.chat([GrokMessage("user", "I can guarantee anything.")])
    assert resp.content == "Great question!"


async def test_missing_transport_raises():
    client = GrokClient(api_key="k")  # no transport
    with pytest.raises(GrokError, match="no transport"):
        await client.chat([GrokMessage("user", "hi")])
