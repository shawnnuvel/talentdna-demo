import streamlit as st
import pandas as pd
from typing import List, Dict
import os
import random

class NuvelProfessionalSimilarityDemo:
    def __init__(self, csv_file='premium_western_demo.csv'):
        self.csv_file = csv_file
        self.df = self.load_data()
        
    def load_data(self) -> pd.DataFrame:
        """Load the premium professional similarity data"""
        try:
            if not os.path.exists(self.csv_file):
                st.error(f"❌ Demo data file '{self.csv_file}' not found.")
                return pd.DataFrame()
            
            df = pd.read_csv(self.csv_file)
            if df.empty:
                st.error("❌ Demo dataset is empty")
                return pd.DataFrame()
                
            return df
        except Exception as e:
            st.error(f"❌ Error loading demo data: {e}")
            return pd.DataFrame()
    
    def get_demo_stats(self) -> Dict:
        """Get key statistics about the demo dataset"""
        if self.df.empty:
            return {}
        
        return {
            'total_relationships': len(self.df),
            'unique_source_profiles': self.df['source_name'].nunique(),
            'unique_similar_professionals': self.df['similar_name'].nunique(),
            'average_similarity': self.df['similarity_score'].mean(),
            'top_companies': list(self.df['source_company'].value_counts().head(10).index),
            'top_locations': list(self.df['source_location'].value_counts().head(8).index)
        }
    
    def search_similar_professionals(self, query: str, max_results: int = 15) -> List[Dict]:
        """Search for professionals and return their similarity matches"""
        if self.df.empty:
            return []
        
        query_lower = query.lower()
        query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
        
        if not query_words:
            return []
        
        matching_results = []
        
        # Search through both source and similar profiles
        for _, row in self.df.iterrows():
            searchable_text = f"{row['source_name']} {row['source_title']} {row['source_company']} {row['similar_name']} {row['similar_title']} {row['similar_company']}".lower()
            
            # Count word matches for relevance scoring
            match_score = sum(1 for word in query_words if word in searchable_text)
            
            if match_score > 0:
                # Return the similar professional as the result
                matching_results.append({
                    'name': row['similar_name'],
                    'title': row['similar_title'],
                    'company': row['similar_company'],
                    'location': row['similar_location'],
                    'similarity_score': row['similarity_score'],
                    'source_reference': f"Similar to {row['source_name']} ({row['source_title']} @ {row['source_company']})",
                    'match_score': match_score
                })
        
        # Sort by match relevance, then by similarity score
        matching_results.sort(key=lambda x: (-x['match_score'], -x['similarity_score']))
        
        # Remove duplicates by name
        seen_names = set()
        unique_results = []
        for result in matching_results:
            if result['name'] not in seen_names:
                seen_names.add(result['name'])
                unique_results.append(result)
        
        return unique_results[:max_results]
    
    def get_featured_professionals(self, count: int = 10) -> List[Dict]:
        """Get featured source professionals with their similarity network size"""
        if self.df.empty:
            return []
        
        # Group by source profile to get network sizes
        source_groups = self.df.groupby(['source_name', 'source_title', 'source_company', 'source_location']).size().reset_index(name='network_size')
        
        # Sort by network size to get most connected professionals
        source_groups = source_groups.sort_values('network_size', ascending=False)
        
        featured = []
        for _, profile in source_groups.head(count).iterrows():
            featured.append({
                'name': profile['source_name'],
                'title': profile['source_title'],
                'company': profile['source_company'],
                'location': profile['source_location'],
                'network_size': profile['network_size']
            })
        
        return featured
    
    def find_similar_to_professional(self, source_name: str) -> List[Dict]:
        """Find all professionals similar to a specific source professional"""
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
        
        # Sort by similarity score
        results.sort(key=lambda x: -x['similarity_score'])
        
        return results

