"""
AI-Powered Shopping Tool - Search and Recommendations
----------------------------------------------------------------------------- 
Tracks version history for the product search and recommendation functionality.
----------------------------------------------------------------------------- 

Version History:
---------------
[please please remember to add your name, date, and version number if you change anything, even when using Github  - thanks, JB]
---------------

100%, 12/12


v0.11 - 9/28/24 - Jakub Bartkowiak
    - Initial implementation for basic search functionality

v0.2-0.3 - 10/7-10/8/24 - Jakub Bartkowiak
    - Added spell check integration
    - Migrated to MySQL database

v0.4 - 10/31/24 - Jakub Bartkowiak
    - Introduced semantic search with 300d vectors
    - Improved result reranking

v0.5-0.6 - 11/8-11/9/24 - Jakub Bartkowiak
    - Added similarity-based recommendations
    - Enhanced product embedding storage

v0.7-0.8 - 11/11-11/12/24 - Jakub Bartkowiak
    - Improved MySQL consistency for better data reliability
    - Added advanced filtering options (e.g., price, rating, brand)

v0.9-1.0 - 11/16-11/17/24 - Jakub Bartkowiak
    - Added support for dynamic embeddings
    - Created extensive [validation.py] user input refinement and parsing for both complex/simple queries
    - Enhanced similarity calculations

v1.1-1.2 - 11/18/24 - Jakub Bartkowiak
    - Added price handling in search
    - Updated product filtering

v1.1-1.3 - 11/22/24 - Dominc Digiacomo
    - Added the get_trending_products function
"""

import os
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from models import Product, ProductEmbedding, Activity
from validation import validate_input
from collections import defaultdict
from dotenv import load_dotenv
from itertools import groupby
from operator import attrgetter

# Load environment variables
load_dotenv()

# Get MySQL configuration from environment variables
mysql_user = os.getenv('MYSQL_USER', 'dominic')
mysql_password = os.getenv('MYSQL_PASSWORD', '1234')
mysql_host = os.getenv('MYSQL_HOST', 'localhost')
mysql_db = os.getenv('MYSQL_DB', 'ASCdb')

# Construct DATABASE_URI from MySQL environment variables
DATABASE_URI = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def generate_query_embedding(query, dimensions=50):  # [SEARC-002-082]
    """Generate embedding vector for search query"""
    np.random.seed(hash(query) % 2**32)
    vector = np.random.rand(dimensions)
    return vector / np.linalg.norm(vector)

def calculate_similarity_scores(query, embeddings, products):  # [SEARC-003-090]
    """
    Calculate similarity scores for embeddings of the same dimension.
    Returns products sorted by similarity score.
    """
    if not embeddings:
        return []
        
    # Get embedding dimension
    embedding_size = embeddings[0].dimensions
    query_vector = generate_query_embedding(query, embedding_size)
    
    # Convert embeddings to numpy arrays
    product_vectors = np.array([np.frombuffer(e.embedding) for e in embeddings])
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity([query_vector], product_vectors)[0]
    
    # Create product-score pairs
    product_scores = []
    for i, embedding in enumerate(embeddings):
        product = next((p for p in products if p.product_id == embedding.product_id), None)
        if product:
            score = (
                0.6 * similarity_scores[i] +
                0.2 * (product.popularity / 1000) +  # Normalize popularity to 0-1
                0.2 * (product.ratings / 5)  # Normalize ratings to 0-1
            )
            product_scores.append((product, score))
    
    return product_scores

def search_products(query, min_price=None, max_price=None, brand=None, min_rating=None, simple_mode=True):  # [SEARC-007-125]
    """
    Search products using semantic similarity and filters.
    Handles both 50-dimensional and 300-dimensional embeddings.
    """
    # Use simple validation mode for testing
    _, product_array = validate_input(query, 0, session.bind, simple_mode=simple_mode)  # [VALID-001-040]
    search_terms = [item[0] for item in product_array if item[2] == 0]
    
    if not search_terms:
        return []
    
    # Query products with all filters  # [SEARC-008-145]
    products_query = session.query(Product)
    
    # Apply filters if provided
    if min_price is not None:
        products_query = products_query.filter(Product.price >= min_price)
    if max_price is not None:
        products_query = products_query.filter(Product.price <= max_price)
    if brand:
        products_query = products_query.filter(Product.brand.ilike(f"%{brand}%"))
    if min_rating is not None:
        products_query = products_query.filter(Product.ratings >= min_rating)
        
    # Execute query to get all matching products
    all_products = products_query.all()
    
    # Filter products by search terms
    matched_products = [
        product for product in all_products
        if any(term.lower() in (
            (product.title or '') + ' ' + 
            (product.tags or '') + ' ' + 
            (product.category or '') + ' ' + 
            (product.description or '')
        ).lower() for term in search_terms)
    ]
    
    if not matched_products:
        return []
    
    # Get embeddings for matched products  # [SEARC-004-185]
    product_ids = [p.product_id for p in matched_products]
    all_embeddings = session.query(ProductEmbedding).filter(
        ProductEmbedding.product_id.in_(product_ids)
    ).all()
    
    # If no embeddings, return basic search results
    if not all_embeddings:
        return [
            {
                'product_id': product.product_id,
                'title': product.title,
                'category': product.category,
                'price': product.price,
                'was_price': product.was_price,
                'discount': product.discount,
                'similarity_score': 1.0  # Default score for basic search
            }
            for product in matched_products[:15]
        ]
    
    # Group embeddings by dimension  # [SEARC-010-250]
    all_embeddings.sort(key=attrgetter('dimensions'))
    dimension_groups = groupby(all_embeddings, key=attrgetter('dimensions'))
    
    # Calculate scores for each dimension group
    all_product_scores = []
    for dimension, embeddings in dimension_groups:
        embeddings_list = list(embeddings)
        product_scores = calculate_similarity_scores(query, embeddings_list, matched_products)
        all_product_scores.extend(product_scores)
    
    # Sort all products by score  # [SEARC-009-275]
    all_product_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top results with price information
    return [
        {
            'product_id': product.product_id,
            'title': product.title,
            'category': product.category,
            'price': product.price,
            'was_price': product.was_price,
            'discount': product.discount,
            'similarity_score': round(score, 3)
        }
        for product, score in all_product_scores[:15]
    ]

