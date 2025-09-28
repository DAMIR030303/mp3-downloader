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
    """Enhanced audio downloader with YouTube bypass"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'restrictfilenames': True,
            'windowsfilenames': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'extract_flat': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_client': ['android', 'web'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Android 11; Mobile; rv:109.0) Gecko/111.0 Firefox/111.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        }
    
    def get_video_info(self, url: str) -> dict:
        """Get video information with multiple fallback methods"""
        
        # Try different extraction methods with more aggressive bypass
        methods = [
            # Method 1: Android client with cookies simulation
            {
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'skip': ['dash', 'hls'],
                        'player_skip': ['configs', 'webpage']
                    }
                },
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/17.31.35 (Linux; U; Android 11) gzip',
                    'X-YouTube-Client-Name': '3',
                    'X-YouTube-Client-Version': '17.31.35'
                }
            },
            # Method 2: iOS client with different approach
            {
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'skip': ['dash', 'hls'],
                        'player_skip': ['webpage']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
                    'X-YouTube-Client-Name': '5',
                    'X-YouTube-Client-Version': '17.33.2'
                }
            },
            # Method 3: TV client (often bypasses restrictions)
            {
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv_embedded'],
                        'skip': ['dash', 'hls']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebKit/538.1',
                    'X-YouTube-Client-Name': '85'
                }
            },
            # Method 4: Basic web with minimal detection
            {
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_skip': ['configs']
                    }
                }
            }
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                with yt_dlp.YoutubeDL(method) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    if info and info.get('title'):
                        duration = info.get('duration', 0)
                        estimated_size = duration * 128 * 1024 // 8 if duration else 0
                        
                        return {
                            'title': info.get('title', 'Unknown')[:50],
                            'duration': duration,
                            'uploader': info.get('uploader', 'Unknown')[:30],
                            'view_count': info.get('view_count', 0),
                            'estimated_size': estimated_size,
                            'method_used': i
                        }
            except Exception as e:
                logger.warning(f"Method {i} failed: {str(e)[:100]}")
                continue
        
        return {'error': 'Video ma\'lumotlarini olishda xatolik. Boshqa video bilan urinib ko\'ring yoki keyinroq qayta urinib ko\'ring.'}
    
    async def download_media(self, url: str, format_type: str, progress_callback: Optional[Callable] = None) -> Tuple[Optional[str], str, int, int]:
        """Download media from URL with specified format"""
        temp_id = str(uuid.uuid4())[:8]
        temp_file = None
        
        # Format configurations
        ffmpeg_available = bool(shutil.which('ffmpeg'))

        def mp3_config(kbps: str):
            cfg = {
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'extension': 'mp3' if ffmpeg_available else 'm4a'
            }
            if ffmpeg_available:
                cfg['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': kbps,
                }]
            return cfg

        format_configs = {
            'mp3_128': mp3_config('128'),
            'mp3_192': mp3_config('192'),
            'mp3_320': mp3_config('320'),
            'm4a': {
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'extension': 'm4a'
            },
            'best_audio': {
                'format': 'bestaudio/best',
                'extension': 'auto'
            }
        }

        format_config = format_configs.get(format_type, format_configs['best_audio'])
        
        # Try different download methods with format-specific config
        download_methods = [
            # Method 1: Android client
            {
                **self.ydl_opts,
                'format': format_config['format'],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'skip': ['dash', 'hls']
                    }
                },
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/17.31.35 (Linux; U; Android 11) gzip',
                    'X-YouTube-Client-Name': '3',
                    'X-YouTube-Client-Version': '17.31.35'
                }
            },
            # Method 2: TV client
            {
                **self.ydl_opts,
                'format': format_config['format'],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv_embedded'],
                        'skip': ['dash', 'hls']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 2.4.0) AppleWebKit/538.1',
                    'X-YouTube-Client-Name': '85'
                }
            },
            # Method 3: iOS client
            {
                **self.ydl_opts,
                'format': format_config['format'],
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'skip': ['dash', 'hls']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
                    'X-YouTube-Client-Name': '5',
                    'X-YouTube-Client-Version': '17.33.2'
                }
            }
        ]
        
        # Add postprocessors if needed (for MP3 conversion)
        if 'postprocessors' in format_config:
            for method in download_methods:
                method['postprocessors'] = format_config['postprocessors']
        
        for method_num, opts in enumerate(download_methods, 1):
            try:
                opts_copy = opts.copy()
                opts_copy['outtmpl'] = str(downloads_dir / f'temp_{temp_id}_{method_num}.%(ext)s')
                
                if progress_callback:
                    def hook(d):
                        if d['status'] == 'downloading':
                            try:
                                percent = (d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)) * 100
                                asyncio.create_task(progress_callback(int(percent)))
                            except:
                                pass
                    
                    opts_copy['progress_hooks'] = [hook]
                
                with yt_dlp.YoutubeDL(opts_copy) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = sanitize_filename(info.get('title', 'Unknown'))
                    duration = info.get('duration', 0)
                    
                    # Find downloaded file (including post-processed files)
                    possible_extensions = ['.mp3', '.m4a', '.mp4', '.webm', '.opus']
                    if format_config['extension'] != 'auto':
                        possible_extensions = [f".{format_config['extension']}"] + possible_extensions
                    
                    for ext in possible_extensions:
                        pattern = f'temp_{temp_id}_{method_num}*{ext}'
                        files = list(downloads_dir.glob(pattern))
                        if files:
                            temp_file = str(files[0])
                            break
                    
                    if temp_file and os.path.exists(temp_file):
                        # Rename file with appropriate extension
                        file_ext = Path(temp_file).suffix
                        final_file = downloads_dir / f"{title}{file_ext}"
                        counter = 1
                        while final_file.exists():
                            final_file = downloads_dir / f"{title}_{counter}{file_ext}"
                            counter += 1
                        
                        shutil.move(temp_file, final_file)
                        file_size = os.path.getsize(final_file)
                        
                        return str(final_file), title, file_size, duration
                        
            except Exception as e:
                logger.warning(f"Download method {method_num} failed for {format_type}: {str(e)[:100]}")
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                continue
        
        return None, f"{format_type.upper()} formatda yuklab olishda xatolik. Boshqa format yoki video bilan urinib ko'ring.", 0, 0

# Initialize downloader
downloader = AudioDownloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler with developer info"""
    welcome_text = """🎵 Unlimited Audio Bot

✨ Xususiyatlar:
🎯 Har qanday hajmdagi audio yuklab olish
🎼 MP3 formatlar (128kbps, 192kbps, 320kbps)
🎼 Original M4A va eng yaxshi sifat
📊 Katta fayllar uchun qism tanlash
⚡ 24/7 ishlaydigan xizmat

🔥 Qanday ishlaydi:
1️⃣ YouTube URL yuboring
2️⃣ Audio formatni tanlang
3️⃣ Yuklab oling!

👨‍💻 Muallif: N.Damir - Senior Dasturchi
⚡ Python • AI • Telegram Bots

🎯 YouTube havola yuboring! 👇"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """
🆘 **Yordam - @unlimited_audio_bot**

