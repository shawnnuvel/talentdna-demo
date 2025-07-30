import streamlit as st
import pandas as pd
from typing import List, Dict
import os

class PremiumWesternSimilarityDemo:
    def __init__(self, csv_file='premium_western_demo.csv'):
        self.csv_file = csv_file
        self.df = self.load_data()
        
    def load_data(self) -> pd.DataFrame:
        """Load the premium Western professional data"""
        try:
            if not os.path.exists(self.csv_file):
                st.error(f"❌ Demo data file '{self.csv_file}' not found. Please run the data preparation script first.")
                return pd.DataFrame()
            
            df = pd.read_csv(self.csv_file)
            if df.empty:
                st.error("❌ Demo dataset is empty")
                return pd.DataFrame()
                
            # Validate required columns
            required_cols = ['source_name', 'source_title', 'source_company', 'source_location',
                           'similar_name', 'similar_title', 'similar_company', 'similar_location', 
                           'similarity_score']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                st.error(f"❌ Missing required columns: {missing_cols}")
                return pd.DataFrame()
                
            return df
        except Exception as e:
            st.error(f"❌ Error loading demo data: {e}")
            return pd.DataFrame()
    
    def get_demo_stats(self) -> Dict:
        """Get key statistics about the premium demo dataset"""
        if self.df.empty:
            return {}
        
        return {
            'total_relationships': len(self.df),
            'unique_source_profiles': self.df['source_name'].nunique(),
            'unique_similar_professionals': self.df['similar_name'].nunique(),
            'average_similarity': self.df['similarity_score'].mean(),
            'top_companies': list(self.df['source_company'].value_counts().head(8).index),
            'top_locations': list(self.df['source_location'].value_counts().head(8).index),
            'company_counts': dict(self.df['source_company'].value_counts().head(5))
        }
    
    def search_professionals(self, query: str, max_results: int = 15) -> List[Dict]:
        """Search for professionals matching query keywords"""
        if self.df.empty:
            return []
        
        query_lower = query.lower()
        query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
        
        if not query_words:
            return []
        
        matching_results = []
        
        # Search through both source and similar profiles
        for _, row in self.df.iterrows():
            # Combine all searchable fields
            searchable_text = f"{row['source_name']} {row['source_title']} {row['source_company']} {row['source_location']} {row['similar_name']} {row['similar_title']} {row['similar_company']} {row['similar_location']}".lower()
            
            # Count word matches for relevance scoring
            match_score = sum(1 for word in query_words if word in searchable_text)
            
            if match_score > 0:
                matching_results.append({
                    'source_name': row['source_name'],
                    'source_title': row['source_title'],
                    'source_company': row['source_company'],
                    'source_location': row['source_location'],
                    'similar_name': row['similar_name'],
                    'similar_title': row['similar_title'],
                    'similar_company': row['similar_company'],
                    'similar_location': row['similar_location'],
                    'similarity_score': row['similarity_score'],
                    'match_score': match_score
                })
        
        # Sort by match relevance, then by similarity score
        matching_results.sort(key=lambda x: (-x['match_score'], -x['similarity_score']))
        
        return matching_results[:max_results]
    
    def get_featured_profiles(self, count: int = 12) -> List[Dict]:
        """Get featured source profiles with their similar professional counts"""
        if self.df.empty:
            return []
        
        # Group by source profile to get unique featured professionals
        source_groups = self.df.groupby(['source_name', 'source_title', 'source_company', 'source_location']).size().reset_index(name='similar_count')
        
        # Sort by similar_count descending to get most connected profiles first
        source_groups = source_groups.sort_values('similar_count', ascending=False)
        
        featured = []
        for _, profile in source_groups.head(count).iterrows():
            featured.append({
                'name': profile['source_name'],
                'title': profile['source_title'],
                'company': profile['source_company'],
                'location': profile['source_location'],
                'similar_count': profile['similar_count']
            })
        
        return featured
    
    def get_similar_to_profile(self, source_name: str) -> List[Dict]:
        """Get all professionals similar to a specific source profile"""
        if self.df.empty:
            return []
        
        similar_profiles = self.df[self.df['source_name'] == source_name]
        
        results = []
        for _, row in similar_profiles.iterrows():
            results.append({
                'name': row['similar_name'],
                'title': row['similar_title'],
                'company': row['similar_company'],
                'location': row['similar_location'],
                'similarity_score': row['similarity_score']
            })
        
        # Sort by similarity score descending
        results.sort(key=lambda x: -x['similarity_score'])
        
        return results