def suggest_products_for_item(item_id, user_id=None):  # [SEARC-005-310]
    """Get product recommendations based on item similarity"""
    current_embedding = session.query(ProductEmbedding).filter_by(
        product_id=item_id
    ).first()
    if not current_embedding:
        return []

    current_vector = np.frombuffer(current_embedding.embedding)
    other_embeddings = session.query(ProductEmbedding).filter(
        ProductEmbedding.product_id != item_id,
        ProductEmbedding.dimensions == current_embedding.dimensions  # Match dimensions
    ).all()
    
    if not other_embeddings:
        return []
        
    other_vectors = np.array([np.frombuffer(e.embedding) for e in other_embeddings])
    other_product_ids = [e.product_id for e in other_embeddings]
    
    content_scores = cosine_similarity([current_vector], other_vectors)[0]
    
    if user_id:
        user_vector = get_user_activity_vector(user_id)
        similar_users = get_similar_users(user_id)
        
        collab_scores = np.zeros_like(content_scores)
        for other_id, user_similarity in similar_users[:5]:
            other_vector = get_user_activity_vector(other_id)
            for i, pid in enumerate(other_product_ids):
                collab_scores[i] += other_vector.get(pid, 0) * user_similarity
        
        if collab_scores.max() > 0:
            collab_scores = collab_scores / collab_scores.max()
        
        final_scores = 0.6 * content_scores + 0.4 * collab_scores
    else:
        final_scores = content_scores
    
    top_indices = np.argsort(final_scores)[::-1][:5]
    recommendations = []
    
    for i in top_indices:
        product = session.query(Product).get(other_product_ids[i])
        if product:
            recommendations.append({
                'product_id': product.product_id,
                'title': product.title,
                'category': product.category,
                'price': product.price,
                'was_price': product.was_price,
                'discount': product.discount,
                'similarity_score': round(float(final_scores[i]), 3)
            })
    
    return recommendations

def get_user_activity_vector(user_id, time_window_days=30):  # [SEARC-006-380]
    """Get user's activity vector with time decay"""
    cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
    
    activities = session.query(Activity).filter(
        Activity.user_id == user_id,
        Activity.timestamp >= cutoff_date
    ).all()
    
    activity_weights = defaultdict(float)
    for activity in activities:
        if activity.product_id:
            days_old = (datetime.utcnow() - activity.timestamp).days
            time_decay = 1.0 / (1.0 + days_old)
            weight = 1.0  # Simplified weight
            activity_weights[activity.product_id] += weight * time_decay
    
    return activity_weights

def get_similar_users(user_id, min_similarity=0.2):  # [SEARC-005-310]
    """Find users with similar behavior patterns"""
    target_vector = get_user_activity_vector(user_id)
    all_users = session.query(Activity.user_id).distinct().all()
    similar_users = []
    
    for other_id, in all_users:
        if other_id != user_id:
            other_vector = get_user_activity_vector(other_id)
            common_products = set(target_vector.keys()) & set(other_vector.keys())
            
            if common_products:
                similarity = sum(
                    target_vector[pid] * other_vector[pid] 
                    for pid in common_products
                ) / (
                    sum(target_vector[pid]**2 for pid in target_vector) ** 0.5 *
                    sum(other_vector[pid]**2 for pid in other_vector) ** 0.5
                )
                
                if similarity >= min_similarity:
                    similar_users.append((other_id, similarity))
    
    return sorted(similar_users, key=lambda x: x[1], reverse=True)

def get_trending_products(limit=10):
    """Fetch trending products based on recent activity or popularity"""
    # Example: Retrieve products based on recent activity or highest ratings
    trending_products = session.query(Product).order_by(Product.popularity.desc()).limit(limit).all()
    
    # Return a list of trending products with details
    return [{
        'product_id': product.product_id,
        'title': product.title,
        'category': product.category,
        'price': product.price,
        'was_price': product.was_price,
        'discount': product.discount,
        'popularity': product.popularity,
        'similarity_score': 1.0  # Can be calculated differently if needed
    } for product in trending_products]
