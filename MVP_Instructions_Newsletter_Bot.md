# MVP Instructions: AI Newsletter Summarization Bot
## One Week Sprint - Junior Developer Guide

### Project Overview
Build a Telegram bot that automatically summarizes South African AI newsletters (starting with OpenLetter) and distributes them to subscribers.

---

## 🎯 MVP Goals (Week 1)
1. **Fetch OpenLetter newsletter** content automatically
2. **Summarize** newsletter using AI (OpenAI API)
3. **Distribute** summaries via Telegram bot
4. **Schedule** daily/weekly processing
5. **Track** basic metrics (subscribers, messages sent)

---

## 🏗️ Simple Architecture

```
Newsletter Source (OpenLetter) 
        ↓
    Content Fetcher
        ↓
    AI Summarizer (OpenAI)
        ↓
    Telegram Bot API
        ↓
    Subscribers
```

### Tech Stack (Keep It Simple!)
- **Language:** Python 3.9+
- **Framework:** FastAPI (lightweight)
- **Database:** SQLite (no setup required)
- **AI Service:** OpenAI API
- **Bot Platform:** Telegram Bot API
- **Scheduling:** Python APScheduler
- **Hosting:** Railway.app or Heroku (free tier)
- **Environment:** Docker (optional, but recommended)

---

## 📋 Day-by-Day Implementation Plan

### Day 1: Project Setup & Environment
**Objectives:**
- Set up development environment
- Create project structure
- Set up basic Telegram bot

**Tasks:**
1. Create project directory and virtual environment
2. Install required dependencies
3. Set up environment variables
4. Create basic Telegram bot and get token
5. Test basic bot functionality

### Day 2: Newsletter Content Fetching
**Objectives:**
- Implement OpenLetter content fetching
- Parse and clean newsletter content

**Tasks:**
1. Research OpenLetter RSS/API access
2. Implement web scraping if needed
3. Create content parser and cleaner
4. Test content extraction

### Day 3: AI Summarization
**Objectives:**
- Integrate OpenAI API
- Implement summarization logic
- Test summary quality

**Tasks:**
1. Set up OpenAI API integration
2. Create summarization prompts
3. Implement error handling
4. Test and refine summary output

### Day 4: Telegram Bot Features
**Objectives:**
- Implement core bot commands
- Add subscriber management
- Create message formatting

**Tasks:**
1. Implement /start, /subscribe, /unsubscribe commands
2. Create user database
3. Format messages for Telegram
4. Add basic error handling

### Day 5: Automation & Scheduling
**Objectives:**
- Implement automated processing
- Set up scheduling system
- Add logging

**Tasks:**
1. Create scheduled task system
2. Implement automatic newsletter processing
3. Add logging and monitoring
4. Test end-to-end workflow

### Day 6: Testing & Refinement
**Objectives:**
- Comprehensive testing
- Bug fixes
- Performance optimization

**Tasks:**
1. Test all bot commands
2. Test newsletter processing pipeline
3. Fix identified bugs
4. Optimize performance

### Day 7: Deployment & Documentation
**Objectives:**
- Deploy to production
- Create documentation
- Final testing

**Tasks:**
1. Deploy to Railway/Heroku
2. Configure production environment
3. Test production deployment
4. Create user documentation

---

## 🛠️ Detailed Implementation Instructions

### Project Structure
```
newsletter_bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── bot.py               # Telegram bot logic
│   ├── newsletter.py        # Newsletter fetching/parsing
│   ├── summarizer.py        # AI summarization
│   ├── database.py          # SQLite database operations
│   └── scheduler.py         # Task scheduling
├── requirements.txt
├── .env
├── Dockerfile
└── README.md
```

### Step 1: Initial Setup

**Create requirements.txt:**
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-telegram-bot==20.7
openai==1.3.7
requests==2.31.0
beautifulsoup4==4.12.2
sqlite3
python-dotenv==1.0.0
apscheduler==3.10.4
feedparser==6.0.10
```

**Create .env file:**
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///newsletter_bot.db
DEBUG=True
```

### Step 2: Basic Telegram Bot (bot.py)

