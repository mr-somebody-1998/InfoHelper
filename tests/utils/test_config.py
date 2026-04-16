from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from src.utils.config import Config, ConfigError


@pytest.fixture
def config_dir(tmp_path):
    """创建临时配置目录"""
    config_yaml = tmp_path / "config.yaml"
    sources_yaml = tmp_path / "sources.yaml"
    return config_yaml, sources_yaml


def write_config(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def make_valid_config(config_path: Path, sources_path: Path, api_key: str = "test-key"):
    write_config(config_path, f"""
claude:
  api_key: {api_key}
  model: claude-sonnet-4-20250514
  max_tokens: 2048
storage:
  knowledge_dir: ./knowledge
  db_path: ./data/test.db
""")
    write_config(sources_path, """
rss:
  - name: Test Feed
    url: https://example.com/feed.xml
    category: ai
crawlers:
  - name: Test Crawler
    url: https://example.com
    parser: test_parser
    category: economics
    access: public
apis:
  - name: Test API
    type: arxiv
    query: "cat:cs.AI"
    category: ai
twitter:
  - name: TestUser
    handle: testuser
    category: ai
""")


class TestConfigLoad:
    def test_load_valid_config(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert config.claude["api_key"] == "test-key"
        assert config.claude["model"] == "claude-sonnet-4-20250514"

    def test_env_var_replacement(self, config_dir, monkeypatch):
        config_path, sources_path = config_dir
        monkeypatch.setenv("TEST_API_KEY", "env-key-123")
        write_config(config_path, """
claude:
  api_key: ${TEST_API_KEY}
  model: claude-sonnet-4-20250514
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, "rss: []\ncrawlers: []")
        config = Config(str(config_path), str(sources_path))
        assert config.claude["api_key"] == "env-key-123"

    def test_env_var_not_set(self, config_dir):
        config_path, sources_path = config_dir
        write_config(config_path, """
claude:
  api_key: ${NONEXISTENT_VAR_12345}
  model: claude-sonnet-4-20250514
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, "rss: []\ncrawlers: []")
        # api_key 保留原始字符串，但验证会失败因为它以 $ 开头
        # 不过 spec 说环境变量未设置只记录 warning，验证由使用方判断
        # 这里 api_key 非空所以验证会通过
        config = Config(str(config_path), str(sources_path))
        assert config.claude["api_key"] == "${NONEXISTENT_VAR_12345}"

    def test_dot_path_access(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert config.get("claude.model") == "claude-sonnet-4-20250514"

    def test_dot_path_default(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert config.get("nonexistent.key", "default") == "default"


class TestConfigSources:
    def test_rss_sources(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert len(config.rss_sources) == 1
        assert config.rss_sources[0]["name"] == "Test Feed"

    def test_crawler_sources(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert len(config.crawler_sources) == 1

    def test_api_sources(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert len(config.api_sources) == 1

    def test_twitter_sources(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert len(config.twitter_sources) == 1

    def test_empty_category(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        write_config(sources_path, "rss: []\ncrawlers: []")
        config = Config(str(config_path), str(sources_path))
        assert config.rss_sources == []

    def test_missing_category(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        write_config(sources_path, "rss: []\ncrawlers: []")
        config = Config(str(config_path), str(sources_path))
        assert config.twitter_sources == []


class TestConfigValidation:
    def test_missing_api_key(self, config_dir):
        config_path, sources_path = config_dir
        write_config(config_path, """
claude:
  model: claude-sonnet-4-20250514
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, "rss: []\ncrawlers: []")
        with pytest.raises(ConfigError, match="claude.api_key"):
            Config(str(config_path), str(sources_path))

    def test_missing_model(self, config_dir):
        config_path, sources_path = config_dir
        write_config(config_path, """
claude:
  api_key: test-key
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, "rss: []\ncrawlers: []")
        with pytest.raises(ConfigError, match="claude.model"):
            Config(str(config_path), str(sources_path))

    def test_rss_missing_name(self, config_dir):
        config_path, sources_path = config_dir
        write_config(config_path, """
claude:
  api_key: test-key
  model: test-model
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, """
rss:
  - url: https://example.com/feed
    category: ai
crawlers: []
""")
        with pytest.raises(ConfigError):
            Config(str(config_path), str(sources_path))

    def test_crawler_missing_parser(self, config_dir):
        config_path, sources_path = config_dir
        write_config(config_path, """
claude:
  api_key: test-key
  model: test-model
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, """
rss: []
crawlers:
  - name: Test
    url: https://example.com
    category: economics
""")
        with pytest.raises(ConfigError):
            Config(str(config_path), str(sources_path))


class TestConfigErrors:
    def test_config_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Config("/nonexistent/config.yaml", "/nonexistent/sources.yaml")

    def test_invalid_yaml(self, config_dir):
        config_path, sources_path = config_dir
        write_config(config_path, ":\ninvalid: [yaml: {broken")
        write_config(sources_path, "rss: []")
        with pytest.raises(ConfigError):
            Config(str(config_path), str(sources_path))

    def test_sources_not_found(self, config_dir):
        config_path, _ = config_dir
        write_config(config_path, """
claude:
  api_key: test-key
  model: test-model
storage:
  db_path: ./data/test.db
""")
        config = Config(str(config_path), str(config_path.parent / "nonexistent.yaml"))
        assert config.rss_sources == []


class TestConfigEdgeCases:
    def test_numeric_value_no_env_replace(self, config_dir):
        config_path, sources_path = config_dir
        make_valid_config(config_path, sources_path)
        config = Config(str(config_path), str(sources_path))
        assert config.claude["max_tokens"] == 2048

    def test_partial_env_var(self, config_dir, monkeypatch):
        config_path, sources_path = config_dir
        monkeypatch.setenv("MY_VAR", "hello")
        write_config(config_path, """
claude:
  api_key: prefix_${MY_VAR}_suffix
  model: test-model
storage:
  db_path: ./data/test.db
""")
        write_config(sources_path, "rss: []\ncrawlers: []")
        config = Config(str(config_path), str(sources_path))
        assert config.claude["api_key"] == "prefix_hello_suffix"
