#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - Optimized versiya (timeout va katta fayllar uchun)
"""

import os
import tempfile
import logging
import re
import shutil
import asyncio
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
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
    filename = re.sub(r'[<>:"/\\|?*⧸@]', '', filename)
    # Ko'p bo'shliqlarni bitta qilish
    filename = re.sub(r'\s+', ' ', filename)
    # Oxirgi nuqta va bo'shliqlarni olib tashlash
    filename = filename.strip('. ')
    return filename[:50]  # Qisqaroq nom

def format_file_size(size_bytes):
    """Fayl hajmini format qilish"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

class TelegramAudioDownloader:
    def __init__(self):
        # Downloads papkasini yaratish
        self.downloads_dir = Path("telegram_downloads")
        self.downloads_dir.mkdir(exist_ok=True)
        
        self.ydl_opts = {
            'format': 'bestaudio[filesize<50M]/bestaudio[ext=m4a]/bestaudio',  # 50MB dan kichik
            'restrictfilenames': False,
            'windowsfilenames': True,
        }
    
    def get_video_info(self, url):
        """Video haqida ma'lumot olish"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Fayl hajmini taxmin qilish
                formats = info.get('formats', [])
                estimated_size = 0
                for fmt in formats:
                    if fmt.get('acodec') != 'none' and 'filesize' in fmt:
                        estimated_size = fmt['filesize']
                        break
                
                return {
                    'title': info.get('title', 'Unknown')[:80],
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:150],
                    'estimated_size': estimated_size
                }
        except Exception as e:
            return {'error': str(e)}
    
    def download_audio(self, url):
        """Audio yuklab olish - optimized versiya"""
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
                        # Fayl hajmini tekshirish
                        file_size = file_path.stat().st_size
                        logger.info(f"Fayl hajmi: {format_file_size(file_size)}")
                        
                        if file_size > 50 * 1024 * 1024:  # 50MB
                            file_path.unlink()  # Faylni o'chirish
                            return None, f"Fayl hajmi juda katta: {format_file_size(file_size)}"
                        
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
                        
                        return str(new_path), title, file_size
                
                return None, "Fayl yuklab olinmadi", 0
                
        except Exception as e:
            logger.error(f"Yuklab olishda xatolik: {e}")
            return None, str(e), 0

downloader = TelegramAudioDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot boshlanganda ko'rsatiladigan xabar"""
    welcome_text = """
🎵 **MP3 Downloader Bot**'ga xush kelibsiz!

**Qanday foydalanish kerak:**
📎 YouTube video havolasini yuboring
🎧 Men sizga audio faylni yuboraman

**Cheklovlar:**
• Maksimal fayl hajmi: 50MB
• Qisqa videolarni tanlang (5-10 daqiqa)

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

**Maslahatlar:**
✅ Qisqa videolar (2-10 daqiqa) tanlang
✅ Sifat o'rniga tezlikni afzal ko'ring
✅ Agar xatolik bo'lsa, boshqa video sinang

**Qo'llab-quvvatlanadigan:**
• M4A format (tavsiya etiladi)
• MP3 format
• WebM format

**Cheklovlar:**
• 50MB dan katta fayllar yuklanmaydi
• Juda uzun videolar (30+ daqiqa) muammoli

**Muammolar:**
• Timeout - qisqaroq video tanlang
• Hajm katta - sifatni pasaytiring
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
    status_msg = await update.message.reply_text("🔍 Video ma'lumotlari tekshirilmoqda...")
    
    # Video ma'lumotlarini olish
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    # Video ma'lumotlarini formatla
    duration = f"{info['duration'] // 60}:{info['duration'] % 60:02d}" if info['duration'] else "Noma'lum"
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    
    # Ogohlantirish qo'shish
    warning = ""
    if info['duration'] and info['duration'] > 600:  # 10 daqiqadan ko'p
        warning = "\n⚠️ **Ogohlantirish:** Video uzun, fayl hajmi katta bo'lishi mumkin!"
    
    if info.get('estimated_size', 0) > 50 * 1024 * 1024:
        warning = "\n⚠️ **Ogohlantirish:** Taxminiy fayl hajmi 50MB dan katta!"
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 **Kanal:** {info['uploader']}
⏱ **Davomiyligi:** {duration}
👀 **Ko'rishlar:** {views}

📝 **Tavsif:** {info.get('description', 'Mavjud emas')[:80]}...{warning}
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
    await query.edit_message_text("⏳ Audio yuklab olinmoqda... Bu biroz vaqt olishi mumkin.")
    
    # Audio yuklab olish
    result = downloader.download_audio(url)
    file_path, title, file_size = result if len(result) == 3 else (result[0], result[1], 0)
    
    if file_path and os.path.exists(file_path):
        try:
            # Audio faylni yuborish (timeout bilan)
            await query.edit_message_text(f"📤 Fayl yuborilmoqda... ({format_file_size(file_size)})")
            
            with open(file_path, 'rb') as audio_file:
                # Katta fayllar uchun uzunroq timeout
                timeout = 300 if file_size > 10 * 1024 * 1024 else 120  # 5 yoki 2 daqiqa
                
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_file,
                    title=title,
                    caption=f"🎵 {title}\n📊 Hajmi: {format_file_size(file_size)}\n\n✅ @mp3_downloader_bot orqali yuklab olindi",
                    read_timeout=timeout,
                    write_timeout=timeout,
                    connect_timeout=60,
                    pool_timeout=60
                )
            
            await query.edit_message_text("✅ Audio muvaffaqiyatli yuborildi!")
            
            # Faylni o'chirish (joy tejash uchun)
            os.remove(file_path)
            
        except Exception as e:
            error_msg = str(e)
            if "Timed out" in error_msg:
                await query.edit_message_text(
                    "❌ Yuborishda timeout xatoligi!\n\n"
                    "💡 Maslahat: Qisqaroq video tanlang yoki keyinroq urinib ko'ring."
                )
            elif "too large" in error_msg.lower():
                await query.edit_message_text(
                    "❌ Fayl hajmi juda katta!\n\n"
                    "💡 Maslahat: 5 daqiqadan qisqa video tanlang."
                )
            else:
                await query.edit_message_text(f"❌ Xatolik: {error_msg}")
            
            # Xatolik bo'lsa ham faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await query.edit_message_text(f"❌ Yuklab olishda xatolik: {title}")

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boshqa xabarlarni qayta ishlash"""
    await update.message.reply_text(
        "🤖 Men faqat YouTube havolalarini tushunaman!\n\n"
        "💡 **Maslahat:** Qisqa videolar (2-10 daqiqa) yaxshi ishlaydi.\n\n"
        "Iltimos, YouTube video havolasini yuboring:\n"
        "• https://youtube.com/watch?v=abc123\n"
        "• https://youtu.be/abc123"
    )

def main():
    """Botni ishga tushirish"""
    # Timeout sozlamalari bilan request yaratish
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=60.0,
        read_timeout=300.0,  # 5 daqiqa
        write_timeout=300.0,  # 5 daqiqa
        pool_timeout=60.0
    )
    
    # Bot ilovasini yaratish
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    
    # Handler'larni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Botni ishga tushirish
    print("🤖 MP3 Downloader Bot (Optimized) ishga tushdi!")
    print("📱 Telegram'da /start buyrug'ini yuboring")
    print("⚡ Timeout: 5 daqiqa, Max fayl: 50MB")
    application.run_polling()

if __name__ == '__main__':
    main()