import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict
import random

# Configuration
MAX_DEMO_SEARCHES = 30
DEFAULT_RESULTS_COUNT = 10

class ProfessionalSimilarityDemo:
    def __init__(self, data_file: str = 'similarity_data_sample_demo_ready.csv'):
        self.data = self.load_data(data_file)
        self.initialize_session_state()
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load the demo dataset"""
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                st.error("Demo dataset is empty. Please run the data preparation script first.")
                return pd.DataFrame()
            
            # Validate required columns
            required_cols = ['source_name', 'similar_name', 'similarity_score', 
                           'source_title', 'similar_title', 'source_company', 'similar_company']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"Demo dataset missing required columns: {missing_cols}")
                return pd.DataFrame()
            
            return df
        except FileNotFoundError:
            st.error("Demo dataset not found. Please run the data preparation script to create 'similarity_data_sample_demo_ready.csv'")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading demo data: {e}")
            return pd.DataFrame()
    
    def initialize_session_state(self):
        """Initialize session tracking"""
        if 'search_count' not in st.session_state:
            st.session_state.search_count = 0
        if 'demo_expired' not in st.session_state:
            st.session_state.demo_expired = False
    
    def search_similar_professionals(self, query: str, max_results: int = 10) -> List[Dict]:
        """Find similar professionals based on query"""
        if self.data.empty:
            return []
        
        query_lower = query.lower()
        
        # Search in source profiles first
        source_matches = self.data[
            (self.data['source_name'].str.lower().str.contains(query_lower, na=False)) |
            (self.data['source_title'].str.lower().str.contains(query_lower, na=False)) |
            (self.data['source_company'].str.lower().str.contains(query_lower, na=False))
        ]
        
        if not source_matches.empty:
            # Get similar profiles for matched sources
            results = []
            for _, row in source_matches.head(max_results).iterrows():
                results.append({
                    'name': row['similar_name'],
                    'title': row['similar_title'], 
                    'company': row['similar_company'],
                    'location': row.get('similar_location', 'Not specified'),
                    'similarity': f"{row['similarity_score']:.1f}%",
                    'source_match': f"{row['source_name']} ({row['source_title']})"
                })
            return results
        
        # Fallback: search in similar profiles  
        similar_matches = self.data[
            (self.data['similar_name'].str.lower().str.contains(query_lower, na=False)) |
            (self.data['similar_title'].str.lower().str.contains(query_lower, na=False)) |
            (self.data['similar_company'].str.lower().str.contains(query_lower, na=False))
        ]
        
        if not similar_matches.empty:
            results = []
            for _, row in similar_matches.head(max_results).iterrows():
                results.append({
                    'name': row['similar_name'],
                    'title': row['similar_title'],
                    'company': row['similar_company'], 
                    'location': row.get('similar_location', 'Not specified'),
                    'similarity': f"{row['similarity_score']:.1f}%",
                    'source_match': f"Similar to {row['source_name']}"
                })
            return results
        
        return []
    
    def get_sample_profiles(self) -> List[Dict]:
        """Get featured sample profiles for browsing"""
        if self.data.empty:
            return []
        
        # Get unique source profiles with good data
        sample_sources = self.data.drop_duplicates('source_name').head(8)
        
        profiles = []
        for _, row in sample_sources.iterrows():
            # Count how many similar profiles this source has
            similar_count = len(self.data[self.data['source_name'] == row['source_name']])
            
            profiles.append({
                'name': row['source_name'],
                'title': row['source_title'],
                'company': row['source_company'], 
                'location': row.get('source_location', 'Not specified'),
                'similar_count': similar_count
            })
        
        return profiles

def main():
    st.set_page_config(
        page_title="Nuvel.ai - Professional Similarity Demo", 
        page_icon="🎯",
        layout="wide"
    )
    
    # Initialize demo
    demo = ProfessionalSimilarityDemo()
    
    # Header
    st.title("🎯 Nuvel.ai Professional Similarity Search")
    st.markdown("**Find professionals similar to your best candidates - instantly**")
    
    # Demo counter and limits
    remaining_searches = MAX_DEMO_SEARCHES - st.session_state.search_count
    
    if remaining_searches <= 0:
        st.error("🚫 Demo searches exhausted! Contact us for unlimited access to 475M profiles.")
        st.markdown("### Ready for full access?")
        st.markdown("📧 **Email:** hello@nuvel.ai")
        return
    else:
        st.info(f"🔄 Demo searches remaining: **{remaining_searches}**")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Search Similar", "👥 Browse Samples", "📞 Get Full Access"])
    
    with tab1:
        st.header("Find Similar Professionals")
        st.markdown("Enter any professional description, name, or company to find similar candidates:")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search for professionals:",
                placeholder="e.g. 'Software Engineer at Google', 'Product Manager', 'Sarah Johnson'",
                key="search_input"
            )
        
        with col2:
            max_results = st.selectbox(
                "Results to show:",
                options=[5, 10, 15, 20],
                index=1
            )
        
        if st.button("🔍 Find Similar Professionals", type="primary"):
            if not search_query:
                st.warning("⚠️ Please enter a search term")
                return
            
            # Increment counter
            st.session_state.search_count += 1
            
            with st.spinner("Searching 475M professional profiles..."):
                results = demo.search_similar_professionals(search_query, max_results)
                
                if results:
                    st.success(f"✅ Found **{len(results)}** similar professionals:")
                    
                    # Display results in clean cards
                    for i, result in enumerate(results, 1):
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**#{i} {result['name']}**")
                                st.markdown(f"*{result['title']}*")
                                st.markdown(f"🏢 {result['company']}")
                                st.markdown(f"📍 {result['location']}")
                                st.caption(f"Similar to: {result['source_match']}")
                            
                            with col2:
                                st.metric("Match", result['similarity'])
                            
                            with col3:
                                if st.button("View Profile", key=f"view_{i}", disabled=True):
                                    st.info("Full profiles available in paid version")
                            
                            st.divider()
                    
                    # Export functionality
                    if st.button("📥 Export Results (CSV)"):
                        st.info("Export functionality available in full version")
                
                else:
                    st.warning("🤔 No similar professionals found for this search. Try different keywords or company names.")
                    st.markdown("**Try searching for:**")
                    st.markdown("- Job titles: 'Software Engineer', 'Product Manager', 'Data Scientist'")
                    st.markdown("- Companies: 'Google', 'Meta', 'Amazon', 'Microsoft'") 
                    st.markdown("- Skills: 'Machine Learning', 'Sales', 'Marketing'")
    
    with tab2:
        st.header("Browse Sample Profiles")
        st.markdown("Click on any profile below to see similar professionals:")
        
        sample_profiles = demo.get_sample_profiles()
        
        if sample_profiles:
            # Display sample profiles in a grid
            cols = st.columns(2)
            
            for i, profile in enumerate(sample_profiles):
                col_idx = i % 2
                
                with cols[col_idx]:
                    with st.container():
                        st.markdown(f"**{profile['name']}**")
                        st.markdown(f"*{profile['title']}*")
                        st.markdown(f"🏢 {profile['company']}")
                        st.markdown(f"📍 {profile['location']}")
                        
                        if st.button(
                            f"Find {profile['similar_count']} similar professionals", 
                            key=f"sample_{i}",
                            type="secondary"
                        ):
                            st.session_state.search_count += 1
                            
                            with st.spinner(f"Finding professionals similar to {profile['name']}..."):
                                results = demo.search_similar_professionals(profile['name'], 8)
                                
                                if results:
                                    st.success(f"Found {len(results)} professionals similar to **{profile['name']}**:")
                                    
                                    for j, result in enumerate(results, 1):
                                        st.markdown(f"**{j}.** {result['name']} - *{result['title']}* at {result['company']} ({result['similarity']})")
                                
                        st.divider()
        else:
            st.error("No sample profiles available. Please check the demo dataset.")
    
    with tab3:
        st.header("Ready for Full Access?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Full Platform Features")
            st.markdown("""
            - **475M professional profiles** across 244 countries
            - **1.8B professional relationships** in our database  
            - **Unlimited searches** with enterprise API access
            - **Real-time data updates** and fresh profiles
            - **Advanced filtering** by location, industry, experience
            - **Bulk export capabilities** for your recruiting workflow
            - **Integration support** for your existing tools
            - **Dedicated customer success** manager
            """)
        
        with col2:
            st.markdown("### 📞 Contact Us")
            
            with st.form("contact_form"):
                name = st.text_input("Your Name*")
                email = st.text_input("Work Email*")
                company = st.text_input("Company*")
                use_case = st.selectbox(
                    "Primary Use Case*",
                    ["Recruiting Agency", "Executive Search", "Sales Prospecting", "HR/Talent Acquisition", "Other"]
                )
                message = st.text_area("Tell us about your needs:")
                
                submitted = st.form_submit_button("🚀 Request Demo")
                
                if submitted:
                    if name and email and company:
                        st.success("✅ Demo request submitted! We'll contact you within 24 hours.")
                        st.balloons()
                    else:
                        st.error("Please fill in all required fields marked with *")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <p><strong>Nuvel.ai</strong> - Professional Similarity Search powered by 1.8B relationships</p>
    <p>This demo shows a small sample of our full dataset. Contact us for enterprise access.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
