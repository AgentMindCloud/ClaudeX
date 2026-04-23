"""Embedder protocol + a deterministic zero-dependency fallback.

Real deployments plug in an xAI / Voyage / OpenAI embedder. The
`HashEmbedder` below is intentionally boring: stable feature hashing so
tests and offline smoke runs work without network calls, and so we have
a sane default that still produces meaningful cosine distances between
semantically overlapping strings (shared tokens → shared coordinates).
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    dim: int

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


_TOKEN_RE = re.compile(r"\w+")


@dataclass
class HashEmbedder:
    """Deterministic feature-hashing embedder. Zero deps, zero network.

    Tokens are lowercased word characters. Each token votes into one of
    `dim` buckets with a signed magnitude derived from a blake2b digest,
    and the final vector is L2-normalised. Similar text → overlapping
    buckets → higher cosine similarity. Collisions exist but are
    uncorrelated with content, so they add noise, not bias.
    """

    dim: int = 128
    seed: int = 0xC0FFEE

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        v = [0.0] * self.dim
        key = self.seed.to_bytes(8, "big", signed=False)
        for tok in _TOKEN_RE.findall(text.lower()):
            digest = hashlib.blake2b(tok.encode("utf-8"), digest_size=8, key=key).digest()
            h = int.from_bytes(digest, "big")
            idx = h % self.dim
            sign = 1.0 if (h >> 63) & 1 else -1.0
            v[idx] += sign
        norm = math.sqrt(sum(x * x for x in v))
        if norm == 0.0:
            return v
        return [x / norm for x in v]


def cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"dim mismatch: {len(a)} vs {len(b)}")
    num = sum(x * y for x, y in zip(a, b))
    # Both sides are expected to be (approximately) unit-length, but guard
    # against pathological zero-vectors from inputs with no tokens.
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return num / (na * nb)
