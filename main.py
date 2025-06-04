import os
import sys
import argparse
import logging
from dotenv import load_dotenv

from src.agents.startup_profiler_agent import StartupProfilerAgent
from src.utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Startup Profiler Agent")
    parser.add_argument(
        "website_url",
        help="The website URL of the company to profile"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive chat mode"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize agent
        agent = StartupProfilerAgent()
        
        if args.interactive:
            # Interactive mode
            print("Startup Profiler Agent - Interactive Mode")
            print("Type 'exit' or 'quit' to end the session")
            print("-" * 50)
            
            while True:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                response = agent.chat(user_input)
                print(f"\nAgent: {response}")
        else:
            # Profile the company
            print(f"Profiling company: {args.website_url}")
            result = agent.profile_company(args.website_url)
            
            if result['status'] == 'success':
                print("\nCompany profile created successfully!")
                print(f"\nCompany Name: {result['data'].get('company_name', 'N/A')}")
                print(f"Industry: {result['data'].get('industry_category', 'N/A')}")
                print(f"\nSummary: {result['data'].get('company_summary', 'N/A')}")
                print(f"\nTarget Audience: {result['data'].get('target_audience', 'N/A')}")
                
                problems = result['data'].get('key_problems_solved', [])
                if problems:
                    print("\nKey Problems Solved:")
                    for problem in problems:
                        print(f"  - {problem}")
                
                competitors = result['data'].get('potential_competitors', [])
                if competitors:
                    print("\nPotential Competitors:")
                    for competitor in competitors:
                        print(f"  - {competitor}")
                
                print(f"\nLatest News Summary: {result['data'].get('news_summary', 'N/A')}")
                
            elif result['status'] == 'exists':
                print("\nCompany profile already exists in the database.")
                print("Skipping re-processing.")
            else:
                print(f"\nError: {result['message']}")
                
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\nFatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()