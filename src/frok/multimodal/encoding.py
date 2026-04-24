"""Encoding helpers for multimodal media refs: MIME detection + base64.

Zero deps. We keep the MIME tables small and focused on what xAI vision
and voice endpoints actually accept today; unknown extensions fall
through to ``application/octet-stream`` for images and ``bin`` for
audio — the caller can pass an explicit hint to override.
"""

from __future__ import annotations

import base64
from pathlib import Path

IMAGE_MIME: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}

AUDIO_FORMATS: dict[str, str] = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".m4a": "m4a",
    ".flac": "flac",
    ".ogg": "ogg",
    ".opus": "opus",
    ".webm": "webm",
}

DEFAULT_IMAGE_MIME = "application/octet-stream"
DEFAULT_AUDIO_FORMAT = "bin"


def detect_image_mime(
    *,
    hint: str | None = None,
    path: str | Path | None = None,
) -> str:
    if hint:
        return hint
    if path:
        return IMAGE_MIME.get(Path(path).suffix.lower(), DEFAULT_IMAGE_MIME)
    return DEFAULT_IMAGE_MIME


def detect_audio_format(
    *,
    hint: str | None = None,
    path: str | Path | None = None,
) -> str:
    if hint:
        return hint
    if path:
        return AUDIO_FORMATS.get(Path(path).suffix.lower(), DEFAULT_AUDIO_FORMAT)
    return DEFAULT_AUDIO_FORMAT


def to_data_url(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
