"""
MP3 Downloader - Core downloader class
"""

import os
import shutil
import logging
import asyncio
from pathlib import Path
from typing import Dict, Tuple, Optional, Callable
import uuid

import yt_dlp

from config import (
    TELEGRAM_DOWNLOADS_DIR, YDL_OPTS_BEST_QUALITY, YDL_OPTS_SMALL_SIZE, 
    YDL_OPTS_MP3_READY, MAX_TELEGRAM_SIZE
)
from utils import (
    sanitize_filename, format_file_size, find_audio_file, 
    convert_to_mp3, is_ffmpeg_available, create_unique_filename,
    estimate_audio_size
)

logger = logging.getLogger(__name__)

class AudioDownloader:
    """Unified audio downloader class"""
    
    def __init__(self, mode: str = "balanced"):
        """
        Initialize downloader
        Args:
            mode: 'small', 'balanced', 'quality', 'mp3'
        """
        self.mode = mode
        self.downloads_dir = TELEGRAM_DOWNLOADS_DIR
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Select appropriate yt-dlp options based on mode
        self.ydl_opts = self._get_ydl_opts()
        
    def _get_ydl_opts(self) -> Dict:
        """Get yt-dlp options based on mode"""
        base_opts = {
            'outtmpl': str(self.downloads_dir / 'temp_%(id)s.%(ext)s'),
        }
        
        if self.mode == "small":
            return {**YDL_OPTS_SMALL_SIZE, **base_opts}
        elif self.mode == "quality":
            return {**YDL_OPTS_BEST_QUALITY, **base_opts}
        elif self.mode == "mp3":
            return {**YDL_OPTS_MP3_READY, **base_opts}
        else:  # balanced
            return {**YDL_OPTS_BEST_QUALITY, **base_opts}
    
    def get_video_info(self, url: str) -> Dict:
        """Get video information"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                duration = info.get('duration', 0)
                estimated_size = estimate_audio_size(duration)
                
                return {
                    'title': info.get('title', 'Unknown')[:80],
                    'duration': duration,
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown')[:50],
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:200],
                    'estimated_size': estimated_size,
                    'id': info.get('id', ''),
                }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {'error': str(e)}
    
    async def download_audio(
        self, 
        url: str, 
        progress_callback: Optional[Callable] = None,
        convert_mp3: bool = None
    ) -> Tuple[Optional[str], str, int]:
        """
        Download audio from URL
        
        Args:
            url: YouTube URL
            progress_callback: Optional progress callback function
            convert_mp3: Force MP3 conversion (overrides mode)
            
        Returns:
            Tuple of (file_path, title, file_size)
        """
        temp_id = str(uuid.uuid4())[:8]
        temp_file = None
        final_file = None
        
        try:
            # Setup options with progress hook
            opts = self.ydl_opts.copy()
            opts['outtmpl'] = str(self.downloads_dir / f'temp_{temp_id}.%(ext)s')
            
            if progress_callback:
                def hook(d):
                    if d['status'] == 'downloading':
                        try:
                            percent = (d.get('downloaded_bytes', 0) / d.get('total_bytes', 1)) * 50
                            asyncio.create_task(progress_callback(int(percent), "Downloading"))
                        except:
                            pass
                
                opts['progress_hooks'] = [hook]
            
            # Download audio
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f"Starting download: {url}")
                info = ydl.extract_info(url, download=True)
                title = sanitize_filename(info.get('title', 'Unknown'))
                
                # Find downloaded file
                temp_file = find_audio_file(self.downloads_dir, f'temp_{temp_id}')
                if not temp_file:
                    return None, "Downloaded file not found", 0
                
                # Check if MP3 conversion is needed
                should_convert_mp3 = (
                    convert_mp3 or 
                    self.mode == "mp3" or 
                    (self.mode == "balanced" and os.path.getsize(temp_file) > MAX_TELEGRAM_SIZE)
                )
                
                if should_convert_mp3 and is_ffmpeg_available():
                    if progress_callback:
                        await progress_callback(75, "Converting to MP3")
                    
                    # Convert to MP3
                    mp3_file = create_unique_filename(self.downloads_dir, title, '.mp3')
                    success, message = convert_to_mp3(temp_file, str(mp3_file))
                    
                    if success:
                        os.remove(temp_file)  # Remove original
                        final_file = str(mp3_file)
                        logger.info(f"Converted to MP3: {final_file}")
                    else:
                        logger.warning(f"MP3 conversion failed: {message}")
                        final_file = str(create_unique_filename(
                            self.downloads_dir, title, Path(temp_file).suffix
                        ))
                        shutil.move(temp_file, final_file)
                else:
                    # Keep original format
                    final_file = str(create_unique_filename(
                        self.downloads_dir, title, Path(temp_file).suffix
                    ))
                    shutil.move(temp_file, final_file)
                
                if progress_callback:
                    await progress_callback(100, "Complete")
                
                file_size = os.path.getsize(final_file)
                logger.info(f"Download complete: {format_file_size(file_size)}")
                
                return final_file, title, file_size
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            # Cleanup on error
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            if final_file and os.path.exists(final_file):
                os.remove(final_file)
            return None, str(e), 0

# Factory function for different downloader modes
def create_downloader(mode: str = "balanced") -> AudioDownloader:
    """Create downloader instance with specified mode"""
    return AudioDownloader(mode)