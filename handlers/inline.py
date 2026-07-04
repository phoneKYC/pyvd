"""
handlers/inline.py — Inline mode: @botname <url>
Returns a single cached/fresh result so the user can send it inline.
"""

import asyncio
import logging
import os
import uuid

from telegram import (
    InlineQueryResultVideo,
    InlineQueryResultAudio,
    InlineQueryResultDocument,
    InputTextMessageContent,
    Update,
)
from telegram.ext import ContextTypes

from config import cfg
from database import cache_get
from downloader import extract_urls, download
from utils import t

logger = logging.getLogger(__name__)


async def handle_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query
    if not query:
        return

    text = query.query.strip()
    urls = extract_urls(text)

    if not urls:
        await query.answer(
            [],
            switch_pm_text="Send me a URL to download",
            switch_pm_parameter="inline_help",
            cache_time=0,
        )
        return

    url = urls[0]

    # Check cache first
    cached = await cache_get(url)
    if cached:
        file_id = cached["file_id"]
        ftype = cached["file_type"]
        result = _build_result(file_id, ftype, url, "Cached media")
        if result:
            await query.answer([result], cache_time=300)
            return

    # For inline, we only answer if already cached to avoid timeout
    # Provide a "tap to send via bot" fallback
    msg_content = InputTextMessageContent(url)
    result = _build_fallback(url)
    await query.answer(
        [result],
        cache_time=0,
        switch_pm_text="⬇️ Tap to download in private chat",
        switch_pm_parameter="start",
    )


def _build_result(file_id: str, ftype: str, url: str, title: str):
    uid = str(uuid.uuid4())
    if ftype == "video":
        return InlineQueryResultVideo(
            id=uid,
            video_url=file_id,
            mime_type="video/mp4",
            thumb_url="https://img.icons8.com/color/48/video.png",
            title=title,
            caption=f'<a href="{url}">source</a>',
            parse_mode="HTML",
        )
    return None


def _build_fallback(url: str):
    from telegram import InlineQueryResultArticle, InputTextMessageContent

    return InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title=f"⬇️ Download: {url[:60]}",
        description="Tap to open in private chat for download",
        input_message_content=InputTextMessageContent(url),
    )
