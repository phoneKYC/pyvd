"""
bot.py — govd-bot entry point.
A feature-complete Python Telegram bot for downloading media
from 1000+ platforms via yt-dlp, inspired by govdbot/govd.

Usage:
    python bot.py
"""

import asyncio
import logging
import os
import signal
import sys

from telegram import BotCommand
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

from config import cfg

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, cfg.log_level, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Silence noisy libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("yt_dlp").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger("govd-bot")


# ─────────────────────────────────────────────────────────────────────────────
# Create downloads directory
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(cfg.downloads_dir, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Bot commands menu
# ─────────────────────────────────────────────────────────────────────────────

BOT_COMMANDS = [
    BotCommand("start",    "Welcome message"),
    BotCommand("help",     "Show all commands"),
    BotCommand("settings", "Configure the bot for this chat"),
    BotCommand("dl",       "Download media from a URL"),
    BotCommand("audio",    "Download audio only from a URL"),
    BotCommand("cancel",   "Cancel active download"),
    BotCommand("stats",    "[Admin] Bot statistics"),
    BotCommand("broadcast","[Admin] Broadcast a message"),
    BotCommand("whitelist","[Admin] Show whitelist"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Build Application
# ─────────────────────────────────────────────────────────────────────────────

def build_app() -> Application:
    from handlers import (
        cmd_start, cmd_help, cmd_settings, cmd_cancel, callback_settings,
        handle_url_message, cmd_dl, cmd_audio,
        cmd_stats, cmd_broadcast, cmd_whitelist,
        handle_inline,
    )

    builder = (
        Application.builder()
        .token(cfg.bot_token)
        .base_url(cfg.bot_api_url + "/bot")
        .base_file_url(cfg.bot_api_url + "/file/bot")
        .concurrent_updates(cfg.concurrent_updates)
        .read_timeout(120)
        .write_timeout(120)
        .connect_timeout(30)
        .pool_timeout(30)
    )

    app = builder.build()

    # ── Commands ──────────────────────────────────────────────
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("help",       cmd_help))
    app.add_handler(CommandHandler("settings",   cmd_settings))
    app.add_handler(CommandHandler("cancel",     cmd_cancel))
    app.add_handler(CommandHandler("dl",         cmd_dl))
    app.add_handler(CommandHandler("audio",      cmd_audio))

    # ── Admin commands ────────────────────────────────────────
    app.add_handler(CommandHandler("stats",      cmd_stats))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))
    app.add_handler(CommandHandler("whitelist",  cmd_whitelist))

    # ── Settings callbacks ────────────────────────────────────
    app.add_handler(
        CallbackQueryHandler(
            callback_settings,
            pattern=r"^(toggle:|lang:|album:)",
        )
    )

    # ── Inline mode ───────────────────────────────────────────
    app.add_handler(InlineQueryHandler(handle_inline))

    # ── Auto URL detection (private chats only) ───────────────
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            handle_url_message,
        )
    )

    # ── Post-init: register commands menu ────────────────────
    async def post_init(application: Application) -> None:
        await application.bot.set_my_commands(BOT_COMMANDS)
        me = await application.bot.get_me()
        logger.info(
            "🤖  govd-bot started as @%s (id=%s)", me.username, me.id
        )
        logger.info(
            "⚙️   Concurrent updates: %s | Max file: %sMB | Max duration: %ss",
            cfg.concurrent_updates,
            cfg.max_file_size_mb,
            cfg.max_duration_sec,
        )
        if cfg.whitelist:
            logger.info("🔒  Whitelist active: %s user(s)", len(cfg.whitelist))
        if cfg.proxy:
            logger.info("🌐  Proxy: %s", cfg.proxy)

    app.post_init = post_init  # type: ignore[assignment]

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    if not cfg.bot_token or cfg.bot_token == "12345678:ABC-DEF1234ghIkl-zyx57W2P0s":
        logger.critical(
            "❌  BOT_TOKEN is not set! Copy .env.example to .env and fill it in."
        )
        sys.exit(1)

    app = build_app()
    logger.info("Starting polling…")
    app.run_polling(
        allowed_updates=[
            "message",
            "callback_query",
            "inline_query",
            "chosen_inline_result",
        ],
        drop_pending_updates=True,
        close_loop=True,
    )


if __name__ == "__main__":
    main()
