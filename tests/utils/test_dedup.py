from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from src.utils.dedup import Deduplicator


@pytest.fixture
def dedup(tmp_path):
    db_path = str(tmp_path / "test.db")
    d = Deduplicator(db_path)
    yield d
    d.close()


class TestURLDedup:
    def test_new_url_not_duplicate(self, dedup):
        assert dedup.is_duplicate("https://example.com/new") is False

    def test_registered_url_is_duplicate(self, dedup):
        dedup.register("https://example.com/a")
        assert dedup.is_duplicate("https://example.com/a") is True

    def test_different_url_not_duplicate(self, dedup):
        dedup.register("https://example.com/a")
        assert dedup.is_duplicate("https://example.com/b") is False

    def test_url_hash_deterministic(self, dedup):
        h1 = dedup._url_hash("https://example.com/test")
        h2 = dedup._url_hash("https://example.com/test")
        assert h1 == h2


class TestTitleDedup:
    def test_similar_title_is_duplicate(self, dedup):
        dedup.register("https://example.com/a", "美联储维持利率不变")
        assert dedup.is_duplicate("https://example.com/b", "美联储维持利率不变，符合预期") is True

    def test_different_title_not_duplicate(self, dedup):
        dedup.register("https://example.com/a", "美联储维持利率")
        assert dedup.is_duplicate("https://example.com/b", "GPT-5 发布") is False

    def test_empty_title_skips_title_match(self, dedup):
        dedup.register("https://example.com/a", "Some Title")
        assert dedup.is_duplicate("https://example.com/new", "") is False

    def test_different_url_similar_title(self, dedup):
        dedup.register("https://site-a.com/article", "央行宣布降息25个基点")
        assert dedup.is_duplicate("https://site-b.com/article", "央行宣布降息25个基点，市场反应积极") is True


class TestRegister:
    def test_register_single(self, dedup):
        dedup.register("https://example.com/a", "Title A")
        assert dedup.is_duplicate("https://example.com/a") is True

    def test_register_batch(self, dedup):
        items = [
            ("https://example.com/1", "Title 1"),
            ("https://example.com/2", "Title 2"),
            ("https://example.com/3", "Title 3"),
            ("https://example.com/4", "Title 4"),
            ("https://example.com/5", "Title 5"),
        ]
        dedup.register_batch(items)
        for url, _ in items:
            assert dedup.is_duplicate(url) is True

    def test_duplicate_register_idempotent(self, dedup):
        dedup.register("https://example.com/a")
        dedup.register("https://example.com/a")
        # 数据库中应只有一条
        count = dedup._conn.execute("SELECT COUNT(*) FROM fingerprints").fetchone()[0]
        assert count == 1


class TestEdgeCases:
    def test_empty_url(self, dedup):
        assert dedup.is_duplicate("") is False

    def test_auto_create_table(self, tmp_path):
        db_path = str(tmp_path / "fresh.db")
        d = Deduplicator(db_path)
        # 表应该已自动创建
        row = d._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='fingerprints'"
        ).fetchone()
        assert row is not None
        d.close()

    def test_large_dataset_performance(self, dedup):
        items = [(f"https://example.com/{i}", f"Title {i}") for i in range(10000)]
        dedup.register_batch(items)
        # 查询应该很快
        assert dedup.is_duplicate("https://example.com/9999") is True
        assert dedup.is_duplicate("https://example.com/99999") is False
