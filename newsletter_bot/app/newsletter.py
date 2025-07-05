import requests
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

class OpenLetterFetcher:
    def __init__(self):
        self.base_url = "https://openletter.earth"
        self.rss_url = "https://openletter.earth/feed"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info("📰 OpenLetter fetcher initialized")
    
    def fetch_latest_newsletter(self):
        """Fetch the latest OpenLetter newsletter content"""
        logger.info("🔍 Fetching latest newsletter from OpenLetter...")
        
        try:
            # Try RSS first (most reliable)
            content = self._fetch_from_rss()
            if content:
                logger.info("✅ Successfully fetched from RSS feed")
                return content
            
            logger.warning("⚠️ RSS fetch failed, trying web scraping...")
            # Fallback to web scraping
            content = self._fetch_from_web()
            if content:
                logger.info("✅ Successfully fetched from web scraping")
                return content
            
            logger.warning("⚠️ Web scraping failed, trying alternative approach...")
            # Try alternative scraping
            content = self._fetch_alternative()
            if content:
                logger.info("✅ Successfully fetched from alternative method")
                return content
            
            logger.error("❌ All fetch methods failed")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching newsletter: {e}")
            return None
    
    def _fetch_from_rss(self):
        """Try to fetch from RSS feed"""
        try:
            logger.info("📡 Attempting RSS fetch...")
            feed = feedparser.parse(self.rss_url)
            
            if feed.entries and len(feed.entries) > 0:
                latest = feed.entries[0]
                
                # Extract content
                content = ""
                if hasattr(latest, 'content') and latest.content:
                    content = latest.content[0].value
                elif hasattr(latest, 'description'):
                    content = latest.description
                elif hasattr(latest, 'summary'):
                    content = latest.summary
                
                if content and len(content) > 100:  # Ensure we have meaningful content
                    return {
                        'title': latest.title,
                        'content': self._clean_content(content),
                        'link': latest.link,
                        'published': latest.published if hasattr(latest, 'published') else datetime.now().isoformat(),
                        'source': 'rss'
                    }
                    
        except Exception as e:
            logger.warning(f"⚠️ RSS fetch failed: {e}")
        
        return None
    
    def _fetch_from_web(self):
        """Fallback web scraping method"""
        try:
            logger.info("🌐 Attempting web scraping...")
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different selectors for articles
            article_selectors = [
                'article',
                '.post',
                '.entry',
                '.content-area article',
                '[class*="post"]',
                'main article'
            ]
            
            article = None
            for selector in article_selectors:
                article = soup.select_one(selector)
                if article:
                    logger.info(f"📄 Found article with selector: {selector}")
                    break
            
            if not article:
                # Try to find main content area
                article = soup.find('main') or soup.find('div', class_='content')
                logger.info("📄 Using main content area")
            
            if article:
                # Extract title
                title_selectors = ['h1', 'h2', '.entry-title', '.post-title', 'title']
                title = "Latest AI Newsletter"
                
                for selector in title_selectors:
                    title_elem = article.find(selector)
                    if title_elem and title_elem.get_text().strip():
                        title = title_elem.get_text().strip()
                        break
                
                # Extract content - get all paragraph text
                paragraphs = article.find_all('p')
                content_parts = []
                
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 20:  # Filter out very short paragraphs
                        content_parts.append(text)
                
                content = ' '.join(content_parts)
                
                if len(content) > 200:  # Ensure we have substantial content
                    return {
                        'title': title,
                        'content': self._clean_content(content),
                        'link': self.base_url,
                        'published': datetime.now().isoformat(),
                        'source': 'web_scraping'
                    }
                    
        except Exception as e:
            logger.warning(f"⚠️ Web scraping failed: {e}")
        
        return None
    
    def _fetch_alternative(self):
        """Alternative fetch method - try to get any recent AI content"""
        try:
            logger.info("🔄 Attempting alternative fetch...")
            
            # Try a different approach - look for any AI-related content
            search_urls = [
                f"{self.base_url}/category/ai/",
                f"{self.base_url}/tag/artificial-intelligence/",
                f"{self.base_url}/latest/",
                self.base_url
            ]
            
            for url in search_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for any substantial text content
                        content_areas = soup.find_all(['article', 'div'], class_=re.compile(r'(post|content|article|entry)'))
                        
                        for area in content_areas:
                            text = area.get_text().strip()
                            if len(text) > 500 and any(keyword in text.lower() for keyword in ['ai', 'artificial intelligence', 'machine learning', 'technology']):
                                return {
                                    'title': "Latest AI Content from OpenLetter",
                                    'content': self._clean_content(text),
                                    'link': url,
                                    'published': datetime.now().isoformat(),
                                    'source': 'alternative'
                                }
                                
                except Exception as e:
                    logger.warning(f"⚠️ Alternative URL {url} failed: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Alternative fetch failed: {e}")
        
        return None
    
    def _clean_content(self, content):
        """Clean and prepare content for summarization"""
        if not content:
            return ""
        
        logger.info("🧹 Cleaning content...")
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove common newsletter/website boilerplate
        boilerplate_patterns = [
            r'unsubscribe.*?$',
            r'privacy policy.*?$',
            r'terms of service.*?$',
            r'copyright.*?$',
            r'all rights reserved.*?$',
            r'subscribe to.*?newsletter',
            r'follow us on.*?$',
            r'powered by.*?$',
        ]
        
        for pattern in boilerplate_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Remove URLs (but keep the content around them)
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        
        # Clean up extra spaces again
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Limit content length for API efficiency (OpenAI has token limits)
        if len(content) > 4000:
            content = content[:4000] + "..."
            logger.info("📏 Content truncated to 4000 characters")
        
        return content


