"""Typed references to image + audio media.

Three sources are supported per modality — path, bytes, URL — with
consistent factories. Refs are frozen dataclasses so they travel
safely between agent teams (§2 #6) without aliasing bugs.

`to_content_part()` yields the xAI / OpenAI-compatible chat content
part; `describe()` yields a short text fallback for when a modality is
disabled on the adapter.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .encoding import (
    DEFAULT_AUDIO_FORMAT,
    DEFAULT_IMAGE_MIME,
    b64,
    detect_audio_format,
    detect_image_mime,
    to_data_url,
)


class MediaSource(enum.Enum):
    URL = "url"
    BYTES = "bytes"
    PATH = "path"


@dataclass(frozen=True)
class ImageRef:
    source: MediaSource
    url: str | None = None
    data: bytes | None = None
    path: str | None = None
    mime: str = DEFAULT_IMAGE_MIME
    alt_text: str | None = None

    # -- factories ------------------------------------------------------
    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        mime: str | None = None,
        alt_text: str | None = None,
    ) -> "ImageRef":
        return cls(
            source=MediaSource.URL,
            url=url,
            mime=mime or DEFAULT_IMAGE_MIME,
            alt_text=alt_text,
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        mime: str,
        alt_text: str | None = None,
    ) -> "ImageRef":
        if not mime:
            raise ValueError("mime is required for bytes-backed images")
        return cls(source=MediaSource.BYTES, data=data, mime=mime, alt_text=alt_text)

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        mime: str | None = None,
        alt_text: str | None = None,
    ) -> "ImageRef":
        p = str(path)
        return cls(
            source=MediaSource.PATH,
            path=p,
            mime=detect_image_mime(hint=mime, path=p),
            alt_text=alt_text,
        )

    # -- conversions ----------------------------------------------------
    def load_bytes(self) -> bytes:
        if self.source is MediaSource.BYTES:
            assert self.data is not None
            return self.data
        if self.source is MediaSource.PATH:
            assert self.path is not None
            return Path(self.path).read_bytes()
        raise ValueError("URL-backed ImageRef has no local bytes; fetch it first")

    def size_bytes(self) -> int | None:
        if self.source is MediaSource.BYTES:
            return len(self.data or b"")
        if self.source is MediaSource.PATH and self.path:
            return Path(self.path).stat().st_size
        return None

    def to_content_part(self) -> dict[str, Any]:
        if self.source is MediaSource.URL:
            return {"type": "image_url", "image_url": {"url": self.url}}
        data = self.load_bytes()
        return {
            "type": "image_url",
            "image_url": {"url": to_data_url(data, self.mime)},
        }

    def describe(self) -> str:
        if self.alt_text:
            return f"[image: {self.alt_text}]"
        if self.source is MediaSource.URL:
            return f"[image at {self.url}]"
        if self.source is MediaSource.PATH:
            size = self.size_bytes()
            size_s = f", {size} bytes" if size is not None else ""
            return f"[image file {self.path} ({self.mime}{size_s})]"
        size = self.size_bytes() or 0
        return f"[image bytes ({self.mime}, {size} bytes)]"


@dataclass(frozen=True)
class AudioRef:
    source: MediaSource
    url: str | None = None
    data: bytes | None = None
    path: str | None = None
    format: str = DEFAULT_AUDIO_FORMAT
    alt_text: str | None = None

    # -- factories ------------------------------------------------------
    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        format: str | None = None,
        alt_text: str | None = None,
    ) -> "AudioRef":
        return cls(
            source=MediaSource.URL,
            url=url,
            format=format or DEFAULT_AUDIO_FORMAT,
            alt_text=alt_text,
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        format: str,
        alt_text: str | None = None,
    ) -> "AudioRef":
        if not format:
            raise ValueError("format is required for bytes-backed audio")
        return cls(
            source=MediaSource.BYTES, data=data, format=format, alt_text=alt_text
        )

    @classmethod
    def from_path(
        cls,
        path: str | Path,
        *,
        format: str | None = None,
        alt_text: str | None = None,
    ) -> "AudioRef":
        p = str(path)
        return cls(
            source=MediaSource.PATH,
            path=p,
            format=detect_audio_format(hint=format, path=p),
            alt_text=alt_text,
        )

    # -- conversions ----------------------------------------------------
    def load_bytes(self) -> bytes:
        if self.source is MediaSource.BYTES:
            assert self.data is not None
            return self.data
        if self.source is MediaSource.PATH:
            assert self.path is not None
            return Path(self.path).read_bytes()
        raise ValueError("URL-backed AudioRef has no local bytes; fetch it first")

    def size_bytes(self) -> int | None:
        if self.source is MediaSource.BYTES:
            return len(self.data or b"")
        if self.source is MediaSource.PATH and self.path:
            return Path(self.path).stat().st_size
        return None

    def to_transcribe_payload(self) -> dict[str, Any]:
        """Payload for the transcription endpoint."""
        if self.source is MediaSource.URL:
            return {"audio": {"url": self.url, "format": self.format}}
        return {
            "audio": {"data": b64(self.load_bytes()), "format": self.format}
        }

    def describe(self) -> str:
        if self.alt_text:
            return f"[audio: {self.alt_text}]"
        if self.source is MediaSource.URL:
            return f"[audio at {self.url} ({self.format})]"
        if self.source is MediaSource.PATH:
            size = self.size_bytes()
            size_s = f", {size} bytes" if size is not None else ""
            return f"[audio file {self.path} ({self.format}{size_s})]"
        size = self.size_bytes() or 0
        return f"[audio bytes ({self.format}, {size} bytes)]"
