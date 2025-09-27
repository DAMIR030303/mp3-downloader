#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - Yangilangan versiya (fayl topish muammosi hal qilindi)
"""

import os
import tempfile
import logging
import re
import shutil
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot tokeni
BOT_TOKEN = "8379762562:AAGwwMRueY17BAmo-HJgLU2zKTTsESswKLs"

def sanitize_filename(filename):
    """Windows uchun fayl nomini tozalash"""
    # Noto'g'ri belgilarni olib tashlash
    filename = re.sub(r'[<>:"/\\|?*⧸]', '', filename)
    # Ko'p bo'shliqlarni bitta qilish
    filename = re.sub(r'\s+', ' ', filename)
    # Oxirgi nuqta va bo'shliqlarni olib tashlash
    filename = filename.strip('. ')
    return filename[:100]  # Uzunlikni cheklash

class TelegramAudioDownloader:
    def __init__(self):
        # Downloads papkasini yaratish
        self.downloads_dir = Path("telegram_downloads")
        self.downloads_dir.mkdir(exist_ok=True)
        
        self.ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
            'restrictfilenames': False,  # Unicode lar uchun
            'windowsfilenames': True,    # Windows uchun xavfsiz
        }
    
    def get_video_info(self, url):
        """Video haqida ma'lumot olish"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown')[:100],
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:200]
                }
        except Exception as e:
            return {'error': str(e)}
    
    def download_audio(self, url):
        """Audio yuklab olish - yangilangan versiya"""
        try:
            # Vaqtinchalik fayl nomi
            import uuid
            temp_id = str(uuid.uuid4())[:8]
            
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = str(self.downloads_dir / f'audio_{temp_id}.%(ext)s')
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f"Yuklab olish boshlandi: {url}")
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'Unknown'))
                
                # Yuklab olingan faylni topish
                for file_path in self.downloads_dir.glob(f'audio_{temp_id}.*'):
                    if file_path.suffix in ['.m4a', '.mp3', '.webm', '.opus']:
                        # Fayl nomini to'g'ri qilib o'zgartirish
                        new_name = f"{title}{file_path.suffix}"
                        new_path = self.downloads_dir / new_name
                        
                        # Agar bir xil nomli fayl bo'lsa, raqam qo'shamiz
                        counter = 1
                        while new_path.exists():
                            new_name = f"{title}_{counter}{file_path.suffix}"
                            new_path = self.downloads_dir / new_name
                            counter += 1
                        
                        # Faylni ko'chirish
                        shutil.move(str(file_path), str(new_path))
                        logger.info(f"Fayl saqlandi: {new_path}")
                        
                        return str(new_path), title
                
                # Agar fayl topilmasa, papkani tekshiramiz
                files = list(self.downloads_dir.glob(f'audio_{temp_id}.*'))
                if files:
                    return str(files[0]), title
                
                return None, "Fayl yuklab olinmadi"
                
        except Exception as e:
            logger.error(f"Yuklab olishda xatolik: {e}")
            return None, str(e)

downloader = TelegramAudioDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot boshlanganda ko'rsatiladigan xabar"""
    welcome_text = """
🎵 **MP3 Downloader Bot**'ga xush kelibsiz!

**Qanday foydalanish kerak:**
📎 YouTube video havolasini yuboring
🎧 Men sizga audio faylni yuboraman

**Qo'llab-quvvatlanadigan formatlar:**
• M4A (yuqori sifat)
• MP3 
• WebM

**Buyruqlar:**
/start - Botni qayta boshlash
/help - Yordam

Endi YouTube havola yuboring! 👇
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyruqi"""
    help_text = """
🆘 **Yordam**

**Bot qanday ishlaydi:**
1️⃣ YouTube video havolasini yuboring
2️⃣ Men video haqida ma'lumot beraman
3️⃣ "Yuklab olish" tugmasini bosing
4️⃣ Audio fayl tayyor bo'lgach yuboraman

**Misollar:**
• https://youtube.com/watch?v=abc123
• https://youtu.be/abc123

**Cheklovlar:**
• Maksimal fayl hajmi: 50MB
• Maksimal davomiyligi: 10 daqiqa

**Muammolar bo'lsa:**
@support ga murojaat qiling
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube URL'ni qayta ishlash"""
    url = update.message.text.strip()
    
    # URL tekshirish
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text(
            "❌ Iltimos, to'g'ri YouTube havolasini yuboring!\n\n"
            "Masalan: https://youtube.com/watch?v=abc123"
        )
        return
    
    # "Yuklanmoqda..." xabari
    status_msg = await update.message.reply_text("🔍 Video ma'lumotlari yuklanmoqda...")
    
    # Video ma'lumotlarini olish
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    # Video ma'lumotlarini formatla
    duration = f"{info['duration'] // 60}:{info['duration'] % 60:02d}" if info['duration'] else "Noma'lum"
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 **Kanal:** {info['uploader']}
⏱ **Davomiyligi:** {duration}
👀 **Ko'rishlar:** {views}

📝 **Tavsif:** {info.get('description', 'Mavjud emas')[:100]}...
    """
    
    # Yuklab olish tugmasi
    keyboard = [
        [InlineKeyboardButton("🎧 Audio Yuklab Olish", callback_data=f"download:{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await status_msg.edit_text(video_info_text, parse_mode='Markdown', reply_markup=reply_markup)

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuklab olish tugmasi bosilganda"""
    query = update.callback_query
    await query.answer()
    
    # URL'ni callback data'dan olish
    url = query.data.split(':', 1)[1]
    
    # Yuklab olish jarayonini boshlash
    await query.edit_message_text("⏳ Audio yuklab olinmoqda, iltimos kuting...")
    
    # Audio yuklab olish
    file_path, result = downloader.download_audio(url)
    
    if file_path and os.path.exists(file_path):
        # Fayl hajmini tekshirish (Telegram 50MB cheklovi)
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:  # 50MB
            await query.edit_message_text("❌ Fayl hajmi juda katta (>50MB). Qisqaroq video tanlang.")
            # Faylni o'chirish
            os.remove(file_path)
            return
        
        try:
            # Audio faylni yuborish
            await query.edit_message_text("📤 Fayl yuborilmoqda...")
            
            with open(file_path, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_file,
                    title=result,
                    caption=f"🎵 {result}\n\n✅ @mp3_downloader_bot orqali yuklab olindi"
                )
            
            await query.edit_message_text("✅ Audio muvaffaqiyatli yuborildi!")
            
            # Faylni o'chirish (joy tejash uchun)
            os.remove(file_path)
            
        except Exception as e:
            await query.edit_message_text(f"❌ Faylni yuborishda xatolik: {str(e)}")
            # Xatolik bo'lsa ham faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await query.edit_message_text(f"❌ Yuklab olishda xatolik: {result}")

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshqa xabarlarni qayta ishlash"""
    await update.message.reply_text(
        "🤖 Men faqat YouTube havolalarini tushunaman!\n\n"
        "Iltimos, YouTube video havolasini yuboring:\n"
        "• https://youtube.com/watch?v=abc123\n"
        "• https://youtu.be/abc123"
    )

def main():
    """Botni ishga tushirish"""
    # Bot ilovasini yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handler'larni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Botni ishga tushirish
    print("🤖 MP3 Downloader Bot (Fixed) ishga tushdi!")
    print("📱 Telegram'da /start buyrug'ini yuboring")
    application.run_polling()

if __name__ == '__main__':
    main()