def main():
    st.set_page_config(
        page_title="Nuvel.ai - Premium Professional Similarity Engine",
        page_icon="🎯",
        layout="wide"
    )
    
    # Initialize demo
    demo = PremiumWesternSimilarityDemo()
    
    # Header
    st.title("🎯 Nuvel.ai Network Similarity Engine")
    st.markdown("**Find senior professionals similar to your best candidates instantly**")
    
    if demo.df.empty:
        st.error("Unable to load premium demo data. Please ensure 'premium_western_demo.csv' exists in your directory.")
        st.info("Run the data preparation script to generate the premium Western demo dataset.")
        return
    
    # Sidebar with impressive stats
    with st.sidebar:
        st.header("📊 Demo Dataset")
        stats = demo.get_demo_stats()
        
        if stats:
            st.metric("Relationships", f"{stats['total_relationships']:,}")
            st.metric("Professionals", f"{stats['unique_source_profiles']:,}")
            st.metric("Similar Candidates", f"{stats['unique_similar_professionals']:,}")
            st.metric("Avg Similarity Score", f"{stats['average_similarity']:.1f}%")
            
            st.subheader("🏢 Top Companies")
            for company, count in stats['company_counts'].items():
                st.write(f"**{company}:** {count} connections")
            
            st.subheader("🌍 Key Markets")
            for location in stats['top_locations'][:5]:
                st.write(f"• {location}")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search Professionals", "⭐ Sample Profiles", "📊 Market Insights", "🚀 Quick Demo"])
    
    with tab1:
        st.header("🔍 Search Professionals")
        st.markdown("Search professionals from top companies:")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "Search professionals:",
                placeholder="software engineer google, director amazon, vp salesforce",
                help="Search by name, title, company, or location"
            )
        with col2:
            max_results = st.selectbox("Results to show:", [10, 15, 20, 25], index=1)
        
        if st.button("🔍 Find Similar Professionals", type="primary") or search_query:
            if search_query:
                with st.spinner("Searching professional database..."):
                    results = demo.search_professionals(search_query, max_results)
                
                if results:
                    st.success(f"✅ Found **{len(results)}** professionals with similarity to '{search_query}'")
                    
                    for i, result in enumerate(results, 1):
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"### {i}. 👤 {result['similar_name']}")
                                st.markdown(f"**{result['similar_title']}** at **{result['similar_company']}**")
                                st.markdown(f"📍 {result['similar_location']}")
                                st.caption(f"Similar to: {result['source_name']} ({result['source_title']} @ {result['source_company']})")
                            
                            with col2:
                                st.metric("Similarity", f"{result['similarity_score']:.1f}%")
                                st.button("📧 Contact", key=f"contact_{i}", help="Full contact info in paid version")
                            
                            st.divider()
                    
                    # Conversion hook
                    if len(results) >= max_results:
                        st.info("🔥 **Showing top matches only.** Full database contains 475M professionals with complete contact information.")
                
                else:
                    st.warning("No premium professionals found for this search.")
                    st.info("💡 Try: 'google engineer', 'salesforce vp', 'meta product manager'")
    
    with tab2:
        st.header("⭐ Sample Profiles")
        st.markdown("**Explore some professionals and their similarity networks:**")
        
        featured_profiles = demo.get_featured_profiles(10)
        
        if featured_profiles:
            for i, profile in enumerate(featured_profiles, 1):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"### {i}. 👤 {profile['name']}")
                        st.markdown(f"**{profile['title']}**")
                        st.markdown(f"🏢 {profile['company']}")
                        st.markdown(f"📍 {profile['location']}")
                    
                    with col2:
                        st.metric("Connected Professionals", profile['similar_count'])
                        st.caption("Similarity matches")
                    
                    with col3:
                        if st.button(f"👥 View Network", key=f"featured_{i}", type="secondary"):
                            similar_pros = demo.get_similar_to_profile(profile['name'])
                            
                            if similar_pros:
                                st.success(f"**{len(similar_pros)}** professionals in {profile['name']}'s network:")
                                
                                # Show top similar professionals
                                for j, similar in enumerate(similar_pros[:6], 1):
                                    with st.expander(f"#{j} {similar['name']} - {similar['company']}", expanded=True):
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            st.markdown(f"**Title:** {similar['title']}")
                                            st.markdown(f"**Company:** {similar['company']}")
                                            st.markdown(f"**Location:** {similar['location']}")
                                        with col_b:
                                            st.metric("Similarity", f"{similar['similarity_score']:.1f}%")
                    
                    st.divider()
    
    with tab3:
        st.header("📊 Demo Data Insights")
        
        stats = demo.get_demo_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏢 Top Companies Represented")
            if stats.get('top_companies'):
                for i, company in enumerate(stats['top_companies'], 1):
                    connections = stats['company_counts'].get(company, 0)
                    st.write(f"**{i}. {company}** - {connections} senior professional connections")
        
        with col2:
            st.subheader("🌍 Markets Covered")
            if stats.get('top_locations'):
                for i, location in enumerate(stats['top_locations'], 1):
                    st.write(f"**{i}. {location}**")
        
        st.subheader("📈 Data Quality Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Relationships", f"{stats['total_relationships']:,}")
        with col2:
            st.metric("Average Similarity Score", f"{stats['average_similarity']:.1f}%")
        with col3:
            st.metric("Professional Coverage", f"{stats['unique_source_profiles']:,}")
    
    with tab4:
        st.header("🚀 Quick Demo - Try These Searches")
        st.markdown("**Click any button below to see instant results:**")
        
        demo_searches = [
            "software engineer google",
            "product manager meta", 
            "director amazon",
            "vp salesforce",
            "data scientist",
            "engineering manager"
        ]
        
        cols = st.columns(3)
        for i, search_term in enumerate(demo_searches):
            with cols[i % 3]:
                if st.button(f"🔍 {search_term.title()}", key=f"quick_{i}"):
                    results = demo.search_professionals(search_term, 5)
                    
                    if results:
                        st.success(f"**{len(results)}** matches for '{search_term}':")
                        for j, result in enumerate(results[:3], 1):
                            st.write(f"**{j}.** {result['similar_name']} - *{result['similar_title']}* @ **{result['similar_company']}** ({result['similarity_score']:.1f}%)")
                    else:
                        st.warning(f"No results found for '{search_term}'")
    
    # Footer with conversion messaging
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **⚠️ Demo Limitations:**
        - Showcases random professionals
        - Full database: **475+M professionals** across **244 countries**  
        - Complete profiles available
        - Advanced filtering, bulk export, and API access in full version
        """)
    
    with col2:
        st.markdown("""
        **🚀 Ready for Full Access?**
        
        **[Schedule Demo Call →](mailto:hello@nuvel.ai)**
        
        Get unlimited access to our complete professional database with:
        - AI/ML-powered network similarity engine
        - Advanced search filters  
        - Bulk export capabilities
        - API integration for your tools
        """)
    
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p><strong>Nuvel.ai Professional Similarity Engine</strong></p>
    <p>🌐 <em>Powered by 1.8+ billion professional relationships</em></p>
    <p><strong>This demo represents less than 0.1% of our full premium database</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
