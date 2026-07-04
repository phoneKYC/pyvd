"""
utils/helpers.py — Miscellaneous helpers.
"""

import os
import re
from typing import Optional


def fmt_duration(seconds: Optional[float]) -> str:
    if not seconds:
        return ""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m {sec:02d}s"
    if m:
        return f"{m}m {sec:02d}s"
    return f"{sec}s"


def fmt_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def safe_caption(text: str, max_len: int = 1024) -> str:
    """Truncate caption to Telegram's limit."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "…"


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def chunk_text(text: str, size: int = 4096):
    """Split text into chunks of at most `size` characters."""
    for i in range(0, len(text), size):
        yield text[i: i + size]
