# ⚡ Railway Quick Start - @unlimited_audio_bot

## 🚀 **5 Daqiqada Deploy Qiling!**

### **1. 🤖 Bot Yaratish (2 daqiqa)**
1. Telegram'da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` yuboring
3. **Bot nomi:** `🚀 Unlimited Audio`
4. **Username:** `unlimited_audio_bot` (yoki boshqa available)
5. **Token'ni copy qiling:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### **2. 🚂 Railway Deploy (3 daqiqa)**
1. [railway.app](https://railway.app) ga boring
2. **"New Project"** tugmasini bosing
3. **"Deploy from GitHub repo"** tanlang
4. Repository: **`DAMIR030303/mp3-downloader`**
5. **Variables** bo'limiga:
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. **Deploy** tugmasini bosing

### **3. ✅ Test (30 soniya)**
- Deploy tugagach logs'da quyidagi xabar ko'rinadi:
```
🚀 Unlimited Audio Bot (@unlimited_audio_bot) started on Railway!
🤖 Bot Token: 1234567890...
📱 Bot tayyor - Telegram'da /start yuboring!
```
- Telegram'da bot'ga `/start` yuboring
- YouTube URL yuboring va sinab ko'ring!

---

## 🔧 **Deploy Logs Ko'rish:**

### **✅ Muvaffaqiyatli Deploy:**
```
╔═════════════════ Nixpacks v1.38.0 ═════════════════╗
║ setup      │ python311, python311Packages.pip      ║
║ install    │ pip install -r requirements.txt       ║
║ build      │ echo "Build completed successfully"    ║
║ start      │ python deploy_bot.py                   ║
╚════════════════════════════════════════════════════╝

✅ Build completed successfully
🚀 Unlimited Audio Bot (@unlimited_audio_bot) started on Railway!
🤖 Bot Token: 1234567890...
📱 Bot tayyor - Telegram'da /start yuboring!
```

### **❌ Agar Xato Bo'lsa:**
- **"BOT_TOKEN not set"** → Variables'da BOT_TOKEN qo'shing
- **"pip install failed"** → Dockerfile deploy qiling (avtomatik)
- **"Bot not responding"** → Token'ni tekshiring

---

## 🎯 **Railway Alternative: Dockerfile**

Agar Nixpacks ishlamasa, Railway avtomatik Dockerfile'ni ishlatadi:
- ✅ Python 3.11
- ✅ FFmpeg installed
- ✅ Optimized dependencies
- ✅ Health check

---

## 📱 **Bot Test Qilish:**

### **Commands:**
- `/start` - Welcome message
- `/help` - Yordam

### **Usage:**
1. YouTube URL yuboring
2. "🎵 Yuklab Olish" tugmasini bosing  
3. Progress ko'ring: `⏳ Yuklab olinmoqda... 45%`
4. Audio oling yoki chunks (50MB+)

---

## 💡 **Pro Tips:**

### **🔋 Resource Optimization:**
Railway bepul tier: **500 soat/oy**
- Bot sleep qilmaydi = ~720 soat/oy
- **Yetishmaydi!** Premium kerak ($5/oy)

### **💰 Cost Saving:**
```python
# deploy_bot.py'da timeout qo'shing:
SLEEP_WHEN_IDLE = True
IDLE_TIMEOUT = 300  # 5 daqiqa
```

### **📊 Monitoring:**
- Railway dashboard'da logs ko'ring
- Memory/CPU usage kuzatib boring
- Uptime statistics

---

## 🎉 **Deploy Tayyor!**

**Bot URL:** `@unlimited_audio_bot`
**Railway Project:** `unlimited-audio-bot-xxx`
**Status:** 🟢 24/7 Running

**Professional Telegram bot 5 daqiqada tayyor!** 🚀

---

## 🆘 **Yordam:**

- **Railway Issues:** [docs.railway.app](https://docs.railway.app)
- **Bot API:** [core.telegram.org/bots](https://core.telegram.org/bots)
- **Repository:** [GitHub Issues](https://github.com/DAMIR030303/mp3-downloader/issues)