```python
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class NewsletterBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect('newsletter_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        conn.commit()
        conn.close()
    
    def setup_handlers(self):
        """Set up command handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.app.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to AI Newsletter Bot SA!

I summarize the latest AI newsletters from South Africa to help you stay updated efficiently.

Commands:
/subscribe - Get AI newsletter summaries
/unsubscribe - Stop receiving summaries
/status - Check your subscription status

Let's help you stay ahead in the AI game! 🚀
        """
        await update.message.reply_text(welcome_message)
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user = update.effective_user
        
        conn = sqlite3.connect('newsletter_bot.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT * FROM subscribers WHERE user_id = ?', (user.id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('UPDATE subscribers SET is_active = TRUE WHERE user_id = ?', (user.id,))
            message = "✅ You're already subscribed! You'll receive AI newsletter summaries."
        else:
            cursor.execute('''
                INSERT INTO subscribers (user_id, username, first_name) 
                VALUES (?, ?, ?)
            ''', (user.id, user.username, user.first_name))
            message = "🎉 Successfully subscribed! You'll receive AI newsletter summaries."
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(message)
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        user = update.effective_user
        
        conn = sqlite3.connect('newsletter_bot.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE subscribers SET is_active = FALSE WHERE user_id = ?', (user.id,))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("😢 You've been unsubscribed. Use /subscribe to rejoin anytime!")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user = update.effective_user
        
        conn = sqlite3.connect('newsletter_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT is_active FROM subscribers WHERE user_id = ?', (user.id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            message = "✅ You're subscribed to AI newsletter summaries!"
        else:
            message = "❌ You're not subscribed. Use /subscribe to get started!"
        
        await update.message.reply_text(message)
    
    def run(self):
        """Start the bot"""
        self.app.run_polling()

if __name__ == "__main__":
    bot = NewsletterBot()
    bot.run()
```

### Step 3: Newsletter Fetcher (newsletter.py)

```python
import requests
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging

class OpenLetterFetcher:
    def __init__(self):
        self.base_url = "https://openletter.earth"
        self.rss_url = "https://openletter.earth/feed"  # Check if RSS exists
    
    def fetch_latest_newsletter(self):
        """Fetch the latest OpenLetter newsletter content"""
        try:
            # Try RSS first
            content = self._fetch_from_rss()
            if content:
                return content
            
            # Fallback to web scraping
            return self._fetch_from_web()
            
        except Exception as e:
            logging.error(f"Error fetching newsletter: {e}")
            return None
    
    def _fetch_from_rss(self):
        """Try to fetch from RSS feed"""
        try:
            feed = feedparser.parse(self.rss_url)
            if feed.entries:
                latest = feed.entries[0]
                return {
                    'title': latest.title,
                    'content': self._clean_content(latest.description),
                    'link': latest.link,
                    'published': latest.published if hasattr(latest, 'published') else datetime.now().isoformat()
                }
        except Exception as e:
            logging.warning(f"RSS fetch failed: {e}")
        return None
    
    def _fetch_from_web(self):
        """Fallback web scraping method"""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract latest article/newsletter (adjust selectors based on actual site)
            article = soup.find('article') or soup.find('div', class_='post')
            if not article:
                # Try to find main content area
                article = soup.find('main') or soup.find('div', class_='content')
            
            if article:
                title = article.find('h1') or article.find('h2')
                title_text = title.get_text().strip() if title else "Latest AI Newsletter"
                
                # Extract text content
                paragraphs = article.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])
                
                return {
                    'title': title_text,
                    'content': self._clean_content(content),
                    'link': self.base_url,
                    'published': datetime.now().isoformat()
                }
        except Exception as e:
            logging.error(f"Web scraping failed: {e}")
        
        return None
    
    def _clean_content(self, content):
        """Clean and prepare content for summarization"""
        if not content:
            return ""
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove common newsletter footer/header text
        content = re.sub(r'unsubscribe|privacy policy|terms of service', '', content, flags=re.IGNORECASE)
        
        return content[:4000]  # Limit content length for API
```

### Step 4: AI Summarizer (summarizer.py)

