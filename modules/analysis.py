import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

def perform_clustering_and_pca(proposals_df, n_clusters=5):
    """
    Perform K-Means clustering and PCA on proposal embeddings.
    Returns the proposals dataframe with cluster assignments and a PCA dataframe.
    """
    # Extract embeddings as numpy array
    embeddings = np.array(proposals_df['embedding'].tolist())
    
    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(embeddings)
    proposals_df['cluster'] = clusters
    
    # Perform PCA for visualization (2D)
    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(embeddings)
    
    # Create PCA dataframe
    pca_df = pd.DataFrame({
        'PC1': pca_result[:, 0],
        'PC2': pca_result[:, 1],
        'cluster': clusters,
        'title': proposals_df['title'].values if 'title' in proposals_df.columns else [f"Proposal {i}" for i in range(len(proposals_df))]
    })
    
    # Add explained variance info
    pca_df.attrs['explained_variance'] = pca.explained_variance_ratio_
    
    return proposals_df, pca_df

def get_cluster_statistics(proposals_df):
    """
    Calculate statistics about clusters.
    """
    cluster_counts = proposals_df['cluster'].value_counts().sort_index()
    cluster_stats = pd.DataFrame({
        'Cluster': cluster_counts.index,
        'Count': cluster_counts.values,
        'Percentage': (cluster_counts.values / len(proposals_df) * 100).round(2)
    })
    return cluster_stats

def get_topic_distribution(proposals_df):
    """
    Get distribution of topics/categories in proposals.
    """
    if 'topic' in proposals_df.columns:
        topic_counts = proposals_df['topic'].value_counts()
        return topic_counts
    elif 'category' in proposals_df.columns:
        topic_counts = proposals_df['category'].value_counts()
        return topic_counts
    else:
        # Fallback to cluster distribution
        return proposals_df['cluster'].value_counts()

def get_lecturer_expertise(lecturers_df):
    """
    Get distribution of lecturer expertise areas.
    """
    if 'expertise' in lecturers_df.columns:
        # Handle comma-separated expertise
        all_expertise = []
        for exp in lecturers_df['expertise']:
            if pd.notna(exp) and exp != '':
                all_expertise.extend([e.strip() for e in str(exp).split(',')])
        
        expertise_counts = pd.Series(all_expertise).value_counts()
        return expertise_counts
    else:
        return pd.Series(dtype=int)

def get_submission_trend(proposals_df):
    """
    Get submission trend over time.
    """
    if 'submission_date' in proposals_df.columns:
        proposals_df['submission_date'] = pd.to_datetime(
            proposals_df['submission_date'], 
            errors='coerce'
        )
        trend = proposals_df.groupby(
            proposals_df['submission_date'].dt.to_period('M')
        ).size()
        return trend
    elif 'date' in proposals_df.columns:
        proposals_df['date'] = pd.to_datetime(
            proposals_df['date'], 
            errors='coerce'
        )
        trend = proposals_df.groupby(
            proposals_df['date'].dt.to_period('M')
        ).size()
        return trend
    else:
        return pd.Series(dtype=int)