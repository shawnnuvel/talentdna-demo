import streamlit as st
import pandas as pd

class ProfessionalSimilarityDemo:
    def __init__(self, data_file: str = 'similarity_data_sample_demo_ready.csv'):
        self.data = self.load_data(data_file)
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            st.error("Demo dataset not found. Please run the data preparation script first.")
            return pd.DataFrame()
    
    def search_similar_professionals(self, query: str, max_results: int = 15) -> list:
        """Improved search that actually finds relevant results"""
        if self.data.empty:
            return []
        
        query_lower = query.lower()
        query_words = [word.strip() for word in query_lower.split() if len(word.strip()) > 2]
        
        # Search across all relevant fields
        matches = []
        for _, row in self.data.iterrows():
            search_text = f"{row['source_name']} {row['source_title']} {row['source_company']} {row['similar_name']} {row['similar_title']} {row['similar_company']}".lower()
            
            # Count matching words
            match_score = sum(1 for word in query_words if word in search_text)
            
            if match_score > 0:
                matches.append({
                    'name': row['similar_name'],
                    'title': row['similar_title'],
                    'company': row['similar_company'],
                    'location': row['similar_location'],
                    'similarity': f"{row['similarity_score']:.1f}%",
                    'source_match': f"Similar to {row['source_name']} ({row['source_title']})",
                    'match_score': match_score
                })
        
        # Sort by match score and similarity
        matches.sort(key=lambda x: (-x['match_score'], -float(x['similarity'].replace('%', ''))))
        return matches[:max_results]

def main():
    st.set_page_config(page_title="Nuvel.ai Demo", layout="wide")
    
    demo = ProfessionalSimilarityDemo()
    
    st.title("🎯 Nuvel.ai Professional Similarity Search")
    st.markdown("**Find professionals similar to your best candidates - Demo Dataset: 1,000+ Professional Relationships**")
    
    # Main search
    st.header("🔍 Search Similar Professionals")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search for professionals:",
            placeholder="software engineer at google, product manager, data scientist",
            key="main_search"
        )
    
    with col2:
        max_results = st.selectbox("Results:", [10, 15, 20, 25], index=1)
    
    if st.button("🔍 Find Similar Professionals", type="primary"):
        if search_query:
            with st.spinner("Searching professional database..."):
                results = demo.search_similar_professionals(search_query, max_results)
                
                if results:
                    st.success(f"✅ Found **{len(results)}** similar professionals:")
                    
                    for i, result in enumerate(results, 1):
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**#{i} {result['name']}**")
                                st.markdown(f"*{result['title']}*")
                                st.markdown(f"🏢 {result['company']}")
                                st.markdown(f"📍 {result['location']}")
                                st.caption(result['source_match'])
                            with col2:
                                st.metric("Match", result['similarity'])
                            st.divider()
                else:
                    st.warning("No matches found. Try different keywords like 'engineer', 'manager', or company names.")
    
    # Quick test searches
    st.markdown("### 🚀 Try These Demo Searches:")
    test_searches = ["software engineer google", "product manager", "data scientist", "director", "sales manager"]
    
    cols = st.columns(len(test_searches))
    for i, search_term in enumerate(test_searches):
        with cols[i]:
            if st.button(f"🔍 {search_term}", key=f"test_{i}"):
                st.session_state.main_search = search_term
                st.rerun()

if __name__ == "__main__":
    main()
