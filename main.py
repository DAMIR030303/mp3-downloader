#!/usr/bin/env python3
"""
MP3 Downloader - YouTube videolaridan audio yuklab olish uchun sodda dastur
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("❌ yt-dlp kutubxonasi topilmadi!")
    print("💡 O'rnatish uchun: pip install yt-dlp")
    sys.exit(1)

class MP3Downloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # yt-dlp sozlamalari
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '44100'
            ],
        }
    
    def download(self, url):
        """YouTube URL'dan MP3 yuklab olish"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                print(f"🎵 Yuklab olinmoqda: {url}")
                ydl.download([url])
                print("✅ Muvaffaqiyatli yuklab olindi!")
                
        except yt_dlp.DownloadError as e:
            print(f"❌ Yuklab olishda xatolik: {e}")
        except Exception as e:
            print(f"❌ Noma'lum xatolik: {e}")
    
    def download_playlist(self, playlist_url):
        """YouTube playlist'dan MP3'larni yuklab olish"""
        opts = self.ydl_opts.copy()
        opts['outtmpl'] = str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s')
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                print(f"🎵 Playlist yuklab olinmoqda: {playlist_url}")
                ydl.download([playlist_url])
                print("✅ Playlist muvaffaqiyatli yuklab olindi!")
                
        except Exception as e:
            print(f"❌ Playlist yuklab olishda xatolik: {e}")

def main():
    parser = argparse.ArgumentParser(description="YouTube'dan MP3 yuklab olish")
    parser.add_argument("url", help="YouTube video yoki playlist URL'i")
    parser.add_argument("-o", "--output", default="downloads", 
                       help="Yuklab olingan fayllar uchun papka (default: downloads)")
    parser.add_argument("-p", "--playlist", action="store_true",
                       help="Playlist sifatida yuklab olish")
    
    args = parser.parse_args()
    
    # Dastur boshlash
    print("🎼 MP3 Downloader - YouTube'dan audio yuklab olish")
    print("=" * 50)
    
    downloader = MP3Downloader(args.output)
    
    if args.playlist:
        downloader.download_playlist(args.url)
    else:
        downloader.download(args.url)
    
    print(f"📁 Fayllar saqlangan: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()