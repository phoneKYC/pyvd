"""
handlers/media.py — URL detection → download → send
Handles private chats, groups (/dl command), and audio mode.
"""

import asyncio
import logging
import os
from typing import List, Optional

from telegram import (
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    Update,
)
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import cfg
from database import cache_get, cache_set, get_settings, stat_inc
from downloader import MediaItem, download, cleanup_file, extract_urls
from utils import fmt_duration, safe_caption, t

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Caption builder
# ─────────────────────────────────────────────────────────────────────────────

def _build_caption(item: MediaItem, settings: dict, lang: str) -> str:
    if not settings.get("captions", 1):
        return ""
    header = cfg.caption_header.replace("{url}", item.webpage_url or item.url)
    header = header.replace("{{url}}", item.webpage_url or item.url)

    parts = [header]
    if item.description:
        desc_tmpl = cfg.caption_description
        desc = desc_tmpl.replace("{text}", item.description[:800])
        desc = desc.replace("{{text}}", item.description[:800])
        parts.append(desc)
    return safe_caption("\n".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# Send a single media item
# ─────────────────────────────────────────────────────────────────────────────

async def _send_item(
    message: Message,
    item: MediaItem,
    caption: str,
    silent: bool,
) -> Optional[str]:
    """
    Send one MediaItem. Returns the Telegram file_id for caching.
    """
    kwargs = dict(
        caption=caption or None,
        parse_mode=ParseMode.HTML,
        disable_notification=silent,
        read_timeout=120,
        write_timeout=120,
        connect_timeout=30,
    )

    try:
        with open(item.path, "rb") as f:
            if item.media_type == "audio":
                msg = await message.reply_audio(
                    audio=f,
                    title=item.title or None,
                    duration=int(item.duration) if item.duration else None,
                    **kwargs,
                )
                return msg.audio.file_id if msg.audio else None

            elif item.media_type == "photo":
                msg = await message.reply_photo(photo=f, **kwargs)
                return msg.photo[-1].file_id if msg.photo else None

            else:  # video / document
                # Use reply_video if it looks like a proper video
                ext = os.path.splitext(item.path)[1].lower()
                if ext in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
                    msg = await message.reply_video(
                        video=f,
                        duration=int(item.duration) if item.duration else None,
                        width=item.width,
                        height=item.height,
                        supports_streaming=True,
                        **kwargs,
                    )
                    return msg.video.file_id if msg.video else None
                else:
                    msg = await message.reply_document(document=f, **kwargs)
                    return msg.document.file_id if msg.document else None

    except TelegramError as exc:
        logger.error("Telegram send error: %s", exc)
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Send multiple items as a media group (album)
# ─────────────────────────────────────────────────────────────────────────────

async def _send_album(
    message: Message,
    items: List[MediaItem],
    settings: dict,
    lang: str,
    silent: bool,
) -> None:
    media_group = []
    opened_files = []

    try:
        for idx, item in enumerate(items):
            caption = _build_caption(item, settings, lang) if idx == 0 else None
            f = open(item.path, "rb")
            opened_files.append(f)

            ext = os.path.splitext(item.path)[1].lower()

            if item.media_type == "photo":
                media_group.append(
                    InputMediaPhoto(
                        media=f,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                    )
                )
            elif item.media_type == "audio":
                media_group.append(
                    InputMediaAudio(
                        media=f,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        title=item.title or None,
                        duration=int(item.duration) if item.duration else None,
                    )
                )
            else:
                if ext in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
                    media_group.append(
                        InputMediaVideo(
                            media=f,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            duration=int(item.duration) if item.duration else None,
                            width=item.width,
                            height=item.height,
                            supports_streaming=True,
                        )
                    )
                else:
                    media_group.append(
                        InputMediaDocument(
                            media=f,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                        )
                    )

        await message.reply_media_group(
            media=media_group,
            disable_notification=silent,
            read_timeout=180,
            write_timeout=180,
        )
    finally:
        for f in opened_files:
            try:
                f.close()
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# Core processing function
# ─────────────────────────────────────────────────────────────────────────────

async def process_url(
    url: str,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    audio_only: bool = False,
) -> None:
    chat_id = message.chat_id
    settings = await get_settings(chat_id)
    lang = settings.get("language", "en")
    silent = bool(settings.get("silent", 0))
    album_limit = settings.get("album_limit", cfg.default_album_limit)

    # Show typing action
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Check file cache for single item
    if cfg.caching and not audio_only:
        cached = await cache_get(url)
        if cached:
            caption = f'<a href="{url}">source</a>'
            try:
                file_id = cached["file_id"]
                ftype = cached["file_type"]
                kw = dict(
                    caption=caption if settings.get("captions", 1) else None,
                    parse_mode=ParseMode.HTML,
                    disable_notification=silent,
                )
                if ftype == "video":
                    await message.reply_video(video=file_id, **kw)
                elif ftype == "audio":
                    await message.reply_audio(audio=file_id, **kw)
                elif ftype == "photo":
                    await message.reply_photo(photo=file_id, **kw)
                else:
                    await message.reply_document(document=file_id, **kw)
                await stat_inc("cache_hits")
                return
            except TelegramError:
                pass  # cache stale, re-download

    # Status message
    status_msg = await message.reply_html(
        t("downloading", lang),
        disable_notification=True,
    )

    await stat_inc("downloads_started")

    # Download
    result = await download(url, audio_only=audio_only, playlist_limit=album_limit)

    if not result.ok:
        await stat_inc("downloads_failed")
        try:
            await status_msg.edit_text(
                t("error_generic", lang, error=result.error),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
        return

    # Update status
    try:
        await status_msg.edit_text(t("sending", lang))
    except TelegramError:
        pass

    items = result.items
    if not items:
        await status_msg.edit_text(t("error_generic", lang, error="No items"))
        return

    try:
        if len(items) == 1:
            caption = _build_caption(items[0], settings, lang)
            file_id = await _send_item(message, items[0], caption, silent)
            # Cache result
            if file_id and cfg.caching:
                ext = os.path.splitext(items[0].path)[1].lower()
                ftype = items[0].media_type
                await cache_set(url, file_id, ftype)
        else:
            await _send_album(message, items, settings, lang, silent)

        await stat_inc("downloads_success")
        try:
            await status_msg.delete()
        except TelegramError:
            pass

    except TelegramError as exc:
        logger.error("Failed to send media: %s", exc)
        await stat_inc("downloads_failed")
        try:
            await status_msg.edit_text(
                t("error_generic", lang, error=str(exc)),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
    finally:
        await cleanup_file(*[item.path for item in items])


# ─────────────────────────────────────────────────────────────────────────────
# Message handler: auto-detect URLs
# ─────────────────────────────────────────────────────────────────────────────

async def handle_url_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not message.text:
        return

    # Access control
    if user and not cfg.is_allowed(user.id):
        await message.reply_text(t("error_forbidden"))
        return

    # In groups, only react to explicit /dl or if the message is just a URL
    is_group = chat.type in ("group", "supergroup")
    if is_group:
        # We handle groups via /dl command instead
        return

    urls = extract_urls(message.text)
    if not urls:
        return

    url = urls[0]  # Take first URL

    task = asyncio.create_task(process_url(url, message, context))
    context.user_data["active_task"] = task


# ─────────────────────────────────────────────────────────────────────────────
# /dl command — works in groups and private chats
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_dl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    lang_settings = await get_settings(update.effective_chat.id)
    lang = lang_settings.get("language", "en")

    if user and not cfg.is_allowed(user.id):
        await message.reply_text(t("error_forbidden"))
        return

    args = context.args
    url = None

    if args:
        url = args[0]
    elif message.reply_to_message and message.reply_to_message.text:
        urls = extract_urls(message.reply_to_message.text)
        url = urls[0] if urls else None

    if not url:
        await message.reply_html(t("error_no_url", lang))
        return

    task = asyncio.create_task(process_url(url, message, context))
    context.user_data["active_task"] = task


# ─────────────────────────────────────────────────────────────────────────────
# /audio command
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    lang_settings = await get_settings(update.effective_chat.id)
    lang = lang_settings.get("language", "en")

    if user and not cfg.is_allowed(user.id):
        await message.reply_text(t("error_forbidden"))
        return

    args = context.args
    url = None
    if args:
        url = args[0]
    elif message.reply_to_message and message.reply_to_message.text:
        urls = extract_urls(message.reply_to_message.text)
        url = urls[0] if urls else None

    if not url:
        await message.reply_html(t("error_no_url", lang))
        return

    task = asyncio.create_task(process_url(url, message, context, audio_only=True))
    context.user_data["active_task"] = task