```python
import openai
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class NewsletterSummarizer:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI()
    
    def summarize_newsletter(self, content, title=""):
        """Summarize newsletter content with South African context"""
        try:
            prompt = self._create_prompt(content, title)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that summarizes newsletters for South African professionals, focusing on actionable AI insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return self._format_summary(summary, title)
            
        except Exception as e:
            logging.error(f"Summarization error: {e}")
            return None
    
    def _create_prompt(self, content, title):
        """Create summarization prompt"""
        return f"""
Please summarize this AI newsletter content for South African professionals and business owners. 
Focus on:
- Actionable AI tools and techniques
- Practical applications for South African businesses  
- Cost-effective solutions
- Local relevance

Title: {title}

Content: {content}

Provide a concise summary (3-5 bullet points) that highlights the most valuable and actionable insights.
Include any specific tools, costs, or implementation steps mentioned.
"""
    
    def _format_summary(self, summary, title):
        """Format summary for Telegram"""
        formatted = f"🤖 **AI Newsletter Summary**\n\n"
        
        if title:
            formatted += f"📰 **{title}**\n\n"
        
        formatted += f"{summary}\n\n"
        formatted += f"🇿🇦 *Curated for South African professionals*\n"
        formatted += f"⚡ *Powered by AI Newsletter Bot SA*"
        
        return formatted
```

### Step 5: Main Application (main.py)

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio
import logging
from bot import NewsletterBot
from newsletter import OpenLetterFetcher
from summarizer import NewsletterSummarizer
from scheduler import NewsletterScheduler

app = FastAPI(title="AI Newsletter Bot SA", version="1.0.0")

# Global instances
bot_instance = None
scheduler_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize bot and scheduler on startup"""
    global bot_instance, scheduler_instance
    
    logging.info("Starting AI Newsletter Bot SA...")
    
    # Initialize components
    bot_instance = NewsletterBot()
    scheduler_instance = NewsletterScheduler(bot_instance)
    
    # Start scheduler
    scheduler_instance.start()
    
    logging.info("Bot and scheduler started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    global scheduler_instance
    if scheduler_instance:
        scheduler_instance.stop()
    logging.info("Bot shut down successfully!")

@app.get("/")
async def root():
    return {"message": "AI Newsletter Bot SA is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy", "service": "AI Newsletter Bot SA"})

@app.post("/trigger-summary")
async def trigger_manual_summary():
    """Manual trigger for testing"""
    try:
        fetcher = OpenLetterFetcher()
        summarizer = NewsletterSummarizer()
        
        # Fetch newsletter
        newsletter = fetcher.fetch_latest_newsletter()
        if not newsletter:
            return {"error": "Could not fetch newsletter"}
        
        # Generate summary
        summary = summarizer.summarize_newsletter(
            newsletter['content'], 
            newsletter['title']
        )
        
        if not summary:
            return {"error": "Could not generate summary"}
        
        return {
            "success": True,
            "title": newsletter['title'],
            "summary": summary,
            "link": newsletter['link']
        }
        
    except Exception as e:
        logging.error(f"Manual trigger error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 6: Scheduler (scheduler.py)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import logging
import sqlite3
from newsletter import OpenLetterFetcher
from summarizer import NewsletterSummarizer

class NewsletterScheduler:
    def __init__(self, bot_instance):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot_instance
        self.fetcher = OpenLetterFetcher()
        self.summarizer = NewsletterSummarizer()
    
    def start(self):
        """Start the scheduler"""
        # Schedule daily newsletter processing at 9 AM
        self.scheduler.add_job(
            self.process_and_send_newsletter,
            CronTrigger(hour=9, minute=0),
            id='daily_newsletter'
        )
        
        # Schedule weekly summary on Friday at 5 PM
        self.scheduler.add_job(
            self.send_weekly_summary,
            CronTrigger(day_of_week=4, hour=17, minute=0),
            id='weekly_summary'
        )
        
        self.scheduler.start()
        logging.info("Newsletter scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logging.info("Newsletter scheduler stopped")
    
    async def process_and_send_newsletter(self):
        """Process latest newsletter and send to subscribers"""
        try:
            logging.info("Processing newsletter...")
            
            # Fetch newsletter
            newsletter = self.fetcher.fetch_latest_newsletter()
            if not newsletter:
                logging.warning("No newsletter content found")
                return
            
            # Generate summary
            summary = self.summarizer.summarize_newsletter(
                newsletter['content'],
                newsletter['title']
            )
            
            if not summary:
                logging.warning("Could not generate summary")
                return
            
            # Add source link
            full_message = f"{summary}\n\n🔗 [Read Full Newsletter]({newsletter['link']})"
            
            # Send to all subscribers
            await self.send_to_subscribers(full_message)
            
            logging.info("Newsletter processed and sent successfully")
            
        except Exception as e:
            logging.error(f"Newsletter processing error: {e}")
    
    async def send_weekly_summary(self):
        """Send weekly summary message"""
        weekly_message = """