def main():
    st.set_page_config(
        page_title="Nuvel.ai - Professional Similarity Engine",
        page_icon="🎯",
        layout="wide"
    )
    
    # Header
    st.title("🎯 Nuvel.ai Similarity Engine")
    st.markdown("**Discover professionals similar to your best candidates - Powered by 1.8B+ professional relationships**")
    
    # Initialize demo
    demo = NuvelProfessionalSimilarityDemo()
    
    if demo.df.empty:
        st.error("Unable to load demo data. Please ensure the CSV file is available.")
        return
    
    # Sidebar with stats
    with st.sidebar:
        st.header("📊 Demo Intelligence")
        stats = demo.get_demo_stats()
        
        if stats:
            st.metric("Similarity Relationships", f"{stats['total_relationships']:,}")
            st.metric("Source Professionals", f"{stats['unique_source_profiles']:,}")
            st.metric("Similar Candidates", f"{stats['unique_similar_professionals']:,}")
            st.metric("Avg Similarity Score", f"{stats['average_similarity']:.1f}%")
            
            st.subheader("🏢 Top Companies")
            for company in stats['top_companies'][:6]:
                st.write(f"• **{company}**")
            
            st.subheader("🌍 Key Markets")
            for location in stats['top_locations'][:5]:
                st.write(f"• {location}")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Similarity Search", "⭐ Featured Professionals", "📊 Demo Insights"])
    
    with tab1:
        st.header("🔍 Professional Similarity Search")
        st.markdown("**Find professionals similar to your target candidates:**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "Search for professionals:",
                placeholder="software engineer google, product manager meta, director amazon",
                help="Search by name, title, company, or location"
            )
        with col2:
            max_results = st.selectbox("Results:", [10, 15, 20], index=1)
        
        if st.button("🔍 Find Similar Professionals", type="primary") or search_query:
            if search_query:
                with st.spinner("Analyzing professional similarity patterns..."):
                    results = demo.search_similar_professionals(search_query, max_results)
                
                if results:
                    st.success(f"✅ Found **{len(results)}** similar professionals matching '{search_query}'")
                    
                    for i, result in enumerate(results, 1):
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"### {i}. 👤 {result['name']}")
                                st.markdown(f"**{result['title']}** at **{result['company']}**")
                                st.markdown(f"📍 {result['location']}")
                                st.caption(result['source_reference'])
                            
                            with col2:
                                st.metric("Similarity", f"{result['similarity_score']:.1f}%")
                                if st.button("📧 Contact", key=f"contact_{i}", help="Full contact info in premium version"):
                                    st.info("Contact information available in full platform")
                            
                            st.divider()
                
                else:
                    st.warning("No similar professionals found for this search.")
                    st.info("💡 Try: 'software engineer', 'google', 'product manager', 'director'")
        
        # Quick demo searches
        st.markdown("### 🚀 Try These Demo Searches")
        demo_searches = [
            "software engineer google",
            "product manager", 
            "goldman sachs",
            "director amazon",
            "data scientist"
        ]
        
        cols = st.columns(len(demo_searches))
        for i, search_term in enumerate(demo_searches):
            with cols[i]:
                if st.button(f"🔍 {search_term.title()}", key=f"demo_{i}"):
                    results = demo.search_similar_professionals(search_term, 5)
                    if results:
                        st.success(f"**{len(results)}** matches:")
                        for j, r in enumerate(results[:3], 1):
                            st.write(f"**{j}.** {r['name']} - *{r['title']}* @ **{r['company']}** ({r['similarity_score']:.1f}%)")
    
    with tab2:
        st.header("⭐ Featured Professional Networks")
        st.markdown("**Explore these professionals and their similarity networks:**")
        
        featured = demo.get_featured_professionals(8)
        
        if featured:
            for i, professional in enumerate(featured, 1):
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"### {i}. 👤 {professional['name']}")
                        st.markdown(f"**{professional['title']}**")
                        st.markdown(f"🏢 {professional['company']}")
                        st.markdown(f"📍 {professional['location']}")
                    
                    with col2:
                        st.metric("Similar Professionals", professional['network_size'])
                        st.caption("In their similarity network")
                    
                    with col3:
                        if st.button(f"👥 View Network", key=f"network_{i}", type="secondary"):
                            similar_pros = demo.find_similar_to_professional(professional['name'])
                            
                            if similar_pros:
                                st.success(f"**{len(similar_pros)}** professionals in {professional['name']}'s network:")
                                
                                for j, similar in enumerate(similar_pros[:6], 1):
                                    with st.expander(f"#{j} {similar['name']} - {similar['company']}", expanded=True):
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            st.markdown(f"**{similar['title']}**")
                                            st.markdown(f"📍 {similar['location']}")
                                        with col_b:
                                            st.metric("Similarity", f"{similar['similarity_score']:.1f}%")
                    
                    st.divider()
    
    with tab3:
        st.header("📊 Demo Intelligence Insights")
        
        stats = demo.get_demo_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏢 Company Distribution")
            if stats.get('top_companies'):
                for i, company in enumerate(stats['top_companies'][:8], 1):
                    st.write(f"**{i}. {company}**")
        
        with col2:
            st.subheader("🌍 Geographic Coverage")
            if stats.get('top_locations'):
                for i, location in enumerate(stats['top_locations'], 1):
                    st.write(f"**{i}. {location}**")
        
        st.subheader("📈 Algorithm Performance")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Similarity Relationships", f"{stats['total_relationships']:,}")
        with col2:
            st.metric("Average Similarity Score", f"{stats['average_similarity']:.1f}%")
        with col3:
            st.metric("Professional Coverage", f"{stats['unique_source_profiles']:,}")
        
        st.info("🎯 **Algorithm Validation Results:** 86.2% same-company accuracy with 77.8% discrimination score - significantly outperforming random matching")
    
    # Footer with conversion messaging
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **⚠️ Demo Limitations:**
        - Sample of professionals from our global database
        - Full platform: **475M professionals** across **244 countries**
        - Complete career histories available
        - **1.8B+ professional relationships** mapped with AI similarity scoring
        """)
    
    with col2:
        st.markdown("""
        **🚀 Ready for Full Access?**
        
        **[Schedule Demo Call →](mailto:hello@nuvel.ai)**
        
        Get unlimited access to our complete similarity engine:
        - Real-time professional similarity matching
        - Complete contact information and LinkedIn profiles
        - Advanced search filters and bulk export
        - API integration for your recruiting tools
        """)
    
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p><strong>Nuvel.ai Professional Similarity Engine</strong></p>
    <p>🌐 <em>Powered by 1.8+ billion professional relationships with validated AI similarity scoring</em></p>
    <p><strong>This demo represents a curated sample designed to showcase our algorithm's precision without providing full access to our proprietary database</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
