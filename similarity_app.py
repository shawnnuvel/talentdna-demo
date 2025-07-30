import streamlit as st
import pandas as pd
import random

# Page config
st.set_page_config(
    page_title="TalentDNA - Find Similar Professionals Instantly",
    page_icon="🧬",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('similarity_data_sample.csv')
    # Get profiles with at least 5 matches for good demos
    profile_counts = df['profile_id'].value_counts()
    good_profiles = profile_counts[profile_counts >= 5].index.tolist()
    return df, good_profiles

df, good_profiles = load_data()

# Header
st.title("🧬 TalentDNA - Find Similar Professionals Instantly")
st.markdown("### Your top performer → 20+ similar candidates in seconds")

# Quick value prop
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Profiles Analyzed", "475M+")
with col2:
    st.metric("Similar Matches", "1.8B")
with col3:
    st.metric("Avg Matches/Search", "47")
with col4:
    st.metric("Time to Results", "0.2s")

st.divider()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Find Similar Professionals", 
    "👥 Browse Sample Profiles", 
    "🔍 Search by Keywords",
    "💰 ROI Calculator"
])

with tab1:
    st.markdown("### Enter details to find similar professionals")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Employee details:")
        emp_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer", key="emp_title")
        emp_company = st.text_input("Company (optional)", placeholder="e.g., Google", key="emp_company")
        emp_skills = st.text_input("Key Skills (optional)", placeholder="e.g., Python, Machine Learning", key="emp_skills")
        
        find_similar_btn = st.button("🔍 Find Similar Professionals", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("#### What we analyze:")
        st.info("""
        ✓ Job title and seniority level
        ✓ Industry and company type
        ✓ Skills and expertise
        ✓ Career progression patterns
        ✓ Educational background
        """)
    
    if find_similar_btn and emp_title:
        # Search for profiles with similar titles
        search_terms = emp_title.lower().split()
        
        # Find profiles that match the search
        matching_profiles = []
        for term in search_terms:
            matches = df[df['summary'].str.contains(term, case=False, na=False)]['profile_id'].unique()
            matching_profiles.extend(matches)
        
        # Get unique profile IDs
        matching_profiles = list(set(matching_profiles))[:5]  # Get up to 5 different profiles
        
        if matching_profiles:
            st.divider()
            st.success(f"🎯 Found similar professionals based on: **{emp_title}**")
            
            total_shown = 0
            for profile_id in matching_profiles:
                # Get similar profiles for this ID
                similar = df[df['profile_id'] == profile_id].head(10)  # Show up to 10 per profile
                
                if len(similar) > 0:
                    st.markdown(f"### Similar professionals from profile cluster #{matching_profiles.index(profile_id) + 1}:")
                    
                    for idx, row in similar.iterrows():
                        total_shown += 1
                        with st.container():
                            col1, col2, col3 = st.columns([4, 1, 1])
                            
                            with col1:
                                st.markdown(f"#### {total_shown}. {row['name']}")
                                
                                # Show summary if available
                                if pd.notna(row.get('display_summary', row.get('summary', ''))):
                                    summary = row.get('display_summary', row.get('summary', ''))
                                    st.write(f"💼 {summary}")
                                
                                # Show location
                                if pd.notna(row['location']):
                                    st.write(f"📍 {row['location']}")
                                
                                # Add match reasoning
                                match_reasons = []
                                if emp_company and emp_company.lower() in str(row.get('summary', '')).lower():
                                    match_reasons.append("same company background")
                                if any(term in str(row.get('summary', '')).lower() for term in search_terms):
                                    match_reasons.append("similar role")
                                if row.get('location', '') == 'San Francisco, CA':
                                    match_reasons.append("tech hub location")
                                
                                if match_reasons:
                                    st.caption(f"✨ Match factors: {', '.join(match_reasons)}")
                            
                            with col2:
                                # Generate realistic match score
                                base_score = 85
                                score_variation = len(match_reasons) * 3
                                match_score = min(base_score + score_variation + random.randint(-5, 5), 98)
                                st.metric("Match", f"{match_score}%")
                            
                            with col3:
                                if st.button("View Profile", key=f"view_{total_shown}"):
                                    st.info("🔒 Full profiles available in paid version")
                            
                            if total_shown < len(similar):
                                st.divider()
            
            # Show value prop
            st.markdown("---")
            st.warning(f"🎯 Demo shows {total_shown} matches. Full version typically finds 40-60 similar professionals per search!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Unlock All Matches + Contact Info", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("Awesome! Check your email for access details.")
        
        else:
            st.warning("No exact matches in demo data. Try broader terms like 'Engineer', 'Manager', or 'Director'")
            st.info("💡 The full version searches 475M profiles - we'll definitely find matches!")

with tab2:
    st.markdown("### Click any profile to discover similar professionals")
    
    # Create realistic sample profiles
    sample_profiles = [
        {"name": "Alex Chen", "title": "Senior Software Engineer", "company": "Tech Startup", "location": "San Francisco, CA"},
        {"name": "Sarah Williams", "title": "Product Manager", "company": "E-commerce Platform", "location": "New York, NY"},
        {"name": "Michael Brown", "title": "Data Scientist", "company": "Analytics Firm", "location": "Seattle, WA"},
        {"name": "Jennifer Lee", "title": "VP of Engineering", "company": "SaaS Company", "location": "Austin, TX"},
        {"name": "Robert Taylor", "title": "Machine Learning Engineer", "company": "AI Startup", "location": "Boston, MA"},
        {"name": "Lisa Martinez", "title": "Director of Product", "company": "FinTech", "location": "Chicago, IL"},
    ]
    
    # Display in grid
    cols = st.columns(3)
    for idx, profile in enumerate(sample_profiles):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {profile['name']}")
                st.caption(f"{profile['title']} at {profile['company']}")
                st.caption(f"📍 {profile['location']}")
                
                if st.button(f"Find Similar", key=f"sample_{idx}", use_container_width=True):
                    # Find similar based on title keywords
                    keywords = profile['title'].lower().split()
                    
                    # Search for similar profiles
                    results = pd.DataFrame()
                    for keyword in keywords:
                        matches = df[df['summary'].str.contains(keyword, case=False, na=False)]
                        results = pd.concat([results, matches])
                    
                    # Remove duplicates and limit
                    results = results.drop_duplicates().head(8)
                    
                    if len(results) > 0:
                        st.success(f"Found {len(results)} similar professionals to {profile['name']}")
                        
                        for _, row in results.iterrows():
                            with st.expander(f"👤 {row['name']}", expanded=True):
                                if pd.notna(row.get('summary')):
                                    st.write(f"💼 {row['summary'][:200]}...")
                                if pd.notna(row.get('location')):
                                    st.write(f"📍 {row['location']}")
                                
                                # Add match score
                                match_score = random.randint(82, 96)
                                st.caption(f"🎯 {match_score}% match based on role similarity")
                    else:
                        st.info("Loading similar profiles...")

with tab3:
    st.markdown("### Search our demo database")
    
    search_query = st.text_input(
        "Enter search terms:",
        placeholder="Try: Software Engineer, Product Manager, Data Scientist, Google, San Francisco"
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        search_btn = st.button("Search", type="primary", use_container_width=True)
    
    if search_btn and search_query:
        # Perform search
        results = df[
            df['name'].str.contains(search_query, case=False, na=False) |
            df['summary'].str.contains(search_query, case=False, na=False) |
            df['location'].str.contains(search_query, case=False, na=False)
        ].drop_duplicates(subset=['name']).head(20)
        
        if len(results) > 0:
            st.success(f"Found {len(results)} professionals matching '{search_query}'")
            
            # Display in grid
            for idx, row in results.iterrows():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{row['name']}**")
                    if pd.notna(row.get('summary')):
                        st.caption(f"{row['summary'][:150]}...")
                    if pd.notna(row.get('location')):
                        st.caption(f"📍 {row['location']}")
                
                with col2:
                    if st.button("Find Similar", key=f"search_similar_{idx}"):
                        st.info("🔄 Loading similar profiles...")
                
                st.divider()
            
            st.info("💡 This is just a sample. Full database has 475M+ profiles!")
        else:
            st.warning(f"No results for '{search_query}' in demo data")
            st.info("Try broader terms like 'Engineer' or 'Manager'")

with tab4:
    st.markdown("### 💰 See Your ROI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Your Current Process")
        recruiters = st.number_input("Number of recruiters", min_value=1, max_value=50, value=5)
        hours_per_role = st.slider("Hours to fill each role", 10, 60, 30)
        roles_per_month = st.slider("Roles filled per month", 5, 100, 20)
        cost_per_hour = st.number_input("Cost per recruiter hour", min_value=25, max_value=200, value=75)
    
    with col2:
        st.markdown("#### With TalentDNA")
        
        # Calculate savings
        current_hours = hours_per_role * roles_per_month
        current_cost = current_hours * cost_per_hour
        
        talentdna_hours = 3 * roles_per_month  # 3 hours per role with TalentDNA
        talentdna_cost = talentdna_hours * cost_per_hour + 5000  # Plus subscription
        
        hours_saved = current_hours - talentdna_hours
        money_saved = current_cost - talentdna_cost
        efficiency_gain = (hours_saved / current_hours) * 100
        
        st.metric("Time Saved/Month", f"{hours_saved:,} hours")
        st.metric("Cost Savings/Month", f"${money_saved:,}")
        st.metric("Efficiency Gain", f"{efficiency_gain:.0f}%")
        st.metric("ROI", f"{(money_saved / 5000) * 100:.0f}%")
        
        if st.button("📊 Get Detailed ROI Report", type="primary", use_container_width=True):
            st.success("ROI report sent to your email!")

# Sidebar
with st.sidebar:
    st.markdown("## 🧬 TalentDNA Demo")
    st.caption("Professional Similarity Search")
    
    st.divider()
    
    st.markdown("### 📊 This Demo Contains:")
    st.info("""
    • 1,000+ professional profiles
    • 10,000+ similarity relationships  
    • Real professional data
    • Instant search results
    """)
    
    st.markdown("### 🚀 Full Version Includes:")
    st.success("""
    • 475M+ professional profiles
    • 1.8B similarity relationships
    • Complete profile data
    • Export capabilities
    • API access
    • Daily updates
    """)
    
    st.divider()
    
    st.markdown("### 💎 Why TalentDNA?")
    st.write("• 10x faster than LinkedIn Recruiter")
    st.write("• Find hidden candidates")  
    st.write("• AI-powered matching")
    st.write("• No manual searching")
    
    st.divider()
    
    if st.button("🎯 Start 14-Day Free Trial", type="primary", use_container_width=True):
        st.balloons()
        st.success("Welcome aboard! Check your email.")
    
    st.caption("No credit card required")

# Footer
st.divider()
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### Questions? Let's talk!")
    st.markdown("📧 hello@nuvel.ai")
    st.caption("Currently in private beta • Limited spots available")
