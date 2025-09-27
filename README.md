# 🚀 Unlimited Audio Bot (@unlimited_audio_bot)

Professional Telegram bot for downloading unlimited audio from YouTube videos.

## ⚡ Quick Deploy (5 minutes)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/unlimited-audio-bot)

**Step-by-step guide:** [RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)

## ✨ Features

- **🚀 Unlimited file size** - No restrictions, auto-splitting for 50MB+ files
- **📊 Progress tracking** - Real-time download progress
- **⚡ Fast downloads** - Best available audio quality (M4A/WebM)
- **🤖 Smart bot** - Professional Telegram interface
- **☁️ 24/7 uptime** - Runs continuously on Railway
- **🔧 Production-ready** - Optimized code, error handling

## 🎯 Bot Commands

- `/start` - Welcome message and bot info
- `/help` - Usage instructions
- **Send YouTube URL** - Instantly download audio

## 🎵 Usage Example

```
You: https://youtu.be/dQw4w9WgXcQ
Bot: 🎵 Rick Astley - Never Gonna Give You Up
     👤 RickAstleyVEVO
     ⏱ 3:33 | 👀 1,234,567,890
     📊 ~8.5MB
     
     [🎵 Yuklab Olish] button
     
     ⏳ Yuklab olinmoqda... 85%
     ✅ Audio yuborildi!
```

## 🚂 Railway Deployment

### Manual Setup:
1. **Create bot:** [@BotFather](https://t.me/BotFather) → `/newbot` → `@unlimited_audio_bot`
2. **Deploy:** [railway.app](https://railway.app) → New Project → GitHub repo
3. **Environment:** Add `BOT_TOKEN=your_token_here`
4. **Done!** Bot will start automatically

### Expected Deploy Logs:
```
🚀 Unlimited Audio Bot (@unlimited_audio_bot) started on Railway!
🤖 Bot Token: 1234567890...
📱 Bot tayyor - Telegram'da /start yuboring!
```

## 📁 Project Structure

```
unlimited-audio-bot/
├── 🐍 deploy_bot.py          # Main bot (production-ready)
├── 📋 requirements.txt       # Dependencies
├── 🐳 Dockerfile            # Alternative deploy method
├── 🔧 nixpacks.toml         # Nixpacks configuration
├── 📄 Procfile              # Process definition
├── ⚙️ railway.json          # Railway settings
└── 📚 README.md             # This file
```

## 🎛️ Technical Specs

| Feature | Details |
|---------|---------|
| **Language** | Python 3.11 |
| **Framework** | python-telegram-bot |
| **Downloader** | yt-dlp (latest) |
| **Platform** | Railway (Nixpacks/Docker) |
| **File Limit** | Unlimited (auto-chunking) |
| **Audio Format** | M4A, WebM, MP3 (smart selection) |
| **Max Quality** | Best available from YouTube |
| **Part Selection** | Interactive menu for large files |

## 🔧 Local Development

```bash
# Clone and setup
git clone https://github.com/DAMIR030303/mp3-downloader.git
cd mp3-downloader
pip install -r requirements.txt

# Configure
export BOT_TOKEN=your_bot_token_here

# Run
python deploy_bot.py
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "BOT_TOKEN not set" | Add environment variable in Railway |
| Build fails | Check Railway logs, try Docker deploy |
| Bot not responding | Verify token with @BotFather |
| Large files timeout | Interactive part selection available |

## 📊 Performance

- **Download Speed:** Up to 50MB/s (depends on source)
- **File Processing:** Instant for <50MB, ~10s for 500MB
- **Uptime:** 99.9% (Railway infrastructure)
- **Concurrent Users:** Unlimited
- **Daily Limit:** None

## 📄 License

MIT License - Free for personal and commercial use.

## ⚠️ Disclaimer

Respect YouTube's terms of service and copyright laws. For personal use only.

---

**🎵 Download any YouTube audio with smart part selection - unlimited and free!**

> **Bot:** [@unlimited_audio_bot](https://t.me/unlimited_audio_bot)  
> **Feature:** Smart part selection for large files  
> **Deploy:** [5-minute guide](RAILWAY_QUICK_START.md)  
> **Status:** 🟢 Production Ready

**Professional • Smart • Unlimited • Free** 🚀