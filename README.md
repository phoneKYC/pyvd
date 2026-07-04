<p align="center">
  <img src="https://img.icons8.com/color/96/telegram-bot.png" width="96" height="96" alt="govd-bot logo"/>
</p>

<h1 align="center">govd-bot</h1>

<p align="center">
  <b>بوت تيليجرام متقدم لتحميل الوسائط من أكثر من 1000 منصة</b><br/>
  <i>Advanced Telegram bot for downloading media from 1000+ platforms</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/yt--dlp-1000%2B%20sites-green.svg" alt="1000+ sites"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/>
  <img src="https://img.shields.io/badge/Developer-IIDZII%20Dev-red.svg" alt="IIDZII Dev"/>
</p>

<p align="center">
  <a href="#-المنصات-المدعومة">المنصات</a> •
  <a href="#-النشر-والتثبيت">النشر</a> •
  <a href="#-الأوامر">الأوامر</a> •
  <a href="#-الإعدادات">الإعدادات</a> •
  <a href="#%EF%B8%8F-deployment-guides">Deployment</a> •
  <a href="#-هيكل-المشروع">الهيكل</a>
</p>

---

## ⚡ المنصات المدعومة | Supported Platforms

TikTok • Instagram • YouTube • Twitter/X • Reddit • Facebook • Pinterest • Twitch Clips • Vimeo • Dailymotion • SoundCloud • Bilibili • Rumble • وأكثر من **1000 موقع آخر** عبر yt-dlp.

---

## 🚀 النشر والتثبيت | Quick Start

### الطريقة 1: تشغيل محلي (Local)

```bash
# 1. استنساخ المشروع
git clone https://github.com/IIDZII-Dev/govd-bot.git
cd govd-bot

# 2. إعداد المتغيرات البيئية
cp .env.example .env
# عدّل .env وضع توكن البوت: BOT_TOKEN=your_token_here

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. تثبيت ffmpeg (مطلوب)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
# Windows: حمّل من https://ffmpeg.org/download.html

# 5. تشغيل البوت
python bot.py
```

### الطريقة 2: Docker (الموصى بها)

```bash
git clone https://github.com/IIDZII-Dev/govd-bot.git
cd govd-bot
cp .env.example .env
# عدّل .env
docker compose up -d
```

---

## 📖 الأوامر | Commands

| الأمر | الوظيفة | الوصول |
|-------|---------|--------|
| `/start` | رسالة الترحيب | الجميع |
| `/help` | عرض جميع الأوامر | الجميع |
| `/settings` | إعدادات البوت للمحادثة | الجميع |
| `/dl <url>` | تحميل وسائط من رابط (يعمل في المجموعات) | الجميع |
| `/audio <url>` | تحميل الصوت فقط | الجميع |
| `/cancel` | إلغاء التحميل الجاري | الجميع |
| `/stats` | إحصائيات البوت | مشرفون |
| `/broadcast <msg>` | إرسال رسالة جماعية | مشرفون |
| `/whitelist` | عرض القائمة البيضاء | مشرفون |

> **الاستخدام التلقائي**: أرسل أي رابط في المحادثة الخاصة وسيكتشفه البوت تلقائياً!

---

## ⚙️ الإعدادات | Settings

من خلال `/settings`:

| الإعداد | الوصف |
|---------|-------|
| 📝 التسميات التوضيحية | إظهار/إخفاء مصدر الوسائط |
| 🔇 الوضع الصامت | إرسال الوسائط بدون إشعار |
| 🔞 المحتوى الصريح | السماح/منع المحتوى الحساس |
| 🗂 حد الألبوم | عدد الوسائط في الألبوم (1-10) |
| 🌐 اللغة | EN / AR |

---

## 🔧 الإعدادات المتقدمة | Environment Variables

| المتغير | الوصف | الافتراضي |
|---------|-------|-----------|
| `BOT_TOKEN` | توكن البوت من @BotFather **(مطلوب)** | — |
| `BOT_API_URL` | عنوان API (رسمي أو محلي) | `https://api.telegram.org` |
| `CONCURRENT_UPDATES` | عدد التحديثات المتزامنة | `50` |
| `MAX_FILE_SIZE` | الحد الأقصى لحجم الملف (MB) | `2000` |
| `MAX_DURATION` | الحد الأقصى لمدة الفيديو | `1h` |
| `PROXY` | البروكسي (http/socks5) | — |
| `WHITELIST` | قائمة المستخدمين المسموح لهم (IDs مفصولة بفاصلة) | (الكل) |
| `ADMINS` | معرّفات المشرفين (IDs مفصولة بفاصلة) | — |
| `CACHING` | تخزين file_id مؤقتاً | `true` |
| `LOG_LEVEL` | مستوى السجل | `INFO` |
| `DEFAULT_LANGUAGE` | اللغة الافتراضية | `en` |
| `DOWNLOADS_DIR` | مجلد التحميلات المؤقت | `downloads` |
| `DB_PATH` | مسار قاعدة بيانات SQLite | `govd_bot.db` |

