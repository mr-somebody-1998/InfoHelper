from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


class ConfigError(Exception):
    """配置错误"""


class Config:
    def __init__(
        self,
        config_path: str = "config/config.yaml",
        sources_path: str = "config/sources.yaml",
    ):
        self._config = self._load_yaml(config_path, required=True)
        self._sources = self._load_yaml(sources_path, required=False)
        self._resolve_env_vars(self._config)
        self._validate()

    def _load_yaml(self, path: str, *, required: bool) -> dict:
        p = Path(path)
        if not p.exists():
            if required:
                raise FileNotFoundError(f"Config file not found: {path}")
            logger.warning("Sources file not found: %s, using empty config", path)
            return {}
        try:
            with open(p, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError as e:
            raise ConfigError(f"YAML parse error in {path}: {e}") from e

    def _resolve_env_vars(self, data: dict | list, _path: str = "") -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = self._replace_env(value)
                elif isinstance(value, (dict, list)):
                    self._resolve_env_vars(value, f"{_path}.{key}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    data[i] = self._replace_env(item)
                elif isinstance(item, (dict, list)):
                    self._resolve_env_vars(item, f"{_path}[{i}]")

    def _replace_env(self, value: str) -> str:
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            env_val = os.environ.get(var_name)
            if env_val is None:
                logger.warning("Environment variable not set: %s", var_name)
                return match.group(0)
            return env_val

        return ENV_VAR_PATTERN.sub(replacer, value)

    def _validate(self) -> None:
        # claude 配置验证
        claude = self._config.get("claude", {})
        if not claude.get("api_key"):
            raise ConfigError("Missing required config: claude.api_key")
        if not claude.get("model"):
            raise ConfigError("Missing required config: claude.model")

        # storage 配置验证
        storage = self._config.get("storage", {})
        if not storage.get("db_path"):
            raise ConfigError("Missing required config: storage.db_path")

        # sources 验证
        for item in self._sources.get("rss", []):
            if not item.get("name") or not item.get("url"):
                raise ConfigError(f"RSS source missing name or url: {item}")

        for item in self._sources.get("crawlers", []):
            if not item.get("name") or not item.get("url") or not item.get("parser"):
                raise ConfigError(f"Crawler source missing name, url, or parser: {item}")

    @property
    def claude(self) -> dict:
        return self._config.get("claude", {})

    @property
    def storage(self) -> dict:
        return self._config.get("storage", {})

    @property
    def rss_sources(self) -> list[dict]:
        return self._sources.get("rss", [])

    @property
    def crawler_sources(self) -> list[dict]:
        return self._sources.get("crawlers", [])

    @property
    def api_sources(self) -> list[dict]:
        return self._sources.get("apis", [])

    @property
    def twitter_sources(self) -> list[dict]:
        return self._sources.get("twitter", [])

    def get(self, key_path: str, default=None):
        keys = key_path.split(".")
        data = self._config
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
                if data is None:
                    return default
            else:
                return default
        return data
