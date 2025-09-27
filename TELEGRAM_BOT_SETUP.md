# Telegram Bot O'rnatish Qo'llanmasi 🤖

## Bot yaratish

### 1. @BotFather bilan bot yaratish

1. Telegram'da @BotFather'ni toping
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `MP3 Downloader Bot`)
4. Bot username'ini kiriting (masalan: `mp3_downloader_unique_bot`)
5. Token olasiz (masalan: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Token'ni sozlash

`telegram_bot.py` faylida:
```python
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"
```

Yoki `.env` fayl yarating:
```bash
BOT_TOKEN=SIZNING_BOT_TOKENINGIZ
```

## Bot ishga tushirish

### Mahalliy kompyuterda:
```bash
python telegram_bot.py
```

### VPS/Cloud serverda:
```bash
# Screen yoki tmux ishlatib
screen -S mp3bot
python telegram_bot.py
# Ctrl+A+D bilan chiqish
```

## Bot funksiyalari

### Qo'llab-quvvatlanadigan formatlar:
- 🎵 M4A (eng yaxshi sifat)
- 🎵 MP3 
- 🎵 WebM

### Cheklovlar:
- Maksimal fayl hajmi: 50MB
- Telegram API cheklovlari
- YouTube rate limiting

### Buyruqlar:
- `/start` - Botni boshlash
- `/help` - Yordam

## Foydalanuvchi qo'llanmasi

1. Botni ishga tushiring: `/start`
2. YouTube video havolasini yuboring
3. Video ma'lumotlarini ko'ring
4. "🎧 Audio Yuklab Olish" tugmasini bosing
5. Fayl tayyor bo'lgach yuklab olinadi

## Maslahatlar

### Xavfsizlik:
- Bot tokenini hech kimga bermang
- Public repository'da token qo'ymang
- `.env` fayldan foydalaning

### Performance:
- VPS da ishlatish tavsiya etiladi
- Yetarli disk bo'sh joy qoldiring
- Internet tezligi muhim

### Muammolarni hal qilish:
- Bot javob bermasa - tokenni tekshiring
- Yuklab olish muvaffaqiyatsiz - URL'ni tekshiring
- Fayl juda katta - qisqaroq video tanlang

## Deploy qilish

### Heroku'da:
1. Heroku account yarating
2. `Procfile` yarating: `worker: python telegram_bot.py`
3. Config vars'da BOT_TOKEN qo'ying
4. Deploy qiling

### VPS'da:
1. Ubuntu/CentOS server oling
2. Python 3.8+ o'rnating
3. Repository'ni klonlang
4. Requirements o'rnating
5. Screen/systemd bilan ishga tushiring

## Qo'shimcha xususiyatlar

Kelajakda qo'shilishi mumkin:
- [ ] Playlist support
- [ ] Audio quality tanlov
- [ ] User statistics
- [ ] Admin panel
- [ ] Multiple language support
- [ ] Custom filename format