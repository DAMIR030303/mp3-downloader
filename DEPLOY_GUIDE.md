# 🚀 Railway Deploy Guide - MP3 Downloader Bot

## 1️⃣ **Bot Token Olish**

1. Telegram'da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: "My Audio Downloader Bot")
4. Bot username kiriting (masalan: "@my_audio_bot")
5. Bot token'ini nusxalab oling (masalan: `1234567890:ABC...`)

## 2️⃣ **Railway Deploy - FIXED VERSION**

### A) Railway.app ga kiring:
1. [Railway.app](https://railway.app) saytiga boring
2. GitHub akkaunt bilan login qiling

### B) Loyiha yarating:
1. "New Project" tugmasini bosing
2. "Deploy from GitHub repo" ni tanlang
3. `DAMIR030303/mp3-downloader` repositorysini toping va tanlang
4. "Deploy Now" tugmasini bosing

### C) Environment Variables sozlang:
1. Deploy bo'lgandan so'ng "Variables" tab'iga boring
2. Yangi variable qo'shing:
   - **Name**: `BOT_TOKEN`
   - **Value**: BotFather'dan olgan token
3. "Save" tugmasini bosing

## ✅ **Deploy Configuration Fixed**

**Muammo edi**: `buildCommand` va `startCommand` bir xil edi  
**Hal qilindi**: 
- ✅ `railway.toml` olib tashlandi
- ✅ `railway.json` bilan to'g'ri konfiguratsiya  
- ✅ `nixpacks.toml` da faqat build commands
- ✅ `Procfile` optimallashtirildi

## 3️⃣ **Deploy Tasdiq**

1. **Logs** tab'ini oching
2. Quyidagi xabarlarni kutinig:
   ```
   🚀 Unlimited Audio Bot (@unlimited_audio_bot) started on Railway!
   🤖 Bot Token: 1234567890...
   📱 Bot tayyor - Telegram'da /start yuboring!
   ```

3. **Muvaffaqiyatli deploy** - log'da xatolik bo'lmasa, bot tayyor!

## 4️⃣ **Test Qilish**

1. Telegram'da botingizga boring
2. `/start` buyrug'ini yuboring
3. YouTube havola yuboring (masalan podcast yoki musiqa)
4. "🎵 Yuklab Olish" tugmasini bosing
5. Agar katta fayl bo'lsa, qismlar menyusini ko'ring:
   ```
   📊 Jami hajmi: 500.0 MB
   ⏱ Jami davomiyligi: 1:30:00
   📦 9 qismga bo'lindi

   📀 1-qism | 45.0 MB | ⏱ 0:00-10:00
   📀 2-qism | 45.0 MB | ⏱ 10:00-20:00
   📦 Barcha qismlar
   ```

## 5️⃣ **Troubleshooting**

### ❌ "BOT_TOKEN not set" xatoligi:
- Railway'da Variables tab'ida BOT_TOKEN o'rnatilganini tekshiring
- Token to'g'ri nusxalanganini tasdiqlang

### ❌ Bot javob bermaydi:
- BotFather'da token faolligini tekshiring
- Railway logs'da xatoliklarni qidiring

### ❌ Deploy muvaffaqiyatsiz:
- GitHub'da eng so'ngi commit'lar mavjudligini tekshiring
- Railway'da rebuild tugmasini bosing
- Variables tab'ida BOT_TOKEN borligini tekshiring

### ✅ **Bu xatolik hal qilindi**:
- ~~Failed to parse service config~~ → **FIXED**
- ~~buildCommand/startCommand conflict~~ → **RESOLVED**

## ✅ **Tayyor!**

Bot endi 24/7 ishlaydi va quyidagi xususiyatlarga ega:

- 🚀 **Cheksiz hajm** - Har qanday video yuklab olish  
- 📊 **Aniq ma'lumot** - Har qism uchun aniq vaqt va hajm
- ⚡ **Tez ishlash** - Professional progress tracking
- 🎯 **Sifatli audio** - Eng yaxshi formatda (M4A/WebM)
- 🤖 **Professional UI** - Batafsil metadata bilan
- 🔧 **FFmpeg support** - Audio processing uchun

---

**🎵 Bot features**:
- Unlimited file size downloads
- Smart part selection with time ranges  
- Professional progress tracking
- Clean metadata display
- 24/7 Railway hosting

**📊 Configuration**:
- ✅ `railway.json` - Clean deployment config
- ✅ `nixpacks.toml` - Build dependencies  
- ✅ `Procfile` - Process definition
- ✅ `requirements.txt` - Python dependencies

**Deploy endi 100% ishlaydı!** 🎉