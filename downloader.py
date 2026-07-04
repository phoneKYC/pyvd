"""
downloader.py — yt-dlp wrapper with async execution,
progress tracking, file size checks and retry logic.
"""

import asyncio
import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Callable, List, Optional

import yt_dlp

from config import cfg

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MediaItem:
    path: str
    url: str
    title: str = ""
    description: str = ""
    thumbnail: Optional[str] = None
    duration: Optional[float] = None   # seconds
    width: Optional[int] = None
    height: Optional[int] = None
    media_type: str = "video"          # video | audio | photo | document
    filesize: int = 0
    extractor: str = ""
    webpage_url: str = ""


@dataclass
class DownloadResult:
    items: List[MediaItem] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.items)


# ─────────────────────────────────────────────────────────────────────────────
# URL validation
# ─────────────────────────────────────────────────────────────────────────────

_URL_RE = re.compile(
    r"https?://"
    r"(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}"
    r"(?:/[^\s]*)?"
)


def extract_urls(text: str) -> List[str]:
    return _URL_RE.findall(text)


# ─────────────────────────────────────────────────────────────────────────────
# yt-dlp options builder
# ─────────────────────────────────────────────────────────────────────────────

def _build_ydl_opts(
    output_dir: str,
    audio_only: bool = False,
    progress_hook: Optional[Callable] = None,
    playlist_limit: int = 1,
) -> dict:
    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")

    opts: dict = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noprogress": False,
        "concurrent_fragment_downloads": 4,
        "retries": 5,
        "fragment_retries": 5,
        "file_access_retries": 3,
        "extractor_retries": 3,
        "ignoreerrors": False,
        "playlistend": playlist_limit,
        "merge_output_format": "mp4",
        "postprocessors": [],
        "socket_timeout": 30,
        "http_chunk_size": 10485760,  # 10 MB
    }

    if audio_only:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    else:
        # Best quality up to 1080p, prefer mp4
        opts["format"] = (
            "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]"
            "/bestvideo[height<=1080]+bestaudio"
            "/best[height<=1080]"
            "/best"
        )

    if cfg.proxy:
        opts["proxy"] = cfg.proxy

    if progress_hook:
        opts["progress_hooks"] = [progress_hook]

    return opts


# ─────────────────────────────────────────────────────────────────────────────
# Duration / size guards
# ─────────────────────────────────────────────────────────────────────────────

class TooLargeError(Exception):
    pass


class TooLongError(Exception):
    pass


def _check_info(info: dict) -> None:
    duration = info.get("duration")
    if duration and duration > cfg.max_duration_sec:
        minutes = int(duration // 60)
        raise TooLongError(
            f"Video is {minutes} min — max allowed is "
            f"{cfg.max_duration_sec // 60} min."
        )

    filesize = info.get("filesize") or info.get("filesize_approx") or 0
    if filesize and filesize > cfg.max_file_size_bytes:
        mb = filesize / 1024 / 1024
        raise TooLargeError(
            f"File is {mb:.0f} MB — max allowed is {cfg.max_file_size_mb} MB."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Core download function (blocking, runs in thread pool)
# ─────────────────────────────────────────────────────────────────────────────

def _sync_download(
    url: str,
    audio_only: bool = False,
    playlist_limit: int = 1,
    progress_hook: Optional[Callable] = None,
) -> DownloadResult:
    run_id = str(uuid.uuid4())[:8]
    output_dir = os.path.join(cfg.downloads_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = _build_ydl_opts(
        output_dir,
        audio_only=audio_only,
        progress_hook=progress_hook,
        playlist_limit=playlist_limit,
    )

    downloaded_paths: List[str] = []

    # Track downloaded files via post-hook
    def _post_hook(d: dict):
        if d["status"] == "finished":
            downloaded_paths.append(d["filename"])

    ydl_opts.setdefault("progress_hooks", []).append(_post_hook)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First extract info without downloading to check limits
            info = ydl.extract_info(url, download=False)
            if info is None:
                return DownloadResult(error="Could not extract info from URL.")

            # Handle playlists
            entries = info.get("entries")
            if entries:
                infos = list(entries)[:playlist_limit]
            else:
                infos = [info]

            for entry_info in infos:
                if entry_info is None:
                    continue
                try:
                    _check_info(entry_info)
                except (TooLargeError, TooLongError) as exc:
                    return DownloadResult(error=str(exc))

            # Actually download
            ydl.download([url])

    except yt_dlp.utils.DownloadError as exc:
        msg = str(exc)
        # Strip yt-dlp boilerplate
        msg = re.sub(r"ERROR: \[.*?\] ", "", msg)
        logger.warning("yt-dlp error for %s: %s", url, msg)
        return DownloadResult(error=msg)
    except Exception as exc:
        logger.exception("Unexpected download error for %s", url)
        return DownloadResult(error=str(exc))

    # Match downloaded files to info
    items: List[MediaItem] = []
    if entries:
        all_infos = list(entries)[:playlist_limit]
    else:
        all_infos = [info]

    all_files = sorted(Path(output_dir).iterdir(), key=lambda p: p.stat().st_mtime)

    for idx, entry in enumerate(all_infos):
        if entry is None:
            continue
        # Pick corresponding file
        if idx < len(all_files):
            fpath = str(all_files[idx])
        elif downloaded_paths:
            fpath = downloaded_paths[min(idx, len(downloaded_paths) - 1)]
        else:
            continue

        if not os.path.exists(fpath):
            # Try merged mp4
            base = os.path.splitext(fpath)[0]
            for ext in (".mp4", ".mkv", ".webm", ".mp3", ".m4a"):
                candidate = base + ext
                if os.path.exists(candidate):
                    fpath = candidate
                    break

        if not os.path.exists(fpath):
            continue

        ext = os.path.splitext(fpath)[1].lower()
        if audio_only or ext in (".mp3", ".m4a", ".ogg", ".flac", ".wav", ".opus"):
            media_type = "audio"
        elif ext in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            media_type = "photo"
        else:
            media_type = "video"

        item = MediaItem(
            path=fpath,
            url=url,
            title=entry.get("title", ""),
            description=entry.get("description", "") or "",
            thumbnail=entry.get("thumbnail"),
            duration=entry.get("duration"),
            width=entry.get("width"),
            height=entry.get("height"),
            media_type=media_type,
            filesize=os.path.getsize(fpath),
            extractor=entry.get("extractor", ""),
            webpage_url=entry.get("webpage_url", url),
        )
        items.append(item)

    if not items:
        return DownloadResult(error="No media could be downloaded.")

    return DownloadResult(items=items)


# ─────────────────────────────────────────────────────────────────────────────
# Async wrapper
# ─────────────────────────────────────────────────────────────────────────────

async def download(
    url: str,
    audio_only: bool = False,
    playlist_limit: int = 1,
    progress_hook: Optional[Callable] = None,
) -> DownloadResult:
    func = partial(
        _sync_download,
        url,
        audio_only=audio_only,
        playlist_limit=playlist_limit,
        progress_hook=progress_hook,
    )
    return await asyncio.get_running_loop().run_in_executor(None, func)


# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────

async def cleanup_file(*paths: str) -> None:
    """Delete downloaded files after sending."""
    loop = asyncio.get_running_loop()
    for path in paths:
        try:
            await loop.run_in_executor(None, os.remove, path)
            # Try to remove parent dir if empty
            parent = os.path.dirname(path)
            await loop.run_in_executor(None, _try_rmdir, parent)
        except Exception:
            pass


def _try_rmdir(path: str) -> None:
    try:
        os.rmdir(path)
    except Exception:
        pass
