#!/usr/bin/env python3
"""
Tez test uchun - kichik fayl yuklab olish
"""

import yt_dlp
import os
from pathlib import Path

def test_download():
    # Kichik fayl uchun test URL (qisqa video)
    test_url = "https://youtu.be/S4BV_6l1UvI?si=qHU65FwdnIWYbtrO"
    
    downloads_dir = Path("quick_test_downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    ydl_opts = {
        'format': 'worstaudio[filesize<10M]/bestaudio[filesize<10M]',  # Eng kichik sifat
        'outtmpl': str(downloads_dir / 'quick_test.%(ext)s'),
        'restrictfilenames': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("📥 Kichik sifatda yuklab olish...")
            info = ydl.extract_info(test_url, download=True)
            
            # Faylni topish
            for file_path in downloads_dir.glob('quick_test.*'):
                if file_path.suffix in ['.m4a', '.mp3', '.webm', '.opus']:
                    file_size = file_path.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    print(f"✅ Fayl yuklab olindi: {file_path}")
                    print(f"📊 Hajmi: {size_mb:.1f} MB")
                    
                    if size_mb < 10:
                        print("✅ Hajm yaxshi, Telegram'ga yuborish mumkin!")
                    else:
                        print("⚠️ Hajm hali ham katta")
                    
                    return file_path, file_size
            
            print("❌ Fayl topilmadi")
            return None, 0
            
    except Exception as e:
        print(f"❌ Xatolik: {e}")
        return None, 0

if __name__ == "__main__":
    test_download()