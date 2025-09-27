# MP3 Downloader 🎵

YouTube videolaridan audio yuklab olish uchun to'liq paket:
- 🖥️ **Command Line** versiya
- 🌐 **Web App** (Flask)
- 🤖 **Telegram Bot**

## Xususiyatlari

- YouTube videolaridan yuqori sifatli audio yuklab olish (M4A, MP3, WebM)
- Playlist'larni to'liq yuklab olish
- Web interfeys orqali oson foydalanish
- Telegram bot orqali tez yuklab olish
- O'zbek tilida interfeys
- FFmpeg'siz ham ishlaydi

## O'rnatish

1. Repository'ni klonlash:
```bash
git clone https://github.com/DAMIR030303/mp3-downloader.git
cd mp3-downloader
```

2. Virtual environment yaratish (tavsiya etiladi):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Kerakli kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

## Foydalanish usullari

### 1. 🖥️ Command Line

**FFmpeg bilan (MP3 format):**
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**FFmpeg'siz (M4A/WebM format):**
```bash
python main_no_ffmpeg.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. 🌐 Web App

```bash
python web_app.py
```
Keyin brauzerda: http://localhost:5000

### 3. 🤖 Telegram Bot

1. @BotFather'dan bot yarating va token oling
2. `telegram_bot.py` faylida `BOT_TOKEN` o'rnating
3. Botni ishga tushiring:
```bash
python telegram_bot.py
```

## Misollar

```bash
# Bitta qo'shiqni yuklab olish
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Playlist'ni yuklab olish
python main.py -p "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy4Qrp4kXZpv9_k5-S6UzjV"

# Maxsus papkaga saqlash
python main.py -o "downloads/uzbek_music" "https://www.youtube.com/watch?v=example"
```

## Texnik ma'lumotlar

- **Til:** Python 3.7+
- **Asosiy kutubxona:** yt-dlp
- **Audio format:** MP3 (192 kbps)
- **Platform:** Windows, macOS, Linux

## Litsenziya

MIT License

## Ogohlantirish

Ushbu dastur faqat shaxsiy foydalanish uchun mo'ljallangan. Mualliflik huquqlariga hurmat qiling va faqat ruxsat etilgan kontentni yuklab oling.