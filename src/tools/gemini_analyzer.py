import os
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_company(self, 
                       scraped_data: Dict[str, any], 
                       news_data: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Analyze company information using Gemini.
        
        Args:
            scraped_data: Data from web scraping
            news_data: Latest news articles
            
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info("Analyzing company data with Gemini")
            
            # Prepare the prompt
            prompt = self._create_analysis_prompt(scraped_data, news_data)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            analysis = self._parse_response(response.text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {str(e)}")
            raise
    
    def _create_analysis_prompt(self, scraped_data: Dict, news_data: List[Dict]) -> str:
        """Create a comprehensive prompt for Gemini analysis."""
        
        news_summary = "\n".join([
            f"- {article['title']} ({article['source_name']})"
            for article in news_data[:5]
        ])
        
        prompt = f"""
        Analyze the following company information and provide structured insights.
        
        Website URL: {scraped_data.get('url', 'N/A')}
        Page Title: {scraped_data.get('title', 'N/A')}
        Meta Description: {scraped_data.get('meta_description', 'N/A')}
        
        Key Headlines (H1):
        {chr(10).join(scraped_data.get('h1_tags', [])[:5])}
        
        Subheadings (H2):
        {chr(10).join(scraped_data.get('h2_tags', [])[:10])}
        
        Website Content (excerpt):
        {scraped_data.get('content', '')[:2000]}
        
        Recent News:
        {news_summary}
        
        Based on this information, provide the following analysis in JSON format:
        
        {{
            "company_summary": "A 100-word summary of what the company does",
            "industry_category": "The primary industry category",
            "target_audience": "Description of the target audience",
            "key_problems_solved": ["Problem 1", "Problem 2", "Problem 3"],
            "potential_competitors": ["Competitor 1", "Competitor 2", "Competitor 3"],
            "news_summary": "A short paragraph summarizing the latest news and developments"
        }}
        
        Ensure your response is valid JSON format only.
        """
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """Parse Gemini's response into structured data."""
        try:
            # Try to extract JSON from the response
            # Sometimes Gemini might include extra text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: Try to parse the entire response
                return json.loads(response_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            # Return a default structure
            return {
                "company_summary": "Unable to generate summary",
                "industry_category": "Unknown",
                "target_audience": "Unknown",
                "key_problems_solved": [],
                "potential_competitors": [],
                "news_summary": "Unable to summarize news"
            }