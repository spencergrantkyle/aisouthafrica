import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class NewsletterBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
        self.init_database()
        logger.info("🤖 Newsletter Bot initialized")
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            
            # Create subscribers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Create newsletter_logs table for tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS newsletter_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    subscribers_count INTEGER,
                    success BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            raise
    
    def setup_handlers(self):
        """Set up command handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.app.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        logger.info("✅ Command handlers set up")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 **Welcome to AI Newsletter Bot SA!**

I help South African professionals stay updated with the latest AI developments by summarizing newsletters into actionable insights.

**What I do:**
📰 Fetch the latest AI newsletters (starting with OpenLetter)
🤖 Summarize them using AI with South African business context
📱 Deliver concise, actionable summaries directly to you

**Commands:**
/subscribe - Get AI newsletter summaries
/unsubscribe - Stop receiving summaries  
/status - Check your subscription status
/help - Show this help message

🚀 **Ready to boost your AI knowledge?**
Use /subscribe to get started!

🇿🇦 *Built for South African professionals*
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"👋 New user started: {update.effective_user.first_name}")
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user = update.effective_user
        
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT * FROM subscribers WHERE user_id = ?', (user.id,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('UPDATE subscribers SET is_active = TRUE WHERE user_id = ?', (user.id,))
                message = "✅ **Welcome back!** You're now subscribed to AI newsletter summaries."
            else:
                cursor.execute('''
                    INSERT INTO subscribers (user_id, username, first_name) 
                    VALUES (?, ?, ?)
                ''', (user.id, user.username, user.first_name))
                message = "🎉 **Successfully subscribed!** You'll receive AI newsletter summaries tailored for South African professionals."
            
            conn.commit()
            conn.close()
            
            # Add helpful follow-up message
            message += "\n\n📅 **What to expect:**\n• Daily AI newsletter summaries\n• Focus on practical, actionable insights\n• South African business context\n\n🔔 You'll receive your first summary soon!"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"✅ User subscribed: {user.first_name} (@{user.username})")
            
        except Exception as e:
            logger.error(f"❌ Subscribe error: {e}")
            await update.message.reply_text("❌ Sorry, there was an error processing your subscription. Please try again later.")
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        user = update.effective_user
        
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE subscribers SET is_active = FALSE WHERE user_id = ?', (user.id,))
            conn.commit()
            conn.close()
            
            message = "😢 **You've been unsubscribed** from AI newsletter summaries.\n\n💡 You can rejoin anytime with /subscribe\n\n🙏 Thanks for using AI Newsletter Bot SA!"
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"👋 User unsubscribed: {user.first_name}")
            
        except Exception as e:
            logger.error(f"❌ Unsubscribe error: {e}")
            await update.message.reply_text("❌ Sorry, there was an error processing your request.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user = update.effective_user
        
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT is_active, subscribed_at FROM subscribers WHERE user_id = ?', (user.id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                subscribed_date = result[1]
                message = f"✅ **You're subscribed!**\n\n📅 Member since: {subscribed_date}\n📰 Receiving AI newsletter summaries\n🇿🇦 Optimized for South African professionals"
            else:
                message = "❌ **You're not subscribed**\n\n💡 Use /subscribe to get AI newsletter summaries\n🚀 Join other South African professionals staying ahead with AI!"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Status error: {e}")
            await update.message.reply_text("❌ Sorry, could not check your status.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
🆘 **AI Newsletter Bot SA - Help**

**About:**
I summarize AI newsletters for South African professionals, focusing on actionable insights for your business and career.

**Commands:**
/start - Welcome message and introduction
/subscribe - Subscribe to newsletter summaries
/unsubscribe - Stop receiving summaries
/status - Check subscription status
/help - Show this help message

**What you'll receive:**
📰 Daily AI newsletter summaries
🎯 Focus on practical applications
💼 South African business context
⚡ Actionable insights and tools

**Source:** Currently processing OpenLetter and expanding to more SA AI sources.

**Support:** This bot is in MVP phase. Report issues or suggestions by messaging this bot.

🇿🇦 *Proudly serving South African AI professionals*
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - public stats"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            
            # Get subscriber count
            cursor.execute('SELECT COUNT(*) FROM subscribers WHERE is_active = TRUE')
            subscriber_count = cursor.fetchone()[0]
            
            # Get recent newsletter count
            cursor.execute('SELECT COUNT(*) FROM newsletter_logs WHERE processed_at > datetime("now", "-7 days")')
            recent_newsletters = cursor.fetchone()[0]
            
            conn.close()
            
            stats_message = f"""
📊 **AI Newsletter Bot SA Stats**

👥 Active subscribers: {subscriber_count}
📰 Newsletters processed (7 days): {recent_newsletters}
🤖 AI summaries generated: {recent_newsletters}
🇿🇦 Serving South African professionals

**Status:** ✅ Active and processing
**Next update:** Daily at 9:00 AM SAST

💡 *Join {subscriber_count} professionals staying ahead with AI!*
            """
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            await update.message.reply_text("❌ Could not retrieve stats at the moment.")
    
    def get_subscriber_count(self):
        """Get current subscriber count"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM subscribers WHERE is_active = TRUE')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"❌ Error getting subscriber count: {e}")
            return 0
    
    def log_newsletter_sent(self, title, subscriber_count, success=True):
        """Log newsletter processing"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO newsletter_logs (title, subscribers_count, success)
                VALUES (?, ?, ?)
            ''', (title, subscriber_count, success))
            conn.commit()
            conn.close()
            logger.info(f"📝 Logged newsletter: {title} to {subscriber_count} subscribers")
        except Exception as e:
            logger.error(f"❌ Error logging newsletter: {e}")
    
    def run(self):
        """Start the bot with polling"""
        try:
            logger.info("🚀 Starting Telegram bot polling...")
            self.app.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"❌ Bot polling error: {e}")
            raise

if __name__ == "__main__":
    bot = NewsletterBot()
    bot.run()