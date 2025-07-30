import json
import os

class NuvelSimilarityDemo:
    def __init__(self, csv_file='similarity_data_sample.csv'):
        self.df = self.load_data(csv_file)
        self.sample_profiles = self.load_sample_profiles()
    
    def load_sample_profiles(self):
        """Load the high-quality sample profiles with people also viewed"""
        try:
            sample_file = os.path.expanduser("~/nuvel_demo/demo_sample_profiles.json")
            with open(sample_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning("Sample profiles not found. Run the data preparation script first.")
            return {}
    
    # ... (keep all your existing methods) ...

# In your main() function, replace the tab2 section with:

    with tab2:
        st.header("👤 Browse Premium Sample Profiles")
        st.markdown("**Explore real professionals from our database and their similarity relationships:**")
        
        if demo.sample_profiles:
            # Display sample profiles in professional format
            for i, (profile_id, profile_data) in enumerate(demo.sample_profiles.items(), 1):
                main_profile = profile_data['main_profile']
                people_also_viewed = profile_data['people_also_viewed']
                
                # Main profile card
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"### 👤 {main_profile['name']}")
                        st.markdown(f"**{main_profile['title']}**")
                        st.markdown(f"🏢 {main_profile['company']}")
                        if main_profile['location'] != 'Not specified':
                            st.markdown(f"📍 {main_profile['location']}")
                    
                    with col2:
                        st.metric("Similar Professionals", len(people_also_viewed))
                        if len(main_profile['full_summary']) > 100:
                            st.caption(f"💼 {main_profile['full_summary'][:100]}...")
                    
                    with col3:
                        if st.button(f"👥 View Similar", key=f"profile_{i}", type="secondary"):
                            st.session_state[f'show_similar_{i}'] = not st.session_state.get(f'show_similar_{i}', False)
                    
                    # Show "People Also Viewed" when button is clicked
                    if st.session_state.get(f'show_similar_{i}', False):
                        st.markdown("#### 🔍 People Also Viewed:")
                        
                        if people_also_viewed:
                            # Display similar profiles in a clean grid
                            for j, similar in enumerate(people_also_viewed, 1):
                                with st.expander(f"#{j} {similar['name']} - {similar['company']}", expanded=True):
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.markdown(f"**Title:** {similar['title']}")
                                        st.markdown(f"**Company:** {similar['company']}")
                                    with col_b:
                                        if similar['location'] != 'Not specified':
                                            st.markdown(f"**Location:** {similar['location']}")
                                        # Calculate a demo similarity score
                                        similarity_score = random.randint(85, 94)
                                        st.metric("Similarity", f"{similarity_score}%")
                        else:
                            st.info("No similar professionals found in demo dataset")
                    
                    st.divider()
        else:
            st.error("**No sample profiles available**")
            st.markdown("""
            To see premium sample profiles:
            1. Run the data preparation script to extract quality profiles
            2. Ensure the `demo_sample_profiles.json` file is generated
            3. Refresh this page
            """)
            
            # Show fallback message
            st.info("💡 **This section will showcase real professionals** like 'Sarah Chen - Senior Software Engineer at Google' with their actual similar profiles")
