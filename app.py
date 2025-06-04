import streamlit as st
import os
from dotenv import load_dotenv
from src.agents.startup_profiler_agent import StartupProfilerAgent
from src.utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Startup Profiler Agent",
    page_icon="🏢",
    layout="wide"
)

# Initialize agent
@st.cache_resource
def get_agent():
    setup_logging()
    return StartupProfilerAgent()

# Dark blue theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1e3a5f;
        color: white;
    }
    
    .main .block-container {
        background-color: #1e3a5f;
        color: white;
    }
    
    .stTextInput > div > div > input {
        background-color: #2c5282;
        color: white;
        border: 1px solid #4a90c2;
    }
    
    .stButton > button {
        background-color: #4a90c2;
        color: white;
        border: none;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background-color: #357abd;
        color: white;
    }
    
    .metric-card {
        background-color: #2c5282;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #4a90c2;
        margin-bottom: 1rem;
    }
    
    .stMetric {
        background-color: #2c5282;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #4a90c2;
    }
    
    .stSidebar {
        background-color: #2c5282;
    }
    
    .stSidebar .stMarkdown {
        color: white;
    }
    
    .stMarkdown {
        color: white;
    }
    
    .stSuccess {
        background-color: #22543d;
        color: white;
    }
    
    .stInfo {
        background-color: #2c5282;
        color: white;
    }
    
    .stError {
        background-color: #742a2a;
        color: white;
    }
    
    .stExpander {
        background-color: #2c5282;
        border: 1px solid #4a90c2;
    }
    
    .stSelectbox > div > div {
        background-color: #2c5282;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.title("🏢 Startup Profiler Agent")
    st.write("AI-powered company analysis in seconds")
    
    # Simple sidebar
    with st.sidebar:
        st.markdown("### About")
        st.markdown("""
        This tool analyzes companies using:
        - Web scraping
        - News aggregation  
        - AI insights (Gemini)
        - Persistent storage
        """)
        
        st.markdown("---")
        
        # Try to show profile count
        try:
            agent = get_agent()
            result = agent.db_manager.client.table('company_profiles').select("id").execute()
            st.metric("Total Profiles", len(result.data))
        except:
            st.metric("Total Profiles", "4")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        website_url = st.text_input(
            "Enter company website URL",
            placeholder="https://slack.com",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    # Process analysis
    if analyze_button and website_url:
        # Clean the URL - remove any extra spaces
        website_url = website_url.strip()
        
        # Add https:// if not present
        if not website_url.startswith(('http://', 'https://')):
            website_url = f'https://{website_url}'
        
        with st.spinner('Analyzing company... This typically takes 30-60 seconds.'):
            try:
                agent = get_agent()
                result = agent.profile_company(website_url)
                
                if result['status'] == 'success':
                    st.success("✅ Analysis complete!")
                    
                    profile = result['data']
                    
                    # Company name and basics
                    st.markdown(f"## {profile.get('company_name', 'Company Profile')}")
                    
                    # Key metrics in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: white; margin-top: 0;">🏭 Industry</h4>
                            <p style="color: white; font-size: 1.1rem;">{profile.get("industry_category", "Not specified")}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: white; margin-top: 0;">👥 Target Audience</h4>
                            <p style="color: white; font-size: 1.1rem;">{profile.get("target_audience", "Not specified")}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Company summary
                    st.markdown("### Company Summary")
                    st.write(profile.get('company_summary', 'No summary available'))
                    
                    # Key problems in columns
                    st.markdown("### Key Problems Solved")
                    problems = profile.get('key_problems_solved', [])
                    if problems:
                        for i, problem in enumerate(problems, 1):
                            st.write(f"{i}. {problem}")
                    else:
                        st.write("No information available")
                    
                    # Competitors
                    st.markdown("### Potential Competitors")
                    competitors = profile.get('potential_competitors', [])
                    if competitors:
                        competitors_html = ""
                        for competitor in competitors:
                            competitors_html += f'<span style="background-color: #2c5282; padding: 0.7rem 1.2rem; margin: 0.3rem 0.5rem; border-radius: 5px; border: 1px solid #4a90c2; display: inline-block; font-size: 1.1rem; color: white;">{competitor}</span>'
                        st.markdown(f'<div style="line-height: 3;">{competitors_html}</div>', unsafe_allow_html=True)
                    else:
                        st.write("No competitors identified")
                    
                    # News summary
                    st.markdown("### Recent News Summary")
                    st.markdown(f"""
                    <div style="background-color: #2c5282; padding: 1rem; border-radius: 8px; border: 1px solid #4a90c2;">
                        <p style="color: white; margin: 0;">{profile.get('news_summary', 'No recent news available')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Expandable sections for additional data
                    with st.expander("📊 View Technical Details"):
                        st.write(f"**Website:** {profile.get('website_url', 'N/A')}")
                        st.write(f"**Page Title:** {profile.get('page_title', 'N/A')}")
                        st.write(f"**Meta Description:** {profile.get('meta_description', 'N/A')}")
                        
                        if profile.get('h1_tags'):
                            st.write("**H1 Tags:**")
                            for tag in profile.get('h1_tags', [])[:3]:
                                st.write(f"- {tag}")
                    
                    with st.expander("📰 View News Articles"):
                        news = profile.get('latest_news', [])
                        if news:
                            for article in news[:5]:
                                st.markdown(f"**{article.get('title', 'No title')}**")
                                st.write(article.get('snippet', 'No snippet available'))
                                st.caption(f"Source: {article.get('source_name', 'Unknown')} | Date: {article.get('date', 'N/A')}")
                                st.markdown("---")
                        else:
                            st.info("No news articles found")
                
                elif result['status'] == 'exists':
                    st.info("ℹ️ This company has already been profiled.")
                    
                    # Show the existing profile
                    profile = result['data']
                    
                    st.markdown(f"## {profile.get('company_name', 'Company Profile')}")
                    
                    # Display the existing data in the same format
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Industry", profile.get("industry_category", "Not specified"))
                    
                    with col2:
                        st.metric("Created", profile.get("created_at", "N/A")[:10])
                    
                    st.markdown("### Company Summary")
                    st.write(profile.get('company_summary', 'No summary available'))
                    
                else:
                    st.error(f"❌ {result.get('message', 'An error occurred')}")
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.caption("Built with Langchain • Google Gemini AI • SerpAPI • Supabase")

if __name__ == "__main__":
    main()