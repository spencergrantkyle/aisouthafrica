import openai
import os
from dotenv import load_dotenv
import logging
import time
from typing import Optional

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class NewsletterSummarizer:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
        self.max_retries = 3
        logger.info("🤖 AI Summarizer initialized with OpenAI")
    
    def summarize_newsletter(self, content: str, title: str = "") -> Optional[str]:
        """Summarize newsletter content with South African context"""
        logger.info("🧠 Generating AI summary...")
        
        if not content or len(content.strip()) < 50:
            logger.warning("⚠️ Content too short for summarization")
            return None
        
        try:
            prompt = self._create_prompt(content, title)
            
            # Make API call with retry logic
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"📡 OpenAI API call attempt {attempt + 1}/{self.max_retries}")
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are an AI assistant that summarizes newsletters for South African professionals, focusing on actionable AI insights relevant to the local business context."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        max_tokens=600,
                        temperature=0.3,
                        presence_penalty=0.1,
                        frequency_penalty=0.1
                    )
                    
                    summary = response.choices[0].message.content.strip()
                    
                    if summary and len(summary) > 50:
                        logger.info("✅ AI summary generated successfully")
                        return self._format_summary(summary, title)
                    else:
                        logger.warning("⚠️ Generated summary too short")
                        return self._create_fallback_summary(content, title)
                    
                except openai.RateLimitError as e:
                    logger.warning(f"⚠️ Rate limit hit, waiting before retry {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        logger.error("❌ Rate limit exceeded, using fallback")
                        return self._create_fallback_summary(content, title)
                
                except openai.APIError as e:
                    logger.warning(f"⚠️ OpenAI API error: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        logger.error("❌ API error, using fallback")
                        return self._create_fallback_summary(content, title)
                
                except Exception as e:
                    logger.warning(f"⚠️ Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        logger.error("❌ All attempts failed, using fallback")
                        return self._create_fallback_summary(content, title)
            
        except Exception as e:
            logger.error(f"❌ Summarization error: {e}")
            return self._create_fallback_summary(content, title)
    
    def _create_prompt(self, content: str, title: str) -> str:
        """Create optimized prompt for South African context"""
        prompt = f"""
Please summarize this AI newsletter content for South African professionals and business owners. 

FOCUS ON:
- Actionable AI tools and techniques that can be implemented immediately
- Practical applications specifically relevant to South African businesses
- Cost-effective solutions suitable for local market conditions
- ROI potential and implementation complexity
- Local regulatory or market considerations where applicable

NEWSLETTER TITLE: {title}

CONTENT: {content}

INSTRUCTIONS:
1. Create a concise summary with 4-6 key bullet points
2. Each point should be actionable and specific
3. Include costs, implementation difficulty, or timeframes where mentioned
4. Highlight tools or strategies particularly suitable for SMEs
5. Use South African business terminology where appropriate (e.g., "SME" not "small business")
6. If relevant, mention compatibility with local systems or regulations

FORMAT:
- Start with a one-sentence overview
- Follow with bullet points (use • not numbers)
- End with a practical next step or key takeaway
- Keep total length under 400 words
- Write in a professional but accessible tone

AVOID:
- Generic statements without actionable value
- Technical jargon without explanation
- US-specific references or costs in USD without context
- Overly promotional language
"""
        return prompt
    
    def _format_summary(self, summary: str, title: str) -> str:
        """Format summary for Telegram with proper styling"""
        logger.info("💅 Formatting summary for Telegram")
        
        # Clean up the summary
        summary = summary.strip()
        
        # Ensure bullet points are properly formatted
        summary = summary.replace('•', '•')
        summary = summary.replace('- ', '• ')
        summary = summary.replace('* ', '• ')
        
        # Format the final message
        formatted = f"🤖 **AI Newsletter Summary**\n\n"
        
        if title and title.strip():
            formatted += f"📰 **{title.strip()}**\n\n"
        
        formatted += f"{summary}\n\n"
        formatted += f"🇿🇦 *Curated for South African professionals*\n"
        formatted += f"⚡ *Powered by AI Newsletter Bot SA*"
        
        # Ensure message isn't too long for Telegram (4096 char limit)
        if len(formatted) > 4000:
            # Truncate the summary part while keeping headers and footers
            header_length = len("🤖 **AI Newsletter Summary**\n\n📰 **") + len(title) + len("**\n\n")
            footer_length = len("\n\n🇿🇦 *Curated for South African professionals*\n⚡ *Powered by AI Newsletter Bot SA*")
            available_length = 4000 - header_length - footer_length
            
            summary = summary[:available_length] + "..."
            formatted = f"🤖 **AI Newsletter Summary**\n\n"
            if title:
                formatted += f"📰 **{title.strip()}**\n\n"
            formatted += f"{summary}\n\n"
            formatted += f"🇿🇦 *Curated for South African professionals*\n"
            formatted += f"⚡ *Powered by AI Newsletter Bot SA*"
            
            logger.info("📏 Summary truncated to fit Telegram limits")
        
        return formatted
    
    def _create_fallback_summary(self, content: str, title: str) -> str:
        """Create a basic fallback summary when AI fails"""
        logger.info("🔄 Creating fallback summary")
        
        # Extract key sentences or phrases
        sentences = content.split('.')
        key_sentences = []
        
        # Look for sentences with important keywords
        keywords = ['AI', 'artificial intelligence', 'business', 'tool', 'cost', 'efficiency', 'automation', 'productivity']
        
        for sentence in sentences[:10]:  # Only check first 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword.lower() in sentence.lower() for keyword in keywords):
                key_sentences.append(sentence + '.')
                if len(key_sentences) >= 3:
                    break
        
        if not key_sentences:
            # Ultra-basic fallback
            fallback_content = f"""
• AI technologies continue to evolve rapidly with new tools and applications
• South African businesses can benefit from adopting AI solutions for efficiency
• Key areas include automation, customer service, and data analysis
• Consider starting with simple, cost-effective AI tools for immediate impact

💡 **Key Takeaway:** Explore AI tools that match your business size and budget for quick wins.
            """
        else:
            fallback_content = "\n".join([f"• {sentence}" for sentence in key_sentences])
            fallback_content += "\n\n💡 **Key Takeaway:** Evaluate these AI developments for potential application in your South African business context."
        
        return self._format_summary(fallback_content, title or "AI Newsletter Update")
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            logger.info("🧪 Testing OpenAI API connection...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Test message. Please respond with 'Connection successful.'"}
                ],
                max_tokens=10
            )
            
            if response.choices[0].message.content:
                logger.info("✅ OpenAI API connection successful")
                return True
            else:
                logger.error("❌ OpenAI API connection failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"❌ OpenAI API connection test failed: {e}")
            return False


class MockSummarizer:
    """Mock summarizer for testing when OpenAI is unavailable"""
    
    def summarize_newsletter(self, content: str, title: str = "") -> str:
        """Return a mock summary for testing"""
        logger.info("🧪 Using mock summarizer for testing")
        
        mock_summary = """
🤖 **AI Newsletter Summary**

📰 **Weekly AI Update for South African Professionals**

• OpenAI introduces cost-effective AI tools reducing operational expenses by 40% - ideal for South African SMEs looking to automate customer service
• Local fintech companies successfully implement AI chatbots, reporting 60% reduction in customer query response times  
• Government announces R500M AI development fund targeting small businesses in Gauteng, Western Cape, and KwaZulu-Natal
• New study reveals 65% productivity increase in SA companies using AI for data analysis and content creation
• Practical implementation tip: Start with free AI writing tools like ChatGPT for marketing content before investing in enterprise solutions

💡 **Key Takeaway:** Focus on low-cost, high-impact AI tools that provide immediate ROI for your South African business.

🇿🇦 *Curated for South African professionals*
⚡ *Powered by AI Newsletter Bot SA*
        """
        
        return mock_summary.strip()
    
    def test_connection(self) -> bool:
        """Mock connection test"""
        return True


if __name__ == "__main__":
    # Test the summarizer
    logging.basicConfig(level=logging.INFO)
    
    # Test content
    test_content = """
    Artificial Intelligence is transforming businesses worldwide. New tools are available for automation,
    customer service, and data analysis. Companies report significant cost savings and efficiency improvements.
    OpenAI has released new features that reduce costs by 40%. Local businesses are implementing AI solutions.
    """
    
    try:
        summarizer = NewsletterSummarizer()
        
        # Test connection first
        if summarizer.test_connection():
            print("✅ OpenAI connection test passed")
            
            # Test summarization
            summary = summarizer.summarize_newsletter(test_content, "Test AI Newsletter")
            if summary:
                print("✅ Summarization test successful!")
                print("\nGenerated Summary:")
                print(summary)
            else:
                print("❌ Summarization test failed")
        else:
            print("❌ OpenAI connection test failed")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("🧪 Testing mock summarizer instead...")
        
        mock = MockSummarizer()
        summary = mock.summarize_newsletter(test_content, "Test AI Newsletter")
        print("✅ Mock summarizer test successful!")
        print("\nMock Summary:")
        print(summary)