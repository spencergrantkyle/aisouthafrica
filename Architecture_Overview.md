# AI Newsletter Bot SA - Architecture Overview

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenLetter    │    │   Other News    │    │  Future Sources │
│   Newsletter    │    │   Sources       │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────┐
                    │   Content Fetcher       │
                    │   (newsletter.py)       │
                    │                         │
                    │ • RSS Feed Reader       │
                    │ • Web Scraper           │
                    │ • Content Cleaner       │
                    └─────────────┬───────────┘
                                  │
                     ┌────────────▼────────────┐
                     │   AI Summarizer         │
                     │   (summarizer.py)       │
                     │                         │
                     │ • OpenAI GPT-3.5        │
                     │ • South African Context │
                     │ • Actionable Insights   │
                     └────────────┬────────────┘
                                  │
                     ┌────────────▼────────────┐
                     │   Scheduler             │
                     │   (scheduler.py)        │
                     │                         │
                     │ • Daily Processing      │
                     │ • Weekly Summaries      │
                     │ • Error Handling        │
                     └────────────┬────────────┘
                                  │
                     ┌────────────▼────────────┐
                     │   Telegram Bot          │
                     │   (bot.py)              │
                     │                         │
                     │ • User Management       │
                     │ • Message Formatting    │
                     │ • Command Handling      │
                     └────────────┬────────────┘
                                  │
                     ┌────────────▼────────────┐
                     │   SQLite Database       │
                     │                         │
                     │ • User Subscriptions    │
                     │ • Message History       │
                     │ • Basic Analytics       │
                     └─────────────────────────┘
```

## Data Flow

```
Newsletter Published
        ↓
   [Scheduler Triggers]
        ↓
   Fetch Content
        ↓
   Clean & Process
        ↓
   AI Summarization
        ↓
   Format for Telegram
        ↓
   Send to Subscribers
        ↓
   Log & Track Metrics
