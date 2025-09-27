#!/bin/bash

# MP3 Downloader - Railway Deploy Script
echo "🚀 Starting MP3 Downloader on Railway..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_clean.txt

# Check if bot token is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN environment variable not set!"
    echo "Please set BOT_TOKEN in Railway environment variables"
    exit 1
fi

echo "✅ BOT_TOKEN found: ${BOT_TOKEN:0:10}..."

# Start the telegram bot
echo "🤖 Starting Telegram Bot..."
python telegram_bot_main.py