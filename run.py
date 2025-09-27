#!/usr/bin/env python3
"""
MP3 Downloader - Universal Launcher
Run this file to start any component of the MP3 Downloader system
"""

import sys
import subprocess
import os
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🎵 MP3 DOWNLOADER - Universal Launcher")
    print("=" * 60)

def check_requirements():
    """Check if requirements are installed"""
    try:
        import yt_dlp
        from telegram.ext import Application
        print("✅ All requirements installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirements: {e}")
        print("💡 Installing requirements...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements_clean.txt"
            ])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            print("💡 Run manually: pip install -r requirements_clean.txt")
            return False

def show_menu():
    """Show main menu"""
    print("\n🚀 Choose what to run:")
    print("1. 🤖 Telegram Bot (Main - Recommended)")
    print("2. 🌐 Web Interface")
    print("3. 🖥️  Command Line Tool")
    print("4. ⚙️  Configuration")
    print("5. 📋 System Info")
    print("0. ❌ Exit")
    print("-" * 40)

def run_telegram_bot():
    """Run the main Telegram bot"""
    print("🤖 Starting Telegram Bot...")
    
    # Check bot token
    from config import BOT_TOKEN
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Bot token not configured!")
        print("💡 Edit config.py and set your bot token")
        return
    
    print(f"🔐 Bot token: {BOT_TOKEN[:10]}...")
    
    try:
        from telegram_bot_main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")

def run_web_interface():
    """Run the web interface"""
    print("🌐 Starting Web Interface...")
    
    try:
        from web_app import app
        from config import FLASK_HOST, FLASK_PORT
        
        print(f"🌍 Web interface starting on http://{FLASK_HOST}:{FLASK_PORT}")
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def run_cli_tool():
    """Run command line tool"""
    print("🖥️  Command Line Tool")
    print("Available CLI tools:")
    print("1. main_no_ffmpeg.py - Audio downloader (no FFmpeg)")
    print("2. main.py - Audio downloader (with FFmpeg)")
    
    choice = input("Choose tool (1-2): ").strip()
    url = input("Enter YouTube URL: ").strip()
    
    if not url:
        print("❌ No URL provided")
        return
    
    try:
        if choice == "1":
            subprocess.run([sys.executable, "main_no_ffmpeg.py", url])
        elif choice == "2":
            subprocess.run([sys.executable, "main.py", url])
        else:
            print("❌ Invalid choice")
    except Exception as e:
        print(f"❌ CLI error: {e}")

def show_configuration():
    """Show configuration options"""
    print("⚙️  Configuration")
    
    try:
        from config import BOT_TOKEN, FLASK_HOST, FLASK_PORT
        from utils import is_ffmpeg_available
        
        print(f"🤖 Bot Token: {BOT_TOKEN[:10]}..." if BOT_TOKEN != "YOUR_BOT_TOKEN_HERE" else "❌ Not configured")
        print(f"🌐 Web Host: {FLASK_HOST}:{FLASK_PORT}")
        print(f"🔧 FFmpeg: {'✅ Available' if is_ffmpeg_available() else '❌ Not found'}")
        
        # Show directories
        from config import DOWNLOADS_DIR, TELEGRAM_DOWNLOADS_DIR
        print(f"📁 Downloads: {DOWNLOADS_DIR}")
        print(f"📱 Telegram Downloads: {TELEGRAM_DOWNLOADS_DIR}")
        
        print("\n💡 To configure:")
        print("- Edit config.py for settings")
        print("- Set BOT_TOKEN environment variable")
        print("- Install FFmpeg for MP3 conversion")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")

def show_system_info():
    """Show system information"""
    print("📋 System Information")
    
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {Path.cwd()}")
    
    # Check dependencies
    try:
        import yt_dlp
        print(f"📺 yt-dlp: {yt_dlp.version.__version__}")
    except:
        print("❌ yt-dlp not installed")
    
    try:
        import telegram
        print(f"🤖 python-telegram-bot: {telegram.__version__}")
    except:
        print("❌ python-telegram-bot not installed")
    
    try:
        import flask
        print(f"🌐 Flask: {flask.__version__}")
    except:
        print("❌ Flask not installed")
    
    # Check FFmpeg
    from utils import is_ffmpeg_available
    print(f"🔧 FFmpeg: {'✅ Available' if is_ffmpeg_available() else '❌ Not installed'}")
    
    # Show project files
    print(f"\n📂 Project files:")
    py_files = list(Path(".").glob("*.py"))
    for file in sorted(py_files):
        size = file.stat().st_size
        print(f"   {file.name}: {size} bytes")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        return
    
    while True:
        try:
            show_menu()
            choice = input("Enter choice (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                run_telegram_bot()
            elif choice == "2":
                run_web_interface()
            elif choice == "3":
                run_cli_tool()
            elif choice == "4":
                show_configuration()
            elif choice == "5":
                show_system_info()
            else:
                print("❌ Invalid choice. Please enter 0-5.")
            
            if choice != "0":
                input("\n📱 Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    main()