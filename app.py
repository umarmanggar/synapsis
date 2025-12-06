import streamlit as st
from modules.auth import check_login, render_login_page
from modules.data_loader import load_all_data, ensure_embeddings
from modules.analysis import perform_clustering_and_pca
from modules.ui_components import render_admin_dashboard, render_student_view

# Page configuration
st.set_page_config(
    page_title="Synapsis - Research Proposal Management",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
    
    # Authentication check
    if not st.session_state.logged_in:
        render_login_page()
        return
    
    # Load data
    try:
        data = load_all_data()
        
        # Ensure embeddings exist
        data['proposals'] = ensure_embeddings(data['proposals'])
        
        # Perform clustering and PCA
        clustered_data, pca_df = perform_clustering_and_pca(data['proposals'])
        data['proposals'] = clustered_data
        data['pca_df'] = pca_df
        
        # Render appropriate view based on role
        if st.session_state.user_role == 'admin':
            render_admin_dashboard(data)
        else:
            render_student_view(data)
            
    except Exception as e:
        st.error(f"Error loading application: {str(e)}")
        st.error("Please ensure all CSV files are present in the data/ folder.")

if __name__ == "__main__":
    main()