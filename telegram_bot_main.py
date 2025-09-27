#!/usr/bin/env python3
"""
MP3 Downloader Telegram Bot - Main Unified Version
Combines all features with clean, optimized code
"""

import os
import logging
import math
import asyncio
from pathlib import Path
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, CallbackQueryHandler
)
from telegram.request import HTTPXRequest

from config import (
    BOT_TOKEN, MAX_TELEGRAM_SIZE, DOWNLOAD_TIMEOUT, 
    UPLOAD_TIMEOUT, CONNECT_TIMEOUT
)
from downloader import create_downloader
from utils import (
    format_file_size, format_duration, format_number,
    split_file, cleanup_files
)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Main Telegram Bot class"""
    
    def __init__(self):
        self.downloader_modes = {
            'small': 'Kichik hajm (tez)',
            'balanced': 'Muvozanatli (tavsiya)',
            'quality': 'Yuqori sifat',
            'mp3': 'MP3 format'
        }
        self.active_mode = 'balanced'
        self.downloader = create_downloader(self.active_mode)
    
    def switch_mode(self, mode: str):
        """Switch downloader mode"""
        if mode in self.downloader_modes:
            self.active_mode = mode
            self.downloader = create_downloader(mode)
            logger.info(f"Switched to mode: {mode}")

# Initialize bot instance
bot_instance = TelegramBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_text = f"""
🎵 **MP3 Downloader Bot** - Universal Edition

**🚀 Xususiyatlar:**
• Har qanday hajmdagi video yuklab olish
• Avtomatik fayl bo'lish (50MB+)
• 4 xil sifat rejimi
• Progress tracking
• FFmpeg MP3 konvertatsiya

**⚙️ Joriy rejim:** {bot_instance.downloader_modes[bot_instance.active_mode]}

**📋 Buyruqlar:**
/start - Botni qayta boshlash
/help - Yordam
/mode - Rejimni o'zgartirish

**YouTube havola yuboring!** 👇
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """
🆘 **Yordam - MP3 Downloader Bot**

**🔧 Rejimlar:**
• **Kichik hajm** - Eng tez, kichik fayllar
• **Muvozanatli** - Sifat va hajm muvozanati (tavsiya)
• **Yuqori sifat** - Eng yaxshi sifat, katta hajm
• **MP3 format** - Har doim MP3 (FFmpeg kerak)

**📤 Fayl yuborish:**
• < 50MB: Audio sifatida
• > 50MB: Avtomatik bo'linib, Document sifatida

**⏱ Timeout:** 10 daqiqa
**📊 Maksimal hajm:** Cheklovsiz

**🎯 Foydalanish:**
1. Rejimni tanlang (/mode)
2. YouTube URL yuboring
3. Yuklab olish tugmasini bosing
4. Kutib turing!

**💡 Maslahat:** Tez yuklab olish uchun "Kichik hajm" rejimini ishlating.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mode selection command"""
    keyboard = []
    for mode_key, mode_name in bot_instance.downloader_modes.items():
        emoji = "✅" if mode_key == bot_instance.active_mode else "⚪"
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {mode_name}", 
                callback_data=f"mode:{mode_key}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚙️ **Rejim tanlang:**\n\nJoriy: {bot_instance.downloader_modes[bot_instance.active_mode]}",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URL"""
    url = update.message.text.strip()
    
    # Validate URL
    if not ('youtube.com' in url or 'youtu.be' in url):
        await update.message.reply_text(
            "❌ Iltimos, to'g'ri YouTube havolasini yuboring!\n\n"
            "Masalan: https://youtube.com/watch?v=abc123"
        )
        return
    
    # Get video info
    status_msg = await update.message.reply_text("🔍 Video ma'lumotlari olinmoqda...")
    
    info = bot_instance.downloader.get_video_info(url)
    
    if 'error' in info:
        await status_msg.edit_text(f"❌ Xatolik: {info['error']}")
        return
    
    # Format video info
    duration = format_duration(info['duration'])
    views = format_number(info['view_count'])
    estimated_size = format_file_size(info['estimated_size'])
    
    # Estimate parts if large file
    parts_info = ""
    if info['estimated_size'] > MAX_TELEGRAM_SIZE:
        parts = math.ceil(info['estimated_size'] / (45*1024*1024))
        parts_info = f"\n📦 **{parts} qismga bo'linadi**"
    
    mode_info = bot_instance.downloader_modes[bot_instance.active_mode]
    
    video_info_text = f"""
🎵 **{info['title']}**

👤 **Kanal:** {info['uploader']}
⏱ **Davomiyligi:** {duration}
👀 **Ko'rishlar:** {views}
📊 **Taxminiy hajm:** ~{estimated_size}

⚙️ **Rejim:** {mode_info}{parts_info}

