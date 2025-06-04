import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        self.timeout = timeout
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_website(self, url: str) -> Dict[str, any]:
        """
        Scrape a website and extract key information.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped data
        """
        try:
            logger.info(f"Scraping website: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract page title
            title = soup.find('title')
            title_text = title.text.strip() if title else ''
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content', '') if meta_desc else ''
            
            # Extract H1 and H2 tags
            h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]
            
            # Extract outbound links
            outbound_links = self._extract_outbound_links(soup, url)
            
            # Extract main content (simplified version)
            content = self._extract_content(soup)
            
            return {
                'url': url,
                'title': title_text,
                'meta_description': meta_description,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'outbound_links': outbound_links[:20],  # Limit to 20 links
                'content': content[:5000],  # Limit content length
                'scraped_at': time.time()
            }
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            raise
    
    def _extract_outbound_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract outbound links from the page."""
        outbound_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Check if it's an outbound link
            if urlparse(absolute_url).netloc != base_domain:
                outbound_links.append(absolute_url)
        
        return list(set(outbound_links))  # Remove duplicates
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main textual content from the page."""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text