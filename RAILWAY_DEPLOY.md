# 🚀 Railway Deploy Guide - MP3 Downloader

## ✅ Railway'ga Deploy Qilish Qo'llanmasi

Railway - Python botlarni bepul deploy qilish uchun eng yaxshi platform!

---

## 📋 **Qadamlar:**

### **1. 🤖 Telegram Bot Yaratish**
```bash
# Telegram'da @BotFather ga boring
/newbot
# Bot nomi: 🚀 Unlimited Audio
# Username: unlimited_audio_bot (yoki boshqa available nom)
# Token oling: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### **2. 🌐 Railway Account**
1. [railway.app](https://railway.app) ga kiring
2. GitHub account bilan sign up/login qiling
3. "New Project" tugmasini bosing

### **3. 📁 GitHub Repository**
1. Ushbu repository'ni fork qiling yoki import qiling:
   ```
   https://github.com/DAMIR030303/mp3-downloader
   ```
2. Railway'da "Deploy from GitHub repo" tanlang
3. Repository'ni tanlang

### **4. ⚙️ Environment Variables**
Railway dashboard'da Variables bo'limiga qo'shing:
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
PYTHON_VERSION=3.11
```

### **5. 🚀 Deploy**
- Railway avtomatik deploy qiladi
- Logs'da deploy jarayonini kuzatib boring
- "🤖 Starting Telegram Bot..." ko'ringanda tayyor!

---

## 📁 **Deploy Fayllar (avtomatik aniqlaydi):**

### **✅ Railway konfiguratsiya:**
- `start.sh` - Railway start script
- `Procfile` - Process definition  
- `railway.json` - Railway config
- `runtime.txt` - Python version
- `requirements_clean.txt` - Dependencies

### **🔧 Deploy Process:**
```bash
1. Repository'ni clone qiladi
2. Python 3.11 o'rnatadi  
3. pip install -r requirements_clean.txt
4. BOT_TOKEN tekshiradi
5. python telegram_bot_main.py ishga tushiradi
```

---

## 📊 **Railway Features:**

### **✅ Bepul Tier:**
- **500 soat/oy** - Botlar uchun yetarli
- **1GB RAM** - MP3 bot uchun ideal
- **1GB Disk** - Temp fayllar uchun
- **No sleep** - 24/7 ishlaydi

### **🔄 Auto-deploy:**
- Git push → avtomatik deploy
- Rolling updates
- Zero downtime

### **📊 Monitoring:**
- Real-time logs
- Resource usage
- Uptime monitoring

---

## 🛠️ **Troubleshooting:**

### **❌ "BOT_TOKEN not set"**
**Hal:** Railway Variables'da BOT_TOKEN qo'shing

### **❌ "Build failed"**  
**Hal:** requirements_clean.txt'ni tekshiring

### **❌ "Bot not responding"**
**Hal:** Logs'da xatolarni ko'ring

### **❌ "Memory limit"**
**Hal:** Katta fayllar uchun chunk size'ni kamaytiring

---

## 📱 **Deploy'dan Keyin:**

### **✅ Test qiling:**
1. Telegram'da bot'ga `/start` yuboring
2. YouTube URL sinab ko'ring
3. Fayl yuklab olishni test qiling

### **⚙️ Monitoring:**  
- Railway dashboard'da metrics ko'ring
- Logs'ni muntazam tekshiring
- Resource usage kuzatib boring

---

## 🎯 **Railway'ga Alternativalar:**

| Platform | Bepul Tier | Pros | Cons |
|----------|------------|------|------|
| **Railway** | 500h/oy | Easy, No sleep | Limited hours |
| **Heroku** | 550h/oy | Popular | Complex setup |
| **Render** | 750h/oy | More hours | Slower |
| **VPS** | $5+/oy | Full control | Manual setup |

---

## 💡 **Pro Tips:**

### **🔋 Battery Saving:**
```python
# config.py'da polling interval'ni oshiring
POLLING_INTERVAL = 2  # default 1
```

### **💾 Memory Optimization:**
```python
# Katta fayllar uchun chunk size'ni kamaytiring  
CHUNK_SIZE = 30 * 1024 * 1024  # 30MB instead of 45MB
```

### **📊 Logging:**
```python
# Production'da log level'ni o'zgartiring
LOGGING_LEVEL = 'WARNING'  # INFO o'rniga
```

---

## 🚀 **Deploy Commands:**

### **Manual Deploy:**
```bash
# Railway CLI'dan (optional)
railway login
railway link [project-id]  
railway up
```

### **Environment:**
```bash
# Variables ko'rish
railway variables

# Variable qo'shish
railway variables set BOT_TOKEN=your_token
```

---

## ✅ **Final Checklist:**

- [ ] Bot token olindi (@BotFather)
- [ ] Railway account yaratildi  
- [ ] Repository import qilindi
- [ ] BOT_TOKEN environment variable qo'shildi
- [ ] Deploy muvaffaqiyatli
- [ ] Bot Telegram'da javob beryapti
- [ ] Test yuklash ishlayapti

---

# 🎉 **Deploy Tayyor!**

**Railway URL:** `https://your-project.up.railway.app`
**Bot:** @unlimited_audio_bot (yoki sizning tanlaganingiz)

**24/7 ishlaydigan professional bot tayyor!** 🚀

---

## 📞 **Yordam:**

**Deploy Issues:** [Railway Docs](https://docs.railway.app)
**Bot Issues:** [Telegram Bot API](https://core.telegram.org/bots/api)

**Success!** 🎊