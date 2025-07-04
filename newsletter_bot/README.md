# AI Newsletter Bot SA - MVP

## Quick Start

1. **Setup Environment:**
   ```bash
   cd newsletter_bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your actual tokens
   ```

3. **Get Telegram Bot Token:**
   - Message @BotFather on Telegram
   - Create new bot with /newbot
   - Copy token to .env file

4. **Get OpenAI API Key:**
   - Visit https://platform.openai.com/api-keys
   - Create new API key
   - Copy to .env file

5. **Run Locally:**
   ```bash
   python app/main.py
   ```

6. **Test Bot:**
   - Find your bot on Telegram
   - Send /start command
   - Try /subscribe

## Project Structure
```
newsletter_bot/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── bot.py               # Telegram bot logic
│   ├── newsletter.py        # Newsletter fetching/parsing
│   ├── summarizer.py        # AI summarization
│   └── scheduler.py         # Task scheduling
├── requirements.txt
├── Dockerfile
├── .env.template
└── README.md
```

## Development Timeline
- Day 1: Setup & Basic Bot
- Day 2: Newsletter Fetching
- Day 3: AI Summarization
- Day 4: Bot Commands & Database
- Day 5: Scheduling & Automation
- Day 6: Testing & Bug Fixes
- Day 7: Deployment & Demo

## Demo Checklist
- [ ] Bot responds to commands
- [ ] Newsletter fetching works
- [ ] AI summaries are generated
- [ ] Messages sent to subscribers
- [ ] Basic error handling
- [ ] Deployed to production

## Support
Check the MVP_Instructions_Newsletter_Bot.md for detailed implementation guide.
