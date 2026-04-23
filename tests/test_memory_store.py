from datetime import datetime, timedelta, timezone

import pytest

from frok.memory import HashEmbedder, MemoryStore


@pytest.fixture
def store(tmp_path):
    s = MemoryStore(tmp_path / "m.db", HashEmbedder(dim=128))
    try:
        yield s
    finally:
        s.close()


async def test_remember_and_recall_roundtrip(store):
    rec = await store.remember("Grok prioritises truth over flattery.")
    assert rec.id > 0
    assert await store.count() == 1
    hits = await store.recall("truth seeking in Grok")
    assert len(hits) == 1
    assert hits[0].id == rec.id
    assert hits[0].score is not None and hits[0].score > 0.0


async def test_recall_ranks_by_similarity(store):
    await store.remember("the capital of France is Paris")
    target = await store.remember("Grok integrates with the X platform for real-time posts")
    await store.remember("rye flour produces a denser sourdough")
    hits = await store.recall("real-time X integration for Grok", k=2)
    assert hits[0].id == target.id
    # scores are sorted descending
    scores = [h.score for h in hits]
    assert scores == sorted(scores, reverse=True)


async def test_kind_filter(store):
    await store.remember("user asked about xAI", kind="user_message")
    a = await store.remember("assistant replied about xAI", kind="assistant_message")
    hits = await store.recall("xAI", kind="assistant_message")
    assert [h.id for h in hits] == [a.id]


async def test_time_filter(store):
    old = datetime(2026, 1, 1, tzinfo=timezone.utc)
    new = datetime(2026, 4, 1, tzinfo=timezone.utc)
    await store.remember("old memory about grok", at=old)
    new_rec = await store.remember("new memory about grok", at=new)
    hits = await store.recall("grok", since=datetime(2026, 3, 1, tzinfo=timezone.utc))
    assert [h.id for h in hits] == [new_rec.id]


async def test_min_score_filter_excludes_unrelated(store):
    await store.remember("quantum chromodynamics lecture notes")
    hits = await store.recall("sourdough starter maintenance", min_score=0.5)
    assert hits == []


async def test_recent_returns_newest_first(store):
    t0 = datetime.now(timezone.utc)
    await store.remember("first", at=t0)
    await store.remember("second", at=t0 + timedelta(seconds=1))
    await store.remember("third", at=t0 + timedelta(seconds=2))
    recent = await store.recent(k=2)
    assert [r.content for r in recent] == ["third", "second"]


async def test_forget(store):
    rec = await store.remember("to be forgotten")
    assert await store.forget(rec.id) is True
    assert await store.forget(rec.id) is False
    assert await store.count() == 0


async def test_remember_many(store):
    recs = await store.remember_many(
        [("alpha note", {"src": "a"}), ("beta note", None)],
        kind="fact",
    )
    assert [r.content for r in recs] == ["alpha note", "beta note"]
    assert recs[0].metadata == {"src": "a"}
    assert await store.count(kind="fact") == 2


async def test_persists_across_reopen(tmp_path):
    emb = HashEmbedder(dim=64)
    path = tmp_path / "persist.db"
    with MemoryStore(path, emb) as s:
        await s.remember("xAI Grok persistent memory works")
    with MemoryStore(path, emb) as s2:
        hits = await s2.recall("persistent memory")
        assert len(hits) == 1
        assert "persistent memory" in hits[0].content
