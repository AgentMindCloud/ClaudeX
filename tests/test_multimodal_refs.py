import base64

import pytest

from frok.multimodal import (
    AudioRef,
    ImageRef,
    MediaSource,
    detect_audio_format,
    detect_image_mime,
    to_data_url,
)


# ---------------------------------------------------------------------------
# encoding helpers
# ---------------------------------------------------------------------------
def test_detect_image_mime_by_extension():
    assert detect_image_mime(path="logo.PNG") == "image/png"
    assert detect_image_mime(path="pic.jpeg") == "image/jpeg"
    assert detect_image_mime(path="weird.xyz") == "application/octet-stream"
    # hint wins
    assert detect_image_mime(hint="image/webp", path="x.png") == "image/webp"


def test_detect_audio_format_by_extension():
    assert detect_audio_format(path="song.MP3") == "mp3"
    assert detect_audio_format(path="clip.wav") == "wav"
    assert detect_audio_format(path="mystery.bin") == "bin"
    assert detect_audio_format(hint="wav", path="x.mp3") == "wav"


def test_to_data_url_roundtrips_bytes():
    url = to_data_url(b"hello", "image/png")
    header, b64 = url.split(",", 1)
    assert header == "data:image/png;base64"
    assert base64.b64decode(b64) == b"hello"


# ---------------------------------------------------------------------------
# ImageRef
# ---------------------------------------------------------------------------
def test_image_from_url_content_part_is_plain_url():
    ref = ImageRef.from_url("https://x.ai/cat.png", alt_text="a cat")
    assert ref.source is MediaSource.URL
    part = ref.to_content_part()
    assert part == {"type": "image_url", "image_url": {"url": "https://x.ai/cat.png"}}
    assert "cat" in ref.describe()


def test_image_from_bytes_content_part_is_data_url():
    ref = ImageRef.from_bytes(b"PNGDATA", mime="image/png")
    assert ref.source is MediaSource.BYTES
    part = ref.to_content_part()
    url = part["image_url"]["url"]
    assert url.startswith("data:image/png;base64,")
    assert base64.b64decode(url.split(",", 1)[1]) == b"PNGDATA"
    assert ref.size_bytes() == len(b"PNGDATA")


def test_image_from_path_detects_mime_and_loads_bytes(tmp_path):
    p = tmp_path / "pic.png"
    p.write_bytes(b"\x89PNGDATA")
    ref = ImageRef.from_path(p, alt_text="the logo")
    assert ref.source is MediaSource.PATH
    assert ref.mime == "image/png"
    assert ref.size_bytes() == len(b"\x89PNGDATA")
    part = ref.to_content_part()
    assert part["image_url"]["url"].startswith("data:image/png;base64,")
    assert "logo" in ref.describe()


def test_image_bytes_requires_mime():
    with pytest.raises(ValueError):
        ImageRef.from_bytes(b"x", mime="")


def test_image_url_load_bytes_raises():
    with pytest.raises(ValueError, match="URL-backed"):
        ImageRef.from_url("https://x.ai/a.png").load_bytes()


# ---------------------------------------------------------------------------
# AudioRef
# ---------------------------------------------------------------------------
def test_audio_from_url_payload():
    ref = AudioRef.from_url("https://x.ai/clip.mp3", format="mp3")
    payload = ref.to_transcribe_payload()
    assert payload == {"audio": {"url": "https://x.ai/clip.mp3", "format": "mp3"}}


def test_audio_from_bytes_payload_is_base64():
    ref = AudioRef.from_bytes(b"WAVDATA", format="wav")
    payload = ref.to_transcribe_payload()
    assert payload["audio"]["format"] == "wav"
    assert base64.b64decode(payload["audio"]["data"]) == b"WAVDATA"


def test_audio_from_path_detects_format(tmp_path):
    p = tmp_path / "voice.wav"
    p.write_bytes(b"RIFFDATA")
    ref = AudioRef.from_path(p, alt_text="greeting")
    assert ref.format == "wav"
    assert ref.size_bytes() == len(b"RIFFDATA")
    assert "greeting" in ref.describe()
    payload = ref.to_transcribe_payload()
    assert base64.b64decode(payload["audio"]["data"]) == b"RIFFDATA"


def test_audio_bytes_requires_format():
    with pytest.raises(ValueError):
        AudioRef.from_bytes(b"x", format="")


def test_describe_fallback_uses_alt_text_first():
    ref = ImageRef.from_url("https://x/ai/a.png", alt_text="alt-xxx")
    assert ref.describe() == "[image: alt-xxx]"
