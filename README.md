# Startup Profiler Agent

An intelligent agent that gathers and stores contextual information about any company/startup. The agent uses Google Gemini for analysis, SerpAPI for fetching recent news, web scraping for extracting website content, and Supabase for data persistence.

## Features

- **Automatic Company Profiling**: Extract comprehensive information from company websites
- **News Integration**: Fetch and summarize latest news about companies
- **AI-Powered Analysis**: Use Google Gemini to analyze and infer insights
- **Data Persistence**: Store structured data in Supabase
- **Duplicate Detection**: Skip re-processing of already profiled companies
- **Docker Support**: Fully containerized application

## Tech Stack

- **Language**: Python 3.10+
- **LLM**: Google Gemini (via REST API)
- **Database**: Supabase (PostgreSQL)
- **Web Search**: SerpAPI
- **Web Scraping**: BeautifulSoup + Requests
- **Framework**: Langchain
- **Containerization**: Docker

## Prerequisites

1. Python 3.10 or higher
2. Docker and Docker Compose (for containerized deployment)
3. API Keys:
   - Google Gemini API key
   - Supabase project URL and key
   - SerpAPI key

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd startup-profiler-agent
```

### 2. Configure Environment Variables

Copy the `.env.template` file to `.env` and fill in your API keys:

```bash
cp .env.template .env
```

Edit `.env` with your actual values:
```
GEMINI_API_KEY=your_actual_gemini_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SERPAPI_KEY=your_serpapi_key
```

### 3. Set Up Supabase Database

Create a new table in your Supabase project using the following SQL:

```sql
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
```

### 4. Install Dependencies (Local Development)

```bash
pip install -r requirements.txt
```

### 5. Run with Docker (Recommended)

```bash
# Build and run the application
docker-compose up

# Run in detached mode
docker-compose up -d
```

## Usage

### Command Line Interface

Profile a company by providing its website URL:

```bash
python main.py https://notion.so
```

### Interactive Mode

Run the agent in interactive chat mode:

```bash
python main.py https://example.com --interactive
```

### Docker Usage

```bash
# Profile a specific company
docker-compose run --rm startup-profiler python main.py https://notion.so

# Interactive mode
docker-compose run --rm startup-profiler python main.py https://example.com --interactive
```

## Agent Workflow

1. **Input Validation**: Check if the company profile already exists in the database
2. **Web Scraping**: Extract page title, meta description, H1/H2 tags, outbound links, and content
3. **News Fetching**: Retrieve top 5 latest news articles using SerpAPI
4. **AI Analysis**: Use Gemini to analyze:
   - Company summary (100 words)
   - Industry category
   - Target audience
   - Key problems solved
   - Potential competitors
   - News summary
5. **Data Storage**: Save the complete profile to Supabase

## Project Structure

```
startup-profiler-agent/
├── src/
│   ├── agents/           # Langchain agent implementation
│   ├── tools/            # Web scraper, news fetcher, Gemini analyzer
│   ├── models/           # Database models and managers
│   └── utils/            # Logging and utility functions
├── tests/                # Test files
├── config/               # Configuration files
├── logs/                 # Application logs
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── .env.template         # Environment variables template
└── README.md             # This file
```

## API Response Format

Successful profile creation:
```json
{
    "status": "success",
    "message": "Company profile created successfully",
    "data": {
        "website_url": "https://notion.so",
        "company_name": "Notion",
        "company_summary": "...",
        "industry_category": "Productivity Software",
        "target_audience": "...",
        "key_problems_solved": ["...", "..."],
        "potential_competitors": ["...", "..."],
        "news_summary": "...",
        ...
    }
}
```

Profile already exists:
```json
{
    "status": "exists",
    "message": "Company profile already exists in database",
    "data": { ... }
}
```

## Logging

Logs are stored in the `logs/` directory with rotation enabled:
- Default log level: INFO
- Log file: `logs/app.log`
- Maximum file size: 10MB
- Backup count: 5

## Error Handling

The agent includes comprehensive error handling for:
- Network timeouts
- Invalid URLs
- API rate limits
- Database connection issues
- Parsing errors

## Optional: Streamlit UI

A Streamlit UI is available for a web interface:

```bash
# Run with Docker Compose
docker-compose --profile ui up

# Or run locally
streamlit run app.py
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- Follow PEP 8 style guidelines
- Use type hints for better code documentation
- Add logging for debugging and monitoring

## Screenshots

The application includes a modern Streamlit web interface:

![Application Interface](images/image%201.png)
*Main interface with company URL input*

![Analysis Results](images/image%202.png)
*Company analysis results with AI-generated insights*

![Detailed View](images/image%203.png)
*Detailed company profile with competitors and news*

![Database Integration](images/image%204.png)
*Real-time data storage and retrieval*

![Complete Analysis](images/image%205.png)
*Full company profiling workflow*

## Troubleshooting

1. **API Key Issues**: Ensure all API keys are correctly set in the `.env` file
2. **Database Connection**: Verify Supabase URL and key are correct
3. **Docker Issues**: Ensure Docker daemon is running
4. **Rate Limits**: Be aware of API rate limits for SerpAPI and Gemini

## License

This project is licensed under the MIT License.