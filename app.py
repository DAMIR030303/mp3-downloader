#!/usr/bin/env python3
"""
Railway-optimized startup script
"""
import os
import sys
import logging

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point optimized for Railway"""
    try:
        logger.info("🚀 Starting Unlimited Audio Bot on Railway...")
        
        # Import and run bot
        from deploy_bot import main as bot_main
        bot_main()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()