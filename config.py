"""
config.py — Central configuration loader for govd-bot
Reads from environment variables / .env file
"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional, Set
from dotenv import load_dotenv

load_dotenv()


def _parse_duration(value: str) -> int:
    """Parse duration string like '1h', '30m', '15s' into seconds."""
    value = value.strip()
    match = re.fullmatch(r"(\d+)(h|m|s)", value)
    if not match:
        raise ValueError(f"Invalid duration format: {value!r}")
    n, unit = int(match[1]), match[2]
    return n * {"h": 3600, "m": 60, "s": 1}[unit]


def _parse_ids(value: str) -> Set[int]:
    """Parse comma-separated list of Telegram IDs."""
    return {int(x.strip()) for x in value.split(",") if x.strip()}


@dataclass
class Config:
    # ── Telegram ──────────────────────────────────────────────
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    bot_api_url: str = field(
        default_factory=lambda: os.getenv("BOT_API_URL", "https://api.telegram.org")
    )
    concurrent_updates: int = field(
        default_factory=lambda: int(os.getenv("CONCURRENT_UPDATES", "50"))
    )

    # ── Storage ───────────────────────────────────────────────
    downloads_dir: str = field(
        default_factory=lambda: os.getenv("DOWNLOADS_DIR", "downloads")
    )
    db_path: str = field(
        default_factory=lambda: os.getenv("DB_PATH", "govd_bot.db")
    )

    # ── Limits ────────────────────────────────────────────────
    max_file_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "2000"))
    )
    max_duration_sec: int = field(
        default_factory=lambda: _parse_duration(os.getenv("MAX_DURATION", "1h"))
    )

    # ── Defaults ──────────────────────────────────────────────
    default_captions: bool = field(
        default_factory=lambda: os.getenv("DEFAULT_ENABLE_CAPTIONS", "true").lower() == "true"
    )
    default_silent: bool = field(
        default_factory=lambda: os.getenv("DEFAULT_ENABLE_SILENT", "false").lower() == "true"
    )
    default_nsfw: bool = field(
        default_factory=lambda: os.getenv("DEFAULT_ENABLE_NSFW", "false").lower() == "true"
    )
    default_album_limit: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_MEDIA_ALBUM_LIMIT", "10"))
    )
    default_language: str = field(
        default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en")
    )
    auto_language: bool = field(
        default_factory=lambda: os.getenv("AUTOMATIC_LANGUAGE_DETECTION", "true").lower() == "true"
    )

    # ── Proxy ─────────────────────────────────────────────────
    proxy: Optional[str] = field(
        default_factory=lambda: os.getenv("PROXY")
    )

    # ── Access control ────────────────────────────────────────
    whitelist_raw: str = field(
        default_factory=lambda: os.getenv("WHITELIST", "")
    )
    admins_raw: str = field(
        default_factory=lambda: os.getenv("ADMINS", "")
    )

    # ── Captions format ───────────────────────────────────────
    caption_header: str = field(
        default_factory=lambda: os.getenv(
            "CAPTIONS_HEADER", "<a href='{url}'>source</a>"
        )
    )
    caption_description: str = field(
        default_factory=lambda: os.getenv(
            "CAPTIONS_DESCRIPTION", "<blockquote expandable>{text}</blockquote>"
        )
    )

    # ── Misc ──────────────────────────────────────────────────
    repo_url: str = field(
        default_factory=lambda: os.getenv("REPO_URL", "https://github.com/IIDZII-Dev/govd-bot")
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )
    caching: bool = field(
        default_factory=lambda: os.getenv("CACHING", "true").lower() == "true"
    )

    # ── Computed ──────────────────────────────────────────────
    @property
    def whitelist(self) -> Set[int]:
        return _parse_ids(self.whitelist_raw) if self.whitelist_raw else set()

    @property
    def admins(self) -> Set[int]:
        return _parse_ids(self.admins_raw) if self.admins_raw else set()

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admins

    def is_allowed(self, user_id: int) -> bool:
        if not self.whitelist:
            return True
        return user_id in self.whitelist or user_id in self.admins


# Singleton
cfg = Config()
