# Gmail Email Extraction Setup Guide 📧

This guide will help you set up Gmail email extraction as your primary newsletter source for the AI Newsletter Bot.

## Overview

The Gmail integration allows the bot to:
- 📧 Extract newsletters directly from your Gmail inbox
- 🔍 Search for AI-related content automatically
- 📊 Score emails by relevance for summarization
- 🔄 Integrate seamlessly with existing summarization pipeline

## Prerequisites

1. **Gmail Account**: Active Gmail account with newsletters
2. **Google Cloud Console Access**: For API setup
3. **Python Environment**: Python 3.9+ with pip

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd newsletter_bot
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

#### A. Create Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click project dropdown → "New Project"
3. Name: "Newsletter Bot Gmail"
4. Click "Create"

#### B. Enable Gmail API
1. Navigate to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Gmail API" → "Enable"

#### C. Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. **If prompted to configure OAuth consent screen:**
   - User Type: **External**
   - App name: **Newsletter Bot**
   - User support email: **your email**
   - Developer contact: **your email**
   - Save and continue through all steps
   - Add your email to "Test users" section
4. Application type: **Desktop application**
5. Name: **Newsletter Bot Gmail Client**
6. Click "Create"

#### D. Download Credentials
1. Click download button next to your credential
2. Save file as `credentials.json` in the `newsletter_bot/` directory
3. The file should contain your OAuth client configuration

### 3. Configuration

#### A. Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Required variables:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
ENABLE_GMAIL=true
```

#### B. Gmail Credentials
Ensure `credentials.json` is in the newsletter_bot directory:
```
newsletter_bot/
├── credentials.json  ← Your Gmail API credentials
├── app/
└── ...
```

### 4. Test Gmail Integration

Run the setup script:
```bash
python gmail_setup.py
```

This will:
- ✅ Verify credentials.json exists and is valid
- 🔐 Walk through OAuth authentication
- 📧 Test email fetching
- 🧪 Validate integration

### 5. First Run

Start the bot:
```bash
python run.py
```

Check logs for Gmail integration:
```
📧 Gmail fetcher added as primary source
📡 Trying GmailNewsletterFetcher (1/2)...
📧 Fetching latest newsletter-like email from Gmail...
✅ Successfully fetched from GmailNewsletterFetcher
```

## How Gmail Integration Works

### Email Search Criteria

The bot searches for emails matching these patterns:

**Subject-based:**
- Contains: newsletter, digest, update, weekly, daily
- Contains: AI, artificial intelligence, machine learning, tech

**Sender-based:**
- From: openai.com, anthropic.com, deepmind.com
- From: techcrunch.com, wired.com, arstechnica.com
- Contains: newsletter, digest, update, news

**Time-based:**
- Recent emails (last 7 days by default)
- Configurable search window

### Email Scoring System

Emails are scored for relevance:

| Criteria | Points |
|----------|---------|
| Subject contains "newsletter/digest" | +10 |
| Subject contains "AI/tech" | +8 |
| From AI company domains | +15 |
| From newsletter services | +5 |
| Content length > 1000 chars | +5 |
| AI-related content | +3 |

The highest-scoring email is selected for summarization.

### Content Processing

1. **Extraction**: Get email body (HTML → text)
2. **Cleaning**: Remove signatures, footers, unsubscribe links
3. **Formatting**: Prepare for AI summarization
4. **Integration**: Feed into existing summarization pipeline

## Customization

### Search Queries

Edit `app/gmail_fetcher.py` to modify search patterns:

```python
self.search_queries = [
    'subject:newsletter OR subject:digest OR subject:update',
    'from:your-favorite-newsletter.com',
    'subject:"custom keyword"',
    # Add your own patterns
]
```

### Scoring Algorithm

Modify `_score_email_relevance()` method:

```python
def _score_email_relevance(self, email: Dict) -> int:
    score = 0
    
    # Add custom scoring logic
    if 'your-keyword' in email['subject'].lower():
        score += 20
    
    return score
```

### Time Range

Adjust search window in `fetch_latest_newsletter()`:

```python
emails = self.fetch_recent_emails(
    max_results=10,  # Number of emails to consider
    days_back=3      # Days to look back
)
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
❌ Gmail authentication failed
```
**Solutions:**
- Check OAuth consent screen is configured
- Verify your email is in "Test users"
- Delete `token.pickle` and re-authenticate
- Check `credentials.json` is valid JSON

#### 2. No Emails Found
```
⚠️ No emails found
```
**Solutions:**
- Check if you have newsletters in Gmail
- Verify search queries match your content
- Increase `days_back` parameter
- Check Gmail API quotas in Google Cloud Console

#### 3. Import Errors
```
❌ Failed to import Gmail modules
```
**Solutions:**
- Install requirements: `pip install -r requirements.txt`
- Check Python environment is activated
- Verify Google API packages are installed

#### 4. Rate Limiting
```
⚠️ Gmail API quota exceeded
```
**Solutions:**
- Check Google Cloud Console quotas
- Reduce fetch frequency
- Implement exponential backoff

### Testing Commands

```bash
# Test Gmail fetcher only
python -c "from app.gmail_fetcher import GmailNewsletterFetcher; print(GmailNewsletterFetcher().fetch_latest_newsletter())"

# Test complete newsletter pipeline
python app/newsletter.py

# Test with debug logging
python run.py --debug

# Clear authentication
rm token.pickle
```

### Log Analysis

Look for these log messages:

**Success:**
```
✅ Gmail authentication successful
📧 Gmail fetcher added as primary source
✅ Successfully fetched from GmailNewsletterFetcher
```

**Issues:**
```
❌ Gmail authentication failed
⚠️ No emails found
⚠️ Gmail integration not available
```

## Security Considerations

### OAuth Tokens
- `token.pickle` contains your OAuth token
- Keep it secure and don't commit to version control
- Token automatically refreshes when expired

### API Keys
- Store in environment variables only
- Never commit `credentials.json` to version control
- Use service accounts for production deployment

### Permissions
- Bot only requests read access to Gmail
- No email modification or sending capabilities
- Limited to search and read operations

## Production Deployment

### Environment Variables
```bash
# Required for production
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_api_key
ENABLE_GMAIL=true

# Optional production settings
MAX_CONTENT_LENGTH=4000
SUMMARY_MAX_TOKENS=500
DAILY_SUMMARY_TIME=09:00
TIMEZONE=Africa/Johannesburg
```

### File Management
- Upload `credentials.json` to production environment
- Ensure `token.pickle` is writable
- Set up log rotation for Gmail API calls

### Monitoring
- Monitor Gmail API quotas
- Track email processing success rates
- Set up alerts for authentication failures

## Next Steps

1. **Test the integration** with your Gmail account
2. **Customize search queries** for your specific newsletters
3. **Monitor performance** and adjust parameters
4. **Add more email sources** if needed
5. **Deploy to production** with proper monitoring

## Support

- Run `python gmail_setup.py` for interactive setup
- Check Google Cloud Console for API quotas
- Review logs for detailed error messages
- Test with a small number of emails first

---

🎉 **Congratulations!** You now have Gmail email extraction as your primary newsletter source. The bot will automatically find and summarize the most relevant AI newsletters from your inbox!