---

## 🌐 Deployment Guides

### 1. Railway 🚂 (الموصى بها)

Railway هي أسهل طريقة لنشر البوت مع دعم تلقائي لـ Python و ffmpeg.

**الخطوات:**

```bash
# 1. أنشئ حساباً على https://railway.app
# 2. أنشئ مشروعاً جديداً (New Project)
# 3. اختر "Deploy from GitHub repo"
# 4. اختر مستودع govd-bot
# 5. سيتم الكشف تلقائياً عن Python و ffmpeg عبر nixpacks.toml
```

**إعداد المتغيرات البيئية:**

1. اذهب إلى **Variables** في مشروع Railway
2. أضف المتغيرات التالية:
   - `BOT_TOKEN` = `توكن_البوت_الخاص_بك`
   - `CONCURRENT_UPDATES` = `50` (اختياري)
   - `LOG_LEVEL` = `INFO` (اختياري)

**ملاحظات Railway:**
- يتم تثبيت `ffmpeg` تلقائياً عبر `nixpacks.toml`
- البوت يعمل كـ worker process عبر `Procfile`
- `runtime.txt` يحدد نسخة Python المطلوبة
- قاعدة البيانات تكون ephemeral (تُفقد عند إعادة النشر) — استخدم Volume مستقل للإنتاج

**استخدام Railway CLI:**

```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# تهيئة المشروع
railway init

# إضافة متغيرات
railway variables set BOT_TOKEN=your_token_here
railway variables set LOG_LEVEL=INFO

# النشر
railway up
```

---

### 2. Render 🎨

```bash
# 1. أنشئ حساباً على https://render.com
# 2. اختر "New" → "Web Service"
# 3. ربط مستودع GitHub
# 4. الإعدادات:
#    - Build Command: pip install -r requirements.txt
#    - Start Command: python bot.py
#    - Environment: Python 3
#    - Plan: Free أو Starter
```

**إعداد المتغيرات البيئية:**
1. في صفحة الخدمة → **Environment**
2. أضف `BOT_TOKEN` وباقي المتغيرات
3. Render لا يوفر ffmpeg افتراضياً — استخدم Docker:

```bash
# اختر "Dockerfile" كبيئة بدلاً من Python
# Render سيبني الصورة من Dockerfile (يتضمن ffmpeg)
```

---

### 3. Heroku 🟣

```bash
# 1. تثبيت Heroku CLI
# 2. تسجيل الدخول
heroku login

# 3. إنشاء التطبيق
heroku create your-bot-name

# 4. إعداد Buildpacks (ffmpeg مطلوب)
heroku buildpacks:set heroku/python
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg.git

# 5. إعداد المتغيرات
heroku config:set BOT_TOKEN=your_token_here
heroku config:set CONCURRENT_UPDATES=50

# 6. النشر
git push heroku main
```

**ملاحظات Heroku:**
- `Procfile` يحدد `worker: python bot.py` — نوع التطبيق يجب أن يكون Worker وليس Web
- Heroku Eco/Basic يكفي لبوت التيليجرام
- ffmpeg مثبت عبر buildpack مخصص

---

### 4. Koyeb ⚡

```bash
# 1. أنشئ حساباً على https://koyeb.com
# 2. اختر "Create Service" → "GitHub"
# 3. اختر المستودع
# 4. الإعدادات:
#    - Build type: Dockerfile
#    - Ports: (لا حاجة — البوت يستخدم polling)
#    - Instances: 1
```

**إعداد المتغيرات البيئية:**
- في صفحة الخدمة → **Environment variables**
- أضف `BOT_TOKEN` وباقي المتغيرات
- Dockerfile يتضمن ffmpeg تلقائياً

---

### 5. Fly.io ✈️

```bash
# 1. تثبيت Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. تسجيل الدخول
fly auth login

# 3. إنشاء التطبيق
fly launch

# عند السؤال عن الإعدادات:
#   - Would you like to set up a PostgreSQL database? No
#   - Would you like to set up an Upstash Redis database? No

# 4. إعداد المتغيرات
fly secrets set BOT_TOKEN=your_token_here

# 5. النشر
fly deploy
```

