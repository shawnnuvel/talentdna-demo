import streamlit as st
import pandas as pd
from typing import List, Dict
import random

class NuvelSimilarityDemo:
    def __init__(self, csv_file='premium_similarity_data.csv'):
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
            'unique_source_profiles': self.df['source_name'].nunique() if 'source_name' in self.df.columns else 0,
            'unique_similar_professionals': self.df['similar_name'].nunique() if 'similar_name' in self.df.columns else 0,
            'data_completeness': {
                'source_names': (self.df['source_name'].notna() & (self.df['source_name'] != '')).sum() if 'source_name' in self.df.columns else 0,
                'similar_names': (self.df['similar_name'].notna() & (self.df['similar_name'] != '')).sum() if 'similar_name' in self.df.columns else 0,
                'similarity_scores': (self.df['similarity_score'].notna()).sum() if 'similarity_score' in self.df.columns else 0
            }
        }
    
    def search_by_keywords(self, keywords: str, max_results: int = 20) -> List[Dict]:
        """Search for professionals matching keywords in both source and similar profiles"""
        if self.df.empty:
            return []
        
        keywords_lower = keywords.lower()
        matching_results = []
        
        # Search in both source and similar profiles
        for _, row in self.df.iterrows():
            # Create searchable text for both source and similar profiles
            source_text = f"{row.get('source_name', '')} {row.get('source_title', '')} {row.get('source_company', '')} {row.get('source_location', '')}".lower()
            similar_text = f"{row.get('similar_name', '')} {row.get('similar_title', '')} {row.get('similar_company', '')} {row.get('similar_location', '')}".lower()
            
            # Check if keywords match either source or similar profile
            if any(word in source_text for word in keywords_lower.split()) or any(word in similar_text for word in keywords_lower.split()):
                # Add both source and similar as potential results
                matching_results.append({
                    'name': row.get('source_name', 'Unknown'),
                    'title': row.get('source_title', 'Professional'),
                    'company': row.get('source_company', 'Company'),
                    'location': row.get('source_location', 'Location'),
                    'profile_type': 'Source Profile',
                    'similarity_info': f"Connected to {row.get('similar_name', 'Unknown')} ({row.get('similarity_score', 0):.1f}% similarity)"
                })
                
                matching_results.append({
                    'name': row.get('similar_name', 'Unknown'),
                    'title': row.get('similar_title', 'Professional'),
                    'company': row.get('similar_company', 'Company'),
                    'location': row.get('similar_location', 'Location'),
                    'profile_type': 'Similar Professional',
                    'similarity_info': f"Similar to {row.get('source_name', 'Unknown')} ({row.get('similarity_score', 0):.1f}% similarity)"
                })
        
        # Remove duplicates and limit results
        seen = set()
        unique_results = []
        for result in matching_results:
            key = f"{result['name']}_{result['company']}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
                
        return unique_results[:max_results]
    
    def get_sample_profiles(self, count: int = 10) -> List[Dict]:
        """Get sample source profiles with their similar counts"""
        if self.df.empty:
            return []
        
        # Group by source profile to get unique source professionals
        source_profiles = self.df.groupby(['source_name', 'source_title', 'source_company', 'source_location']).size().reset_index(name='similar_count')
        
        samples = []
        for _, profile in source_profiles.head(count).iterrows():
            samples.append({
                'name': profile['source_name'],
                'title': profile['source_title'],
                'company': profile['source_company'],
                'location': profile['source_location'],
                'similar_count': profile['similar_count']
            })
        
        return samples
    
    def find_similar_to_profile(self, source_name: str) -> List[Dict]:
        """Find people similar to a specific source profile"""
        if self.df.empty:
            return []
        
        similar_profiles = self.df[self.df['source_name'] == source_name]
        
        results = []
        for _, row in similar_profiles.iterrows():
            results.append({
                'name': row.get('similar_name', 'Unknown'),
                'title': row.get('similar_title', 'Professional'),
                'company': row.get('similar_company', 'Company'),
                'location': row.get('similar_location', 'Location'),
                'similarity_score': row.get('similarity_score', 0)
            })
        
        return results
    
    def get_top_locations(self, top_n: int = 10) -> Dict[str, int]:
        """Get top locations from both source and similar profiles"""
        if self.df.empty:
            return {}
        
        # Combine both source and similar locations
        all_locations = pd.concat([
            self.df['source_location'].dropna(),
            self.df['similar_location'].dropna()
        ])
        
        return dict(all_locations.value_counts().head(top_n))
    
    def get_company_mentions(self) -> Dict[str, int]:
        """Count mentions of major companies in both source and similar profiles"""
        if self.df.empty:
            return {}
        
        companies = ['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Tesla', 'Netflix', 'Uber', 'LinkedIn', 'Salesforce', 'Goldman Sachs', 'McKinsey', 'BCG', 'Deloitte']
        
        # Combine both source and similar companies
        all_companies = pd.concat([
            self.df['source_company'].dropna(),
            self.df['similar_company'].dropna()
        ]).str.lower()
        
        mentions = {}
        for company in companies:
            count = all_companies.str.contains(company.lower(), na=False).sum()
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
            st.metric("Unique Source Profiles", f"{stats['unique_source_profiles']:,}")
            st.metric("Similar Professionals", f"{stats['unique_similar_professionals']:,}")
            
            st.subheader("Data Quality")
            total_records = stats['total_relationships']
            if total_records > 0:
                source_pct = (stats['data_completeness']['source_names'] / total_records) * 100
                similar_pct = (stats['data_completeness']['similar_names'] / total_records) * 100
                score_pct = (stats['data_completeness']['similarity_scores'] / total_records) * 100
                
                st.write(f"**Source Names:** {stats['data_completeness']['source_names']:,} ({source_pct:.1f}%)")
                st.write(f"**Similar Names:** {stats['data_completeness']['similar_names']:,} ({similar_pct:.1f}%)")
                st.write(f"**Similarity Scores:** {stats['data_completeness']['similarity_scores']:,} ({score_pct:.1f}%)")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search Professionals", "👤 Browse Sample Profiles", "📊 Dataset Insights", "🎮 Interactive Demo"])
    
    with tab1:
        st.header("🔍 Search for Similar Professionals")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "Enter search keywords:",
                placeholder="software engineer, Google, Goldman Sachs, marketing manager, McKinsey",
                help="Search across names, job titles, companies, and locations"
            )
        with col2:
            max_results = st.selectbox("Max Results:", [10, 15, 20, 30], index=1)
        
        if st.button("🔍 Search", type="primary") or search_query:
            if search_query:
                with st.spinner("Searching professional database..."):
                    results = demo.search_by_keywords(search_query, max_results)
                
                if results:
                    st.success(f"✅ Found **{len(results)}** professionals matching '{search_query}'")
                    
                    # Display results in clean format
                    for idx, result in enumerate(results, 1):
                        with st.container():
                            st.markdown(f"**{idx}. 👤 {result['name']}**")
                            st.markdown(f"💼 {result['title']} at **{result['company']}**")
                            st.markdown(f"📍 {result['location']}")
                            st.markdown(f"🔗 {result['similarity_info']}")
                            st.caption(f"Profile Type: {result['profile_type']}")
                            st.divider()
                else:
                    st.warning("No professionals found matching your search.")
                    st.info("💡 Try different keywords like: Google, software engineer, Goldman Sachs, McKinsey, product manager")
    
    with tab2:
        st.header("👤 Browse Premium Sample Profiles")
        st.markdown("**Explore real professionals from our database and their similarity relationships:**")
        
        sample_profiles = demo.get_sample_profiles(10)
        
        if sample_profiles:
            # Display sample profiles in professional format
            for i, profile in enumerate(sample_profiles, 1):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"### 👤 {profile['name']}")
                        st.markdown(f"**{profile['title']}**")
                        st.markdown(f"🏢 {profile['company']}")
                        if profile['location'] != 'Location':
                            st.markdown(f"📍 {profile['location']}")
                    
                    with col2:
                        st.metric("Similar Professionals", profile['similar_count'])
                    
                    with col3:
                        if st.button(f"👥 View Similar", key=f"profile_{i}", type="secondary"):
                            st.session_state[f'show_similar_{i}'] = not st.session_state.get(f'show_similar_{i}', False)
                    
                    # Show similar professionals when button is clicked
                    if st.session_state.get(f'show_similar_{i}', False):
                        st.markdown("#### 🔍 People Also Viewed:")
                        
                        similar_results = demo.find_similar_to_profile(profile['name'])
                        
                        if similar_results:
                            # Display similar profiles in a clean grid
                            for j, similar in enumerate(similar_results[:6], 1):  # Show top 6
                                with st.expander(f"#{j} {similar['name']} - {similar['company']}", expanded=True):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown(f"**Title:** {similar['title']}")
                                        st.markdown(f"**Company:** {similar['company']}")
                                        st.markdown(f"**Location:** {similar['location']}")
                                    with col_b:
                                        st.metric("Similarity", f"{similar['similarity_score']:.1f}%")
                        else:
                            st.info("No similar professionals found")
                    
                    st.divider()
        else:
            st.error("**No sample profiles available**")
    
    with tab3:
        st.header("📊 Dataset Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Top Locations")
            locations = demo.get_top_locations(10)
            if locations:
                for location, count in locations.items():
                    st.write(f"**{location}:** {count:,} professionals")
            else:
                st.info("No location data available")
        
        with col2:
            st.subheader("🏢 Company Mentions")
            companies = demo.get_company_mentions()
            if companies:
                for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"**{company}:** {count:,} mentions")
            else:
                st.info("No company mentions found")
        
        # Average similarity score
        if not demo.df.empty and 'similarity_score' in demo.df.columns:
            avg_similarity = demo.df['similarity_score'].mean()
            st.subheader("📈 Data Quality Metrics")
            st.write(f"**Average Similarity Score:** {avg_similarity:.1f}%")
            st.write(f"**Total Professional Relationships:** {len(demo.df):,}")
    
    with tab4:
        st.header("🎮 Interactive Demo")
        st.markdown("Try these pre-configured searches to see the similarity engine in action:")
        
        demo_searches = [
            "software engineer Google",
            "Goldman Sachs",
            "McKinsey consultant", 
            "product manager Meta",
            "director Amazon",
            "data scientist",
            "CEO"
        ]
        
        cols = st.columns(3)
        for i, search_term in enumerate(demo_searches):
            with cols[i % 3]:
                if st.button(f"🔍 {search_term}", key=f"demo_{search_term}"):
                    results = demo.search_by_keywords(search_term, 5)
                    
                    if results:
                        st.success(f"**{len(results)}** results for '{search_term}':")
                        for idx, result in enumerate(results[:3], 1):  # Show top 3
                            st.write(f"**{idx}.** {result['name']} - {result['title']} @ {result['company']}")
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
