#!/usr/bin/env python3
"""
Quick setup script for AI Newsletter Bot SA MVP
Run this to create the complete project structure
"""

import os
import sys

def create_directory_structure():
    """Create the project directory structure"""
    directories = [
        "newsletter_bot",
        "newsletter_bot/app",
        "newsletter_bot/tests"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_requirements_txt():
    """Create requirements.txt file"""
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
python-telegram-bot==20.7
openai==1.3.7
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
apscheduler==3.10.4
feedparser==6.0.10"""
    
    with open("newsletter_bot/requirements.txt", "w") as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_env_template():
    """Create .env template file"""
    env_template = """# Copy this to .env and fill in your actual tokens
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///newsletter_bot.db
DEBUG=True"""
    
    with open("newsletter_bot/.env.template", "w") as f:
        f.write(env_template)
    print("✅ Created .env.template")

def create_dockerfile():
    """Create Dockerfile"""
    dockerfile = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]"""
    
    with open("newsletter_bot/Dockerfile", "w") as f:
        f.write(dockerfile)
    print("✅ Created Dockerfile")

def create_init_files():
    """Create __init__.py files"""
    init_files = [
        "newsletter_bot/app/__init__.py",
        "newsletter_bot/tests/__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, "w") as f:
            f.write("# This file makes Python treat the directory as a package\n")
        print(f"✅ Created {init_file}")

def create_readme():
    """Create README.md"""
    readme = """# AI Newsletter Bot SA - MVP

## Quick Start

1. **Setup Environment:**
   ```bash
   cd newsletter_bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
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
"""
    
    with open("newsletter_bot/README.md", "w") as f:
        f.write(readme)
    print("✅ Created README.md")

def create_gitignore():
    """Create .gitignore"""
    gitignore = """.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.db
*.sqlite3
.venv/
venv/
.idea/
.vscode/
*.log
.DS_Store"""
    
    with open("newsletter_bot/.gitignore", "w") as f:
        f.write(gitignore)
    print("✅ Created .gitignore")

def main():
    print("🚀 Setting up AI Newsletter Bot SA MVP Project...")
    print()
    
    # Create directory structure
    create_directory_structure()
    
    # Create configuration files
    create_requirements_txt()
    create_env_template()
    create_dockerfile()
    create_gitignore()
    
    # Create Python package files
    create_init_files()
    
    # Create documentation
    create_readme()
    
    print()
    print("🎉 Project setup complete!")
    print()
    print("Next steps:")
    print("1. cd newsletter_bot")
    print("2. cp .env.template .env")
    print("3. Edit .env with your API keys")
    print("4. python -m venv venv")
    print("5. source venv/bin/activate")
    print("6. pip install -r requirements.txt")
    print("7. Follow the MVP_Instructions_Newsletter_Bot.md guide")
    print()
    print("📖 Check README.md for detailed setup instructions")

if __name__ == "__main__":
    main()