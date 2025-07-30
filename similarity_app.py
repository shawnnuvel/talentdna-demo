import streamlit as st
import pandas as pd
from typing import List, Dict

class NuvelSimilarityDemo:
    def __init__(self, csv_file='similarity_data_sample.csv'):
        self.df = self.load_data(csv_file)
        
    def load_data(self, csv_file):
        try:
            df = pd.read_csv(csv_file)
            if df.empty:
                st.error("Demo dataset is empty")
                return pd.DataFrame()
            return df
        except FileNotFoundError:
            st.error(f"Demo dataset '{csv_file}' not found")
            return pd.DataFrame()
    
    def get_data_stats(self):
        """Return key statistics about the dataset"""
        if self.df.empty:
            return {}
        
        return {
            'total_relationships': len(self.df),
            'unique_profiles': self.df['profile_id'].nunique() if 'profile_id' in self.df.columns else 0,
            'unique_professionals': self.df['name'].nunique() if 'name' in self.df.columns else 0,
            'data_completeness': {
                'names': (self.df['name'].notna() & (self.df['name'] != '')).sum() if 'name' in self.df.columns else 0,
                'summaries': (self.df['summary'].notna() & (self.df['summary'] != '')).sum() if 'summary' in self.df.columns else 0,
                'locations': (self.df['location'].notna() & (self.df['location'] != '')).sum() if 'location' in self.df.columns else 0
            }
        }
    
    def search_by_keywords(self, keywords: str, max_results: int = 20) -> pd.DataFrame:
        """Search for professionals matching keywords"""
        if self.df.empty:
            return pd.DataFrame()
        
        keywords_lower = keywords.lower()
        search_columns = ['name', 'summary', 'location']
        
        # Create search mask
        mask = pd.Series([False] * len(self.df))
        for col in search_columns:
            if col in self.df.columns:
                mask |= self.df[col].str.lower().str.contains(keywords_lower, na=False)
        
        return self.df[mask].head(max_results)
    
    def get_sample_profiles(self, count: int = 10) -> List[Dict]:
        """Get sample profile IDs with their similar counts"""
        if self.df.empty or 'profile_id' not in self.df.columns:
            return []
        
        unique_profiles = self.df['profile_id'].unique()[:count]
        samples = []
        
        for profile_id in unique_profiles:
            similar_count = len(self.df[self.df['profile_id'] == profile_id])
            samples.append({
                'profile_id': profile_id,
                'similar_count': similar_count
            })
        
        return samples
    
    def find_similar_to_profile(self, profile_id: str) -> pd.DataFrame:
        """Find people similar to a specific profile"""
        if self.df.empty or 'profile_id' not in self.df.columns:
            return pd.DataFrame()
        
        return self.df[self.df['profile_id'] == profile_id]
    
    def get_top_locations(self, top_n: int = 10) -> pd.Series:
        """Get top locations from the dataset"""
        if self.df.empty or 'location' not in self.df.columns:
            return pd.Series()
        
        return self.df['location'].value_counts().head(top_n)
    
    def get_company_mentions(self) -> Dict[str, int]:
        """Count mentions of major companies in summaries"""
        if self.df.empty or 'summary' not in self.df.columns:
            return {}
        
        companies = ['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Tesla', 'Netflix', 'Uber', 'LinkedIn', 'Salesforce']
        all_summaries = ' '.join(self.df['summary'].dropna().astype(str)).lower()
        
        mentions = {}
        for company in companies:
            count = all_summaries.count(company.lower())
            if count > 0:
                mentions[company] = count
        
        return mentions

