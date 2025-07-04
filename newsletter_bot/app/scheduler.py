from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from newsletter import NewsletterFetcher
from summarizer import NewsletterSummarizer

# Configure logging
logger = logging.getLogger(__name__)

class NewsletterScheduler:
    def __init__(self, bot_instance):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot_instance
        self.fetcher = NewsletterFetcher()
        self.summarizer = NewsletterSummarizer()
        self.is_running = False
        logger.info("📅 Newsletter scheduler initialized")
    
    def start(self):
        """Start the scheduler with all configured jobs"""
        try:
            # Schedule daily newsletter processing at 9 AM SAST
            self.scheduler.add_job(
                self.process_and_send_newsletter,
                CronTrigger(hour=9, minute=0, timezone='Africa/Johannesburg'),
                id='daily_newsletter',
                name='Daily Newsletter Processing',
                max_instances=1,
                coalesce=True
            )
            
            # Schedule weekly summary on Friday at 5 PM SAST
            self.scheduler.add_job(
                self.send_weekly_summary,
                CronTrigger(day_of_week=4, hour=17, minute=0, timezone='Africa/Johannesburg'),
                id='weekly_summary',
                name='Weekly Summary',
                max_instances=1,
                coalesce=True
            )
            
            # Schedule daily test message for testing (remove in production)
            # Uncomment the line below to test every 10 minutes
            # self.scheduler.add_job(
            #     self.send_test_message,
            #     'interval',
            #     minutes=10,
            #     id='test_message',
            #     name='Test Message Every 10 Minutes'
            # )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Newsletter scheduler started successfully")
            logger.info("📅 Daily processing: 9:00 AM SAST")
            logger.info("📅 Weekly summary: Friday 5:00 PM SAST")
            
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
            self.is_running = False
            logger.info("🛑 Newsletter scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.is_running and self.scheduler.running
    
    async def process_and_send_newsletter(self):
        """Main function: Process latest newsletter and send to subscribers"""
        logger.info("🚀 Starting scheduled newsletter processing...")
        
        try:
            # Check if we already processed a newsletter today
            if self._already_processed_today():
                logger.info("ℹ️ Newsletter already processed today, skipping")
                return
            
            # Fetch newsletter content
            logger.info("📰 Fetching latest newsletter...")
            newsletter = self.fetcher.fetch_latest_newsletter()
            
            if not newsletter:
                logger.warning("⚠️ No newsletter content found")
                await self._send_error_notification("No newsletter content available")
                return
            
            logger.info(f"✅ Newsletter fetched: {newsletter['title']}")
            
            # Generate AI summary
            logger.info("🤖 Generating AI summary...")
            summary = self.summarizer.summarize_newsletter(
                newsletter['content'],
                newsletter['title']
            )
            
            if not summary:
                logger.warning("⚠️ Could not generate summary")
                await self._send_error_notification("Failed to generate summary")
                return
            
            logger.info("✅ AI summary generated successfully")
            
            # Add source link to the message
            source_link = newsletter.get('link', '')
            if source_link:
                full_message = f"{summary}\n\n🔗 [Read Full Newsletter]({source_link})"
            else:
                full_message = summary
            
            # Send to all subscribers
            subscriber_count = await self.send_to_subscribers(full_message)
            
            # Log the successful processing
            self.bot.log_newsletter_sent(newsletter['title'], subscriber_count, True)
            
            logger.info(f"🎉 Newsletter processed and sent to {subscriber_count} subscribers")
            
        except Exception as e:
            logger.error(f"❌ Newsletter processing error: {e}")
            await self._send_error_notification(f"Processing error: {str(e)}")
            
            # Log the failed processing
            try:
                self.bot.log_newsletter_sent("Processing Failed", 0, False)
            except:
                pass
    
    async def send_weekly_summary(self):
        """Send weekly summary message"""
        logger.info("📊 Sending weekly summary...")
        
        try:
            # Get stats for the week
            subscriber_count = self.bot.get_subscriber_count()
            
            # Get newsletters processed this week
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM newsletter_logs 
                WHERE processed_at > datetime('now', '-7 days') AND success = TRUE
            ''')
            newsletters_this_week = cursor.fetchone()[0]
            conn.close()
            
            weekly_message = f"""
📊 **Weekly AI Newsletter Update**

This week with AI Newsletter Bot SA:

📰 **Newsletters processed:** {newsletters_this_week}
👥 **Active community:** {subscriber_count} South African professionals
🤖 **AI summaries delivered:** {newsletters_this_week}

**Coming up:**
🔄 Fresh AI insights next week
💡 New features in development
🚀 More South African AI sources being added

**Feedback welcome!** Reply to this message with your thoughts or suggestions.

🇿🇦 *Proudly serving South African AI professionals*
⚡ *Powered by AI Newsletter Bot SA*
            """
            
            sent_count = await self.send_to_subscribers(weekly_message)
            logger.info(f"📊 Weekly summary sent to {sent_count} subscribers")
            
        except Exception as e:
            logger.error(f"❌ Weekly summary error: {e}")
    
    async def send_test_message(self):
        """Send a test message (for debugging)"""
        logger.info("🧪 Sending test message...")
        
        test_message = f"""
🧪 **Test Message - {datetime.now().strftime('%H:%M')}**

This is an automated test message to verify the scheduler is working.

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S SAST')}
🤖 Status: All systems operational
📱 Delivery: Successful

*This is a test message and can be ignored.*
        """
        
        try:
            sent_count = await self.send_to_subscribers(test_message)
            logger.info(f"🧪 Test message sent to {sent_count} subscribers")
        except Exception as e:
            logger.error(f"❌ Test message error: {e}")
    
    async def send_to_subscribers(self, message: str) -> int:
        """Send message to all active subscribers"""
        logger.info("📤 Broadcasting message to subscribers...")
        
        try:
            # Get all active subscribers
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, first_name FROM subscribers WHERE is_active = TRUE')
            subscribers = cursor.fetchall()
            conn.close()
            
            if not subscribers:
                logger.warning("⚠️ No active subscribers found")
                return 0
            
            successful_sends = 0
            failed_sends = 0
            
            logger.info(f"📤 Sending to {len(subscribers)} subscribers...")
            
            for user_id, first_name in subscribers:
                try:
                    await self.bot.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    successful_sends += 1
                    logger.debug(f"✅ Sent to {first_name} ({user_id})")
                    
                    # Rate limiting - respect Telegram limits
                    await asyncio.sleep(0.05)  # 20 messages per second max
                    
                except Exception as e:
                    failed_sends += 1
                    error_msg = str(e).lower()
                    
                    # Handle specific Telegram errors
                    if 'blocked' in error_msg or 'user is deactivated' in error_msg:
                        logger.info(f"👋 User {first_name} ({user_id}) blocked the bot, deactivating")
                        self._deactivate_user(user_id)
                    elif 'chat not found' in error_msg:
                        logger.info(f"👻 Chat not found for {first_name} ({user_id}), deactivating")
                        self._deactivate_user(user_id)
                    else:
                        logger.warning(f"⚠️ Failed to send to {first_name} ({user_id}): {e}")
                    
                    await asyncio.sleep(0.1)  # Longer pause after error
            
            logger.info(f"📊 Broadcast complete: {successful_sends} sent, {failed_sends} failed")
            return successful_sends
            
        except Exception as e:
            logger.error(f"❌ Broadcast error: {e}")
            return 0
    
    def _deactivate_user(self, user_id: int):
        """Deactivate a user who blocked the bot"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE subscribers SET is_active = FALSE WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"🚫 Deactivated user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error deactivating user {user_id}: {e}")
    
    def _already_processed_today(self) -> bool:
        """Check if we already processed a newsletter today"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM newsletter_logs 
                WHERE date(processed_at) = date('now') AND success = TRUE
            ''')
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logger.error(f"❌ Error checking today's processing: {e}")
            return False
    
    async def _send_error_notification(self, error_msg: str):
        """Send error notification to admin (you can extend this)"""
        logger.error(f"🚨 System error: {error_msg}")
        
        # In a production system, you might want to send this to an admin chat
        # For now, we just log it
        admin_message = f"""
🚨 **System Alert**

An error occurred during newsletter processing:

**Error:** {error_msg}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S SAST')}

Please check the logs for more details.
        """
        
        # You could send this to a specific admin user_id if needed
        # await self.bot.app.bot.send_message(chat_id=ADMIN_USER_ID, text=admin_message)
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        try:
            jobs = self.scheduler.get_jobs()
            next_runs = []
            
            for job in jobs:
                if job.next_run_time:
                    next_runs.append({
                        'job_name': job.name,
                        'next_run': job.next_run_time
                    })
            
            return next_runs
        except Exception as e:
            logger.error(f"❌ Error getting next run times: {e}")
            return []
    
    def trigger_manual_run(self):
        """Manually trigger newsletter processing (for testing)"""
        logger.info("🔧 Manual trigger requested")
        try:
            # Schedule the job to run immediately
            self.scheduler.add_job(
                self.process_and_send_newsletter,
                'date',
                run_date=datetime.now() + timedelta(seconds=5),
                id='manual_trigger',
                name='Manual Newsletter Processing',
                max_instances=1
            )
            logger.info("✅ Manual processing scheduled for 5 seconds")
            return True
        except Exception as e:
            logger.error(f"❌ Manual trigger error: {e}")
            return False


if __name__ == "__main__":
    # Test the scheduler (without bot integration)
    import logging
    logging.basicConfig(level=logging.INFO)
    
    class MockBot:
        def log_newsletter_sent(self, title, count, success):
            print(f"Mock log: {title}, {count} users, success: {success}")
        
        def get_subscriber_count(self):
            return 5
        
        class MockApp:
            class MockBot:
                async def send_message(self, chat_id, text, **kwargs):
                    print(f"Mock message to {chat_id}: {text[:50]}...")
        
        def __init__(self):
            self.app = self.MockApp()
            self.app.bot = self.MockApp.MockBot()
    
    # Test scheduler creation
    mock_bot = MockBot()
    scheduler = NewsletterScheduler(mock_bot)
    
    print("✅ Scheduler test successful!")
    print(f"📅 Scheduler running: {scheduler.is_running}")
    
    # Test job scheduling
    next_runs = scheduler.get_next_run_time()
    print(f"📋 Scheduled jobs: {len(next_runs)}")
    
    # Don't actually start scheduler in test
    print("🧪 Test complete - scheduler not started")