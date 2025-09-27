#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - Unlimited versiya (katta fayllar uchun)
"""

import os
import tempfile
import logging
import re
import shutil
import asyncio
import math
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
    return filename[:30]

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

def split_file(file_path, chunk_size=45*1024*1024):  # 45MB chunks
    """Katta faylni kichik qismlarga bo'lish"""
    chunks = []
    file_size = os.path.getsize(file_path)
    
    if file_size <= 50*1024*1024:  # 50MB dan kichik bo'lsa bo'lmaslik
        return [file_path]
    
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break
            
            chunk_filename = f"{file_path}.part{chunk_num+1}"
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            chunks.append(chunk_filename)
            chunk_num += 1
    
    return chunks

class TelegramAudioDownloader:
    def __init__(self):
        self.downloads_dir = Path("telegram_downloads")
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Katta fayllar uchun optimizatsiya
        self.ydl_opts = {
            'format': 'bestaudio/best',  # Eng yaxshi sifat
            'restrictfilenames': True,
            'windowsfilenames': True,
        }
    
    def get_video_info(self, url):
        """Video haqida ma'lumot olish"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Taxminiy fayl hajmini hisoblash
                duration = info.get('duration', 0)
                estimated_size = duration * 128 * 1024 / 8 if duration else 0  # 128kbps taxmin
                
                return {
                    'title': info.get('title', 'Unknown')[:50],
                    'duration': duration,
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown')[:30],
                    'view_count': info.get('view_count', 0),
                    'estimated_size': estimated_size
                }
        except Exception as e:
            return {'error': str(e)}
    
    def download_audio(self, url, progress_callback=None):
        """Audio yuklab olish - katta fayllar uchun"""
        try:
            import uuid
            temp_id = str(uuid.uuid4())[:8]
            
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = str(self.downloads_dir / f'audio_{temp_id}.%(ext)s')
            
            # Progress callback qo'shish
            if progress_callback:
                def hook(d):
                    if d['status'] == 'downloading':
                        try:
                            percent = (d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)) * 100
                            asyncio.create_task(progress_callback(int(percent)))
                        except:
                            pass
                
                opts['progress_hooks'] = [hook]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f"Katta fayl yuklab olish: {url}")
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'Unknown'))
                
                # Yuklab olingan faylni topish
                for file_path in self.downloads_dir.glob(f'audio_{temp_id}.*'):
                    if file_path.suffix in ['.webm', '.m4a', '.mp3', '.opus']:
                        file_size = file_path.stat().st_size
                        logger.info(f"Fayl hajmi: {format_file_size(file_size)}")
                        
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
🎵 **MP3 Downloader Bot** (Unlimited)

**Yangi xususiyatlar:**
📦 Katta fayllar qo'llab-quvvatlanadi
🔄 Avtomatik fayl bo'lish (50MB+)
⚡ Progress tracking
🎧 Yuqori sifatli audio

**Cheklovlar yo'q:**
• Har qanday hajmdagi video
• Uzun videolar ham yuklanadi
• Multiple parts yuboriladi

Endi YouTube havola yuboring! 👇
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyruqi"""
    help_text = """
🆘 **Unlimited Bot Yordam**

**Xususiyatlar:**
✅ Katta fayllar (100MB+)
✅ Avtomatik bo'lish (50MB chunks)
✅ Progress tracking
✅ Yuqori sifat

**Qanday ishlaydi:**
1️⃣ Video URL yuboring
2️⃣ Bot hajmni tekshiradi
3️⃣ Katta bo'lsa, bo'laklarga ajratadi
4️⃣ Har bir qismni alohida yuboradi

**Format:** M4A/WebM (eng yaxshi sifat)
**Vaqt:** Hajmiga qarab (2-10 daqiqa)
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube URL'ni qayta ishlash"""
    url = update.message.text.strip()
    
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text(
            "❌ YouTube havolasini yuboring!\n"
            "Bu bot **katta fayllar**ni ham yuklab oladi! 🚀"
        )
        return
    
    status_msg = await update.message.reply_text("🔍 Video ma'lumotlari tekshirilmoqda...")
    
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    duration = f"{info['duration'] // 60}:{info['duration'] % 60:02d}" if info['duration'] else "?"
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    estimated_size = format_file_size(info.get('estimated_size', 0))
    
    # Katta fayl uchun ogohlantirish
    size_warning = ""
    if info.get('estimated_size', 0) > 50*1024*1024:
        parts = math.ceil(info.get('estimated_size', 0) / (45*1024*1024))
        size_warning = f"\n📦 **Katta fayl!** {parts} qismga bo'linadi"
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 {info['uploader']}
⏱ {duration} | 👀 {views}
📊 Taxminiy hajm: {estimated_size}

