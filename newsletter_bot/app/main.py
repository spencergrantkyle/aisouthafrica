from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
import threading
import sys
import os

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import NewsletterBot
from newsletter import OpenLetterFetcher
from summarizer import NewsletterSummarizer
from scheduler import NewsletterScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
bot_instance = None
scheduler_instance = None
bot_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global bot_instance, scheduler_instance, bot_thread
    
    logger.info("🚀 Starting AI Newsletter Bot SA...")
    
    try:
        # Initialize components
        bot_instance = NewsletterBot()
        scheduler_instance = NewsletterScheduler(bot_instance)
        
        # Start scheduler
        scheduler_instance.start()
        
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=bot_instance.run, daemon=True)
        bot_thread.start()
        
        logger.info("✅ Bot and scheduler started successfully!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🛑 Shutting down...")
        if scheduler_instance:
            scheduler_instance.stop()

app = FastAPI(
    title="AI Newsletter Bot SA", 
    version="1.0.0",
    description="AI-powered newsletter summarization bot for South African professionals",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🤖 AI Newsletter Bot SA is running!", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if bot is running
        bot_status = "running" if bot_instance and bot_thread and bot_thread.is_alive() else "stopped"
        
        # Check if scheduler is running
        scheduler_status = "running" if scheduler_instance and scheduler_instance.is_running() else "stopped"
        
        return JSONResponse({
            "status": "healthy",
            "service": "AI Newsletter Bot SA",
            "components": {
                "bot": bot_status,
                "scheduler": scheduler_status
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            {"status": "unhealthy", "error": str(e)},
            status_code=500
        )

@app.post("/trigger-summary")
async def trigger_manual_summary():
    """Manual trigger for testing newsletter processing"""
    try:
        logger.info("📝 Manual summary trigger requested")
        
        fetcher = OpenLetterFetcher()
        summarizer = NewsletterSummarizer()
        
        # Fetch newsletter
        logger.info("📰 Fetching newsletter...")
        newsletter = fetcher.fetch_latest_newsletter()
        if not newsletter:
            return {"error": "Could not fetch newsletter content"}
        
        # Generate summary
        logger.info("🤖 Generating AI summary...")
        summary = summarizer.summarize_newsletter(
            newsletter['content'], 
            newsletter['title']
        )
        
        if not summary:
            return {"error": "Could not generate summary"}
        
        logger.info("✅ Summary generated successfully")
        
        return {
            "success": True,
            "title": newsletter['title'],
            "summary": summary,
            "link": newsletter.get('link', ''),
            "content_length": len(newsletter['content'])
        }
        
    except Exception as e:
        logger.error(f"Manual trigger error: {e}")
        return {"error": str(e)}

@app.post("/send-test-message")
async def send_test_message():
    """Send a test message to all subscribers"""
    try:
        if not bot_instance:
            return {"error": "Bot not initialized"}
        
        test_message = """
🧪 **Test Message from AI Newsletter Bot SA**

This is a test message to verify the bot is working correctly!

🇿🇦 *Serving South African AI professionals*
⚡ *Powered by AI Newsletter Bot SA*
        """
        
        # Use the scheduler to send the message
        if scheduler_instance:
            await scheduler_instance.send_to_subscribers(test_message)
            return {"success": True, "message": "Test message sent to all subscribers"}
        else:
            return {"error": "Scheduler not available"}
            
    except Exception as e:
        logger.error(f"Test message error: {e}")
        return {"error": str(e)}

@app.get("/stats")
async def get_stats():
    """Get basic bot statistics"""
    try:
        if not bot_instance:
            return {"error": "Bot not initialized"}
        
        # Get subscriber count from database
        subscriber_count = bot_instance.get_subscriber_count()
        
        return {
            "subscribers": subscriber_count,
            "status": "active",
            "features": ["newsletter_summarization", "telegram_distribution", "scheduled_processing"]
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )