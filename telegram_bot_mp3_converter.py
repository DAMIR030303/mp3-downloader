#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - MP3 konverter bilan (katta fayllar uchun)
"""

import os
import tempfile
import logging
import re
import shutil
import asyncio
import math
import subprocess
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

def convert_to_mp3(input_file, output_file, bitrate="128k"):
    """FFmpeg orqali MP3'ga konvertatsiya qilish"""
    try:
        cmd = [
            'ffmpeg', '-i', input_file,
            '-acodec', 'mp3',
            '-ab', bitrate,
            '-ar', '44100',
            '-y',  # Overwrite
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Konvertatsiya muvaffaqiyatli"
        else:
            return False, result.stderr
            
    except FileNotFoundError:
        return False, "FFmpeg topilmadi. O'rnatish kerak."
    except Exception as e:
        return False, str(e)

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
        
        # Eng yaxshi sifat, keyin MP3 ga konvert qilamiz
        self.ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'restrictfilenames': True,
            'windowsfilenames': True,
        }
    
    def get_video_info(self, url):
        """Video haqida ma'lumot olish"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                duration = info.get('duration', 0)
                # MP3 128kbps uchun taxminiy hajm
                estimated_mp3_size = duration * 128 * 1024 / 8 if duration else 0
                
                return {
                    'title': info.get('title', 'Unknown')[:50],
                    'duration': duration,
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown')[:30],
                    'view_count': info.get('view_count', 0),
                    'estimated_size': estimated_mp3_size
                }
        except Exception as e:
            return {'error': str(e)}
    
    def download_and_convert(self, url, progress_callback=None):
        """Audio yuklab olish va MP3'ga konvertatsiya qilish"""
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
                            percent = (d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)) * 50  # 50% yuklab olish uchun
                            asyncio.create_task(progress_callback(int(percent), "Yuklab olinmoqda"))
                        except:
                            pass
                
                opts['progress_hooks'] = [hook]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f"Audio yuklab olish: {url}")
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'Unknown'))
                
                # Yuklab olingan faylni topish
                source_file = None
                for file_path in self.downloads_dir.glob(f'audio_{temp_id}.*'):
                    if file_path.suffix in ['.webm', '.m4a', '.mp3', '.opus']:
                        source_file = str(file_path)
                        break
                
                if not source_file:
                    return None, "Fayl topilmadi", 0
                
                # MP3'ga konvertatsiya qilish
                if progress_callback:
                    asyncio.create_task(progress_callback(60, "MP3'ga konvertatsiya qilinmoqda"))
                
                mp3_file = str(self.downloads_dir / f"{title}.mp3")
                success, message = convert_to_mp3(source_file, mp3_file, "128k")
                
                if not success:
                    logger.error(f"Konvertatsiya xatoligi: {message}")
                    # FFmpeg bo'lmasa original faylni qaytaramiz
                    final_file = str(self.downloads_dir / f"{title}{Path(source_file).suffix}")
                    shutil.move(source_file, final_file)
                    file_size = os.path.getsize(final_file)
                    return final_file, title, file_size
                
                # Original faylni o'chirish
                os.remove(source_file)
                
                if progress_callback:
                    asyncio.create_task(progress_callback(100, "Tayyor"))
                
                file_size = os.path.getsize(mp3_file)
                logger.info(f"MP3 yaratildi: {mp3_file}, hajmi: {format_file_size(file_size)}")
                
                return mp3_file, title, file_size
                
        except Exception as e:
            logger.error(f"Yuklab olishda xatolik: {e}")
            return None, str(e), 0