🎧 **Format:** M4A/WebM (yuqori sifat){size_warning}
    """
    
    keyboard = [
        [InlineKeyboardButton("🚀 Unlimited Yuklab Olish", callback_data=f"download:{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await status_msg.edit_text(video_info_text, parse_mode='Markdown', reply_markup=reply_markup)

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuklab olish tugmasi"""
    query = update.callback_query
    await query.answer()
    
    url = query.data.split(':', 1)[1]
    
    progress_msg = await query.edit_message_text("⏳ Yuklab olish boshlandi... 0%")
    
    # Progress callback
    async def update_progress(percent):
        try:
            await progress_msg.edit_text(f"⏳ Yuklab olinmoqda... {percent}%")
        except:
            pass
    
    # Audio yuklab olish
    file_path, title, file_size = downloader.download_audio(url, update_progress)
    
    if file_path and os.path.exists(file_path):
        try:
            await progress_msg.edit_text(f"📊 Fayl hajmi: {format_file_size(file_size)}")
            
            # Katta fayl bo'lsa bo'lish
            if file_size > 50*1024*1024:
                await progress_msg.edit_text("📦 Katta fayl! Bo'laklarga ajratilmoqda...")
                
                chunks = split_file(file_path)
                await progress_msg.edit_text(f"📤 {len(chunks)} qism yuborilmoqda...")
                
                for i, chunk_path in enumerate(chunks, 1):
                    chunk_size = os.path.getsize(chunk_path)
                    
                    with open(chunk_path, 'rb') as chunk_file:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=chunk_file,
                            filename=f"{title}_part{i}{Path(file_path).suffix}",
                            caption=f"🎵 {title} - Qism {i}/{len(chunks)}\n📊 {format_file_size(chunk_size)}",
                            read_timeout=600,
                            write_timeout=600,
                            connect_timeout=60,
                            pool_timeout=60
                        )
                    
                    # Chunk faylni o'chirish
                    os.remove(chunk_path)
                
                await progress_msg.edit_text(f"✅ {len(chunks)} qism muvaffaqiyatli yuborildi!")
                
            else:
                # Kichik fayl - odatdagidek yuborish
                await progress_msg.edit_text(f"📤 Yuborilmoqda... ({format_file_size(file_size)})")
                
                with open(file_path, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=audio_file,
                        title=title,
                        caption=f"🎵 {title}\n📊 {format_file_size(file_size)}\n✅ Unlimited bot orqali",
                        read_timeout=300,
                        write_timeout=300,
                        connect_timeout=60,
                        pool_timeout=60
                    )
                
                await progress_msg.edit_text("✅ Muvaffaqiyatli yuborildi!")
            
            # Asosiy faylni o'chirish
            os.remove(file_path)
            
        except Exception as e:
            error_msg = str(e)
            if "too large" in error_msg.lower():
                await progress_msg.edit_text("❌ Fayl juda katta! Document sifatida yuboriladi.")
            else:
                await progress_msg.edit_text(f"❌ Xatolik: {error_msg}")
            
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await progress_msg.edit_text(f"❌ Yuklab olishda xatolik: {title}")

def main():
    """Botni ishga tushirish"""
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=60.0,
        read_timeout=600.0,  # 10 daqiqa
        write_timeout=600.0,  # 10 daqiqa
        pool_timeout=60.0
    )
    
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download:"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    print("🚀 MP3 Downloader Bot (Unlimited) ishga tushdi!")
    print("📦 Katta fayllar avtomatik bo'linadi")
    print("⏱ Timeout: 10 daqiqa")
    application.run_polling()

if __name__ == '__main__':
    main()