**Foydalanish:**
1. YouTube URL yuboring
2. "🎵 Yuklab olish" tugmasidan formatni tanlang
3. Katta fayl bo'lsa:
   - Qismlar menyusi chiqadi
   - Kerakli qismni tanlang
   - Yoki "🎵 Barchasi"ni bosing

**Qism tanlash misoli:**
```
🎙️ 1-soatlik podcast (500MB)
🎚️ 9 qismga bo'linadi

🎙️ 1-qism (45MB) ~1-10 daq
🎙️ 2-qism (45MB) ~11-20 daq
🎙️ 3-qism (45MB) ~21-30 daq
...
🎵 Barchasi
```

**Formatlar:**
• MP3 128kbps, 192kbps, 320kbps
• M4A original sifat
• Eng yaxshi mavjud audio

**Cheklovlar:**
• Maksimal: Cheklovsiz
• Timeout: 10 daqiqa
• Katta fayllar avtomatik bo'linadi
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URL"""
    url = update.message.text.strip()
    
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text("❌ YouTube havolasini yuboring!")
        return
    
    status_msg = await update.message.reply_text("🔍 Havola tekshirilmoqda...")
    
    info = downloader.get_video_info(url)
    
    if 'error' in info:
        error_msg = info['error']
        
        # Provide helpful suggestions for bot detection errors
        if 'bot' in error_msg.lower() or 'sign in' in error_msg.lower():
            helpful_msg = f"""❌ YouTube bot detection xatoligi

