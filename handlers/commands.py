"""
handlers/commands.py — /start, /help, /settings, /cancel
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import cfg
from database import get_settings, save_settings
from utils import t, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _lang(update: Update) -> str:
    chat_id = update.effective_chat.id
    s = await get_settings(chat_id)
    return s.get("language", "en")


# ─────────────────────────────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user and not cfg.is_allowed(update.effective_user.id):
        await update.message.reply_text(t("error_forbidden"))
        return

    lang = await _lang(update)
    await update.message.reply_html(t("start", lang))


# ─────────────────────────────────────────────────────────────────────────────
# /help
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = await _lang(update)
    await update.message.reply_html(t("help", lang))


# ─────────────────────────────────────────────────────────────────────────────
# /settings
# ─────────────────────────────────────────────────────────────────────────────

def _settings_keyboard(s: dict, lang: str) -> InlineKeyboardMarkup:
    def state(val: int) -> str:
        return t("on", lang) if val else t("off", lang)

    rows = [
        [
            InlineKeyboardButton(
                f"{t('settings_captions', lang)}: {state(s['captions'])}",
                callback_data="toggle:captions",
            )
        ],
        [
            InlineKeyboardButton(
                f"{t('settings_silent', lang)}: {state(s['silent'])}",
                callback_data="toggle:silent",
            )
        ],
        [
            InlineKeyboardButton(
                f"{t('settings_nsfw', lang)}: {state(s['nsfw'])}",
                callback_data="toggle:nsfw",
            )
        ],
        [
            InlineKeyboardButton(
                f"{t('settings_album', lang)}: {s['album_limit']}",
                callback_data="album:decr",
            ),
            InlineKeyboardButton(
                f"{t('settings_album', lang)}: {s['album_limit']}",
                callback_data="album:noop",
            ),
            InlineKeyboardButton("➕", callback_data="album:incr"),
            InlineKeyboardButton("➖", callback_data="album:decr"),
        ],
    ]

    # Language selector
    lang_buttons = []
    for code in SUPPORTED_LANGUAGES:
        marker = "✅ " if code == s["language"] else ""
        lang_buttons.append(
            InlineKeyboardButton(
                f"{marker}{code.upper()}", callback_data=f"lang:{code}"
            )
        )
    rows.append(lang_buttons)

    return InlineKeyboardMarkup(rows)


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    s = await get_settings(chat_id)
    lang = s.get("language", "en")
    kb = _settings_keyboard(s, lang)
    await update.message.reply_html(t("settings_menu", lang), reply_markup=kb)


# ─────────────────────────────────────────────────────────────────────────────
# Callback: toggle / language / album limit
# ─────────────────────────────────────────────────────────────────────────────

async def callback_settings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    data = query.data  # e.g. "toggle:captions" | "lang:ar" | "album:incr"
    s = await get_settings(chat_id)
    lang = s.get("language", "en")

    prefix, value = data.split(":", 1)

    if prefix == "toggle":
        current = s[value]
        new_val = 0 if current else 1
        await save_settings(chat_id, **{value: new_val})
        s[value] = new_val

    elif prefix == "lang":
        await save_settings(chat_id, language=value)
        s["language"] = value
        lang = value

    elif prefix == "album":
        if value == "incr":
            new_limit = min(s["album_limit"] + 1, cfg.default_album_limit)
            await save_settings(chat_id, album_limit=new_limit)
            s["album_limit"] = new_limit
        elif value == "decr":
            new_limit = max(s["album_limit"] - 1, 1)
            await save_settings(chat_id, album_limit=new_limit)
            s["album_limit"] = new_limit

    kb = _settings_keyboard(s, lang)
    try:
        await query.edit_message_reply_markup(reply_markup=kb)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# /cancel
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = await _lang(update)
    task = context.user_data.pop("active_task", None)
    if task and not task.done():
        task.cancel()
        await update.message.reply_text(t("cancelled", lang))
    else:
        await update.message.reply_text(t("cancel_nothing", lang))
