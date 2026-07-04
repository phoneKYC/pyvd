"""
utils/i18n.py — Simple i18n helper.
Add more languages by adding keys to STRINGS.
"""

from typing import Optional

STRINGS: dict = {
    "en": {
        "start": (
            "👋 <b>Welcome to govd-bot!</b>\n\n"
            "Send me any media URL (TikTok, Instagram, YouTube, Twitter/X, Reddit, "
            "Facebook, Pinterest, Twitch clips, Vimeo, Dailymotion, and 1000+ more) "
            "and I'll download it for you.\n\n"
            "🔧 Use /settings to configure.\n"
            "ℹ️ Use /help for commands.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Developed by IIDZII Dev</b>\n"
            "<i>Advanced media downloader bot powered by yt-dlp</i>"
        ),
        "help": (
            "📖 <b>Commands</b>\n\n"
            "/start — Welcome message\n"
            "/help — This message\n"
            "/settings — Configure bot for this chat\n"
            "/audio &lt;url&gt; — Download audio only\n"
            "/dl &lt;url&gt; — Force download (works in groups)\n"
            "/cancel — Cancel active download\n\n"
            "<b>Usage:</b> Just send a URL and I'll detect it automatically!"
        ),
        "settings_menu": "⚙️ <b>Settings</b> for this chat:",
        "settings_captions": "📝 Captions",
        "settings_silent": "🔇 Silent mode",
        "settings_nsfw": "🔞 NSFW content",
        "settings_language": "🌐 Language",
        "settings_album": "🗂 Album limit",
        "on": "✅ ON",
        "off": "❌ OFF",
        "toggled": "✅ <b>{key}</b> is now <b>{state}</b>.",
        "downloading": "⬇️ Downloading…",
        "processing": "⚙️ Processing…",
        "sending": "📤 Sending…",
        "done": "✅ Done!",
        "error_generic": "❌ Could not download:\n<code>{error}</code>",
        "error_no_url": "❌ Please provide a URL.",
        "error_unsupported": "❌ This URL is not supported.",
        "error_too_large": "❌ File too large (max {max}MB).",
        "error_too_long": "❌ Video too long (max {max}).",
        "error_forbidden": "⛔ You are not allowed to use this bot.",
        "cancelled": "🚫 Download cancelled.",
        "cancel_nothing": "Nothing to cancel.",
        "stats_title": "📊 <b>Bot Statistics</b>",
        "stats_line": "• {key}: <b>{value}</b>",
        "admin_only": "⛔ Admin only.",
        "broadcast_usage": "Usage: /broadcast &lt;message&gt;",
        "inline_placeholder": "Paste a URL to download…",
        "inline_result_title": "⬇️ Download: {title}",
        "inline_result_desc": "Tap to send this media",
        "caption_format": '<a href="{url}">source</a>',
        "album_limit_changed": "✅ Album limit set to <b>{n}</b>.",
    },
    "ar": {
        "start": (
            "👋 <b>مرحباً بك في govd-bot!</b>\n\n"
            "أرسل لي أي رابط وسائط (TikTok، Instagram، YouTube، Twitter/X، Reddit، "
            "Facebook، Pinterest، Twitch clips، Vimeo، وأكثر من 1000 موقع آخر) "
            "وسأقوم بتحميله لك.\n\n"
            "🔧 استخدم /settings للإعدادات.\n"
            "ℹ️ استخدم /help للأوامر.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>تطوير بواسطة IIDZII Dev</b>\n"
            "<i>بوت متقدم لتحميل الوسائط مدعوم بـ yt-dlp</i>"
        ),
        "help": (
            "📖 <b>الأوامر</b>\n\n"
            "/start — رسالة الترحيب\n"
            "/help — هذه الرسالة\n"
            "/settings — إعدادات البوت لهذه المحادثة\n"
            "/audio &lt;رابط&gt; — تحميل الصوت فقط\n"
            "/dl &lt;رابط&gt; — تحميل إجباري (يعمل في المجموعات)\n"
            "/cancel — إلغاء التحميل الحالي\n\n"
            "<b>الاستخدام:</b> فقط أرسل رابطاً وسأكتشفه تلقائياً!"
        ),
        "settings_menu": "⚙️ <b>الإعدادات</b> لهذه المحادثة:",
        "settings_captions": "📝 التسميات التوضيحية",
        "settings_silent": "🔇 الوضع الصامت",
        "settings_nsfw": "🔞 المحتوى الصريح",
        "settings_language": "🌐 اللغة",
        "settings_album": "🗂 حد الألبوم",
        "on": "✅ مفعّل",
        "off": "❌ معطّل",
        "toggled": "✅ <b>{key}</b> الآن <b>{state}</b>.",
        "downloading": "⬇️ جارٍ التحميل…",
        "processing": "⚙️ جارٍ المعالجة…",
        "sending": "📤 جارٍ الإرسال…",
        "done": "✅ تم!",
        "error_generic": "❌ فشل التحميل:\n<code>{error}</code>",
        "error_no_url": "❌ يرجى تقديم رابط.",
        "error_unsupported": "❌ هذا الرابط غير مدعوم.",
        "error_too_large": "❌ الملف كبير جداً (الحد الأقصى {max} ميجابايت).",
        "error_too_long": "❌ الفيديو طويل جداً (الحد الأقصى {max}).",
        "error_forbidden": "⛔ غير مسموح لك باستخدام هذا البوت.",
        "cancelled": "🚫 تم إلغاء التحميل.",
        "cancel_nothing": "لا يوجد شيء لإلغائه.",
        "stats_title": "📊 <b>إحصائيات البوت</b>",
        "stats_line": "• {key}: <b>{value}</b>",
        "admin_only": "⛔ للمشرفين فقط.",
        "broadcast_usage": "الاستخدام: /broadcast &lt;رسالة&gt;",
        "inline_placeholder": "الصق رابطاً للتحميل…",
        "inline_result_title": "⬇️ تحميل: {title}",
        "inline_result_desc": "اضغط لإرسال الوسائط",
        "caption_format": '<a href="{url}">المصدر</a>',
        "album_limit_changed": "✅ تم تغيير حد الألبوم إلى <b>{n}</b>.",
    },
}

SUPPORTED_LANGUAGES = list(STRINGS.keys())


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Translate a key to the given language, falling back to English."""
    lang_map = STRINGS.get(lang) or STRINGS["en"]
    text = lang_map.get(key) or STRINGS["en"].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
