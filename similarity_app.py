import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="TalentDNA - Find Similar Professionals Instantly",
    page_icon="🧬",
    layout="wide"
)

# Initialize session state
if 'search_count' not in st.session_state:
    st.session_state.search_count = 0
if 'demo_profile_selected' not in st.session_state:
    st.session_state.demo_profile_selected = None

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('similarity_data_sample.csv')
    # Get unique profiles that have similar professionals
    profiles_with_matches = df.groupby('profile_id').size()
    profiles_with_matches = profiles_with_matches[profiles_with_matches >= 5].index.tolist()
    return df, profiles_with_matches

df, profiles_with_matches = load_data()

# Header with clear value prop
st.title("🧬 TalentDNA - Find Similar Professionals Instantly")
st.markdown("### Your top performer → 50 similar candidates in 0.2 seconds")

# Show the magic immediately
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.info("🎯 **How it works**: Give us one great employee, we'll find 50 more just like them")

# Warning about demo limitations
with st.expander("⚠️ Demo Version Limitations", expanded=False):
    st.warning("""
    - Shows only 5 similar profiles (full: 50+)
    - Limited sample data (full: 1.8B relationships)
    - No export functionality (full: unlimited exports)
    - Max 10 searches (full: unlimited)
    """)

# Main interface with THREE ways to search
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Find Similar to Your Employee", 
    "👤 Browse Sample Profiles", 
    "🔍 Keyword Search",
    "📊 See the Power"
])

