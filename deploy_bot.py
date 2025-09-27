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

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    """Format duration in MM:SS or HH:MM:SS format"""
    if seconds is None:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def calculate_part_duration(total_duration: int, part_num: int, total_parts: int) -> str:
    """Calculate estimated duration for each part"""
    if not total_duration or total_parts <= 0:
        return "Unknown"
    
    duration_per_part = total_duration / total_parts
    start_time = int((part_num - 1) * duration_per_part)
    end_time = int(min(part_num * duration_per_part, total_duration))
    
    start_formatted = format_duration(start_time)
    end_formatted = format_duration(end_time)
    
    return f"{start_formatted}-{end_formatted}"

def split_file(file_path: str, title: str, total_duration: int = 0) -> list:
    """Split large file into chunks with detailed metadata"""
    chunks = []
    file_size = os.path.getsize(file_path)
    
    if file_size <= MAX_TELEGRAM_SIZE:
        return [{'path': file_path, 'part': 1, 'total': 1, 'size': file_size, 'title': title, 'duration': format_duration(total_duration) if total_duration else "Unknown"}]
    
    total_parts = math.ceil(file_size / CHUNK_SIZE)
    
    with open(file_path, 'rb') as f:
        for part_num in range(total_parts):
            chunk_data = f.read(CHUNK_SIZE)
            if not chunk_data:
                break
            
            chunk_filename = f"{file_path}.part{part_num+1}"
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            
            # Calculate duration for this part
            part_duration = calculate_part_duration(total_duration, part_num + 1, total_parts)
            
            chunks.append({
                'path': chunk_filename,
                'part': part_num + 1,
                'total': total_parts,
                'size': len(chunk_data),
                'title': title,
                'duration': part_duration,
                'size_mb': f"{len(chunk_data)/(1024*1024):.1f} MB"
            })
    
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
    
    async def download_audio(self, url: str, progress_callback: Optional[Callable] = None) -> Tuple[Optional[str], str, int, int]:
        """Download audio from URL - returns file_path, title, file_size, duration"""
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
                duration = info.get('duration', 0)
                
                # Find downloaded file
                for file_path in downloads_dir.glob(f'temp_{temp_id}.*'):
                    if file_path.suffix in ['.webm', '.m4a', '.mp3', '.opus']:
                        temp_file = str(file_path)
                        break
                
                if not temp_file:
                    return None, "File not found", 0, 0
                
                # Rename file
                final_file = downloads_dir / f"{title}{Path(temp_file).suffix}"
                counter = 1
                while final_file.exists():
                    final_file = downloads_dir / f"{title}_{counter}{Path(temp_file).suffix}"
                    counter += 1
                
                shutil.move(temp_file, final_file)
                file_size = os.path.getsize(final_file)
                
                return str(final_file), title, file_size, duration
                
        except Exception as e:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            return None, str(e), 0, 0

# Initialize downloader
downloader = AudioDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_text = """
🚀 **Unlimited Audio Bot (@unlimited_audio_bot)**

**Xususiyatlar:**
• Har qanday hajmdagi video yuklab olish
• Katta fayllar uchun aniq qism tanlash
• Har bir qism uchun aniq vaqt va hajm ko'rsatish
• Professional progress tracking
• 24/7 ishlaydigan xizmat

**Qanday ishlaydi:**
1. **Kichik fayllar (<50MB)** - Darhol yuboriladi
2. **Katta fayllar (>50MB)** - Qismlar menyusi:

**Yangilangan misol: 9 qismga bo'lingan video**
```
📊 Jami hajmi: 500.0 MB
⏱ Jami davomiyligi: 1:30:00
📦 9 qismga bo'lindi

📀 1-qism | 45.0 MB | ⏱ 0:00-10:00
📀 2-qism | 45.0 MB | ⏱ 10:00-20:00
📀 3-qism | 45.0 MB | ⏱ 20:00-30:00
...
📦 Barcha qismlar
```

**YouTube havola yuboring!** 👇
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """
🆘 **Yordam - @unlimited_audio_bot**

**Foydalanish:**
1. YouTube URL yuboring
2. "🎵 Yuklab olish" tugmasini bosing
3. Agar fayl katta bo'lsa:
   - Qismlar menyusi ko'rinadi
   - Kerakli qismni tanlang
   - Yoki "📦 Barchasi" ni bosing

**Qism tanlash misoli:**
```
🎵 1-soatlik podcast (500MB)
📦 9 qismga bo'lindi

📀 1-qism (45MB) ~1-10 daq
📀 2-qism (45MB) ~11-20 daq  
📀 3-qism (45MB) ~21-30 daq
...
📦 Barchasi
```

