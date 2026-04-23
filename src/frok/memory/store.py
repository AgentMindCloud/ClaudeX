"""SQLite-backed memory store with pluggable embeddings.

Small-scale design: embeddings live next to their row as a BLOB of
float32s; recall loads candidate rows (optionally filtered by kind and
time), computes cosine in Python, and returns the top-k. Fine for the
low-millions-of-rows single-agent case we care about in Phase 2; §2 #7
telemetry + a follow-up can swap in sqlite-vss / an ANN index behind the
same `MemoryStore` surface without changing callers.
"""

from __future__ import annotations

import json
import sqlite3
import struct
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .embedder import Embedder, cosine

DEFAULT_KIND = "episode"


@dataclass
class MemoryRecord:
    id: int
    kind: str
    content: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float | None = None  # populated by `recall()`


class MemoryStore:
    """Persistent memory keyed by id, with semantic recall."""

    def __init__(self, path: str | Path, embedder: Embedder):
        self.path = str(path)
        self.embedder = embedder
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._init_schema()

    # ------------------------------------------------------------------
    # schema
    # ------------------------------------------------------------------
    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding BLOB,
                    dim INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)"
            )

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "MemoryStore":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # writes
    # ------------------------------------------------------------------
    async def remember(
        self,
        content: str,
        *,
        kind: str = DEFAULT_KIND,
        metadata: dict[str, Any] | None = None,
        at: datetime | None = None,
        embed: bool = True,
    ) -> MemoryRecord:
        ts = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        emb: list[float] | None = None
        if embed:
            emb = (await self.embedder.embed([content]))[0]
        blob = _pack(emb) if emb is not None else None
        meta = dict(metadata or {})
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO memories(kind, content, created_at, metadata, embedding, dim) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (kind, content, ts.isoformat(), json.dumps(meta), blob, len(emb) if emb else 0),
            )
        return MemoryRecord(
            id=int(cur.lastrowid),
            kind=kind,
            content=content,
            created_at=ts,
            metadata=meta,
        )

    async def remember_many(
        self,
        items: Iterable[tuple[str, dict[str, Any] | None]],
        *,
        kind: str = DEFAULT_KIND,
    ) -> list[MemoryRecord]:
        pairs = list(items)
        if not pairs:
            return []
        contents = [c for c, _ in pairs]
        embs = await self.embedder.embed(contents)
        now = datetime.now(timezone.utc).isoformat()
        rows = [
            (kind, content, now, json.dumps(meta or {}), _pack(emb), len(emb))
            for (content, meta), emb in zip(pairs, embs)
        ]
        out: list[MemoryRecord] = []
        with self._conn:
            for row in rows:
                cur = self._conn.execute(
                    "INSERT INTO memories(kind, content, created_at, metadata, embedding, dim) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    row,
                )
                out.append(
                    MemoryRecord(
                        id=int(cur.lastrowid),
                        kind=row[0],
                        content=row[1],
                        created_at=datetime.fromisoformat(row[2]),
                        metadata=json.loads(row[3]),
                    )
                )
        return out

    async def forget(self, memory_id: int) -> bool:
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM memories WHERE id = ?", (memory_id,)
            )
        return cur.rowcount > 0

    # ------------------------------------------------------------------
    # reads
    # ------------------------------------------------------------------
    async def recall(
        self,
        query: str,
        *,
        k: int = 5,
        kind: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        min_score: float = -1.0,
    ) -> list[MemoryRecord]:
        q_emb = (await self.embedder.embed([query]))[0]
        where = ["embedding IS NOT NULL"]
        params: list[Any] = []
        if kind is not None:
            where.append("kind = ?")
            params.append(kind)
        if since is not None:
            where.append("created_at >= ?")
            params.append(since.astimezone(timezone.utc).isoformat())
        if until is not None:
            where.append("created_at <= ?")
            params.append(until.astimezone(timezone.utc).isoformat())
        sql = (
            "SELECT id, kind, content, created_at, metadata, embedding, dim "
            f"FROM memories WHERE {' AND '.join(where)}"
        )
        rows = self._conn.execute(sql, params).fetchall()
        scored: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            v = _unpack(row["embedding"], row["dim"])
            score = cosine(q_emb, v)
            if score >= min_score:
                scored.append((score, row))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [_row_to_record(r, score=s) for s, r in scored[:k]]

    async def recent(
        self, *, k: int = 10, kind: str | None = None
    ) -> list[MemoryRecord]:
        params: list[Any] = []
        where_sql = ""
        if kind is not None:
            where_sql = "WHERE kind = ?"
            params.append(kind)
        params.append(k)
        rows = self._conn.execute(
            f"SELECT id, kind, content, created_at, metadata "
            f"FROM memories {where_sql} ORDER BY created_at DESC, id DESC LIMIT ?",
            params,
        ).fetchall()
        return [_row_to_record(r) for r in rows]

    async def count(self, *, kind: str | None = None) -> int:
        if kind is None:
            row = self._conn.execute("SELECT COUNT(*) AS n FROM memories").fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM memories WHERE kind = ?", (kind,)
            ).fetchone()
        return int(row["n"])


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _pack(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _unpack(blob: bytes, dim: int) -> list[float]:
    return list(struct.unpack(f"{dim}f", blob))


def _row_to_record(row: sqlite3.Row, *, score: float | None = None) -> MemoryRecord:
    return MemoryRecord(
        id=int(row["id"]),
        kind=row["kind"],
        content=row["content"],
        created_at=datetime.fromisoformat(row["created_at"]),
        metadata=json.loads(row["metadata"]),
        score=score,
    )
