#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - Production Deploy Version
Minimal version for Railway/Heroku deployment
"""

import os
import logging
import math
import asyncio
import re
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple, Callable
import tempfile

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, CallbackQueryHandler
)
from telegram.request import HTTPXRequest
import yt_dlp

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHUNK_SIZE = 45 * 1024 * 1024  # 45MB
MAX_TELEGRAM_SIZE = 50 * 1024 * 1024  # 50MB
DOWNLOAD_TIMEOUT = 600  # 10 minutes
UPLOAD_TIMEOUT = 600

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create downloads directory
downloads_dir = Path("downloads")
downloads_dir.mkdir(exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Clean filename for cross-platform compatibility"""
    filename = re.sub(r'[<>:"/\\|?*⧸@._-]', '', filename)
    filename = re.sub(r'\s+', ' ', filename)
    filename = filename.strip('. ')
    return filename[:30]

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

def format_duration(seconds: int) -> str:
    """Format duration in MM:SS format"""
    if not seconds:
        return "Unknown"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"

def split_file(file_path: str) -> list:
    """Split large file into chunks"""
    chunks = []
    file_size = os.path.getsize(file_path)
    
    if file_size <= MAX_TELEGRAM_SIZE:
        return [file_path]
    
    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_data = f.read(CHUNK_SIZE)
            if not chunk_data:
                break
            
            chunk_filename = f"{file_path}.part{chunk_num+1}"
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            chunks.append(chunk_filename)
            chunk_num += 1
    
    return chunks

class AudioDownloader:
    """Simple audio downloader"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'windowsfilenames': True,
        }
    
    def get_video_info(self, url: str) -> dict:
        """Get video information"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                duration = info.get('duration', 0)
                estimated_size = duration * 128 * 1024 // 8 if duration else 0
                
                return {
                    'title': info.get('title', 'Unknown')[:50],
                    'duration': duration,
                    'uploader': info.get('uploader', 'Unknown')[:30],
                    'view_count': info.get('view_count', 0),
                    'estimated_size': estimated_size,
                }
        except Exception as e:
            return {'error': str(e)}
    
    async def download_audio(self, url: str, progress_callback: Optional[Callable] = None) -> Tuple[Optional[str], str, int]:
        """Download audio from URL"""
        temp_id = str(uuid.uuid4())[:8]
        temp_file = None
        
        try:
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = str(downloads_dir / f'temp_{temp_id}.%(ext)s')
            
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
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'Unknown'))
                
                # Find downloaded file
                for file_path in downloads_dir.glob(f'temp_{temp_id}.*'):
                    if file_path.suffix in ['.webm', '.m4a', '.mp3', '.opus']:
                        temp_file = str(file_path)
                        break
                
                if not temp_file:
                    return None, "File not found", 0
                
                # Rename file
                final_file = downloads_dir / f"{title}{Path(temp_file).suffix}"
                counter = 1
                while final_file.exists():
                    final_file = downloads_dir / f"{title}_{counter}{Path(temp_file).suffix}"
                    counter += 1
                
                shutil.move(temp_file, final_file)
                file_size = os.path.getsize(final_file)
                
                return str(final_file), title, file_size
                
        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            return None, str(e), 0

# Initialize downloader
downloader = AudioDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_text = """
🚀 **Unlimited Audio Bot**

**Xususiyatlar:**
• Har qanday hajmdagi video yuklab olish
• Avtomatik fayl bo'lish (50MB+)
• Progress tracking
• 24/7 ishlaydi

**YouTube havola yuboring!** 👇
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """
🆘 **Yordam**

**Foydalanish:**
1. YouTube URL yuboring
2. "Yuklab olish" tugmasini bosing
3. Kutib turing!

**Cheklovlar:**
• Maksimal: Cheklovsiz
• 50MB+ fayllar bo'linadi
• Timeout: 10 daqiqa

**Format:** M4A/WebM (eng yaxshi sifat)
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URL"""
    url = update.message.text.strip()
    
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text("❌ YouTube havolasini yuboring!")
        return
    
    status_msg = await update.message.reply_text("🔍 Video tekshirilmoqda...")
    
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    duration = format_duration(info['duration'])
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    estimated_size = format_file_size(info['estimated_size'])
    
    parts_info = ""
    if info['estimated_size'] > MAX_TELEGRAM_SIZE:
        parts = math.ceil(info['estimated_size'] / CHUNK_SIZE)
        parts_info = f"\n📦 **{parts} qismga bo'linadi**"
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 {info['uploader']}
⏱ {duration} | 👀 {views}
📊 ~{estimated_size}{parts_info}
    """
    
    keyboard = [[InlineKeyboardButton("🎵 Yuklab Olish", callback_data=f"download:{url}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await status_msg.edit_text(video_info_text, parse_mode='Markdown', reply_markup=reply_markup)

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle download button press"""
    query = update.callback_query
    await query.answer()
    
    url = query.data.split(':', 1)[1]
    progress_msg = await query.edit_message_text("⏳ Yuklab olish boshlandi... 0%")
    
    async def update_progress(percent: int):
        try:
            await progress_msg.edit_text(f"⏳ Yuklab olinmoqda... {percent}%")
        except:
            pass
    
    file_path, title, file_size = await downloader.download_audio(url, update_progress)
    
    if not file_path:
        await progress_msg.edit_text(f"❌ Xatolik: {title}")
        return
    
    try:
        await progress_msg.edit_text(f"📊 Tayyor: {format_file_size(file_size)}")
        
        if file_size > MAX_TELEGRAM_SIZE:
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
                        read_timeout=UPLOAD_TIMEOUT,
                        write_timeout=UPLOAD_TIMEOUT
                    )
                
                os.remove(chunk_path)
            
            await progress_msg.edit_text(f"✅ {len(chunks)} qism yuborildi!")
        else:
            with open(file_path, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_file,
                    title=title,
                    caption=f"🎵 {title}\n📊 {format_file_size(file_size)}",
                    read_timeout=UPLOAD_TIMEOUT,
                    write_timeout=UPLOAD_TIMEOUT
                )
            
            await progress_msg.edit_text("✅ Audio yuborildi!")
        
        os.remove(file_path)
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Xatolik: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    """Main function"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN environment variable not set!")
        return
    
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=60.0,
        read_timeout=DOWNLOAD_TIMEOUT,
        write_timeout=UPLOAD_TIMEOUT,
        pool_timeout=60.0
    )
    
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download:"))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(youtube\.com|youtu\.be)'), handle_url))
    
    print("🚀 Unlimited Audio Bot started on Railway!")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()