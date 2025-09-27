# 🚀 Unlimited Audio Bot

Professional Telegram bot for downloading audio from YouTube videos.

## ✨ Features

- **Unlimited file size** - No size restrictions
- **Automatic file splitting** - Files >50MB split into chunks
- **Progress tracking** - Real-time download progress
- **24/7 uptime** - Runs continuously on Railway
- **High quality audio** - Best available audio format

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/mp3-downloader)

### Manual Deploy:

1. **Create Telegram Bot:**
   - Go to [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Name: `🚀 Unlimited Audio`
   - Username: `unlimited_audio_bot` (or any available)
   - Save the token

2. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect this repository
   - Add environment variable: `BOT_TOKEN=your_bot_token_here`
   - Click Deploy

3. **Test:**
   - Send `/start` to your bot
   - Send any YouTube URL
   - Click "🎵 Yuklab Olish" button

## 📁 Project Structure

```
mp3-downloader/
├── deploy_bot.py      # Main bot code (production-ready)
├── requirements.txt   # Python dependencies
├── nixpacks.toml     # Build configuration
├── Procfile          # Process definition
├── railway.json      # Railway settings
└── README.md         # This file
```

## ⚙️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | ✅ Yes |

## 🎯 Bot Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information
- Send YouTube URL - Download audio from video

## 📊 Specifications

- **Language:** Python 3.11
- **Framework:** python-telegram-bot
- **Deployment:** Railway (Nixpacks)
- **Uptime:** 24/7
- **File limit:** Unlimited (auto-splitting)
- **Audio format:** M4A/WebM (best quality)

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/DAMIR030303/mp3-downloader.git
cd mp3-downloader

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export BOT_TOKEN=your_bot_token_here

# Run bot
python deploy_bot.py
```

## 📄 License

MIT License - feel free to use for personal projects.

## ⚠️ Disclaimer

For personal use only. Respect copyright laws and YouTube's terms of service.

---

**🎵 Download any YouTube audio instantly and unlimited!**

> Professional, fast, reliable, and completely free!