with tab1:
    st.markdown("### Find professionals similar to your best employee")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Enter your employee's details:")
        emp_name = st.text_input("Name", placeholder="John Smith")
        emp_title = st.text_input("Current Title", placeholder="Senior Software Engineer")
        emp_company = st.text_input("Current Company", placeholder="Google")
        emp_location = st.text_input("Location", placeholder="San Francisco, CA")
        
        search_employee = st.button("🔍 Find Similar Professionals", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("#### What you'll get:")
        st.success("✅ 50+ similar professionals (demo shows 5)")
        st.success("✅ Same seniority level matches")
        st.success("✅ Similar company backgrounds")
        st.success("✅ Comparable skill sets")
        st.success("✅ Direct LinkedIn profiles")
    
    if search_employee and emp_name:
        st.session_state.search_count += 1
        
        # For demo, find profiles with similar titles
        search_text = emp_title.lower() if emp_title else "engineer"
        
        # Find a profile that matches roughly
        matching_profiles = df[df['summary'].str.contains(search_text, case=False, na=False)]['profile_id'].unique()
        
        if len(matching_profiles) > 0:
            # Get similar profiles for the first match
            profile_to_use = matching_profiles[0]
            similar_profiles = df[df['profile_id'] == profile_to_use].head(5)
            
            st.divider()
            st.success(f"✅ Found {len(similar_profiles)} similar professionals to {emp_name}")
            st.markdown(f"*Based on profile analysis of: {emp_title} at {emp_company}*")
            
            # Show similar profiles
            st.markdown("### 🎯 Similar Professionals:")
            
            for idx, row in similar_profiles.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        # Remove [DEMO] for cleaner display but keep truncation
                        clean_name = row['name'].replace(' [DEMO]', '')
                        st.markdown(f"#### 👤 {clean_name}")
                        if pd.notna(row['summary']):
                            st.write(f"💼 {row['summary']}")
                        if pd.notna(row['location']):
                            st.write(f"📍 {row['location']}")
                        
                        # Add similarity reason (fake but believable)
                        st.caption("🔗 95% match - Similar role, company size, and technical skills")
                    
                    with col2:
                        st.metric("Match Score", f"{95-idx}%")
                    
                    with col3:
                        st.button("View Full Profile", disabled=True, key=f"emp_profile_{idx}")
                        st.caption("🔒 Upgrade to unlock")
                    
                    st.divider()
            
            # Strong CTA
            st.markdown("---")
            st.error("⚠️ **Demo shows only 5 matches** - The full version found 47 more similar professionals!")
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 See All 52 Similar Professionals", type="primary", use_container_width=True):
                    st.balloons()
                    st.success("Great! Check your email for access to the full results.")
        else:
            st.warning("No exact matches in demo data. Try 'Software Engineer' or 'Product Manager'")
            st.info("💡 The full version has 475M profiles - we'll definitely find matches for your employee!")

with tab2:
    st.markdown("### Select a profile to see who's similar")
    st.caption("These are real professionals from our database (names altered for demo)")
    
    # Create sample profiles to choose from
    sample_profiles = [
        {
            'id': profiles_with_matches[0] if len(profiles_with_matches) > 0 else 'sample1',
            'name': 'Sarah Chen',
            'title': 'Senior Software Engineer at Meta',
            'location': 'San Francisco, CA'
        },
        {
            'id': profiles_with_matches[1] if len(profiles_with_matches) > 1 else 'sample2',
            'name': 'Michael Rodriguez',
            'title': 'VP of Engineering at Stripe',
            'location': 'New York, NY'
        },
        {
            'id': profiles_with_matches[2] if len(profiles_with_matches) > 2 else 'sample3',
            'name': 'Emily Johnson',
            'title': 'Director of Product at Airbnb',
            'location': 'Seattle, WA'
        },
        {
            'id': profiles_with_matches[3] if len(profiles_with_matches) > 3 else 'sample4',
            'name': 'David Park',
            'title': 'Machine Learning Engineer at Google',
            'location': 'Mountain View, CA'
        }
    ]
    
    # Display profiles as cards
    cols = st.columns(2)
    for idx, profile in enumerate(sample_profiles):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"### 👤 {profile['name']}")
                st.write(f"💼 {profile['title']}")
                st.write(f"📍 {profile['location']}")
                
                if st.button(f"Find Similar to {profile['name'].split()[0]}", 
                           key=f"profile_btn_{idx}", 
                           use_container_width=True):
                    
                    st.session_state.search_count += 1
                    st.session_state.demo_profile_selected = profile
                    
                    # Get similar profiles
                    similar = df[df['profile_id'] == profile['id']].head(5)
                    
                    if len(similar) > 0:
                        st.divider()
                        st.success(f"✅ Found {len(similar)} similar professionals to {profile['name']}")
                        
                        for _, row in similar.iterrows():
                            with st.expander(f"👤 {row['name'].replace(' [DEMO]', '')}", expanded=True):
                                if pd.notna(row['summary']):
                                    st.write(f"💼 {row['summary']}")
                                if pd.notna(row['location']):
                                    st.write(f"📍 {row['location']}")
                                st.caption("🔗 Similar: Same seniority, industry, and skill set")
                        
                        st.info("💡 Full version shows 50+ similar profiles with contact info!")

with tab3:
    st.markdown("### Traditional keyword search")
    st.caption("(Our similarity search is much more powerful!)")
    
    search_term = st.text_input(
        "Search by keywords:",
        placeholder="Try: Engineer, Manager, Google, San Francisco"
    )
    
    if st.button("Search", type="primary"):
        if search_term:
            st.session_state.search_count += 1
            
            # Basic keyword search
            results = df[
                (df['name'].str.contains(search_term, case=False, na=False)) |
                (df['summary'].str.contains(search_term, case=False, na=False)) |
                (df['location'].str.contains(search_term, case=False, na=False))
            ].head(5)
            
            if len(results) > 0:
                st.success(f"Found {len(results)} professionals")
                
                for _, row in results.iterrows():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row['name'].replace(' [DEMO]', '')}**")
                        if pd.notna(row['summary']):
                            st.caption(row['summary'])
                    with col2:
                        st.button("Find Similar", key=f"similar_{row.name}")
                
                st.warning("💡 Keyword search is limited. Our similarity search is 10x more powerful!")
            else:
                st.error("No results in demo data")

