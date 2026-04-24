from datetime import datetime, timezone

import pytest

from frok.content import (
    MediaKind,
    extract_hashtags,
    extract_mentions,
    extract_urls,
    normalize_post,
    thread_from_posts,
)


def test_extractors_basic():
    text = "Hey @Alice and @bob, check #Grok and #frok: https://x.ai/post"
    assert extract_hashtags(text) == ("grok", "frok")
    assert extract_mentions(text) == ("alice", "bob")
    assert extract_urls(text) == ("https://x.ai/post",)


def test_extractors_ignore_emails_and_mid_word():
    assert extract_mentions("mail alice@example.com") == ()
    assert extract_hashtags("C#is a language") == ()


def test_normalize_v2_payload_with_includes():
    payload = {
        "data": {
            "id": "1",
            "author_id": "42",
            "text": "Hello #world from @frok https://x.ai",
            "created_at": "2026-01-15T12:00:00Z",
            "lang": "en",
            "conversation_id": "1",
            "public_metrics": {"like_count": 10, "retweet_count": 2, "impression_count": 999},
            "entities": {
                "hashtags": [{"tag": "World"}],
                "mentions": [{"username": "Frok"}],
                "urls": [{"url": "t.co/x", "expanded_url": "https://x.ai"}],
            },
        },
        "includes": {
            "media": [
                {"media_key": "m2", "type": "video", "url": "https://v.ai/2"},
                {"media_key": "m1", "type": "photo", "url": "https://v.ai/1"},
            ]
        },
    }
    post = normalize_post(payload)
    assert post.id == "1"
    assert post.author_id == "42"
    assert post.lang == "en"
    assert post.hashtags == ("world",)
    assert post.mentions == ("frok",)
    assert post.urls == ("https://x.ai",)
    assert post.metrics["like_count"] == 10
    assert post.created_at == datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    # media stable-sorted by key
    assert [m.media_key for m in post.media] == ["m1", "m2"]
    assert post.media[1].kind is MediaKind.VIDEO


def test_normalize_falls_back_to_text_extraction_without_entities():
    payload = {
        "id": "7",
        "author_id": "1",
        "text": "read #frok https://x.ai @grok",
        "created_at": "2026-04-01T00:00:00+00:00",
    }
    post = normalize_post(payload)
    assert post.hashtags == ("frok",)
    assert post.mentions == ("grok",)
    assert post.urls == ("https://x.ai",)


def test_normalize_parses_numeric_and_datetime_timestamps():
    ts = datetime(2026, 4, 23, 10, 0, tzinfo=timezone.utc)
    p1 = normalize_post({"id": "1", "author_id": "1", "text": "", "created_at": ts})
    p2 = normalize_post(
        {"id": "2", "author_id": "1", "text": "", "created_at": ts.timestamp()}
    )
    assert p1.created_at == p2.created_at == ts


def test_normalize_rejects_missing_id():
    with pytest.raises(ValueError):
        normalize_post({"author_id": "1", "text": "", "created_at": "2026-01-01T00:00:00Z"})


def test_canonical_text_strips_zero_width():
    payload = {
        "id": "9",
        "author_id": "1",
        "text": "​hi‌ there﻿",
        "created_at": "2026-01-01T00:00:00Z",
    }
    post = normalize_post(payload)
    assert post.canonical_text() == "hi there"


def test_reply_detected_from_referenced_tweets():
    payload = {
        "data": {
            "id": "b",
            "author_id": "2",
            "text": "reply",
            "created_at": "2026-01-01T00:01:00Z",
            "conversation_id": "a",
            "referenced_tweets": [{"type": "replied_to", "id": "a"}],
        }
    }
    post = normalize_post(payload)
    assert post.reply_to_id == "a"
    assert post.conversation_id == "a"


def _mk(pid, reply_to=None, conv=None, minute=0):
    return normalize_post(
        {
            "id": pid,
            "author_id": "x",
            "text": f"post {pid}",
            "created_at": f"2026-01-01T00:{minute:02d}:00Z",
            "conversation_id": conv,
            "referenced_tweets": [{"type": "replied_to", "id": reply_to}] if reply_to else [],
        }
    )


def test_thread_groups_replies_and_sorts_chronologically():
    root = _mk("a", conv="a", minute=0)
    r1 = _mk("b", reply_to="a", conv="a", minute=1)
    r2 = _mk("c", reply_to="b", conv="a", minute=2)
    orphan = _mk("z", minute=5)
    threads = thread_from_posts([r2, orphan, r1, root])
    assert [[p.id for p in t] for t in threads] == [["a", "b", "c"], ["z"]]
