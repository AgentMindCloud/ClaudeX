"""X-platform content ingestion.

Takes raw payloads (X API v2 shape, or arbitrary dicts from scrape/export)
and normalises them into a canonical `XPost` record that the rest of the
Frok stack can rely on:

  * deterministic ordering of media references
  * consistent timestamp (UTC, aware)
  * pre-extracted hashtags / mentions / urls (regardless of whether the
    source payload included an `entities` block)
  * threading helper that stitches replies into root-ordered lists

This module intentionally avoids any network I/O; callers hand it already-
fetched payloads.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


class MediaKind(enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    GIF = "animated_gif"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: str | None) -> "MediaKind":
        if not value:
            return cls.UNKNOWN
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


@dataclass(frozen=True)
class MediaRef:
    media_key: str
    kind: MediaKind
    url: str | None = None
    alt_text: str | None = None


@dataclass(frozen=True)
class XPost:
    id: str
    author_id: str
    text: str
    created_at: datetime
    lang: str | None = None
    reply_to_id: str | None = None
    conversation_id: str | None = None
    hashtags: tuple[str, ...] = ()
    mentions: tuple[str, ...] = ()
    urls: tuple[str, ...] = ()
    media: tuple[MediaRef, ...] = ()
    metrics: Mapping[str, int] = field(default_factory=dict)

    def canonical_text(self) -> str:
        """Text with surrounding whitespace and zero-width chars stripped."""
        return _CLEAN_RE.sub("", self.text).strip()


_HASHTAG_RE = re.compile(r"(?<![\w])#(\w{1,140})")
_MENTION_RE = re.compile(r"(?<![\w])@(\w{1,15})")
_URL_RE = re.compile(
    r"https?://[^\s<>\"']+", re.IGNORECASE
)
# zero-width / BOM / directional-marker chars we strip from canonical_text
_CLEAN_RE = re.compile("[​‌‍‎‏﻿]")


def extract_hashtags(text: str) -> tuple[str, ...]:
    return tuple(m.group(1).lower() for m in _HASHTAG_RE.finditer(text))


def extract_mentions(text: str) -> tuple[str, ...]:
    return tuple(m.group(1).lower() for m in _MENTION_RE.finditer(text))


def extract_urls(text: str) -> tuple[str, ...]:
    return tuple(m.group(0) for m in _URL_RE.finditer(text))


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        # X API v2 uses RFC 3339 with trailing 'Z'.
        v = value.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(v)
        except ValueError as exc:
            raise ValueError(f"unrecognised timestamp: {value!r}") from exc
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    raise ValueError(f"unrecognised timestamp: {value!r}")


def _parse_media(items: Iterable[Mapping[str, Any]] | None) -> tuple[MediaRef, ...]:
    if not items:
        return ()
    refs = [
        MediaRef(
            media_key=str(item.get("media_key") or item.get("id") or ""),
            kind=MediaKind.parse(item.get("type")),
            url=item.get("url") or item.get("preview_image_url"),
            alt_text=item.get("alt_text"),
        )
        for item in items
        if item
    ]
    # Stable: by media_key, then by kind.
    refs.sort(key=lambda r: (r.media_key, r.kind.value))
    return tuple(refs)


def normalize_post(payload: Mapping[str, Any]) -> XPost:
    """Normalise an arbitrary X post payload into an `XPost`.

    Accepts X API v2 shape (``data`` or a bare tweet object) and the looser
    shapes emitted by scrapers/exports. Unknown fields are ignored.
    """
    data = payload.get("data") if "data" in payload else payload
    if not isinstance(data, Mapping):
        raise ValueError("payload has no tweet object")

    tweet_id = data.get("id") or data.get("id_str")
    if not tweet_id:
        raise ValueError("payload missing id")
    text = data.get("text") or data.get("full_text") or ""
    author_id = str(data.get("author_id") or data.get("user_id") or "")
    created_at = _parse_timestamp(data.get("created_at"))

    entities = data.get("entities") or {}
    hashtags = (
        tuple(h.get("tag", "").lower() for h in entities.get("hashtags", []) if h.get("tag"))
        or extract_hashtags(text)
    )
    mentions = (
        tuple(
            (m.get("username") or m.get("screen_name") or "").lower()
            for m in entities.get("mentions", [])
            if m.get("username") or m.get("screen_name")
        )
        or extract_mentions(text)
    )
    urls = (
        tuple(u.get("expanded_url") or u.get("url") for u in entities.get("urls", []) if u.get("url") or u.get("expanded_url"))
        or extract_urls(text)
    )

    reply_to_id: str | None = None
    for ref in data.get("referenced_tweets") or []:
        if ref.get("type") == "replied_to":
            reply_to_id = str(ref.get("id"))
            break
    if reply_to_id is None:
        reply_to_id = data.get("in_reply_to_status_id_str") or data.get("in_reply_to_status_id")
        reply_to_id = str(reply_to_id) if reply_to_id else None

    metrics_raw = data.get("public_metrics") or {}
    metrics = {k: int(v) for k, v in metrics_raw.items() if isinstance(v, (int, float))}

    media_payload = (
        (payload.get("includes") or {}).get("media")
        if "includes" in payload
        else data.get("media") or (data.get("extended_entities") or {}).get("media")
    )

    return XPost(
        id=str(tweet_id),
        author_id=author_id,
        text=text,
        created_at=created_at,
        lang=data.get("lang"),
        reply_to_id=reply_to_id,
        conversation_id=str(data.get("conversation_id")) if data.get("conversation_id") else None,
        hashtags=tuple(h for h in hashtags if h),
        mentions=tuple(m for m in mentions if m),
        urls=tuple(u for u in urls if u),
        media=_parse_media(media_payload),
        metrics=metrics,
    )


def thread_from_posts(posts: Iterable[XPost]) -> list[list[XPost]]:
    """Group posts into threads, each sorted oldest → newest.

    A thread is the transitive closure of posts linked by ``reply_to_id``
    and ``conversation_id``. Orphan posts become singleton threads. The
    returned list is sorted by the earliest post in each thread.
    """
    by_id = {p.id: p for p in posts}
    # union-find on conversation_id || reply chain
    parent: dict[str, str] = {pid: pid for pid in by_id}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for p in by_id.values():
        if p.reply_to_id and p.reply_to_id in by_id:
            union(p.id, p.reply_to_id)
        if p.conversation_id and p.conversation_id in by_id:
            union(p.id, p.conversation_id)

    groups: dict[str, list[XPost]] = {}
    for p in by_id.values():
        groups.setdefault(find(p.id), []).append(p)
    threads = [sorted(g, key=lambda p: p.created_at) for g in groups.values()]
    threads.sort(key=lambda t: t[0].created_at)
    return threads