🗓️ **Weekly AI Recap**

Thanks for staying updated with AI Newsletter Bot SA this week!

🔄 New summaries coming next week
💡 Have suggestions? Reply to this message
🚀 Keep innovating with AI!

*Your South African AI Newsletter Bot*
        """
        await self.send_to_subscribers(weekly_message)
    
    async def send_to_subscribers(self, message):
        """Send message to all active subscribers"""
        try:
            conn = sqlite3.connect('newsletter_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM subscribers WHERE is_active = TRUE')
            subscribers = cursor.fetchall()
            conn.close()
            
            for (user_id,) in subscribers:
                try:
                    await self.bot.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    logging.warning(f"Could not send to user {user_id}: {e}")
            
            logging.info(f"Message sent to {len(subscribers)} subscribers")
            
        except Exception as e:
            logging.error(f"Broadcast error: {e}")
```

### Step 7: Deployment Configuration

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Railway deployment (railway.json):**
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## 🧪 Testing Checklist

### Day 6 Testing Tasks:
- [ ] Test Telegram bot commands (/start, /subscribe, /unsubscribe)
- [ ] Test newsletter fetching from OpenLetter
- [ ] Test AI summarization with sample content
- [ ] Test scheduled tasks (manual trigger)
- [ ] Test database operations
- [ ] Test error handling
- [ ] Test message formatting in Telegram

### Test Commands:
```bash
# Test bot locally
python app/bot.py

# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/trigger-summary

# Test newsletter fetching
python -c "from app.newsletter import OpenLetterFetcher; print(OpenLetterFetcher().fetch_latest_newsletter())"
```

---

## 🚀 Deployment Instructions

### Option 1: Railway (Recommended)
1. Create account at railway.app
2. Connect GitHub repository
3. Add environment variables in Railway dashboard
4. Deploy automatically

### Option 2: Heroku
1. Install Heroku CLI
2. Create new app: `heroku create newsletter-bot-sa`
3. Set environment variables: `heroku config:set TELEGRAM_BOT_TOKEN=xxx`
4. Deploy: `git push heroku main`

---

## 📊 Success Metrics for Week 1

### Must-Have:
- [ ] Bot responds to basic commands
- [ ] Successfully fetches OpenLetter content
- [ ] Generates AI summaries
- [ ] Sends summaries to subscribers
- [ ] Basic error handling works

### Nice-to-Have:
- [ ] Scheduled automatic processing
- [ ] 10+ test subscribers
- [ ] Clean message formatting
- [ ] Basic analytics/logging

---

## 🎯 Post-Week 1 Roadmap

### Week 2: Enhancement
- Add more newsletter sources
- Improve summarization prompts
- Add user feedback collection
- Implement basic analytics

### Week 3: Scale
- Add newsletter archiving
- Implement user preferences
- Add rich media support
- Optimize performance

---

## 🆘 Troubleshooting Guide

### Common Issues:
1. **Telegram Bot Token Issues**: Check bot creation with @BotFather
2. **OpenAI API Errors**: Verify API key and billing account
3. **Newsletter Fetching Fails**: Check if OpenLetter changed their structure
4. **Database Errors**: Ensure SQLite file permissions
5. **Deployment Issues**: Check environment variables

### Debug Commands:
```python
# Test individual components
from app.newsletter import OpenLetterFetcher
from app.summarizer import NewsletterSummarizer

# Test fetcher
fetcher = OpenLetterFetcher()
content = fetcher.fetch_latest_newsletter()
print(content)

# Test summarizer
summarizer = NewsletterSummarizer()
summary = summarizer.summarize_newsletter("Test content", "Test Title")
print(summary)
```

---

## ✅ Final Checklist for Demo

Before the demo:
- [ ] Bot is deployed and accessible
- [ ] At least one successful newsletter summary generated
- [ ] Test users can subscribe/unsubscribe
- [ ] Manual trigger endpoint works
- [ ] Basic error handling in place
- [ ] Logs are readable and helpful

Demo Script:
1. Show bot subscription process
2. Demonstrate manual newsletter fetch and summary
3. Show automated message delivery
4. Explain next features (more sources, scheduling)

**Time Estimate: 40-50 hours (doable in 1 week with focused effort)**