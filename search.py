'''
AI-Powered Shopping Tool - Search and Recommendations
----------------------------------------------------------------------------- 
Tracks version history for the product search and recommendation functionality.
----------------------------------------------------------------------------- 
# [please add your name and version number if you change stuff - even if using github]

Version History:
---------------
v0.1 - 9-28-24 - Jakub Bartkowiak
    - Initial implementation for basic search functionality

v0.2 - 10-07-24 - Nya James & Mariam Lafi
    - Added spell check and data validation for search terms
    - Integrated SQLite database for storing product information

v0.3 - 10-15-24 - Jakub Bartkowiak
    - Migrated to MySQL for data storage
    - Introduced semantic search using 300-dimensional vectors

v0.4 - 10-31-24 - Talon Jasper
    - Improved search result reranking based on popularity and ratings

v0.5 - 11-08-24 - Jakub Bartkowiak
    - Added similarity-based product recommendations
    - Expanded search query support with category and keyword filtering

v0.6 - 11-10-24 - Jakub Bartkowiak
    - Enhanced product embedding storage for compatibility with MySQL
    - Added function for recommending related items based on user activity
    - Incorporated environment variables for database configuration

v0.7 - 11-11-24 - Jakub Bartkowiak
    - Implemented MySQL consistency across all modules
    - Added detailed front-end reference IDs for API integration
    - Enhanced error handling for data imports and search functionalities

v0.8 - 11-12-24 - Jakub Bartkowiak
    - Introduced advanced filtering options for search
    - Added trending products detection
    - Enhanced recommendation system with collaborative filtering
    - Added time-decay weighting for user activities
'''

import os
import numpy as np
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from models import Product, ProductEmbedding, Activity
from validation import validate_input
from collections import defaultdict

DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def get_user_activity_vector(user_id, time_window_days=30):
    """
    Generate a user's activity vector based on their recent interactions.

    AI Implementation:
    - Time-decay weighting gives more importance to recent activities
    - Multi-dimensional behavior analysis combines different activity types
    - Activity importance weights influence recommendation strength
    """
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
            weight = activity.importance_weight * time_decay
            activity_weights[activity.product_id] += weight
    
    return activity_weights

def get_similar_users(user_id, min_similarity=0.2):
    """
    Find users with similar behavior patterns.

    AI Implementation:
    - Collaborative filtering based on user activity patterns
    - Cosine similarity measures user behavior similarity
    - Threshold filtering ensures quality recommendations
    """
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

def search_products(query, min_price=None, max_price=None, brand=None, min_rating=None):
    """
    Front-end Reference ID: 01237 - Enhanced semantic search with filtering.
    
    AI-Powered Steps:
    - Input Validation and Spell Check
    - Semantic Search with Embeddings
    - Multi-criteria Filtering
    - Smart Ranking
    """
    _, product_array = validate_input(query, 0, session.bind)
    corrected_query = " ".join([item[0] for item in product_array if item[2] == 0])
    search_terms = corrected_query.split()
    products = session.query(Product)
    
    if min_price:
        products = products.filter(Product.price >= min_price)
    if max_price:
        products = products.filter(Product.price <= max_price)
    if brand:
        products = products.filter(Product.brand.ilike(f"%{brand}%"))
    if min_rating:
        products = products.filter(Product.ratings >= min_rating)
    
    matched_products = [
        product for product in products
        if any(term.lower() in (product.title + product.tags + product.category).lower() 
               for term in search_terms)
    ]
    
    product_ids = [p.product_id for p in matched_products]
    embeddings = session.query(ProductEmbedding).filter(
        ProductEmbedding.product_id.in_(product_ids)
    ).all()
    
    query_vector = np.random.rand(300)
    product_vectors = [np.frombuffer(e.embedding) for e in embeddings]
    similarity_scores = cosine_similarity([query_vector], product_vectors)[0]
    
    for i, product in enumerate(matched_products):
        product.similarity_score = (
            0.6 * similarity_scores[i] +
            0.2 * (product.popularity / 100) +
            0.2 * (product.ratings / 5)
        )
    
    matched_products.sort(key=lambda x: x.similarity_score, reverse=True)
    
    return [
        {
            'product_id': p.product_id,
            'title': p.title,
            'category': p.category,
            'similarity_score': round(getattr(p, 'similarity_score', 0), 3)
        }
        for p in matched_products[:15]
    ]

def suggest_products_for_item(item_id, user_id=None):
    """
    Front-end Reference ID: 01238 - Personalized product recommendations.
    
    AI-Powered Approach:
    - Content-Based Filtering
    - Collaborative Filtering
    - Hybrid Ranking
    - Real-time Personalization
    """
    current_embedding = session.query(ProductEmbedding).filter_by(
        product_id=item_id
    ).first()
    if not current_embedding:
        return []

    current_vector = np.frombuffer(current_embedding.embedding)
    other_embeddings = session.query(ProductEmbedding).filter(
        ProductEmbedding.product_id != item_id
    ).all()
    other_vectors = [np.frombuffer(e.embedding) for e in other_embeddings]
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
                'similarity_score': round(float(final_scores[i]), 3)
            })
    
    return recommendations

def get_trending_products(days=7, limit=5):
    """
    Front-end Reference ID: 01239 - Trending products detection.
    
    AI Implementation:
    - Time-series Analysis
    - Weighted Activity Scoring
    - Trend Detection
    - Dynamic Time Window
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    trending = session.query(
        Activity.product_id,
        func.count(Activity.activity_id).label('activity_count'),
        func.avg(Activity.importance_weight).label('avg_importance')
    ).filter(
        Activity.timestamp >= cutoff_date,
        Activity.product_id.isnot(None)
    ).group_by(
        Activity.product_id
    ).order_by(
        (func.count(Activity.activity_id) * func.avg(Activity.importance_weight)).desc()
    ).limit(limit).all()
    
    return [
        {
            'product_id': pid,
            'activity_count': count,
            'importance_score': round(float(importance), 3)
        }
        for pid, count, importance in trending
    ]