🔧 **Yechimlar:**
1. **Boshqa video** bilan urinib ko'ring
2. **Kichikroq/mashhur videolar** yaxshi ishlaydi  
3. **Bir necha daqiqadan keyin** qayta urinib ko'ring
4. **Qisqa videolar** (5-10 daqiqa) bilan sinab ko'ring

💡 **Test uchun tavsiya:**
• Mashhur music videolar
• Kichik tutorial videolar
• Podcast'ning qisqa qismlari

Keyinroq qayta urinib ko'ring! 🔄"""
        else:
            helpful_msg = f"❌ Xatolik: {error_msg}\n\n💡 Boshqa video bilan urinib ko'ring!"
        
        await status_msg.edit_text(helpful_msg)
        return
    
    duration = format_duration(info['duration'])
    views = f"{info['view_count']:,}" if info['view_count'] else "0"
    estimated_size = format_file_size(info['estimated_size'])
    
    # Store URL in context to avoid callback data issues
    user_id = update.effective_user.id
    context.user_data[f'url_{user_id}'] = url
    
    # Clean title and uploader for display (remove problematic characters)
    clean_title = info['title'].replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')[:60]
    clean_uploader = info['uploader'].replace('*', '').replace('_', '').replace('`', '')[:30]
    
    video_info_text = f"""🎵 {clean_title}

👤 {clean_uploader}
⏱ {duration} | 👀 {views}
📊 ~{estimated_size}

Format tanlang:"""
    
    # Format selection keyboard with short callback data
    keyboard = [
        [
            InlineKeyboardButton("🎵 MP3 128 kbps", callback_data=f"fmt:mp3_128:{user_id}"),
            InlineKeyboardButton("🎶 MP3 192 kbps", callback_data=f"fmt:mp3_192:{user_id}")
        ],
        [
            InlineKeyboardButton("🎧 MP3 320 kbps", callback_data=f"fmt:mp3_320:{user_id}"),
            InlineKeyboardButton("🎼 M4A (Original)", callback_data=f"fmt:m4a:{user_id}")
        ],
        [
            InlineKeyboardButton("💎 Eng yaxshi audio", callback_data=f"fmt:best_audio:{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await status_msg.edit_text(video_info_text, reply_markup=reply_markup)
    except Exception as e:
        # Fallback: send new message if edit fails
        try:
            await status_msg.delete()
        except:
            pass
        await update.message.reply_text(video_info_text, reply_markup=reply_markup)

async def format_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle format selection"""
    query = update.callback_query
    await query.answer()
    
    # Parse callback data: fmt:type:user_id
    parts = query.data.split(':', 2)
    if len(parts) != 3:
        await query.edit_message_text("❌ Noto'g'ri format tanlandi.")
        return
    
    _, format_type, user_id = parts
    
    # Get URL from context
    url = context.user_data.get(f'url_{user_id}')
    if not url:
        await query.edit_message_text("❌ URL topilmadi. Qayta urinib ko'ring.")
        return
    
    # Format display names
    format_names = {
        'mp3_128': '🎵 MP3 128 kbps',
        'mp3_192': '🎶 MP3 192 kbps',
        'mp3_320': '🎧 MP3 320 kbps',
        'm4a': '🎼 M4A (Original)',
        'best_audio': '💎 Eng yaxshi audio'
    }
    
    format_name = format_names.get(format_type, format_type.upper())
    progress_msg = await query.edit_message_text(f"⏳ {format_name} formatda yuklab olinmoqda... 0%")
    
    async def update_progress(percent: int):
        try:
            await progress_msg.edit_text(f"⏳ {format_name} yuklab olinmoqda... {percent}%")
        except:
            pass
    
    file_path, title, file_size, duration = await downloader.download_media(url, format_type, update_progress)
    
    if not file_path:
        await progress_msg.edit_text(f"❌ Xatolik: {title}")
        return
    
    # Clean up URL from context
    try:
        del context.user_data[f'url_{user_id}']
    except:
        pass
    
    try:
        if file_size > MAX_TELEGRAM_SIZE:
            # Show preparing message
            await progress_msg.edit_text(f"📊 Tayyor: {format_file_size(file_size)}\n⚙️ Qismlar tayyorlanmoqda...")
            
            chunks = split_file(file_path, title, duration)
            
            # Show parts selection menu with format info
            keyboard = []
            for chunk in chunks:
                part_text = f"📀 {chunk['part']}-qism | {chunk['size_mb']} | ⏱ {chunk['duration']}"
                keyboard.append([InlineKeyboardButton(part_text, callback_data=f"part:{chunk['path']}")])
            
            keyboard.append([InlineKeyboardButton("📦 Barcha qismlar", callback_data=f"all_parts:{file_path}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            clean_title = title.replace('*', '').replace('_', '').replace('`', '')[:50]
            parts_info = f"""🎵 {clean_title}
📁 Format: {format_name}

📊 Jami hajmi: {format_file_size(file_size)}
⏱ Jami davomiyligi: {format_duration(duration)}
📦 {len(chunks)} qismga bo'lindi

Qaysi qismni tanlaysiz?"""
            
            await progress_msg.edit_text(parts_info, reply_markup=reply_markup)
            
            # Store chunks info for later use
            context.user_data[f'chunks_{query.message.chat_id}'] = chunks
            
        else:
            await progress_msg.edit_text(f"📊 Tayyor: {format_file_size(file_size)}\n📤 Yuborilmoqda...")

            caption = f"🎵 {title[:50]}\n🎧 {format_name}\n📦 {format_file_size(file_size)}\n⏱ {format_duration(duration)}"
            suffix = Path(file_path).suffix.lower()
            audio_suffixes = {'.mp3', '.m4a', '.aac', '.wav', '.flac', '.ogg', '.opus'}

            with open(file_path, 'rb') as media_file:
                if suffix in audio_suffixes:
                    await context.bot.send_audio(
                        chat_id=query.message.chat_id,
                        audio=media_file,
                        title=title,
                        caption=caption,
                        duration=duration if duration else None,
                        read_timeout=UPLOAD_TIMEOUT,
                        write_timeout=UPLOAD_TIMEOUT
                    )
                else:
                    filename = f"{title}{suffix or '.audio'}"
                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=media_file,
                        filename=filename,
                        caption=caption,
                        read_timeout=UPLOAD_TIMEOUT,
                        write_timeout=UPLOAD_TIMEOUT
                    )

            await progress_msg.edit_text(f"✅ {format_name} yuborildi!")
            os.remove(file_path)
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Xatolik: {str(e)[:100]}")
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
    application.add_handler(CallbackQueryHandler(format_callback, pattern="^fmt:"))
    application.add_handler(CallbackQueryHandler(part_callback, pattern="^(part:|all_parts:)"))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(youtube\.com|youtu\.be)'), handle_url))
    
    print("Unlimited Audio Bot (@unlimited_audio_bot) started!")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print("Bot tayyor - Telegram'da /start yuboring!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