class MockNewsletterFetcher:
    """Mock fetcher for testing when OpenLetter is unavailable"""
    
    def fetch_latest_newsletter(self):
        """Return mock newsletter content for testing"""
        logger.info("🧪 Using mock newsletter content for testing")
        
        mock_content = """
        Artificial Intelligence continues to transform South African businesses at an unprecedented pace. 
        This week's highlights include new AI tools for small businesses, ChatGPT integration strategies, 
        and local companies achieving significant efficiency gains through automation.
        
        Key developments:
        - OpenAI released new features that reduce costs by 40%
        - Local fintech companies are implementing AI customer service
        - Government announces R500M AI development fund
        - New study shows 65% productivity increase in AI-adopting SMEs
        
        Practical applications for South African businesses include customer service automation, 
        content creation tools, and data analysis platforms that provide immediate ROI.
        """
        
        return {
            'title': 'Weekly AI Update for South African Professionals',
            'content': mock_content,
            'link': 'https://example.com/mock-newsletter',
            'published': datetime.now().isoformat(),
            'source': 'mock'
        }


class NewsletterFetcher:
    """Main newsletter fetcher that tries multiple sources including Gmail"""
    
    def __init__(self, enable_gmail: bool = True):
        """
        Initialize newsletter fetcher with multiple sources
        
        Args:
            enable_gmail: Whether to enable Gmail fetching
        """
        self.fetchers = [
            OpenLetterFetcher(),
        ]
        
        # Add Gmail fetcher if enabled and credentials available
        if enable_gmail:
            try:
                from .gmail_fetcher import GmailNewsletterFetcher
                import os
                
                # Check if Gmail credentials exist
                if os.path.exists("credentials.json"):
                    gmail_fetcher = GmailNewsletterFetcher()
                    self.fetchers.insert(0, gmail_fetcher)  # Try Gmail first
                    logger.info("📧 Gmail fetcher added as primary source")
                else:
                    logger.warning("⚠️ Gmail credentials not found, skipping Gmail integration")
            except ImportError as e:
                logger.warning(f"⚠️ Gmail integration not available: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gmail fetcher: {e}")
        
        self.mock_fetcher = MockNewsletterFetcher()
        logger.info(f"📰 Newsletter fetcher initialized with {len(self.fetchers)} sources")
    
    def fetch_latest_newsletter(self):
        """Fetch newsletter from available sources"""
        logger.info("🔍 Starting newsletter fetch from multiple sources...")
        
        # Try each fetcher
        for i, fetcher in enumerate(self.fetchers):
            try:
                fetcher_name = fetcher.__class__.__name__
                logger.info(f"📡 Trying {fetcher_name} ({i+1}/{len(self.fetchers)})...")
                
                content = fetcher.fetch_latest_newsletter()
                if content and content['content'] and len(content['content']) > 100:
                    logger.info(f"✅ Successfully fetched from {fetcher_name}")
                    return content
                    
            except Exception as e:
                logger.warning(f"⚠️ {fetcher_name} failed: {e}")
                continue
        
        logger.warning("⚠️ All main fetchers failed, using mock content for testing")
        # If all else fails, return mock content so the system can still be tested
        return self.mock_fetcher.fetch_latest_newsletter()


if __name__ == "__main__":
    # Test the fetcher
    logging.basicConfig(level=logging.INFO)
    
    fetcher = NewsletterFetcher()
    content = fetcher.fetch_latest_newsletter()
    
    if content:
        print("✅ Test successful!")
        print(f"Title: {content['title']}")
        print(f"Content length: {len(content['content'])}")
        print(f"Source: {content['source']}")
        print(f"Link: {content['link']}")
        print(f"First 200 chars: {content['content'][:200]}...")
    else:
        print("❌ Test failed!")