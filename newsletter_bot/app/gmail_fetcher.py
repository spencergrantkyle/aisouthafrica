import os
import pickle
import base64
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailFetcher:
    """Fetcher for Gmail emails that integrates with the existing newsletter system"""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        """
        Initialize Gmail fetcher
        
        Args:
            credentials_file: Path to Gmail API credentials JSON file
            token_file: Path to store OAuth token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.search_queries = [
            # Common newsletter and AI-related queries
            'subject:newsletter OR subject:digest OR subject:update',
            'from:newsletter OR from:digest OR from:update',
            'subject:AI OR subject:"artificial intelligence" OR subject:"machine learning"',
            'from:openai.com OR from:anthropic.com OR from:deepmind.com',
            'subject:"tech news" OR subject:"technology update"',
            'from:techcrunch.com OR from:wired.com OR from:arstechnica.com',
        ]
        logger.info("📧 Gmail fetcher initialized")
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        try:
            logger.info("🔐 Authenticating with Gmail API...")
            
            creds = None
            # Load existing token
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"❌ Credentials file not found: {self.credentials_file}")
                        raise FileNotFoundError(f"Gmail credentials file not found: {self.credentials_file}")
                    
                    logger.info("🆕 Getting new credentials...")
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("✅ Gmail authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Gmail authentication failed: {e}")
            return False
    
    def fetch_recent_emails(self, max_results: int = 10, days_back: int = 7) -> List[Dict]:
        """
        Fetch recent emails based on search queries
        
        Args:
            max_results: Maximum number of emails to fetch
            days_back: Number of days back to search
            
        Returns:
            List of email dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        logger.info(f"📧 Fetching recent emails (last {days_back} days, max {max_results} results)")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        date_query = f"after:{start_date.strftime('%Y/%m/%d')}"
        
        all_emails = []
        
        try:
            # Search with different queries
            for query in self.search_queries:
                full_query = f"{query} {date_query}"
                logger.info(f"🔍 Searching with query: {full_query}")
                
                try:
                    # Search for messages
                    results = self.service.users().messages().list(
                        userId='me',
                        q=full_query,
                        maxResults=max_results
                    ).execute()
                    
                    messages = results.get('messages', [])
                    logger.info(f"📨 Found {len(messages)} messages for query")
                    
                    # Fetch detailed email content
                    for message in messages[:max_results]:
                        email_data = self._get_email_content(message['id'])
                        if email_data:
                            all_emails.append(email_data)
                    
                except HttpError as e:
                    logger.warning(f"⚠️ Search query failed: {e}")
                    continue
            
            # Remove duplicates based on message ID
            seen_ids = set()
            unique_emails = []
            for email in all_emails:
                if email['id'] not in seen_ids:
                    seen_ids.add(email['id'])
                    unique_emails.append(email)
            
            # Sort by date (newest first)
            unique_emails.sort(key=lambda x: x['date'], reverse=True)
            
            # Limit results
            final_emails = unique_emails[:max_results]
            
            logger.info(f"✅ Successfully fetched {len(final_emails)} unique emails")
            return final_emails
            
        except Exception as e:
            logger.error(f"❌ Error fetching emails: {e}")
            return []
    
    def _get_email_content(self, message_id: str) -> Optional[Dict]:
        """
        Get detailed content of a specific email
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary with email content or None if failed
        """
        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = self._get_header_value(headers, 'Subject')
            sender = self._get_header_value(headers, 'From')
            date = self._get_header_value(headers, 'Date')
            
            # Extract body content
            body = self._extract_body(message['payload'])
            
            if not body or len(body) < 50:
                logger.warning(f"⚠️ Email {message_id} has insufficient content")
                return None
            
            # Clean and process content
            cleaned_body = self._clean_email_content(body)
            
            return {
                'id': message_id,
                'subject': subject or 'No Subject',
                'sender': sender or 'Unknown Sender',
                'date': self._parse_date(date),
                'body': cleaned_body,
                'raw_body': body,
                'source': 'gmail'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get email content for {message_id}: {e}")
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> Optional[str]:
        """Extract header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        body = self._html_to_text(html_body)
                        break
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif payload['mimeType'] == 'text/html':
                if 'data' in payload['body']:
                    html_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                    body = self._html_to_text(html_body)
        
        return body
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        except:
            # Fallback: simple HTML tag removal
            return re.sub(r'<[^>]+>', '', html)
    
    def _clean_email_content(self, content: str) -> str:
        """Clean email content for summarization"""
        if not content:
            return ""
        
        # Remove common email signatures and footers
        lines = content.split('\n')
        cleaned_lines = []
        
        skip_patterns = [
            r'unsubscribe',
            r'privacy policy',
            r'terms of service',
            r'copyright',
            r'all rights reserved',
            r'this email was sent to',
            r'you received this email because',
            r'click here to',
            r'follow us on',
            r'powered by',
            r'manage your preferences',
            r'update your email preferences',
        ]
        
        for line in lines:
            line = line.strip()
            if line and not any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove URLs
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        
        # Limit content length
        if len(content) > 4000:
            content = content[:4000] + "..."
        
        return content
    
    def _parse_date(self, date_str: str) -> str:
        """Parse email date string to ISO format"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()
    
    def fetch_latest_newsletter(self) -> Optional[Dict]:
        """
        Fetch the latest newsletter-like email (compatible with existing system)
        
        Returns:
            Dictionary in the same format as other newsletter fetchers
        """
        logger.info("📧 Fetching latest newsletter-like email from Gmail...")
        
        # Fetch recent emails
        emails = self.fetch_recent_emails(max_results=5, days_back=3)
        
        if not emails:
            logger.warning("⚠️ No emails found")
            return None
        
        # Find the best email for summarization
        best_email = None
        best_score = 0
        
        for email in emails:
            score = self._score_email_relevance(email)
            if score > best_score:
                best_score = score
                best_email = email
        
        if best_email:
            logger.info(f"✅ Selected email: {best_email['subject']}")
            
            # Convert to newsletter format
            return {
                'title': best_email['subject'],
                'content': best_email['body'],
                'link': f"gmail://message/{best_email['id']}",
                'published': best_email['date'],
                'source': 'gmail',
                'sender': best_email['sender']
            }
        
        logger.warning("⚠️ No suitable email found for summarization")
        return None
    
    def _score_email_relevance(self, email: Dict) -> int:
        """Score email relevance for newsletter summarization"""
        score = 0
        
        subject = email['subject'].lower()
        sender = email['sender'].lower()
        body = email['body'].lower()
        
        # Subject scoring
        if any(keyword in subject for keyword in ['newsletter', 'digest', 'update', 'weekly', 'daily']):
            score += 10
        
        if any(keyword in subject for keyword in ['ai', 'artificial intelligence', 'machine learning', 'tech']):
            score += 8
        
        # Sender scoring
        if any(domain in sender for domain in ['openai.com', 'anthropic.com', 'deepmind.com']):
            score += 15
        
        if any(keyword in sender for keyword in ['newsletter', 'digest', 'update', 'news']):
            score += 5
        
        # Content length scoring
        if len(email['body']) > 1000:
            score += 5
        
        # Content quality scoring
        if any(keyword in body for keyword in ['artificial intelligence', 'machine learning', 'technology', 'innovation']):
            score += 3
        
        return score


class GmailNewsletterFetcher:
    """Gmail newsletter fetcher that integrates with the existing newsletter system"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize Gmail newsletter fetcher
        
        Args:
            credentials_file: Path to Gmail API credentials JSON file
        """
        self.gmail_fetcher = GmailFetcher(credentials_file)
        logger.info("📧 Gmail newsletter fetcher initialized")
    
    def fetch_latest_newsletter(self) -> Optional[Dict]:
        """
        Fetch latest newsletter content from Gmail
        
        Returns:
            Dictionary compatible with existing newsletter system
        """
        return self.gmail_fetcher.fetch_latest_newsletter()


if __name__ == "__main__":
    # Test the Gmail fetcher
    logging.basicConfig(level=logging.INFO)
    
    fetcher = GmailNewsletterFetcher()
    content = fetcher.fetch_latest_newsletter()
    
    if content:
        print("✅ Gmail test successful!")
        print(f"Title: {content['title']}")
        print(f"Content length: {len(content['content'])}")
        print(f"Source: {content['source']}")
        print(f"Sender: {content.get('sender', 'Unknown')}")
        print(f"First 200 chars: {content['content'][:200]}...")
    else:
        print("❌ Gmail test failed!")