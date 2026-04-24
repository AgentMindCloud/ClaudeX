import base64
import json
from dataclasses import dataclass, field

import pytest

from frok.clients import GrokClient, GrokMessage
from frok.multimodal import (
    AdapterConfig,
    AudioRef,
    ImageRef,
    MultimodalAdapter,
    MultimodalError,
)


@dataclass
class StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(
            {
                "url": url,
                "body": json.loads(body.decode("utf-8")),
                "headers": dict(headers),
            }
        )
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(content, *, prompt=5, completion=3):
    return (
        200,
        {
            "model": "grok-4-vision",
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


def _transcript(text):
    return (200, {"text": text})


def _client(transport):
    return GrokClient(api_key="k", transport=transport, sleep=_noop_sleep)


# ---------------------------------------------------------------------------
# happy path: vision chat uses image_url content part
# ---------------------------------------------------------------------------
async def test_describe_image_sends_image_content_part():
    transport = StubTransport([_final("A cat on a red couch.")])
    adapter = MultimodalAdapter(client=_client(transport))
    img = ImageRef.from_bytes(b"PNGDATA", mime="image/png")
    resp = await adapter.describe_image(img, prompt="What is this?")
    assert resp.content == "A cat on a red couch."

    sent = transport.calls[0]["body"]["messages"][0]
    assert sent["role"] == "user"
    assert isinstance(sent["content"], list)
    parts = sent["content"]
    assert parts[0] == {"type": "text", "text": "What is this?"}
    assert parts[1]["type"] == "image_url"
    data_url = parts[1]["image_url"]["url"]
    assert data_url.startswith("data:image/png;base64,")
    assert base64.b64decode(data_url.split(",", 1)[1]) == b"PNGDATA"


async def test_chat_accepts_mixed_parts_including_url_image():
    transport = StubTransport([_final("ack")])
    adapter = MultimodalAdapter(client=_client(transport))
    img = ImageRef.from_url("https://x.ai/frok.png")
    await adapter.chat(["Compare these:", img, "and tell me which is better."])
    parts = transport.calls[0]["body"]["messages"][0]["content"]
    assert [p["type"] for p in parts] == ["text", "image_url", "text"]
    assert parts[1]["image_url"]["url"] == "https://x.ai/frok.png"


# ---------------------------------------------------------------------------
# fallback: vision disabled → image becomes text descriptor
# ---------------------------------------------------------------------------
async def test_vision_disabled_falls_back_to_descriptor():
    transport = StubTransport([_final("I cannot see the image but...")])
    adapter = MultimodalAdapter(
        client=_client(transport),
        config=AdapterConfig(vision_enabled=False),
    )
    img = ImageRef.from_url("https://x.ai/thing.png", alt_text="a red thing")
    await adapter.describe_image(img, prompt="Describe the thing.")
    parts = transport.calls[0]["body"]["messages"][0]["content"]
    # No image_url parts at all — only safety-padded text parts.
    assert all(p["type"] == "text" for p in parts)
    combined = " ".join(p["text"] for p in parts)
    assert "image unavailable" in combined
    assert "red thing" in combined


# ---------------------------------------------------------------------------
# audio: voice enabled → transcribe endpoint; disabled → descriptor
# ---------------------------------------------------------------------------
async def test_voice_enabled_routes_to_transcribe_endpoint():
    transport = StubTransport(
        [
            _transcript("the quick brown fox"),
            _final("Sure, I see it."),
        ]
    )
    adapter = MultimodalAdapter(
        client=_client(transport),
        config=AdapterConfig(voice_enabled=True, voice_model="grok-voice"),
    )
    audio = AudioRef.from_bytes(b"WAVDATA", format="wav")
    await adapter.chat(["Summarize:", audio])

    transcribe_call = transport.calls[0]
    assert transcribe_call["url"].endswith("/audio/transcriptions")
    assert transcribe_call["body"]["model"] == "grok-voice"
    audio_part = transcribe_call["body"]["audio"]
    assert audio_part["format"] == "wav"
    assert base64.b64decode(audio_part["data"]) == b"WAVDATA"

    chat_call = transport.calls[1]
    parts = chat_call["body"]["messages"][0]["content"]
    combined = " ".join(p["text"] for p in parts if p["type"] == "text")
    assert "[audio transcript] the quick brown fox" in combined
    assert all(p["type"] == "text" for p in parts)


async def test_voice_disabled_falls_back_to_audio_descriptor(tmp_path):
    transport = StubTransport([_final("acknowledged")])
    adapter = MultimodalAdapter(client=_client(transport))  # voice_enabled=False
    path = tmp_path / "clip.mp3"
    path.write_bytes(b"MP3DATA")
    audio = AudioRef.from_path(path, alt_text="greeting clip")
    await adapter.chat(["What is this?", audio])

    # Only one request — no transcribe hop.
    assert len(transport.calls) == 1
    parts = transport.calls[0]["body"]["messages"][0]["content"]
    combined = " ".join(p["text"] for p in parts)
    assert "audio unavailable" in combined
    assert "greeting clip" in combined


async def test_transcribe_audio_standalone_returns_text():
    transport = StubTransport([_transcript("hello world")])
    adapter = MultimodalAdapter(
        client=_client(transport),
        config=AdapterConfig(voice_enabled=True),
    )
    audio = AudioRef.from_url("https://x.ai/clip.mp3", format="mp3")
    assert await adapter.transcribe_audio(audio) == "hello world"


async def test_transcribe_audio_disabled_returns_descriptor():
    transport = StubTransport([])
    adapter = MultimodalAdapter(client=_client(transport))
    audio = AudioRef.from_url("https://x.ai/clip.mp3", format="mp3", alt_text="clip")
    out = await adapter.transcribe_audio(audio)
    assert "clip" in out
    assert transport.calls == []


async def test_transcribe_audio_missing_text_raises():
    transport = StubTransport([(200, {"oops": "no text"})])
    adapter = MultimodalAdapter(
        client=_client(transport),
        config=AdapterConfig(voice_enabled=True),
    )
    audio = AudioRef.from_url("https://x.ai/clip.mp3", format="mp3")
    with pytest.raises(MultimodalError, match="no text"):
        await adapter.transcribe_audio(audio)


# ---------------------------------------------------------------------------
# safety still applies to text parts only
# ---------------------------------------------------------------------------
async def test_safety_rewrites_text_parts_but_leaves_images_alone():
    transport = StubTransport([_final("ok")])
    adapter = MultimodalAdapter(client=_client(transport))
    img = ImageRef.from_bytes(b"PNGDATA", mime="image/png")
    await adapter.chat(["email me at alice@example.com", img])

    parts = transport.calls[0]["body"]["messages"][0]["content"]
    text_parts = [p for p in parts if p["type"] == "text"]
    image_parts = [p for p in parts if p["type"] == "image_url"]
    assert "alice@example.com" not in text_parts[0]["text"]
    assert "[REDACTED_EMAIL]" in text_parts[0]["text"]
    # Image part untouched.
    assert image_parts[0]["image_url"]["url"].startswith("data:image/png;base64,")


async def test_safety_block_on_text_part_raises_before_network():
    transport = StubTransport([])
    adapter = MultimodalAdapter(client=_client(transport))
    img = ImageRef.from_bytes(b"PNGDATA", mime="image/png")
    with pytest.raises(Exception, match="prompt blocked"):
        await adapter.chat(["I can guarantee anything", img])
    assert transport.calls == []


async def test_empty_parts_list_raises():
    adapter = MultimodalAdapter(client=_client(StubTransport([])))
    with pytest.raises(MultimodalError):
        await adapter.chat([])


async def test_unsupported_part_type_raises():
    adapter = MultimodalAdapter(client=_client(StubTransport([])))
    with pytest.raises(MultimodalError, match="unsupported part type"):
        await adapter.chat([42])  # type: ignore[list-item]
