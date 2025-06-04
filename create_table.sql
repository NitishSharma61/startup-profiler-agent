-- Create company_profiles table
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

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_website_url ON company_profiles(website_url);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE company_profiles ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow all operations (for development)
CREATE POLICY "Allow all operations" ON company_profiles
    FOR ALL USING (true) WITH CHECK (true);