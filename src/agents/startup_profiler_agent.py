import logging
from typing import Dict, Optional
from urllib.parse import urlparse
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools.web_scraper import WebScraper
from src.tools.news_fetcher import NewsFetcher
from src.tools.gemini_analyzer import GeminiAnalyzer
from src.models.database import SupabaseManager
from src.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


class StartupProfilerAgent:
    def __init__(self):
        setup_logging()
        
        # Initialize tools
        self.web_scraper = WebScraper()
        self.news_fetcher = NewsFetcher()
        self.gemini_analyzer = GeminiAnalyzer()
        self.db_manager = SupabaseManager()
        
        # Initialize Langchain components
        import os
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3,
            google_api_key=os.getenv('GEMINI_API_KEY')
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Define tools for the agent
        self.tools = [
            Tool(
                name="WebScraper",
                func=self._scrape_website,
                description="Scrapes a website to extract title, meta description, headings, links, and content"
            ),
            Tool(
                name="NewsFetcher",
                func=self._fetch_news,
                description="Fetches latest news articles about a company"
            ),
            Tool(
                name="DatabaseChecker",
                func=self._check_database,
                description="Checks if company profile already exists in database"
            ),
            Tool(
                name="ProfileSaver",
                func=self._save_profile,
                description="Saves company profile to database"
            )
        ]
        
        # Initialize agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def profile_company(self, website_url: str) -> Dict[str, any]:
        """
        Main method to profile a company based on its website URL.
        
        Args:
            website_url: The company's website URL
            
        Returns:
            Dictionary containing the company profile
        """
        try:
            logger.info(f"Starting profiling for: {website_url}")
            
            # Extract company name from URL
            company_name = self._extract_company_name(website_url)
            
            # Check if profile already exists
            if self.db_manager.check_company_exists(website_url):
                logger.info(f"Company profile already exists for {website_url}")
                return {
                    "status": "exists",
                    "message": "Company profile already exists in database",
                    "data": self.db_manager.get_company_profile(website_url)
                }
            
            # Scrape website
            logger.info("Scraping website...")
            scraped_data = self.web_scraper.scrape_website(website_url)
            
            # Fetch news
            logger.info("Fetching latest news...")
            news_data = self.news_fetcher.fetch_company_news(
                company_name or scraped_data.get('title', '')
            )
            
            # Analyze with Gemini
            logger.info("Analyzing with Gemini...")
            analysis = self.gemini_analyzer.analyze_company(scraped_data, news_data)
            
            # Prepare complete profile
            profile_data = {
                "website_url": website_url,
                "company_name": company_name or scraped_data.get('title', ''),
                "page_title": scraped_data.get('title', ''),
                "meta_description": scraped_data.get('meta_description', ''),
                "h1_tags": scraped_data.get('h1_tags', []),
                "h2_tags": scraped_data.get('h2_tags', []),
                "outbound_links": scraped_data.get('outbound_links', []),
                "scraped_content": scraped_data.get('content', ''),
                "latest_news": news_data,
                **analysis
            }
            
            # Save to database
            logger.info("Saving to database...")
            saved_profile = self.db_manager.save_company_profile(profile_data)
            
            return {
                "status": "success",
                "message": "Company profile created successfully",
                "data": saved_profile
            }
            
        except Exception as e:
            logger.error(f"Error profiling company: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }
    
    def _extract_company_name(self, url: str) -> str:
        """Extract company name from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        # Extract the main part of the domain
        parts = domain.split('.')
        if len(parts) > 1:
            return parts[0].capitalize()
        return domain.capitalize()
    
    def _scrape_website(self, url: str) -> Dict:
        """Tool function for website scraping."""
        return self.web_scraper.scrape_website(url)
    
    def _fetch_news(self, company_name: str) -> list:
        """Tool function for news fetching."""
        return self.news_fetcher.fetch_company_news(company_name)
    
    def _check_database(self, url: str) -> bool:
        """Tool function for database checking."""
        return self.db_manager.check_company_exists(url)
    
    def _save_profile(self, profile_data: Dict) -> Dict:
        """Tool function for saving profile."""
        return self.db_manager.save_company_profile(profile_data)
    
    def chat(self, message: str) -> str:
        """
        Interactive chat method for the agent.
        
        Args:
            message: User's message
            
        Returns:
            Agent's response
        """
        try:
            response = self.agent.run(message)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"I encountered an error: {str(e)}"