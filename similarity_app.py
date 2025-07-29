import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TalentDNA - Professional Similarity Search",
    page_icon="🧬",
    layout="wide"
)

# Initialize session state for search counting
if 'search_count' not in st.session_state:
    st.session_state.search_count = 0

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('similarity_data_sample.csv')

df = load_data()

# Header
st.title("🧬 TalentDNA Professional Similarity Search")
st.subheader("Find professionals similar to anyone in seconds")

# Warning about demo limitations
st.warning("""
⚠️ **DEMO VERSION LIMITATIONS:**
- Showing only 5 similar profiles (full version shows up to 50)
- Limited to 5,000 sample relationships (full version: 1.8 billion)  
- Profile summaries truncated (full version: complete profiles)
- No export functionality (full version: unlimited exports)
- Maximum 10 searches per session (full version: unlimited)
""")

# Sidebar stats
with st.sidebar:
    st.header("📊 Full Dataset Stats")
    st.metric("Total Relationships", "1.8B")
    st.metric("Unique Professionals", "475M")
    st.metric("C-Suite Executives", "127K")
    st.metric("Director+ Level", "2.1M")
    
    st.divider()
    
    st.header("🎯 Demo Limitations")
    st.metric("Demo Relationships", f"{len(df):,}")
    st.metric("Searches Remaining", f"{10 - st.session_state.search_count}")
    
    st.divider()
    
    st.header("💰 Pricing")
    st.write("**Starter**: $2,500/month")
    st.write("**Professional**: $5,000/month")  
    st.write("**Enterprise**: $10,000+/month")
    
    if st.button("🚀 Start Free Trial", type="primary", use_container_width=True):
        st.balloons()
        st.success("Demo request sent! We'll contact you within 24 hours.")

# Check if user has exceeded search limit
if st.session_state.search_count >= 10:
    st.error("🔒 Demo search limit reached (10 searches)")
    st.info("👉 Schedule a call to see unlimited searches: sales@nuvel.ai")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.button("📅 Schedule Demo Call", type="primary", use_container_width=True)
    
    st.stop()

# Main search interface
tab1, tab2, tab3 = st.tabs(["🔍 Search by Keywords", "🏢 Popular Searches", "📈 Sample Analytics"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "Search for professionals:",
            placeholder="Try: Software Engineer, Google, Product Manager, San Francisco"
        )
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_button and search_term:
        # Increment search counter
        st.session_state.search_count += 1
        
        # Search logic
        search_lower = search_term.lower()
        results = df[
            (df['name'].str.lower().str.contains(search_lower, na=False)) |
            (df['summary'].str.lower().str.contains(search_lower, na=False)) |
            (df['location'].str.lower().str.contains(search_lower, na=False))
        ].head(5)  # Limit to 5 results in demo
        
        if len(results) > 0:
            st.success(f"✅ Found professionals matching '{search_term}'")
            st.info("💡 **Demo shows only 5 results.** Full version shows 50+ similar profiles with complete data!")
            
            # Display results
            for idx, row in results.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### 👤 {row['name']}")
                        if pd.notna(row['summary']):
                            st.write(f"💼 {row['summary']}")
                        if pd.notna(row['location']):
                            st.write(f"📍 {row['location']}")
                        st.caption("🔒 Full profile available in paid version")
                    with col2:
                        st.button("View Full Profile", disabled=True, key=f"profile_{idx}")
                        st.caption("Upgrade to unlock")
                    st.divider()
            
            # Upgrade prompt
            st.markdown("---")
            st.markdown("### 🚀 Want to see ALL similar profiles?")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("Start Free Trial - See All Results", type="primary", use_container_width=True):
                    st.success("Demo request sent! Check your email.")
            
        else:
            st.warning(f"No results found for '{search_term}' in demo data.")
            st.info("The full version searches across 1.8B relationships. Schedule a demo to see more!")

with tab2:
    st.header("🔥 Popular Searches (Click to Try)")
    
    # Demo searches that always work
    demo_searches = {
        "🎯 Senior Engineers": "Engineer",
        "💼 Directors": "Director", 
        "🏢 Tech Companies": "Google",
        "📍 San Francisco": "San Francisco",
        "🤖 Data Scientists": "Data"
    }
    
    cols = st.columns(5)
    for idx, (label, search_term) in enumerate(demo_searches.items()):
        with cols[idx]:
            if st.button(label, use_container_width=True):
                st.session_state.search_count += 1
                
                # Auto search
                results = df[
                    (df['name'].str.contains(search_term, case=False, na=False)) |
                    (df['summary'].str.contains(search_term, case=False, na=False))
                ].head(3)  # Show only 3 for demo
                
                st.success(f"Found professionals matching '{search_term}'")
                
                for _, row in results.iterrows():
                    with st.container():
                        st.markdown(f"**{row['name']}**")
                        if pd.notna(row['summary']):
                            st.caption(row['summary'])
                
                st.info("🔒 See all results with full profiles - Upgrade now!")

with tab3:
    st.header("📊 What You Get With Full Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Geographic Coverage")
        st.markdown("""
        - **United States**: 124M profiles
        - **Europe**: 89M profiles  
        - **Asia Pacific**: 156M profiles
        - **Rest of World**: 106M profiles
        """)
        
        st.subheader("💼 Seniority Breakdown")
        st.markdown("""
        - **C-Suite**: 127,000 executives
        - **VP Level**: 1.2M professionals
        - **Directors**: 2.1M professionals
        - **Senior ICs**: 45M professionals
        """)
    
    with col2:
        st.subheader("🏢 Company Coverage")
        st.markdown("""
        - **Fortune 500**: All companies
        - **Unicorns**: 1,200+ startups
        - **Scale-ups**: 50,000+ companies  
        - **Total**: 19M+ organizations
        """)
        
        st.subheader("🔍 Search Capabilities")
        st.markdown("""
        - Instant similarity matching
        - 50+ similar profiles per search
        - Bulk search up to 1,000 profiles
        - API access for integration
        """)

# Export button (disabled for demo)
st.divider()
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if st.button("📥 Export Results to CSV", disabled=True, use_container_width=True):
        pass
    st.caption("🔒 Export feature requires paid subscription")

# Footer
st.divider()
st.markdown("### Ready to unlock the full power of TalentDNA?")
st.markdown("📧 Contact: hello@nuvel.ai")
st.markdown("*Currently in private beta - Limited spots available*")

# Hidden tracking
searches_left = 10 - st.session_state.search_count
if searches_left <= 3 and searches_left > 0:
    st.warning(f"⚠️ Only {searches_left} demo searches remaining!")
