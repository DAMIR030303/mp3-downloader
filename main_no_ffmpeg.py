#!/usr/bin/env python3
"""
MP3 Downloader - YouTube videolaridan audio yuklab olish uchun sodda dastur (FFmpeg'siz)
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

class AudioDownloader:
    def __init__(self, output_dir="downloads", prefer_mp3=True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if prefer_mp3:
            # MP3 formatini qidiramiz (FFmpeg kerak emas)
            self.ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            }
        else:
            # Har qanday audio format (WebM, M4A, va h.k.)
            self.ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            }
    
    def download(self, url):
        """YouTube URL'dan audio yuklab olish"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                print(f"🎵 Yuklab olinmoqda: {url}")
                
                # Video haqida ma'lumot olish
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    print(f"📽️ Video: {title}")
                    print(f"⏱️ Davomiyligi: {minutes}:{seconds:02d}")
                
                # Yuklab olish
                ydl.download([url])
                print("✅ Muvaffaqiyatli yuklab olindi!")
                
        except yt_dlp.DownloadError as e:
            print(f"❌ Yuklab olishda xatolik: {e}")
        except Exception as e:
            print(f"❌ Noma'lum xatolik: {e}")
    
    def download_playlist(self, playlist_url):
        """YouTube playlist'dan audio'larni yuklab olish"""
        opts = self.ydl_opts.copy()
        opts['outtmpl'] = str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s')
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                print(f"🎵 Playlist yuklab olinmoqda: {playlist_url}")
                
                # Playlist haqida ma'lumot
                info = ydl.extract_info(playlist_url, download=False)
                playlist_title = info.get('title', 'Unknown Playlist')
                entry_count = len(info.get('entries', []))
                
                print(f"📋 Playlist: {playlist_title}")
                print(f"🔢 Qo'shiqlar soni: {entry_count}")
                
                ydl.download([playlist_url])
                print("✅ Playlist muvaffaqiyatli yuklab olindi!")
                
        except Exception as e:
            print(f"❌ Playlist yuklab olishda xatolik: {e}")

def main():
    parser = argparse.ArgumentParser(description="YouTube'dan audio yuklab olish (FFmpeg'siz)")
    parser.add_argument("url", help="YouTube video yoki playlist URL'i")
    parser.add_argument("-o", "--output", default="downloads", 
                       help="Yuklab olingan fayllar uchun papka (default: downloads)")
    parser.add_argument("-p", "--playlist", action="store_true",
                       help="Playlist sifatida yuklab olish")
    parser.add_argument("--any-format", action="store_true",
                       help="Har qanday audio formatni qabul qilish (WebM, M4A, va h.k.)")
    
    args = parser.parse_args()
    
    # Dastur boshlash
    print("🎼 Audio Downloader - YouTube'dan audio yuklab olish")
    print("=" * 55)
    
    if args.any_format:
        print("ℹ️  Har qanday audio format rejimi")
    else:
        print("ℹ️  MP3/M4A formatni afzal ko'rish rejimi")
    
    downloader = AudioDownloader(args.output, prefer_mp3=not args.any_format)
    
    if args.playlist:
        downloader.download_playlist(args.url)
    else:
        downloader.download(args.url)
    
    print(f"📁 Fayllar saqlangan: {os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()