import os
from typing import List, Dict, Optional
import logging
from serpapi import GoogleSearch

logger = logging.getLogger(__name__)


class NewsFetcher:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        if not self.api_key:
            raise ValueError("SerpAPI key not provided")
    
    def fetch_company_news(self, company_name: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Fetch latest news about a company using SerpAPI.
        
        Args:
            company_name: Name of the company to search for
            num_results: Number of results to return (default: 5)
            
        Returns:
            List of news articles with title, snippet, source, and date
        """
        try:
            logger.info(f"Fetching news for: {company_name}")
            
            # Search query
            search_query = f"{company_name} latest news"
            
            params = {
                "q": search_query,
                "api_key": self.api_key,
                "num": num_results,
                "tbm": "nws",  # News search
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            news_articles = []
            
            if "news_results" in results:
                for article in results["news_results"][:num_results]:
                    news_item = {
                        "title": article.get("title", ""),
                        "snippet": article.get("snippet", ""),
                        "source": article.get("link", ""),
                        "date": article.get("date", ""),
                        "source_name": article.get("source", {}).get("name", "") if isinstance(article.get("source"), dict) else article.get("source", "")
                    }
                    news_articles.append(news_item)
            
            # If no news results, try organic results
            elif "organic_results" in results:
                for result in results["organic_results"][:num_results]:
                    news_item = {
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("link", ""),
                        "date": result.get("date", ""),
                        "source_name": result.get("displayed_link", "")
                    }
                    news_articles.append(news_item)
            
            logger.info(f"Found {len(news_articles)} news articles")
            return news_articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {company_name}: {str(e)}")
            return []
    
    def fetch_company_info(self, company_name: str) -> Dict[str, any]:
        """
        Fetch general web results about the company.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dictionary with search results
        """
        try:
            logger.info(f"Fetching general info for: {company_name}")
            
            params = {
                "q": company_name,
                "api_key": self.api_key,
                "num": 10,
                "hl": "en",
                "gl": "us"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            return {
                "organic_results": results.get("organic_results", []),
                "knowledge_graph": results.get("knowledge_graph", {}),
                "related_searches": results.get("related_searches", [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching info for {company_name}: {str(e)}")
            return {}