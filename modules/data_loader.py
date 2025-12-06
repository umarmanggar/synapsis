import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Global model instance (loaded once)
_embedding_model = None

def get_embedding_model():
    """
    Lazy load the sentence transformer model.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model

def load_csv(filepath):
    """
    Load a CSV file with error handling.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)

def load_all_data():
    """
    Load all CSV files from the data folder.
    Returns a dictionary with dataframes.
    """
    data = {
        'lecturers': load_csv('data/lecturers.csv'),
        'proposals': load_csv('data/proposals.csv'),
        'publications': load_csv('data/publications.csv'),
        'users': load_csv('data/users.csv')
    }
    
    # Basic data cleaning
    for key in data:
        # Strip whitespace from column names
        data[key].columns = data[key].columns.str.strip()
        # Handle potential undefined values
        data[key] = data[key].fillna('')
    
    return data

def generate_embeddings(texts):
    """
    Generate embeddings for a list of texts.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings

def ensure_embeddings(proposals_df):
    """
    Ensure proposal embeddings are generated.
    Combines title and abstract for embedding generation.
    """
    # Create combined text for embedding
    if 'title' in proposals_df.columns and 'abstract' in proposals_df.columns:
        proposals_df['combined_text'] = (
            proposals_df['title'].astype(str) + " " + 
            proposals_df['abstract'].astype(str)
        )
    elif 'title' in proposals_df.columns:
        proposals_df['combined_text'] = proposals_df['title'].astype(str)
    else:
        raise ValueError("Proposals dataframe must contain 'title' column")
    
    # Generate embeddings
    embeddings = generate_embeddings(proposals_df['combined_text'].tolist())
    
    # Store embeddings as a new column (as lists)
    proposals_df['embedding'] = list(embeddings)
    
    return proposals_df