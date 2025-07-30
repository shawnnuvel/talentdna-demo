import streamlit as st
import pandas as pd

class ProfessionalSimilarityDemo:
    def __init__(self, data_file: str = 'similarity_data_sample_demo_ready.csv'):
        self.data = self.load_data(data_file)

    def load_data(self, file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                st.error("Demo dataset is empty. Run your data prep script first.")
            return df
        except FileNotFoundError:
            st.error("Demo dataset not found. Run your data prep script first.")
            return pd.DataFrame()

    def search_similar_professionals(self, query: str, max_results: int = 15) -> list:
        """Return the top matches for a free-text query."""
        if self.data.empty:
            return []

        query_words = [w for w in query.lower().split() if len(w) > 2]
        results = []

        for _, row in self.data.iterrows():
            # Combine all key fields into a single searchable string
            text = " ".join([
                str(row['source_name']), str(row['source_title']), str(row['source_company']),
                str(row['similar_name']), str(row['similar_title']), str(row['similar_company'])
            ]).lower()

            # Simple word-matching relevance
            score = sum(1 for w in query_words if w in text)
            if score > 0:
                results.append({
                    'name': row['similar_name'],
                    'title': row['similar_title'],
                    'company': row['similar_company'],
                    'location': row.get('similar_location', 'Not specified'),
                    'similarity': f"{row['similarity_score']:.1f}%",
                    'source': f"{row['source_name']} ({row['source_title']})",
                    'match_score': score
                })

        # Sort by relevance (match_score) then by similarity%
        results.sort(key=lambda x: (-x['match_score'], -float(x['similarity'].strip('%'))))
        return results[:max_results]


def main():
    st.set_page_config(page_title="Nuvel.ai Demo", layout="wide")
    st.title("🎯 Nuvel.ai Professional Similarity Search (Demo)")
    st.markdown("**Instantly find professionals similar to your best candidates**")

    demo = ProfessionalSimilarityDemo()

    # ——— Main Search Box ———
    st.header("🔍 Search Similar Professionals")
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Enter role, company or name:",
            placeholder="e.g. software engineer at google"
        )
    with col2:
        max_results = st.selectbox("Results to show:", [10, 15, 20, 25], index=1)

    if st.button("🔍 Find Similar Professionals"):
        if not search_query:
            st.warning("Please enter a search term above.")
        else:
            with st.spinner("Searching..."):
                matches = demo.search_similar_professionals(search_query, max_results)
            if matches:
                st.success(f"✅ Found {len(matches)} similar professionals:")
                for i, m in enumerate(matches, 1):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.markdown(f"**#{i} {m['name']}**")
                        st.markdown(f"*{m['title']}* at **{m['company']}**")
                        st.markdown(f"📍 {m['location']}")
                        st.caption(f"Similar to {m['source']}")
                    with cols[1]:
                        st.metric("Match", m['similarity'])
                    if i < len(matches):
                        st.divider()
            else:
                st.error("No matches found. Try different keywords like ‘engineer’, ‘manager’, or a company name.")

    # ——— Quick Demo Buttons ———
    st.markdown("### 🚀 Try These Demo Searches")
    test_searches = [
        "software engineer google",
        "product manager",
        "data scientist",
        "director",
        "sales manager"
    ]
    cols = st.columns(len(test_searches))
    for idx, term in enumerate(test_searches):
        with cols[idx]:
            if st.button(term, key=f"demo_{idx}"):
                with st.spinner(f"Searching for “{term}”..."):
                    matches = demo.search_similar_professionals(term, max_results)
                if matches:
                    st.success(f"✅ {len(matches)} results for “{term}”")
                    for j, m in enumerate(matches, 1):
                        st.markdown(f"- **{m['name']}** | {m['title']} @ {m['company']} | {m['similarity']}")
                else:
                    st.warning(f"No results for “{term}”")

    st.markdown("---")
    st.markdown("🌐 mapped based on 1.8+ billion relationships")

if __name__ == "__main__":
    main()
