"""
MP3 Downloader - Configuration file
"""

import os
from pathlib import Path

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
TELEGRAM_DOWNLOADS_DIR = BASE_DIR / "telegram_downloads"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Create directories
DOWNLOADS_DIR.mkdir(exist_ok=True)
TELEGRAM_DOWNLOADS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# Audio Settings
AUDIO_FORMATS = ['.m4a', '.mp3', '.webm', '.opus']
DEFAULT_BITRATE = "128k"
CHUNK_SIZE = 45 * 1024 * 1024  # 45MB
MAX_TELEGRAM_SIZE = 50 * 1024 * 1024  # 50MB

# Timeout Settings
DOWNLOAD_TIMEOUT = 600  # 10 minutes
UPLOAD_TIMEOUT = 600    # 10 minutes
CONNECT_TIMEOUT = 60    # 1 minute

# yt-dlp Settings
YDL_OPTS_BASE = {
    'restrictfilenames': True,
    'windowsfilenames': True,
}

YDL_OPTS_BEST_QUALITY = {
    **YDL_OPTS_BASE,
    'format': 'bestaudio/best',
}

YDL_OPTS_SMALL_SIZE = {
    **YDL_OPTS_BASE,
    'format': '249/250/worstaudio/bestaudio',
}

YDL_OPTS_MP3_READY = {
    **YDL_OPTS_BASE,
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
}

# Flask Settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Logging
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LEVEL = 'INFO'