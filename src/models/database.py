import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
from supabase import create_client, Client
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class SupabaseManager:
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be provided")
        
        self.client: Client = create_client(self.url, self.key)
        self.table_name = "company_profiles"
    
    def check_company_exists(self, website_url: str) -> bool:
        """
        Check if a company profile already exists for the given website.
        
        Args:
            website_url: The website URL to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            # Normalize URL for comparison
            normalized_url = self._normalize_url(website_url)
            
            result = self.client.table(self.table_name).select("id").eq(
                "website_url", normalized_url
            ).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking company existence: {str(e)}")
            return False
    
    def save_company_profile(self, profile_data: Dict[str, any]) -> Dict[str, any]:
        """
        Save company profile to Supabase.
        
        Args:
            profile_data: Dictionary containing all company information
            
        Returns:
            The saved record
        """
        try:
            # Prepare data for insertion
            record = {
                "website_url": self._normalize_url(profile_data['website_url']),
                "company_name": profile_data.get('company_name', ''),
                "page_title": profile_data.get('page_title', ''),
                "meta_description": profile_data.get('meta_description', ''),
                "company_summary": profile_data.get('company_summary', ''),
                "industry_category": profile_data.get('industry_category', ''),
                "target_audience": profile_data.get('target_audience', ''),
                "key_problems_solved": profile_data.get('key_problems_solved', []),
                "potential_competitors": profile_data.get('potential_competitors', []),
                "news_summary": profile_data.get('news_summary', ''),
                "h1_tags": profile_data.get('h1_tags', []),
                "h2_tags": profile_data.get('h2_tags', []),
                "outbound_links": profile_data.get('outbound_links', []),
                "latest_news": profile_data.get('latest_news', []),
                "scraped_content": profile_data.get('scraped_content', ''),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table(self.table_name).insert(record).execute()
            
            logger.info(f"Successfully saved company profile for {record['website_url']}")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error saving company profile: {str(e)}")
            raise
    
    def get_company_profile(self, website_url: str) -> Optional[Dict[str, any]]:
        """
        Retrieve company profile by website URL.
        
        Args:
            website_url: The website URL
            
        Returns:
            Company profile data or None
        """
        try:
            normalized_url = self._normalize_url(website_url)
            
            result = self.client.table(self.table_name).select("*").eq(
                "website_url", normalized_url
            ).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error retrieving company profile: {str(e)}")
            return None
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent storage and comparison."""
        parsed = urlparse(url.lower())
        # Remove www. prefix if present
        netloc = parsed.netloc.replace('www.', '')
        # Ensure https scheme
        scheme = 'https' if parsed.scheme in ['http', 'https'] else parsed.scheme
        return f"{scheme}://{netloc}{parsed.path}".rstrip('/')
    
    def create_table_if_not_exists(self):
        """
        Create the company_profiles table if it doesn't exist.
        This method returns the SQL that should be run in Supabase.
        """
        return """
        CREATE TABLE IF NOT EXISTS company_profiles (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            website_url TEXT UNIQUE NOT NULL,
            company_name TEXT,
            page_title TEXT,
            meta_description TEXT,
            company_summary TEXT,
            industry_category TEXT,
            target_audience TEXT,
            key_problems_solved TEXT[],
            potential_competitors TEXT[],
            news_summary TEXT,
            h1_tags TEXT[],
            h2_tags TEXT[],
            outbound_links TEXT[],
            latest_news JSONB[],
            scraped_content TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_website_url ON company_profiles(website_url);
        """