#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - Final versiya (eng kichik hajm)
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
    filename = re.sub(r'[<>:"/\\|?*⧸@._-]', '', filename)
    filename = re.sub(r'\s+', ' ', filename)
    filename = filename.strip('. ')
    return filename[:30]  # Juda qisqa nom

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
        
        # Eng kichik audio sifatni tanlash
        self.ydl_opts = {
            'format': '249/250/worstaudio/bestaudio',  # Eng kichik formatlar
            'restrictfilenames': True,
            'windowsfilenames': True,
        }
    
    def get_video_info(self, url):
        """Video haqida ma'lumot olish"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown')[:50],
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown')[:30],
                    'view_count': info.get('view_count', 0),
                }
        except Exception as e:
            return {'error': str(e)}
    
    def download_audio(self, url):
        """Audio yuklab olish - eng kichik hajm"""
        try:
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
                    if file_path.suffix in ['.webm', '.m4a', '.mp3', '.opus']:
                        file_size = file_path.stat().st_size
                        logger.info(f"Fayl hajmi: {format_file_size(file_size)}")
                        
                        # 50MB dan katta fayllar uchun xatolik
                        if file_size > 50 * 1024 * 1024:
                            file_path.unlink()
                            return None, f"Fayl hajmi juda katta: {format_file_size(file_size)}", 0
                        
                        # Fayl nomini o'zgartirish
                        new_name = f"{title}{file_path.suffix}"
                        new_path = self.downloads_dir / new_name
                        
                        counter = 1
                        while new_path.exists():
                            new_name = f"{title}_{counter}{file_path.suffix}"
                            new_path = self.downloads_dir / new_name
                            counter += 1
                        
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
🎵 **MP3 Downloader Bot** (Kichik hajm)

**Xususiyatlari:**
📦 Eng kichik hajmdagi audio
⚡ Tez yuklash va yuborish
🎧 WebM/Opus format (sifat yaxshi)

**Cheklovlar:**
• Maksimal: 50MB
• Qisqa videolar tavsiya etiladi

Endi YouTube havola yuboring! 👇
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyruqi"""
    help_text = """
🆘 **Yordam**

**Bu bot:**
✅ Eng kichik hajmdagi audio yuklab oladi
✅ WebM/Opus format (zamonaviy)
✅ Tez ishlaydi

**Maslahatlar:**
• 2-15 daqiqa videolar ideal
• Qo'shiq/musiqa uchun eng yaxshi
• Sifat vs hajm muvozanati

**Format:** WebM (Opus codec)
**Sifat:** 48-58 kbps (yetarli)
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube URL'ni qayta ishlash"""
    url = update.message.text.strip()
    
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text(
            "❌ Iltimos, YouTube havolasini yuboring!\n"
            "Masalan: https://youtube.com/watch?v=abc123"
        )
        return
    
    status_msg = await update.message.reply_text("🔍 Video tekshirilmoqda...")
    
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    duration = f"{info['duration'] // 60}:{info['duration'] % 60:02d}" if info['duration'] else "?"
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 {info['uploader']}
⏱ {duration} | 👀 {views}

📦 **Format:** WebM (kichik hajm)
🎧 **Sifat:** 48-58 kbps
    """
    
    keyboard = [
        [InlineKeyboardButton("⚡ Tez Yuklab Olish", callback_data=f"download:{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await status_msg.edit_text(video_info_text, parse_mode='Markdown', reply_markup=reply_markup)

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuklab olish tugmasi"""
    query = update.callback_query
    await query.answer()
    
    url = query.data.split(':', 1)[1]
    
    await query.edit_message_text("⏳ Kichik hajmda yuklab olinmoqda...")
    
    file_path, title, file_size = downloader.download_audio(url)
    
    if file_path and os.path.exists(file_path):
        try:
            await query.edit_message_text(f"📤 Yuborilmoqda... ({format_file_size(file_size)})")
            
            with open(file_path, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_file,
                    title=title,
                    caption=f"🎵 {title}\n📦 {format_file_size(file_size)} | Format: WebM\n✅ Kichik hajmda yuklab olindi",
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=30,
                    pool_timeout=30
                )
            
            await query.edit_message_text("✅ Muvaffaqiyatli yuborildi!")
            os.remove(file_path)
            
        except Exception as e:
            error_msg = str(e)
            if "Timed out" in error_msg:
                await query.edit_message_text("❌ Timeout! Boshqa video sinab ko'ring.")
            else:
                await query.edit_message_text(f"❌ Xatolik: {error_msg}")
            
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await query.edit_message_text(f"❌ Yuklab olishda xatolik: {title}")

def main():
    """Botni ishga tushirish"""
    request = HTTPXRequest(
        connection_pool_size=4,
        connect_timeout=30.0,
        read_timeout=120.0,
        write_timeout=120.0,
        pool_timeout=30.0
    )
    
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    print("🎵 MP3 Downloader Bot (Kichik hajm) ishga tushdi!")
    print("📦 Format: WebM (Opus), Hajm: Minimal")
    application.run_polling()

if __name__ == '__main__':
    main()