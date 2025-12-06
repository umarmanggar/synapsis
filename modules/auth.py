import streamlit as st
import pandas as pd
import os

def check_login(username, password, users_df):
    """
    Validate user credentials against the users dataframe.
    Returns (is_valid, role) tuple.
    """
    user = users_df[
        (users_df['username'] == username) & 
        (users_df['password'] == password)
    ]
    
    if not user.empty:
        return True, user.iloc[0]['role']
    return False, None

def render_login_page():
    """
    Render the login interface.
    """
    st.title("🎓 Synapsis Login")
    st.markdown("### Research Proposal Management System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    try:
                        # Load users data
                        users_df = pd.read_csv('data/users.csv')
                        is_valid, role = check_login(username, password, users_df)
                        
                        if is_valid:
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.username = username
                            st.success(f"Welcome, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    except FileNotFoundError:
                        st.error("Users database not found. Please ensure data/users.csv exists.")
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
                    st.warning("Please enter both username and password")
        
        with col_btn2:
            if st.button("Reset", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        # st.info("**Demo Credentials:**\n- Admin: `admin` / `admin123`\n- Student: `student` / `student123`")