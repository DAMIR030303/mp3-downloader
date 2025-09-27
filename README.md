# 🎵 MP3 Downloader - Professional Edition

YouTube videolaridan audio yuklab olish uchun professional dastur.

## ✨ Xususiyatlar

- **🚀 Har qanday hajmdagi video** - Cheklovsiz yuklab olish
- **⚙️ 4 xil sifat rejimi** - Kichik/Muvozanatli/Yuqori/MP3
- **📦 Avtomatik fayl bo'lish** - 50MB+ fayllar chunks'ga bo'linadi
- **🔄 Progress tracking** - Real-time progress ko'rsatish
- **🤖 Telegram bot** - Unified bot barcha xususiyatlar bilan
- **🌐 Web interface** - Browser orqali foydalanish
- **🖥️ CLI tools** - Command line interface

## 🚀 Bitta Buyruq Bilan Ishga Tushirish

```bash
python run.py
```

Bu universal launcher avtomatik ravishda:
- Requirements o'rnatadi
- Menyu ko'rsatadi
- Komponent tanlash imkonini beradi

## 📱 Telegram Bot

### Sozlash:
1. @BotFather'dan bot yarating
2. `config.py`da token o'rnating
3. `python run.py` ishga tushiring
4. Menyu → "1" (Telegram Bot)

### Xususiyatlar:
- `/mode` - Sifat rejimini tanlash
- Inline keyboard'lar
- Progress tracking
- Smart file handling

## 🌐 Web Interface

```bash
python run.py
# Menyu → 2 (Web Interface)
# Browser: http://localhost:5000
```

## 📁 Loyiha Strukturasi

```
mp3-downloader/
├── run.py              # 🎯 ASOSIY FAYL - buni ishga tushiring
├── config.py           # ⚙️ Sozlamalar
├── utils.py            # 🛠️ Yordamchi funksiyalar  
├── downloader.py       # 📥 Yuklab olish klassi
├── telegram_bot_main.py # 🤖 Unified telegram bot
├── web_app.py          # 🌐 Web interface
├── requirements_clean.txt # 📋 Dependencies
└── README.md           # 📚 Bu fayl
```

## ⚙️ Sozlamalar

`config.py` faylida barcha sozlamalar:
- Bot token
- Fayl yo'llari
- Timeout'lar
- yt-dlp sozlamalari

## 🎯 Rejimlar

1. **Kichik hajm** - Tez (WebM ~10MB)
2. **Muvozanatli** - Tavsiya etiladi (M4A ~25MB)
3. **Yuqori sifat** - Eng yaxshi (M4A ~50MB)  
4. **MP3 format** - Universal (FFmpeg kerak)

## 📊 Cheklovlar

- **Fayl hajmi:** Cheklovsiz (avtomatik bo'linadi)
- **Video uzunligi:** Cheklovsiz
- **Formatlar:** M4A, MP3, WebM, Opus
- **Telegram limit:** 50MB (avtomatik chunks)

## 🔧 Talablar

- Python 3.7+
- Internet aloqasi  
- FFmpeg (MP3 konvertatsiya uchun, ixtiyoriy)

## 📚 Hujjatlar

- [Optimizatsiya Qo'llanmasi](OPTIMIZED_GUIDE.md)
- [Katta Fayllar Support](LARGE_FILES_SUPPORT.md)
- [Loyiha Hisoboti](FINAL_REPORT.md)

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating
3. Commit qiling
4. Pull request yuboring

## 📄 Litsenziya

MIT License - bepul foydalaning!

## ⚠️ Ogohlantirish

Faqat shaxsiy foydalanish uchun. Mualliflik huquqlariga rioya qiling.

---

**🎵 Endi har qanday YouTube audio'ni osongina yuklab oling!**

> Professional darajada, cheklovsiz, tez va ishonchli!