```

## Component Details

### 1. Content Fetcher (`newsletter.py`)
**Purpose:** Retrieve newsletter content from various sources
- **Primary Source:** OpenLetter (RSS/Web scraping)
- **Fallback Methods:** Direct web scraping if RSS fails
- **Content Processing:** Clean HTML, remove boilerplate, limit length
- **Error Handling:** Graceful fallback between methods

### 2. AI Summarizer (`summarizer.py`)
**Purpose:** Generate actionable summaries for South African context
- **AI Model:** OpenAI GPT-3.5-turbo
- **Prompt Engineering:** Focused on SA business applications
- **Output Format:** 3-5 bullet points with practical insights
- **Cost Optimization:** Content length limits, efficient prompts

### 3. Telegram Bot (`bot.py`)
**Purpose:** Handle user interactions and message delivery
- **Core Commands:**
  - `/start` - Welcome message
  - `/subscribe` - Join newsletter updates
  - `/unsubscribe` - Stop receiving updates
  - `/status` - Check subscription status
- **Message Broadcasting:** Send summaries to all subscribers
- **Rate Limiting:** Prevent API throttling

### 4. Scheduler (`scheduler.py`)
**Purpose:** Automate newsletter processing and delivery
- **Daily Schedule:** 9 AM processing (configurable)
- **Weekly Updates:** Friday 5 PM summary
- **Error Recovery:** Retry failed operations
- **Logging:** Track processing success/failures

### 5. Database (SQLite)
**Purpose:** Store user data and basic analytics
```sql
CREATE TABLE subscribers (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 6. FastAPI Web Server (`main.py`)
**Purpose:** Provide API endpoints and health monitoring
- **Health Check:** `/health` endpoint
- **Manual Trigger:** `/trigger-summary` for testing
- **Status Monitoring:** Bot and scheduler status
- **Webhook Support:** Future Telegram webhook integration

## Technology Stack

### Core Technologies
- **Language:** Python 3.9+
- **Web Framework:** FastAPI
- **Bot Library:** python-telegram-bot
- **AI Service:** OpenAI API
- **Database:** SQLite
- **Scheduling:** APScheduler

### External Services
- **AI Processing:** OpenAI GPT-3.5-turbo
- **Messaging:** Telegram Bot API
- **Hosting:** Railway.app / Heroku
- **Monitoring:** Built-in logging + FastAPI health checks

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Railway/Heroku                      │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │   FastAPI       │  │   SQLite DB     │             │
│  │   Web Server    │  │   (Persistent   │             │
│  │                 │  │    Volume)      │             │
│  └─────────┬───────┘  └─────────────────┘             │
│            │                                           │
│  ┌─────────▼───────┐  ┌─────────────────┐             │
│  │   Telegram Bot  │  │   Scheduler     │             │
│  │   (Polling)     │  │   Background    │             │
│  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
              │                              │
              ▼                              ▼
    ┌─────────────────┐              ┌─────────────────┐
    │  Telegram API   │              │   OpenAI API    │
    │                 │              │                 │
    └─────────────────┘              └─────────────────┘
```

## Security Considerations

### API Keys
- Store in environment variables
- Never commit to version control
- Rotate keys regularly

### User Data
- Minimal data collection (only Telegram user ID)
- GDPR compliance for SA users
- Option to delete user data

### Rate Limiting
- Respect Telegram API limits (30 messages/second)
- OpenAI API rate limiting
- Implement backoff strategies

## Scalability Plan

### Phase 1 (MVP - Week 1)
- Single OpenLetter source
- Basic Telegram bot
- SQLite database
- Manual deployment

### Phase 2 (Week 2-4)
- Multiple newsletter sources
- Improved AI prompts
- User preferences
- Automated deployment

### Phase 3 (Month 2+)
- PostgreSQL database
- Redis caching
- Webhook mode for Telegram
- Analytics dashboard
- Load balancing

## Error Handling Strategy

### Newsletter Fetching
```python
try:
    content = fetch_from_rss()
except Exception:
    content = fetch_from_web()
    if not content:
        log_error_and_skip()
```

### AI Summarization
```python
try:
    summary = openai_summarize(content)
except RateLimitError:
    wait_and_retry()
except APIError:
    use_fallback_summary()
```

### Message Delivery
```python
for user in subscribers:
    try:
        send_message(user, summary)
    except UserBlocked:
        deactivate_user(user)
    except NetworkError:
        retry_later(user, summary)
```

## Monitoring & Metrics

### Key Metrics
- Newsletter processing success rate
- AI summarization quality scores
- User engagement (subscription/retention)
- Message delivery success rate
- System uptime and performance

### Logging Strategy
```python
logging.info(f"Newsletter processed: {title}")
logging.warning(f"Failed to send to user {user_id}: {error}")
logging.error(f"Critical error in scheduler: {exception}")
```

### Health Checks
- FastAPI `/health` endpoint
- Database connectivity test
- External API availability check
- Background task status verification

## Future Enhancements

### Week 2-4 Roadmap
1. **Additional Sources:**
   - TechCentral SA
   - MyBroadband AI section
   - Local AI meetup announcements

2. **Enhanced Features:**
   - User preferences (topics, frequency)
   - Feedback collection (👍/👎)
   - Newsletter archives
   - Rich media support (images, videos)

3. **Analytics:**
   - User engagement tracking
   - Content performance metrics
   - A/B testing for summaries
   - Business impact measurement

### Long-term Vision
- Multi-language support (Afrikaans, Zulu)
- Industry-specific newsletters
- Interactive AI assistant
- Community features (discussions, Q&A)
- Integration with South African business tools

---

## Quick Start for Developers

1. **Run Setup Script:**
   ```bash
   python setup_project.py
   ```

2. **Configure Environment:**
   ```bash
   cd newsletter_bot
   cp .env.template .env
   # Edit .env with your API keys
   ```

3. **Install Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Test Components:**
   ```bash
   # Test newsletter fetching
   python -c "from app.newsletter import OpenLetterFetcher; print(OpenLetterFetcher().fetch_latest_newsletter())"
   
   # Test bot commands
   python app/bot.py
   ```

5. **Deploy:**
   ```bash
   # Railway
   railway login
   railway deploy
   
   # Or Heroku
   heroku create newsletter-bot-sa
   git push heroku main
   ```

This architecture is designed to be simple enough for a junior developer to implement in one week while being scalable for future enhancements.