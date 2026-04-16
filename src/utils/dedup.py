from __future__ import annotations

import hashlib
import logging
import sqlite3
from datetime import datetime, timezone
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

TITLE_SIMILARITY_THRESHOLD = 0.85


class Deduplicator:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._ensure_table()

    def _ensure_table(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                url_hash TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_title ON fingerprints(title);
        """)

    def is_duplicate(self, url: str, title: str = "") -> bool:
        if not url:
            return False

        url_hash = self._url_hash(url)
        row = self._conn.execute(
            "SELECT 1 FROM fingerprints WHERE url_hash = ?", (url_hash,)
        ).fetchone()
        if row:
            return True

        if title:
            rows = self._conn.execute(
                "SELECT title FROM fingerprints WHERE title != ''"
            ).fetchall()
            for (existing_title,) in rows:
                if self._title_similarity(title, existing_title) > TITLE_SIMILARITY_THRESHOLD:
                    return True

        return False

    def register(self, url: str, title: str = "") -> None:
        if not url:
            return
        url_hash = self._url_hash(url)
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "INSERT OR IGNORE INTO fingerprints (url_hash, url, title, created_at) VALUES (?, ?, ?, ?)",
            (url_hash, url, title, now),
        )
        self._conn.commit()

    def register_batch(self, items: list[tuple[str, str]]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        rows = [
            (self._url_hash(url), url, title, now)
            for url, title in items
            if url
        ]
        self._conn.executemany(
            "INSERT OR IGNORE INTO fingerprints (url_hash, url, title, created_at) VALUES (?, ?, ?, ?)",
            rows,
        )
        self._conn.commit()

    def _url_hash(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    def _title_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def close(self) -> None:
        self._conn.close()
