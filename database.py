"""
database.py — Async SQLite via aiosqlite
Stores per-chat settings and file caches.
"""

import json
import logging
from typing import Optional
import aiosqlite

from config import cfg

logger = logging.getLogger(__name__)

DB_PATH = cfg.db_path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_settings (
    chat_id     INTEGER PRIMARY KEY,
    captions    INTEGER NOT NULL DEFAULT 1,
    silent      INTEGER NOT NULL DEFAULT 0,
    nsfw        INTEGER NOT NULL DEFAULT 0,
    language    TEXT    NOT NULL DEFAULT 'en',
    album_limit INTEGER NOT NULL DEFAULT 10
);

CREATE TABLE IF NOT EXISTS file_cache (
    url_hash    TEXT PRIMARY KEY,
    file_id     TEXT NOT NULL,
    file_type   TEXT NOT NULL,
    created_at  REAL  NOT NULL DEFAULT (unixepoch('now'))
);

CREATE TABLE IF NOT EXISTS stats (
    key   TEXT PRIMARY KEY,
    value INTEGER NOT NULL DEFAULT 0
);
"""

# ─────────────────────────────────────────────────────────────────────────────
# Connection helper
# ─────────────────────────────────────────────────────────────────────────────

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.executescript(_SCHEMA)
    await db.commit()
    return db


# ─────────────────────────────────────────────────────────────────────────────
# Chat settings
# ─────────────────────────────────────────────────────────────────────────────

async def get_settings(chat_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript(_SCHEMA)
        async with db.execute(
            "SELECT * FROM chat_settings WHERE chat_id = ?", (chat_id,)
        ) as cur:
            row = await cur.fetchone()
    if row:
        return dict(row)
    # Return defaults
    return {
        "chat_id": chat_id,
        "captions": int(cfg.default_captions),
        "silent": int(cfg.default_silent),
        "nsfw": int(cfg.default_nsfw),
        "language": cfg.default_language,
        "album_limit": cfg.default_album_limit,
    }


async def save_settings(chat_id: int, **kwargs) -> None:
    current = await get_settings(chat_id)
    current.update(kwargs)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.execute(
            """
            INSERT INTO chat_settings (chat_id, captions, silent, nsfw, language, album_limit)
            VALUES (:chat_id, :captions, :silent, :nsfw, :language, :album_limit)
            ON CONFLICT(chat_id) DO UPDATE SET
                captions    = excluded.captions,
                silent      = excluded.silent,
                nsfw        = excluded.nsfw,
                language    = excluded.language,
                album_limit = excluded.album_limit
            """,
            current,
        )
        await db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# File cache  (avoid re-uploading the same file)
# ─────────────────────────────────────────────────────────────────────────────

import hashlib

def _hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def cache_get(url: str) -> Optional[dict]:
    if not cfg.caching:
        return None
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript(_SCHEMA)
        async with db.execute(
            "SELECT file_id, file_type FROM file_cache WHERE url_hash = ?",
            (_hash(url),),
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None


async def cache_set(url: str, file_id: str, file_type: str) -> None:
    if not cfg.caching:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.execute(
            """
            INSERT INTO file_cache (url_hash, file_id, file_type)
            VALUES (?, ?, ?)
            ON CONFLICT(url_hash) DO UPDATE SET file_id = excluded.file_id
            """,
            (_hash(url), file_id, file_type),
        )
        await db.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────────────────────────────────────

async def stat_inc(key: str, amount: int = 1) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.execute(
            """
            INSERT INTO stats (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = value + excluded.value
            """,
            (key, amount),
        )
        await db.commit()


async def stat_get(key: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript(_SCHEMA)
        async with db.execute("SELECT value FROM stats WHERE key = ?", (key,)) as cur:
            row = await cur.fetchone()
    return row["value"] if row else 0


async def stat_all() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript(_SCHEMA)
        async with db.execute("SELECT key, value FROM stats") as cur:
            rows = await cur.fetchall()
    return {r["key"]: r["value"] for r in rows}
