# MP3 Downloader 🎵

YouTube videolaridan MP3 formatida audio yuklab olish uchun sodda Python dasturi.

## Xususiyatlari

- YouTube videolaridan yuqori sifatli MP3 yuklab olish
- Playlist'larni to'liq yuklab olish
- 192 kbps sifatda audio
- O'zbek tilida interfeys
- Sodda foydalanish

## O'rnatish

1. Repository'ni klonlash:
```bash
git clone https://github.com/yourusername/mp3-downloader.git
cd mp3-downloader
```

2. Kerakli kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

**Muhim:** FFmpeg ham kerak bo'ladi. Windows uchun [FFmpeg](https://ffmpeg.org/download.html) yuklab olib PATH'ga qo'shing.

## Foydalanish

### Bitta video yuklab olish:
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Playlist yuklab olish:
```bash
python main.py -p "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Boshqa papkaga saqlash:
```bash
python main.py -o "mening_musiqalarim" "https://www.youtube.com/watch?v=VIDEO_ID"
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