def main():
    st.set_page_config(
        page_title="Nuvel.ai Professional Similarity Engine",
        page_icon="🎯",
        layout="wide"
    )
    
    # Header
    st.title("🎯 Nuvel Professional Similarity API Demo")
    st.markdown("**Discover professionals similar to your best candidates**")
    
    # Initialize demo
    demo = NuvelSimilarityDemo()
    
    if demo.df.empty:
        st.error("Unable to load demo data. Please ensure your CSV file is available.")
        return
    
    # Sidebar with data overview
    with st.sidebar:
        st.header("📊 Demo Dataset Overview")
        stats = demo.get_data_stats()
        
        if stats:
            st.metric("Similarity Relationships", f"{stats['total_relationships']:,}")
            st.metric("Unique Source Profiles", f"{stats['unique_profiles']:,}")
            st.metric("Similar Professionals", f"{stats['unique_professionals']:,}")
            
            st.subheader("Data Completeness")
            total_records = stats['total_relationships']
            if total_records > 0:
                name_pct = (stats['data_completeness']['names'] / total_records) * 100
                summary_pct = (stats['data_completeness']['summaries'] / total_records) * 100
                location_pct = (stats['data_completeness']['locations'] / total_records) * 100
                
                st.write(f"**Names:** {stats['data_completeness']['names']:,} ({name_pct:.1f}%)")
                st.write(f"**Summaries:** {stats['data_completeness']['summaries']:,} ({summary_pct:.1f}%)")
                st.write(f"**Locations:** {stats['data_completeness']['locations']:,} ({location_pct:.1f}%)")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search Professionals", "👤 Browse Sample Profiles", "📊 Dataset Insights", "🎮 Interactive Demo"])
    
    with tab1:
        st.header("🔍 Search for Similar Professionals")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "Enter search keywords:",
                placeholder="software engineer, Google, San Francisco, marketing manager",
                help="Search across names, job summaries, and locations"
            )
        with col2:
            max_results = st.selectbox("Max Results:", [10, 20, 30, 50], index=1)
        
        if st.button("🔍 Search", type="primary") or search_query:
            if search_query:
                with st.spinner("Searching professional database..."):
                    results = demo.search_by_keywords(search_query, max_results)
                
                if not results.empty:
                    st.success(f"✅ Found **{len(results):,}** professionals matching '{search_query}'")
                    
                    # Display results in clean format
                    for idx, (_, row) in enumerate(results.iterrows(), 1):
                        with st.container():
                            st.markdown(f"**{idx}. 👤 {row.get('name', 'Unknown')}")
                            
                            if pd.notna(row.get('summary', '')) and row.get('summary', '') != '':
                                st.markdown(f"💼 {row['summary']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if pd.notna(row.get('location', '')) and row.get('location', '') != '':
                                    st.markdown(f"📍 {row['location']}")
                            with col2:
                                if pd.notna(row.get('link', '')) and row.get('link', '') != '':
                                    st.markdown(f"🔗 [Profile Link]({row['link']})")
                            
                            st.divider()
                else:
                    st.warning("No professionals found matching your search.")
                    st.info("💡 Try different keywords like: engineer, manager, marketing, Google, San Francisco")
    
    with tab2:
        st.header("👤 Sample Profile Browser")
        st.markdown("Explore similarity relationships from our demo dataset:")
        
        sample_profiles = demo.get_sample_profiles(10)
        
        if sample_profiles:
            # Display sample profiles in a nice format
            for i, profile in enumerate(sample_profiles, 1):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{i}. Profile ID:** `{profile['profile_id']}`")
                with col2:
                    st.metric("Similar Professionals", profile['similar_count'])
                with col3:
                    if st.button(f"View Similar", key=f"profile_{i}"):
                        similar_results = demo.find_similar_to_profile(profile['profile_id'])
                        
                        if not similar_results.empty:
                            st.success(f"Found {len(similar_results)} professionals similar to Profile {profile['profile_id']}:")
                            
                            for idx, (_, row) in enumerate(similar_results.head(5).iterrows(), 1):
                                st.markdown(f"**{idx}. {row.get('name', 'Unknown')}**")
                                if pd.notna(row.get('summary', '')):
                                    st.caption(f"💼 {row['summary']}")
                                if pd.notna(row.get('location', '')):
                                    st.caption(f"📍 {row['location']}")
                                st.write("")
        else:
            st.info("No sample profiles available in the current dataset.")
    
    with tab3:
        st.header("📊 Dataset Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Top Locations")
            locations = demo.get_top_locations(10)
            if not locations.empty:
                for location, count in locations.items():
                    if pd.notna(location):
                        st.write(f"**{location}:** {count:,} professionals")
            else:
                st.info("No location data available")
        
        with col2:
            st.subheader("🏢 Company Mentions")
            companies = demo.get_company_mentions()
            if companies:
                for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"**{company}:** mentioned {count:,} times")
            else:
                st.info("No company mentions found")
        
        # Profile with most similar professionals
        if not demo.df.empty and 'profile_id' in demo.df.columns:
            profile_counts = demo.df['profile_id'].value_counts()
            if not profile_counts.empty:
                top_profile = profile_counts.index[0]
                top_count = profile_counts.iloc[0]
                st.subheader("👑 Most Connected Profile")
                st.write(f"**Profile ID:** `{top_profile}` has **{top_count}** similar professionals")
    
    with tab4:
        st.header("🎮 Interactive Demo")
        st.markdown("Try these pre-configured searches to see the similarity engine in action:")
        
        demo_searches = [
            "software engineer",
            "Google",
            "San Francisco", 
            "marketing manager",
            "director",
            "data scientist",
            "product manager"
        ]
        
        cols = st.columns(3)
        for i, search_term in enumerate(demo_searches):
            with cols[i % 3]:
                if st.button(f"🔍 {search_term}", key=f"demo_{search_term}"):
                    results = demo.search_by_keywords(search_term, 5)
                    
                    if not results.empty:
                        st.success(f"**{len(results)}** results for '{search_term}':")
                        for idx, (_, row) in enumerate(results.iterrows(), 1):
                            st.write(f"**{idx}.** {row.get('name', 'Unknown')}")
                            if pd.notna(row.get('summary', '')):
                                st.caption(row['summary'])
                    else:
                        st.warning(f"No results for '{search_term}'")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <p><strong>Nuvel.ai Professional Similarity Engine</strong></p>
    <p>🌐 <em>Powered by 1.8+ billion professional relationships</em></p>
    <p><strong>This demo represents a small sample of our full 475M professional database</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
