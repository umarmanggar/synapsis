import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.analysis import (
    get_cluster_statistics,
    get_topic_distribution,
    get_lecturer_expertise,
    get_submission_trend
)

def render_header(role):
    """
    Render the application header with logout button.
    """
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("🎓 Synapsis - Research Proposal Management")
        st.markdown(f"**Role:** {role.title()} | **User:** {st.session_state.username}")
    
    with col2:
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()

def render_metrics(data):
    """
    Render key metrics cards.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(data['users']))
    
    with col2:
        st.metric("Total Lecturers", len(data['lecturers']))
    
    with col3:
        st.metric("Total Proposals", len(data['proposals']))
    
    with col4:
        st.metric("Total Publications", len(data['publications']))

def render_cluster_scatter(pca_df):
    """
    Render the PCA cluster scatter plot.
    """
    st.subheader("📊 Proposal Clusters (K-Means + PCA)")
    
    fig = px.scatter(
        pca_df,
        x='PC1',
        y='PC2',
        color='cluster',
        hover_data=['title'],
        title='Research Proposal Clusters (5 Clusters)',
        labels={'cluster': 'Cluster ID'},
        color_continuous_scale='Viridis'
    )
    
    fig.update_traces(marker=dict(size=10, opacity=0.7))
    fig.update_layout(
        height=500,
        xaxis_title='Principal Component 1',
        yaxis_title='Principal Component 2'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show explained variance
    if 'explained_variance' in pca_df.attrs:
        var_ratio = pca_df.attrs['explained_variance']
        st.info(
            f"**PCA Explained Variance:** PC1: {var_ratio[0]:.2%}, "
            f"PC2: {var_ratio[1]:.2%}, Total: {sum(var_ratio):.2%}"
        )

def render_topic_distribution(proposals_df):
    """
    Render topic/category distribution chart.
    """
    st.subheader("📚 Topic Distribution")
    
    topic_counts = get_topic_distribution(proposals_df)
    
    if not topic_counts.empty:
        fig = px.bar(
            x=topic_counts.index,
            y=topic_counts.values,
            labels={'x': 'Topic', 'y': 'Number of Proposals'},
            title='Proposals by Topic/Category',
            color=topic_counts.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No topic information available in the dataset.")

def render_lecturer_expertise(lecturers_df):
    """
    Render lecturer expertise distribution.
    """
    st.subheader("👨‍🏫 Lecturer Expertise Areas")
    
    expertise_counts = get_lecturer_expertise(lecturers_df)
    
    if not expertise_counts.empty:
        # Take top 10 for readability
        top_expertise = expertise_counts.head(10)
        
        fig = px.pie(
            values=top_expertise.values,
            names=top_expertise.index,
            title='Top 10 Expertise Areas',
            hole=0.3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expertise information available in the dataset.")

def render_submission_trend(proposals_df):
    """
    Render submission trend over time.
    """
    st.subheader("📈 Proposal Submission Trend")
    
    trend = get_submission_trend(proposals_df)
    
    if not trend.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[str(period) for period in trend.index],
            y=trend.values,
            mode='lines+markers',
            name='Submissions',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Monthly Proposal Submissions',
            xaxis_title='Month',
            yaxis_title='Number of Submissions',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No submission date information available in the dataset.")

def render_cluster_table(proposals_df):
    """
    Render cluster statistics table.
    """
    st.subheader("🔢 Cluster Statistics")
    
    cluster_stats = get_cluster_statistics(proposals_df)
    st.dataframe(cluster_stats, use_container_width=True, hide_index=True)

def render_admin_dashboard(data):
    """
    Render the complete admin dashboard.
    """
    render_header('admin')
    st.markdown("---")
    
    # Metrics section
    render_metrics(data)
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        render_cluster_scatter(data['pca_df'])
        render_topic_distribution(data['proposals'])
    
    with col2:
        render_cluster_table(data['proposals'])
        render_lecturer_expertise(data['lecturers'])
    
    # Full width chart
    render_submission_trend(data['proposals'])
    
    # Data tables in expander
    with st.expander("📋 View Raw Data"):
        tab1, tab2, tab3, tab4 = st.tabs(["Proposals", "Lecturers", "Publications", "Users"])
        
        with tab1:
            display_df = data['proposals'].drop(columns=['embedding', 'combined_text'], errors='ignore')
            st.dataframe(display_df, use_container_width=True)
        
        with tab2:
            st.dataframe(data['lecturers'], use_container_width=True)
        
        with tab3:
            st.dataframe(data['publications'], use_container_width=True)
        
        with tab4:
            display_users = data['users'].drop(columns=['password'], errors='ignore')
            st.dataframe(display_users, use_container_width=True)

def render_student_view(data):
    """
    Render the simplified student view.
    """
    render_header('student')
    st.markdown("---")
    
    # Simple metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Available Lecturers", len(data['lecturers']))
    
    with col2:
        st.metric("Research Topics", data['proposals']['cluster'].nunique())
    
    with col3:
        st.metric("Publications", len(data['publications']))
    
    st.markdown("---")
    
    # Simplified visualizations
    render_cluster_scatter(data['pca_df'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_topic_distribution(data['proposals'])
    
    with col2:
        render_lecturer_expertise(data['lecturers'])
    
    # Simple data view
    st.subheader("📚 Recent Proposals")
    display_df = data['proposals'][['title', 'cluster']].head(10) if 'title' in data['proposals'].columns else data['proposals'].head(10)
    st.dataframe(display_df, use_container_width=True, hide_index=True)