downloader = TelegramAudioDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot boshlanganda ko'rsatiladigan xabar"""
    welcome_text = """
🎵 **MP3 Downloader Bot** (MP3 Konverter)

**Xususiyatlar:**
🎧 Har doim MP3 format (128kbps)
📦 Katta fayllar avtomatik bo'linadi
⚡ FFmpeg konvertatsiya
🔄 Progress tracking

**FFmpeg status:**
MP3 konvertatsiya qo'llab-quvvatlanadi

**Qo'llab-quvvatlash:**
• Har qanday hajmdagi video
• Avtomatik MP3 128kbps
• Katta fayllar bo'linadi

YouTube havola yuboring! 👇
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyruqi"""
    help_text = """
🆘 **MP3 Konverter Bot**

**Jarayon:**
1️⃣ YouTube'dan eng yaxshi sifat yuklab oladi
2️⃣ FFmpeg orqali MP3 128kbps ga konvert qiladi
3️⃣ Katta bo'lsa 45MB qismlarga bo'ladi
4️⃣ Har bir qismni yuboradi

**Format:** 
• **Chiqish:** MP3 (128kbps, 44.1kHz)
• **Sifat:** Universal, barcha playerlar
• **Hajm:** Optimal (video uzunligi * 1MB/min)

**Afzalliklari:**
✅ Har doim MP3 format
✅ Katta fayllar ham ishlaydi
✅ Universal qo'llab-quvvatlash
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube URL'ni qayta ishlash"""
    url = update.message.text.strip()
    
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text(
            "❌ YouTube havolasini yuboring!\n"
            "Bu bot **MP3 formatda** audio yaratadi! 🎵"
        )
        return
    
    status_msg = await update.message.reply_text("🔍 Video ma'lumotlari olınmoqda...")
    
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    duration = f"{info['duration'] // 60}:{info['duration'] % 60:02d}" if info['duration'] else "?"
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    estimated_mp3_size = format_file_size(info.get('estimated_size', 0))
    
    # Katta fayl uchun ma'lumot
    parts_info = ""
    if info.get('estimated_size', 0) > 50*1024*1024:
        parts = math.ceil(info.get('estimated_size', 0) / (45*1024*1024))
        parts_info = f"\n📦 **{parts} qismga bo'linadi**"
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 {info['uploader']}
⏱ {duration} | 👀 {views}
📊 MP3 hajmi: ~{estimated_mp3_size}

🎧 **Format:** MP3 (128kbps, 44.1kHz)
⚡ **Konverter:** FFmpeg{parts_info}
    """
    
    keyboard = [
        [InlineKeyboardButton("🎵 MP3 Yuklab Olish", callback_data=f"download:{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await status_msg.edit_text(video_info_text, parse_mode='Markdown', reply_markup=reply_markup)

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuklab olish tugmasi"""
    query = update.callback_query
    await query.answer()
    
    url = query.data.split(':', 1)[1]
    
    progress_msg = await query.edit_message_text("⏳ Jarayon boshlandi... 0%")
    
    # Progress callback
    async def update_progress(percent, stage="Yuklab olinmoqda"):
        try:
            await progress_msg.edit_text(f"⏳ {stage}... {percent}%")
        except:
            pass
    
    # Audio yuklab olish va konvertatsiya
    file_path, title, file_size = downloader.download_and_convert(url, update_progress)
    
    if file_path and os.path.exists(file_path):
        try:
            await progress_msg.edit_text(f"📊 MP3 tayyor: {format_file_size(file_size)}")
            
            # Katta fayl bo'lsa bo'lish
            if file_size > 50*1024*1024:
                await progress_msg.edit_text("📦 Katta MP3! Bo'laklarga ajratilmoqda...")
                
                chunks = split_file(file_path)
                await progress_msg.edit_text(f"📤 {len(chunks)} qism MP3 yuborilmoqda...")
                
                for i, chunk_path in enumerate(chunks, 1):
                    chunk_size = os.path.getsize(chunk_path)
                    
                    with open(chunk_path, 'rb') as chunk_file:
                        await context.bot.send_audio(
                            chat_id=query.message.chat_id,
                            audio=chunk_file,
                            title=f"{title} - Qism {i}",
                            performer="MP3 Downloader Bot",
                            caption=f"🎵 {title} - Qism {i}/{len(chunks)}\n📊 {format_file_size(chunk_size)} | MP3 128kbps",
                            read_timeout=600,
                            write_timeout=600,
                            connect_timeout=60,
                            pool_timeout=60
                        )
                    
                    os.remove(chunk_path)
                
                await progress_msg.edit_text(f"✅ {len(chunks)} qism MP3 yuborildi!")
                
            else:
                # Kichik fayl - odatdagidek yuborish
                await progress_msg.edit_text(f"📤 MP3 yuborilmoqda... ({format_file_size(file_size)})")
                
                with open(file_path, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=audio_file,
                        title=title,
                        performer="YouTube",
                        caption=f"🎵 {title}\n📊 {format_file_size(file_size)} | MP3 128kbps\n✅ FFmpeg konverter",
                        read_timeout=300,
                        write_timeout=300,
                        connect_timeout=60,
                        pool_timeout=60
                    )
                
                await progress_msg.edit_text("✅ MP3 muvaffaqiyatli yuborildi!")
            
            # Faylni o'chirish
            os.remove(file_path)
            
        except Exception as e:
            error_msg = str(e)
            await progress_msg.edit_text(f"❌ Xatolik: {error_msg}")
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await progress_msg.edit_text(f"❌ Xatolik: {title}")

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
    
    print("🎵 MP3 Downloader Bot (MP3 Konverter) ishga tushdi!")
    print("🔄 FFmpeg konvertatsiya: MP3 128kbps")
    print("📦 Katta fayllar avtomatik bo'linadi")
    application.run_polling()

if __name__ == '__main__':
    main()