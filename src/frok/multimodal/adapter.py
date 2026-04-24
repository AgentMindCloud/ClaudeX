"""Multimodal IO adapter wrapping a `GrokClient`.

Takes heterogeneous parts — plain strings, `ImageRef`, `AudioRef` — and
routes them to the right Grok endpoint:

* Images → xAI `/chat/completions` with an `image_url` content part,
  transported through the normal safety / telemetry / retry path on
  `GrokClient.chat`.
* Audio → `/audio/transcriptions` (path configurable) via
  `GrokClient.request_json`; the transcript is then injected as a text
  part so the model still reasons over one flat conversation.

When a modality is disabled on `AdapterConfig`, the media is replaced
with a short text descriptor (`ImageRef.describe()` /
`AudioRef.describe()`) so the chat can proceed instead of blowing up.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence, Union

from ..clients.grok import GrokClient, GrokMessage, GrokResponse
from .refs import AudioRef, ImageRef

Part = Union[str, ImageRef, AudioRef]


@dataclass
class AdapterConfig:
    vision_enabled: bool = True
    voice_enabled: bool = False
    audio_transcribe_path: str = "/audio/transcriptions"
    voice_model: str | None = None
    vision_fallback_prefix: str = "(image unavailable, description follows)"
    audio_fallback_prefix: str = "(audio unavailable, description follows)"
    audio_transcript_prefix: str = "[audio transcript]"
    default_describe_prompt: str = "Describe this image in concrete detail."


class MultimodalError(RuntimeError):
    pass


@dataclass
class MultimodalAdapter:
    client: GrokClient
    config: AdapterConfig = field(default_factory=AdapterConfig)

    # ------------------------------------------------------------------
    # public surface
    # ------------------------------------------------------------------
    async def describe_image(
        self,
        image: ImageRef,
        *,
        prompt: str | None = None,
        system: str | None = None,
    ) -> GrokResponse:
        return await self.chat(
            [prompt or self.config.default_describe_prompt, image],
            system=system,
        )

    async def transcribe_audio(self, audio: AudioRef) -> str:
        """Transcribe via the voice endpoint. If voice is disabled on the
        config, returns a textual descriptor of the audio ref so callers
        always get *something* usable."""
        if not self.config.voice_enabled:
            return audio.describe()

        payload: dict[str, Any] = dict(audio.to_transcribe_payload())
        if self.config.voice_model:
            payload["model"] = self.config.voice_model
        raw = await self.client.request_json(
            self.config.audio_transcribe_path, payload
        )
        text = raw.get("text")
        if not isinstance(text, str):
            raise MultimodalError(
                f"voice endpoint returned no text: {raw!r}"
            )
        return text

    async def chat(
        self,
        parts: Sequence[Part],
        *,
        system: str | None = None,
    ) -> GrokResponse:
        content_parts = await self._build_parts(parts)

        messages: list[GrokMessage] = []
        if system:
            messages.append(GrokMessage("system", system))
        messages.append(
            GrokMessage(
                role="user",
                content="",
                parts=tuple(content_parts),
            )
        )
        return await self.client.chat(messages)

    # ------------------------------------------------------------------
    # internal assembly
    # ------------------------------------------------------------------
    async def _build_parts(self, parts: Sequence[Part]) -> list[dict[str, Any]]:
        if not parts:
            raise MultimodalError("at least one part is required")
        out: list[dict[str, Any]] = []
        for p in parts:
            if isinstance(p, str):
                if not p:
                    continue
                out.append({"type": "text", "text": p})
            elif isinstance(p, ImageRef):
                if self.config.vision_enabled:
                    out.append(p.to_content_part())
                else:
                    out.append(
                        {
                            "type": "text",
                            "text": f"{self.config.vision_fallback_prefix} {p.describe()}",
                        }
                    )
            elif isinstance(p, AudioRef):
                if self.config.voice_enabled:
                    transcript = await self.transcribe_audio(p)
                    out.append(
                        {
                            "type": "text",
                            "text": f"{self.config.audio_transcript_prefix} {transcript}",
                        }
                    )
                else:
                    out.append(
                        {
                            "type": "text",
                            "text": f"{self.config.audio_fallback_prefix} {p.describe()}",
                        }
                    )
            else:
                raise MultimodalError(
                    f"unsupported part type: {type(p).__name__}"
                )
        if not out:
            raise MultimodalError("no usable parts after assembly")
        return out
