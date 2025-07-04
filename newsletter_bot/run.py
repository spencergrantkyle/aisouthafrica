#!/usr/bin/env python3
"""
Simple launcher script for AI Newsletter Bot SA
"""

import os
import sys
import subprocess
import logging

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please check your .env file or set these environment variables")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import telegram
        import openai
        import requests
        import beautifulsoup4
        import apscheduler
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n💡 Run: pip install -r requirements.txt")
        return False

def run_bot():
    """Run the bot application"""
    if not check_environment():
        return False
    
    if not check_dependencies():
        return False
    
    print("🚀 Starting AI Newsletter Bot SA...")
    
    try:
        # Import and run the main application
        from app.main import app
        import uvicorn
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        return False

if __name__ == "__main__":
    print("🤖 AI Newsletter Bot SA - Launcher")
    print("=" * 40)
    
    success = run_bot()
    
    if success:
        print("✅ Bot stopped successfully")
    else:
        print("❌ Bot stopped with errors")
        sys.exit(1)