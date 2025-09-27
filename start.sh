#!/bin/bash

# MP3 Downloader - Railway Start Script
echo "🚀 Starting MP3 Downloader Bot on Railway..."

# Check if bot token is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN environment variable not set!"
    echo "Please set BOT_TOKEN in Railway dashboard"
    exit 1
fi

echo "✅ BOT_TOKEN configured"
echo "🤖 Starting Unlimited Audio Bot..."

# Start the telegram bot
exec python telegram_bot_main.py