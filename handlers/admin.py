"""
handlers/admin.py — Admin-only commands: /stats, /broadcast, /whitelist
"""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import cfg
from database import stat_all
from utils import t, chunk_text

logger = logging.getLogger(__name__)


def _admin_check(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return cfg.is_admin(user_id)


# ─────────────────────────────────────────────────────────────────────────────
# /stats
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _admin_check(user.id if user else None):
        await update.message.reply_text(t("admin_only"))
        return

    stats = await stat_all()
    if not stats:
        await update.message.reply_text("No stats yet.")
        return

    lines = [t("stats_title")]
    for key, value in sorted(stats.items()):
        lines.append(t("stats_line", key=key.replace("_", " ").title(), value=value))

    await update.message.reply_html("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# /broadcast
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _admin_check(user.id if user else None):
        await update.message.reply_text(t("admin_only"))
        return

    if not context.args:
        await update.message.reply_html(t("broadcast_usage"))
        return

    text = " ".join(context.args)

    # Broadcast to whitelisted IDs
    targets = cfg.whitelist | cfg.admins
    if not targets:
        await update.message.reply_text("No users in whitelist/admins to broadcast to.")
        return

    sent = 0
    failed = 0
    for uid in targets:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=text,
                parse_mode=ParseMode.HTML,
            )
            sent += 1
        except Exception as exc:
            logger.warning("Broadcast to %s failed: %s", uid, exc)
            failed += 1

    await update.message.reply_text(
        f"📣 Broadcast complete.\n✅ Sent: {sent}\n❌ Failed: {failed}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# /whitelist info
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _admin_check(user.id if user else None):
        await update.message.reply_text(t("admin_only"))
        return

    wl = cfg.whitelist
    admins = cfg.admins
    msg = (
        f"<b>Whitelist</b> ({len(wl)} users):\n"
        + (", ".join(str(i) for i in wl) or "(none)")
        + f"\n\n<b>Admins</b> ({len(admins)}):\n"
        + (", ".join(str(i) for i in admins) or "(none)")
    )
    await update.message.reply_html(msg)