📝 **Tavsif:** {info.get('description', 'Mavjud emas')[:100]}...
    """
    
    keyboard = [
        [InlineKeyboardButton("🎵 Yuklab Olish", callback_data=f"download:{url}")],
        [InlineKeyboardButton("⚙️ Rejim", callback_data="mode_inline")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await status_msg.edit_text(
        video_info_text, 
        parse_mode='Markdown', 
        reply_markup=reply_markup
    )

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle download button press"""
    query = update.callback_query
    await query.answer()
    
    url = query.data.split(':', 1)[1]
    
    progress_msg = await query.edit_message_text("⏳ Yuklab olish boshlandi... 0%")
    
    # Progress callback
    async def update_progress(percent: int, stage: str = "Processing"):
        try:
            await progress_msg.edit_text(f"⏳ {stage}... {percent}%")
        except:
            pass  # Ignore rate limit errors
    
    # Download audio
    file_path, title, file_size = await bot_instance.downloader.download_audio(
        url, update_progress
    )
    
    if not file_path or not os.path.exists(file_path):
        await progress_msg.edit_text(f"❌ Yuklab olishda xatolik: {title}")
        return
    
    try:
        await progress_msg.edit_text(f"📊 Fayl tayyor: {format_file_size(file_size)}")
        
        # Handle large files
        if file_size > MAX_TELEGRAM_SIZE:
            await progress_msg.edit_text("📦 Katta fayl! Bo'laklarga ajratilmoqda...")
            
            chunks = split_file(file_path)
            total_chunks = len(chunks)
            
            await progress_msg.edit_text(f"📤 {total_chunks} qism yuborilmoqda...")
            
            # Send chunks
            for i, chunk_path in enumerate(chunks, 1):
                chunk_size = os.path.getsize(chunk_path)
                
                await progress_msg.edit_text(f"📤 Yuborilmoqda... ({i}/{total_chunks})")
                
                with open(chunk_path, 'rb') as chunk_file:
                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=chunk_file,
                        filename=f"{title}_part{i}{Path(file_path).suffix}",
                        caption=(
                            f"🎵 **{title}** - Qism {i}/{total_chunks}\n"
                            f"📊 {format_file_size(chunk_size)}\n"
                            f"⚙️ {bot_instance.downloader_modes[bot_instance.active_mode]}"
                        ),
                        parse_mode='Markdown',
                        read_timeout=UPLOAD_TIMEOUT,
                        write_timeout=UPLOAD_TIMEOUT,
                        connect_timeout=CONNECT_TIMEOUT,
                        pool_timeout=CONNECT_TIMEOUT
                    )
            
            # Cleanup chunks
            cleanup_files(*chunks)
            
            await progress_msg.edit_text(
                f"✅ {total_chunks} qism muvaffaqiyatli yuborildi!\n"
                f"⚙️ {bot_instance.downloader_modes[bot_instance.active_mode]} rejimi"
            )
            
        else:
            # Send as audio
            await progress_msg.edit_text(f"📤 Audio yuborilmoqda... ({format_file_size(file_size)})")
            
            with open(file_path, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=audio_file,
                    title=title,
                    performer="YouTube",
                    caption=(
                        f"🎵 {title}\n"
                        f"📊 {format_file_size(file_size)}\n"
                        f"⚙️ {bot_instance.downloader_modes[bot_instance.active_mode]}"
                    ),
                    read_timeout=UPLOAD_TIMEOUT,
                    write_timeout=UPLOAD_TIMEOUT,
                    connect_timeout=CONNECT_TIMEOUT,
                    pool_timeout=CONNECT_TIMEOUT
                )
            
            await progress_msg.edit_text("✅ Audio muvaffaqiyatli yuborildi!")
        
        # Cleanup main file
        cleanup_files(file_path)
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        await progress_msg.edit_text(f"❌ Yuborishda xatolik: {str(e)}")
        cleanup_files(file_path)

async def mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mode selection callback"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "mode_inline":
        # Show mode selection inline
        keyboard = []
        for mode_key, mode_name in bot_instance.downloader_modes.items():
            emoji = "✅" if mode_key == bot_instance.active_mode else "⚪"
            keyboard.append([
                InlineKeyboardButton(
                    f"{emoji} {mode_name}", 
                    callback_data=f"mode:{mode_key}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⚙️ **Rejim tanlang:**\n\nJoriy: {bot_instance.downloader_modes[bot_instance.active_mode]}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        # Switch mode
        mode = query.data.split(':', 1)[1]
        bot_instance.switch_mode(mode)
        
        await query.edit_message_text(
            f"✅ Rejim o'zgartirildi: **{bot_instance.downloader_modes[mode]}**\n\n"
            "Endi YouTube havola yuboring!",
            parse_mode='Markdown'
        )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-URL messages"""
    await update.message.reply_text(
        "🤖 Men faqat YouTube havolalarini tushunaman!\n\n"
        "💡 **Maslahat:** /mode buyrug'i bilan sifat rejimini o'zgartiring.\n\n"
        "YouTube video havolasini yuboring:\n"
        "• https://youtube.com/watch?v=abc123\n"
        "• https://youtu.be/abc123"
    )

def main():
    """Main function to start the bot"""
    # Setup HTTP request with timeouts
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=CONNECT_TIMEOUT,
        read_timeout=DOWNLOAD_TIMEOUT,
        write_timeout=UPLOAD_TIMEOUT,
        pool_timeout=CONNECT_TIMEOUT
    )
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mode", mode_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download:"))
    application.add_handler(CallbackQueryHandler(mode_callback, pattern="^mode"))
    
    # Message handlers
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'(youtube\.com|youtu\.be)'),
        handle_url
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_other_messages
    ))
    
    # Start bot
    print("🎵 MP3 Downloader Bot (Universal Edition) ishga tushdi!")
    print(f"⚙️ Joriy rejim: {bot_instance.downloader_modes[bot_instance.active_mode]}")
    print(f"📦 Katta fayllar avtomatik bo'linadi")
    print(f"⏱ Timeout: {DOWNLOAD_TIMEOUT//60} daqiqa")
    print("🚀 Bot tayyor! Telegram'da /start yuboring.")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()