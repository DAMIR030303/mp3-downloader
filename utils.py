"""
MP3 Downloader - Utility functions
"""

import os
import re
import math
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple, Optional

from config import AUDIO_FORMATS, CHUNK_SIZE, DEFAULT_BITRATE

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """Clean filename for Windows/cross-platform compatibility"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*⧸@._-]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Strip dots and spaces from ends
    filename = filename.strip('. ')
    # Limit length
    return filename[:max_length]

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
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

def format_number(num: int) -> str:
    """Format number with thousand separators"""
    if not num:
        return "0"
    return f"{num:,}"

def split_file(file_path: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split large file into chunks"""
    chunks = []
    file_size = os.path.getsize(file_path)
    
    logger.info(f"File size: {format_file_size(file_size)}")
    
    # If file is small enough, don't split
    if file_size <= chunk_size + 5*1024*1024:  # 5MB buffer
        logger.info("File is small enough, no splitting needed")
        return [file_path]
    
    total_chunks = math.ceil(file_size / chunk_size)
    logger.info(f"Large file! Splitting into {total_chunks} parts")
    
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
            logger.info(f"Created part {chunk_num}: {format_file_size(len(chunk_data))}")
    
    return chunks

def convert_to_mp3(input_file: str, output_file: str, bitrate: str = DEFAULT_BITRATE) -> Tuple[bool, str]:
    """Convert audio file to MP3 using FFmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', input_file,
            '-acodec', 'mp3',
            '-ab', bitrate,
            '-ar', '44100',
            '-y',  # Overwrite output file
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return True, "Conversion successful"
        else:
            return False, result.stderr
            
    except FileNotFoundError:
        return False, "FFmpeg not found. Please install FFmpeg."
    except subprocess.TimeoutExpired:
        return False, "Conversion timeout (5 minutes)"
    except Exception as e:
        return False, str(e)

def is_ffmpeg_available() -> bool:
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        return True
    except:
        return False

def find_audio_file(directory: Path, prefix: str) -> Optional[str]:
    """Find audio file in directory with given prefix"""
    for file_path in directory.glob(f'{prefix}.*'):
        if file_path.suffix in AUDIO_FORMATS:
            return str(file_path)
    return None

def cleanup_files(*file_paths: str) -> None:
    """Clean up temporary files"""
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup {file_path}: {e}")

def estimate_audio_size(duration: int, bitrate: int = 128) -> int:
    """Estimate audio file size in bytes"""
    if not duration:
        return 0
    # Formula: duration(s) * bitrate(kbps) * 1024 / 8
    return duration * bitrate * 1024 // 8

def create_unique_filename(directory: Path, base_name: str, extension: str) -> Path:
    """Create unique filename if file already exists"""
    file_path = directory / f"{base_name}{extension}"
    counter = 1
    
    while file_path.exists():
        file_path = directory / f"{base_name}_{counter}{extension}"
        counter += 1
    
    return file_path