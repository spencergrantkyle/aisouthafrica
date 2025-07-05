#!/usr/bin/env python3
"""
Gmail API Setup Script for Newsletter Bot

This script helps set up Gmail API integration for the newsletter bot.
It provides step-by-step instructions and validates the setup.
"""

import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("📧 Gmail API Setup for Newsletter Bot")
    print("=" * 60)
    print()

def check_credentials_file():
    """Check if credentials.json exists"""
    credentials_path = Path("credentials.json")
    
    if credentials_path.exists():
        print("✅ credentials.json found")
        
        # Validate JSON structure
        try:
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
            
            if 'installed' in creds or 'web' in creds:
                print("✅ credentials.json appears to be valid")
                return True
            else:
                print("❌ credentials.json has invalid structure")
                return False
                
        except json.JSONDecodeError:
            print("❌ credentials.json is not valid JSON")
            return False
    else:
        print("❌ credentials.json not found")
        return False

def print_setup_instructions():
    """Print detailed setup instructions"""
    print("\n📋 Gmail API Setup Instructions:")
    print("-" * 40)
    print()
    
    print("1. 🌐 Go to the Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    
    print("2. 🆕 Create a new project or select an existing one:")
    print("   - Click on the project dropdown")
    print("   - Click 'New Project'")
    print("   - Name: 'Newsletter Bot Gmail'")
    print("   - Click 'Create'")
    print()
    
    print("3. 📧 Enable Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API'")
    print("   - Click on 'Gmail API'")
    print("   - Click 'Enable'")
    print()
    
    print("4. 🔐 Create credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - If prompted, configure OAuth consent screen first:")
    print("     - User Type: External")
    print("     - App name: Newsletter Bot")
    print("     - User support email: your email")
    print("     - Developer contact: your email")
    print("     - Save and continue through all steps")
    print("   - Application type: Desktop application")
    print("   - Name: Newsletter Bot Gmail Client")
    print("   - Click 'Create'")
    print()
    
    print("5. 📁 Download credentials:")
    print("   - Click the download button next to your credential")
    print("   - Save the file as 'credentials.json' in the newsletter_bot folder")
    print("   - The file should be in the same directory as this script")
    print()
    
    print("6. 🔧 Configure OAuth consent screen (if not done):")
    print("   - Go to 'APIs & Services' > 'OAuth consent screen'")
    print("   - Add your email to 'Test users' section")
    print("   - This allows you to use the app during development")
    print()

def test_gmail_integration():
    """Test Gmail integration"""
    print("\n🧪 Testing Gmail Integration:")
    print("-" * 30)
    
    try:
        # Import Gmail fetcher
        from app.gmail_fetcher import GmailNewsletterFetcher
        
        print("✅ Gmail fetcher module imported successfully")
        
        # Initialize fetcher
        fetcher = GmailNewsletterFetcher()
        print("✅ Gmail fetcher initialized")
        
        # Test authentication (this will prompt for OAuth if needed)
        print("🔐 Testing Gmail authentication...")
        print("Note: This will open a browser window for OAuth authentication")
        print("Please authorize the application to access your Gmail")
        
        if fetcher.gmail_fetcher.authenticate():
            print("✅ Gmail authentication successful")
            
            # Test fetching emails
            print("📧 Testing email fetching...")
            emails = fetcher.gmail_fetcher.fetch_recent_emails(max_results=1, days_back=7)
            
            if emails:
                print(f"✅ Successfully fetched {len(emails)} email(s)")
                print(f"   First email: {emails[0]['subject']}")
                return True
            else:
                print("⚠️ No emails found (this might be normal)")
                return True
                
        else:
            print("❌ Gmail authentication failed")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import Gmail modules: {e}")
        print("Make sure you've installed the requirements:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Gmail integration test failed: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check if credentials exist
    if not check_credentials_file():
        print_setup_instructions()
        print("\n⚠️ Please complete the setup steps above and run this script again.")
        return
    
    # Test integration
    print("\n🎯 Credentials found! Testing integration...")
    
    if test_gmail_integration():
        print("\n🎉 Gmail integration setup complete!")
        print("\n📝 Next steps:")
        print("1. Run the newsletter bot: python run.py")
        print("2. The bot will now fetch emails from Gmail as the primary source")
        print("3. Check the logs to see Gmail email fetching in action")
        print()
        print("💡 Tips:")
        print("- Make sure you have newsletters in your Gmail inbox")
        print("- The bot looks for emails with 'newsletter', 'digest', 'update' keywords")
        print("- AI-related emails get higher priority for summarization")
        print("- Check app/gmail_fetcher.py to customize search queries")
    else:
        print("\n❌ Setup incomplete. Please check the error messages above.")

if __name__ == "__main__":
    main()