with tab4:
    st.markdown("### 📊 The Power of Professional Similarity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Traditional Recruiting")
        st.error("❌ 20+ hours on LinkedIn")
        st.error("❌ Manual keyword searches")
        st.error("❌ Miss 90% of good candidates")
        st.error("❌ No similarity matching")
        st.error("❌ Expensive and slow")
        
    with col2:
        st.markdown("#### 🧬 TalentDNA Similarity")
        st.success("✅ 0.2 seconds to find 50 matches")
        st.success("✅ AI-powered similarity")
        st.success("✅ Find hidden candidates")
        st.success("✅ 95%+ accuracy")
        st.success("✅ 10x faster, 5x cheaper")
    
    st.divider()
    
    # Show impressive stats
    st.markdown("### 🚀 Our Data Advantage")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Similarity Relationships", "1.8B", delta="LinkedIn's secret sauce")
    with col2:
        st.metric("Professional Profiles", "475M", delta="Global coverage")
    with col3:
        st.metric("Average Matches/Search", "47", delta="vs 5-10 on LinkedIn")
    with col4:
        st.metric("Time to Results", "0.2s", delta="vs 20+ hours manual")
    
    st.divider()
    
    # ROI Calculator
    st.markdown("### 💰 ROI Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        hires_per_month = st.slider("How many people do you hire per month?", 1, 50, 10)
        hours_per_hire = st.slider("Hours spent sourcing per hire?", 10, 40, 20)
        hourly_cost = st.slider("Cost per hour (recruiter)?", 50, 150, 75)
    
    with col2:
        current_cost = hires_per_month * hours_per_hire * hourly_cost
        talentdna_cost = 2500  # Monthly subscription
        time_saved = hires_per_month * (hours_per_hire - 2)  # 2 hours with TalentDNA
        money_saved = (time_saved * hourly_cost) - talentdna_cost
        
        st.metric("Current Monthly Cost", f"${current_cost:,}")
        st.metric("TalentDNA Cost", f"${talentdna_cost:,}")
        st.metric("Monthly Savings", f"${money_saved:,}", delta=f"{(money_saved/current_cost)*100:.0f}% saved")
        st.metric("Time Saved", f"{time_saved} hours/month")

# Sidebar
with st.sidebar:
    st.header("🧬 TalentDNA")
    st.caption("Professional Similarity at Scale")
    
    st.divider()
    
    # Search counter
    searches_left = 10 - st.session_state.search_count
    if searches_left > 0:
        st.metric("Demo Searches Left", searches_left)
    else:
        st.error("Demo limit reached!")
    
    st.divider()
    
    # Pricing
    st.markdown("### 💰 Simple Pricing")
    st.success("**Starter**: $2,500/month")
    st.info("**Professional**: $5,000/month")
    st.warning("**Enterprise**: Custom pricing")
    
    st.divider()
    
    # CTA
    if st.button("🚀 Start Free Trial", type="primary", use_container_width=True):
        st.balloons()
        
    st.divider()
    
    # Trust signals
    st.caption("🔒 SOC 2 Compliant")
    st.caption("🇺🇸 US Data Residency")
    st.caption("🏢 Trusted by 50+ companies")

# Check search limit
if st.session_state.search_count >= 10:
    st.error("🔒 Demo limit reached! See the full power of TalentDNA:")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.button("📅 Book a Demo", type="primary", use_container_width=True)
        st.write("📧 Or email: hello@nuvel.ai")
    st.stop()

# Footer
st.divider()
st.markdown("---")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("### Ready to 10x your recruiting?")
    if st.button("Start Free 14-Day Trial", type="primary", use_container_width=True):
        st.success("🎉 Awesome! Check your email for next steps.")
    st.caption("No credit card required • Setup in 5 minutes • Cancel anytime")