**ملف `fly.toml` (يُنشأ تلقائياً أو يدوياً):**

```toml
app = "govd-bot"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"

[vm]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

---

### 6. VPS / خادم افتراضي 🖥️ (Ubuntu/Debian)

```bash
# 1. تحديث النظام
sudo apt update && sudo apt upgrade -y

# 2. تثبيت المتطلبات
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# 3. استنساخ المشروع
git clone https://github.com/IIDZII-Dev/govd-bot.git
cd govd-bot

# 4. إعداد البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. إعداد المتغيرات
cp .env.example .env
nano .env  # عدّل BOT_TOKEN

# 6. تشغيل البوت
python bot.py
```

**تشغيل كخدمة systemd (تلقائية عند إعادة التشغيل):**

```bash
sudo tee /etc/systemd/system/govd-bot.service << 'EOF'
[Unit]
Description=govd-bot Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/govd-bot
Environment=PATH=/home/your_username/govd-bot/venv/bin
ExecStart=/home/your_username/govd-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable govd-bot
sudo systemctl start govd-bot

# مراقبة السجلات
sudo journalctl -u govd-bot -f
```

---

### 7. Docker عام (أي خادم يدعم Docker)

```bash
# 1. استنساخ المشروع
git clone https://github.com/IIDZII-Dev/govd-bot.git
cd govd-bot

# 2. إعداد المتغيرات
cp .env.example .env
nano .env

# 3. تشغيل عبر Docker Compose
docker compose up -d

# مراقبة السجلات
docker compose logs -f

# إيقاف
docker compose down

# إعادة بناء وتشغيل
docker compose up -d --build
```

**تشغيل مباشر بـ Docker:**

```bash
docker build -t govd-bot .
docker run -d --name govd-bot \
  --env BOT_TOKEN=your_token_here \
  --restart unless-stopped \
  -v ./downloads:/app/downloads \
  govd-bot
```

---

## 🏗️ هيكل المشروع | Project Structure

```
govd-bot/
├── bot.py                # نقطة الدخول الرئيسية
├── config.py             # قراءة المتغيرات البيئية
├── database.py           # SQLite (إعدادات + كاش)
├── downloader.py         # yt-dlp wrapper (async)
├── handlers/
│   ├── __init__.py
│   ├── commands.py       # /start /help /settings /cancel
│   ├── media.py          # كشف URLs + تحميل + إرسال
│   ├── admin.py          # /stats /broadcast /whitelist
│   └── inline.py         # الوضع المضمّن
├── utils/
│   ├── __init__.py
│   ├── i18n.py           # الترجمة (EN/AR)
│   └── helpers.py        # دوال مساعدة
├── Procfile              # Railway / Heroku
├── runtime.txt           # نسخة Python
├── nixpacks.toml         # Railway Nixpacks config
├── Dockerfile            # بناء Docker
├── docker-compose.yml    # Docker Compose
├── requirements.txt      # مكتبات Python
├── .env.example          # قالب المتغيرات البيئية
├── .gitignore            # ملفات Git المهملة
├── LICENSE               # رخصة MIT
└── README.md             # هذا الملف
```

---

## 🌍 الترجمة | Localization

لإضافة لغة جديدة، افتح `utils/i18n.py` وأضف مفاتيحك:

```python
STRINGS["fr"] = {
    "start": "Bienvenue sur govd-bot!\n\nDéveloppé par IIDZII Dev",
    "help": "📖 <b>Commandes</b>\n\n/start — Message de bienvenue\n...",
    # ... أضف كل المفاتيح المطلوبة
}
SUPPORTED_LANGUAGES = list(STRINGS.keys())  # سيتم تحديثها تلقائياً
```

---

## 🛡️ الأمان | Security

- البوت يعمل بمستخدم غير root في Docker
- المتغيرات الحساسة تُقرأ من البيئة فقط
- لا يتم تخزين أي بيانات شخصية
- القائمة البيضاء (Whitelist) تسمح بتقييد الوصول
- `.env` مستبعد من Git عبر `.gitignore`

---

## 🤝 المساهمة | Contributing

1. Fork المشروع
2. أنشئ فرعاً جديداً (`git checkout -b feature/amazing-feature`)
3. أرسل التعديلات (`git commit -m 'Add amazing feature'`)
4. ارفع الفرع (`git push origin feature/amazing-feature`)
5. افتح Pull Request

---

## 📄 الترخيص | License

هذا المشروع مرخص تحت رخصة [MIT](LICENSE).

Developed with ❤️ by **[IIDZII Dev](https://github.com/IIDZII-Dev)**