**Cheklovlar:**
• Maksimal: Cheklovsiz
• Timeout: 10 daqiqa
• Format: M4A/WebM (best quality)
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
    
    file_path, title, file_size, duration = await downloader.download_audio(url, update_progress)
    
    if not file_path:
        await progress_msg.edit_text(f"❌ Xatolik: {title}")
        return
    
    try:
        if file_size > MAX_TELEGRAM_SIZE:
            # Show preparing message
            await progress_msg.edit_text(f"📊 Tayyor: {format_file_size(file_size)}\n⚙️ Qismlar tayyorlanmoqda...")
            
            chunks = split_file(file_path, title, duration)
            
            # Show parts selection menu with detailed info
            keyboard = []
            for chunk in chunks:
                part_text = f"📀 {chunk['part']}-qism | {chunk['size_mb']} | ⏱ {chunk['duration']}"
                keyboard.append([InlineKeyboardButton(part_text, callback_data=f"part:{chunk['path']}")])
            
            keyboard.append([InlineKeyboardButton("📦 Barcha qismlar", callback_data=f"all_parts:{file_path}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            parts_info = f"""🎵 **{title}**

📊 Jami hajmi: {format_file_size(file_size)}
⏱ Jami davomiyligi: {format_duration(duration)}
📦 {len(chunks)} qismga bo'lindi

**Qaysi qismni tanlaysiz?**"""
            
            await progress_msg.edit_text(
                parts_info,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Store chunks info for later use
            context.user_data[f'chunks_{query.message.chat_id}'] = chunks
            
        else:
            await progress_msg.edit_text(f"📊 Tayyor: {format_file_size(file_size)}\n📤 Yuborilmoqda...")
            
            with open(file_path, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_file,
                    title=title,
                    caption=f"🎵 {title}\n📊 {format_file_size(file_size)}\n⏱ {format_duration(duration)}",
                    read_timeout=UPLOAD_TIMEOUT,
                    write_timeout=UPLOAD_TIMEOUT
                )
            
            await progress_msg.edit_text("✅ Audio yuborildi!")
            os.remove(file_path)
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Xatolik: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)

async def part_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle part selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("part:"):
        part_path = query.data.split(':', 1)[1]
        
        try:
            await query.edit_message_text("📤 Tanlangan qism tayyor qilinmoqda...")
            
            part_size = os.path.getsize(part_path)
            part_name = Path(part_path).name
            
            # Get chunk info from stored data
            chunks_key = f'chunks_{query.message.chat_id}'
            chunk_info = None
            if chunks_key in context.user_data:
                chunks = context.user_data[chunks_key]
                for chunk in chunks:
                    if chunk['path'] == part_path:
                        chunk_info = chunk
                        break
            
            await query.edit_message_text("📤 Tanlangan qism yuborilmoqda...")
            
            caption = f"🎵 Tanlangan qism\n📊 {format_file_size(part_size)}"
            if chunk_info:
                caption += f"\n📀 Qism {chunk_info['part']}/{chunk_info['total']}\n⏱ Davomiyligi: {chunk_info['duration']}"
            
            with open(part_path, 'rb') as part_file:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=part_file,
                    filename=part_name,
                    caption=caption,
                    read_timeout=UPLOAD_TIMEOUT,
                    write_timeout=UPLOAD_TIMEOUT
                )
            
            await query.edit_message_text("✅ Tanlangan qism yuborildi!")
            
            # Clean up the part file
            os.remove(part_path)
            
        except Exception as e:
            await query.edit_message_text(f"❌ Xatolik: {str(e)}")
    
    elif query.data.startswith("all_parts:"):
        file_path = query.data.split(':', 1)[1]
        chunks_key = f'chunks_{query.message.chat_id}'
        
        if chunks_key in context.user_data:
            chunks = context.user_data[chunks_key]
            
            await query.edit_message_text(f"📤 Barcha {len(chunks)} qism tayyorlanmoqda...")
            
            total_sent = 0
            for i, chunk in enumerate(chunks, 1):
                try:
                    # Update progress
                    await query.edit_message_text(f"📤 {i}/{len(chunks)}-qism yuborilmoqda...")
                    
                    chunk_size = os.path.getsize(chunk['path'])
                    chunk_name = f"{chunk['title']}_part{chunk['part']}{Path(file_path).suffix}"
                    
                    with open(chunk['path'], 'rb') as chunk_file:
                        await context.bot.send_document(
                            chat_id=query.message.chat_id,
                            document=chunk_file,
                            filename=chunk_name,
                            caption=f"🎵 {chunk['title']}\n📀 Qism {chunk['part']}/{chunk['total']}\n📊 {chunk['size_mb']}\n⏱ {chunk['duration']}",
                            read_timeout=UPLOAD_TIMEOUT,
                            write_timeout=UPLOAD_TIMEOUT
                        )
                    
                    os.remove(chunk['path'])
                    total_sent += 1
                    
                except Exception as e:
                    logger.error(f"Error sending chunk {chunk['part']}: {e}")
            
            await query.edit_message_text(f"✅ Barcha {total_sent} qism muvaffaqiyatli yuborildi!")
            
            # Clean up original file and chunks data
            if os.path.exists(file_path):
                os.remove(file_path)
            del context.user_data[chunks_key]

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
    application.add_handler(CallbackQueryHandler(part_callback, pattern="^(part:|all_parts:)"))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(youtube\.com|youtu\.be)'), handle_url))
    
    print("🚀 Unlimited Audio Bot (@unlimited_audio_bot) started on Railway!")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    print("📱 Bot tayyor - Telegram'da /start yuboring!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()