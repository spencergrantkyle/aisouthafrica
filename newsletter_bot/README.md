# AI Newsletter Bot SA 🤖

Automatically summarize AI newsletters and distribute them via Telegram, with Gmail integration for extracting newsletter content directly from your inbox.

## Features

- 📧 **Gmail Integration**: Extract newsletters directly from your Gmail inbox
- 🤖 **AI Summarization**: Powered by OpenAI GPT-3.5-turbo
- 🇿🇦 **South African Context**: Focused on local AI applications and businesses
- 📱 **Telegram Bot**: Easy subscription management and message delivery
- 🔄 **Automated Scheduling**: Daily and weekly newsletter processing
- 📊 **Multiple Sources**: Gmail, OpenLetter, and extensible for more sources

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Gmail API (New Primary Source!)
```bash
# Run the Gmail setup script
python gmail_setup.py
```

This will guide you through:
- Creating a Google Cloud project
- Enabling Gmail API
- Setting up OAuth credentials
- Testing the integration

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required API keys:
- `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/botfather)
- `OPENAI_API_KEY`: Get from [OpenAI](https://platform.openai.com/api-keys)

### 4. Run the Bot
```bash
python run.py
```

## Gmail Integration Setup

### Prerequisites
1. Google account with Gmail access
2. Google Cloud Console access

### Step-by-Step Setup
1. **Google Cloud Console**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

3. **Create Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Create OAuth 2.0 client ID (Desktop application)
   - Download as `credentials.json`

4. **Configure OAuth Consent**:
   - Set up OAuth consent screen
   - Add your email to test users

5. **Place Credentials**:
   - Save `credentials.json` in the `newsletter_bot/` directory
   - Run `python gmail_setup.py` to test

### Gmail Search Queries
The bot searches for emails with these patterns:
- Subject contains: newsletter, digest, update, AI, artificial intelligence
- From domains: openai.com, anthropic.com, deepmind.com, techcrunch.com
- Recent emails (last 7 days by default)

You can customize search queries in `app/gmail_fetcher.py`.

## Architecture

```
Gmail Inbox → Gmail API → Content Extraction → AI Summarization → Telegram Bot → Users
     ↓
OpenLetter → Web Scraping → Content Cleaning → Same Pipeline Above
```

## Bot Commands

- `/start` - Welcome message and instructions
- `/subscribe` - Subscribe to newsletter summaries
- `/unsubscribe` - Unsubscribe from summaries
- `/status` - Check subscription status

## File Structure

```
newsletter_bot/
├── app/
│   ├── bot.py              # Telegram bot logic
│   ├── gmail_fetcher.py    # Gmail email extraction (NEW!)
│   ├── newsletter.py       # Multiple source content fetching
│   ├── summarizer.py       # AI summarization
│   ├── scheduler.py        # Task scheduling
│   └── main.py            # FastAPI application
├── credentials.json        # Gmail API credentials
├── token.pickle           # Gmail OAuth token (auto-generated)
├── requirements.txt       # Python dependencies
├── gmail_setup.py         # Gmail setup helper
├── run.py                 # Application entry point
└── .env                   # Environment configuration
```

## Development

### Testing Gmail Integration
```bash
# Test Gmail fetcher directly
python -c "from app.gmail_fetcher import GmailNewsletterFetcher; print(GmailNewsletterFetcher().fetch_latest_newsletter())"

# Test complete newsletter pipeline
python app/newsletter.py
```

### Adding New Email Sources
1. Create a new fetcher class in `app/gmail_fetcher.py`
2. Implement `fetch_latest_newsletter()` method
3. Add to `NewsletterFetcher` in `app/newsletter.py`

### Customizing AI Prompts
Edit `app/summarizer.py` to modify:
- Summarization prompts
- South African context
- Output formatting
- Token limits

## Environment Variables

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key

# Optional
ENABLE_GMAIL=true                    # Enable Gmail integration
MAX_CONTENT_LENGTH=4000             # Max content length for AI
SUMMARY_MAX_TOKENS=500              # Max tokens in summary
DAILY_SUMMARY_TIME=09:00            # Daily processing time
TIMEZONE=Africa/Johannesburg        # Local timezone
```

## Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Heroku
```bash
# Install Heroku CLI
# Create app
heroku create newsletter-bot-sa
git push heroku main
```

### Docker
```bash
# Build image
docker build -t newsletter-bot .

# Run container
docker run -e TELEGRAM_BOT_TOKEN=your_token -e OPENAI_API_KEY=your_key newsletter-bot
```

## Troubleshooting

### Gmail Issues
- **Authentication fails**: Check OAuth consent screen setup
- **No emails found**: Verify search queries match your newsletters
- **Rate limiting**: Gmail API has daily quotas (check Google Cloud Console)

### Bot Issues
- **Bot doesn't respond**: Check Telegram bot token
- **No summaries**: Verify OpenAI API key and credits
- **Scheduling issues**: Check timezone settings

### Common Solutions
```bash
# Clear Gmail auth token
rm token.pickle

# Reset database
rm newsletter_bot.db

# Check logs
python run.py --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

MIT License - feel free to use for personal and commercial projects.

## Support

- Create an issue on GitHub
- Check the troubleshooting section
- Run `python gmail_setup.py` for Gmail setup help

---

Built with ❤️ for the South African AI community 🇿🇦
