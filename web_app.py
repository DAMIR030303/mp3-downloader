#!/usr/bin/env python3
"""
MP3 Downloader Web App - Flask bilan yaratilgan web interfeys
"""

import os
import tempfile
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import yt_dlp
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mp3-downloader-secret-key'
app.config['UPLOAD_FOLDER'] = 'downloads'

# Global o'zgaruvchilar
download_status = {}

class WebAudioDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
        }
    
    def get_video_info(self, url):
        """Video haqida ma'lumot olish"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0)
                }
        except Exception as e:
            return {'error': str(e)}
    
    def download_audio(self, url, download_id):
        """Audio yuklab olish (background'da)"""
        global download_status
        
        try:
            download_status[download_id] = {'status': 'downloading', 'progress': 0}
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        download_status[download_id]['progress'] = int(percent)
            
            opts = self.ydl_opts.copy()
            opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                
                # Yuklab olish
                ydl.download([url])
                
                # Fayl nomini topish
                title = info.get('title', 'Unknown')
                for ext in ['.m4a', '.mp3', '.webm']:
                    potential_file = self.output_dir / f"{title}{ext}"
                    if potential_file.exists():
                        download_status[download_id] = {
                            'status': 'completed',
                            'progress': 100,
                            'filename': potential_file.name,
                            'title': title
                        }
                        return
                
                download_status[download_id] = {'status': 'error', 'error': 'Fayl topilmadi'}
                
        except Exception as e:
            download_status[download_id] = {'status': 'error', 'error': str(e)}

downloader = WebAudioDownloader()

@app.route('/')
def index():
    """Asosiy sahifa"""
    return render_template('index.html')

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Video ma'lumotlarini olish"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL kiritilmagan'})
    
    info = downloader.get_video_info(url)
    return jsonify(info)

@app.route('/api/download', methods=['POST'])
def start_download():
    """Yuklab olishni boshlash"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL kiritilmagan'})
    
    # Download ID yaratish
    import uuid
    download_id = str(uuid.uuid4())
    
    # Background'da yuklab olishni boshlash
    thread = threading.Thread(target=downloader.download_audio, args=(url, download_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({'download_id': download_id})

@app.route('/api/status/<download_id>')
def download_status_api(download_id):
    """Yuklab olish holatini tekshirish"""
    global download_status
    status = download_status.get(download_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/download/<filename>')
def download_file(filename):
    """Faylni yuklab olish"""
    try:
        file_path = downloader.output_dir / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Fayl topilmadi'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)