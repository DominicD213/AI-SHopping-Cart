"""
AI-Powered Shopping Tool - Search and Recommendations
----------------------------------------------------------------------------- 
Implements semantic search and recommendation functionality using embeddings,
collaborative filtering, and hybrid scoring approaches.
----------------------------------------------------------------------------- 

Version History:
v1.4 - 11/19/24 - Jakub Bartkowiak
    - Standardized on 300-dimensional embeddings
    - Updated ML/AI documentation references
"""

import numpy as np
from sqlalchemy import func
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from models import Product, ProductEmbedding, Activity, Session, initialize_database_config
from validation import validate_input
from collections import defaultdict
from operator import attrgetter
from contextlib import contextmanager

# Initialize database configuration
DATABASE_URI = initialize_database_config()

# Standard embedding dimension
EMBEDDING_DIMENSIONS = 300

@contextmanager
def get_session():
    """Context manager for handling database sessions"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def generate_query_embedding(query):  # [SEARC-002-065]
    """Generate normalized embedding vector for search query"""
    np.random.seed(hash(query) % 2**32)
    vector = np.random.rand(EMBEDDING_DIMENSIONS)
    return vector / np.linalg.norm(vector)

def calculate_similarity_scores(query, embeddings, products):  # [SEARC-003-110]
    """Calculate weighted similarity scores combining semantic and social signals"""
    if not embeddings:
        return []
    
    query_vector = generate_query_embedding(query)
    
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

def search_products(query, min_price=None, max_price=None, brand=None, min_rating=None, simple_mode=True):  # [SEARC-007-180]
    """Execute semantic search pipeline with filters and ranking"""
    with get_session() as session:
        # Use simple validation mode for testing
        _, product_array = validate_input(query, 0, session.bind, simple_mode=simple_mode)
        search_terms = [item[0] for item in product_array if item[2] == 0]
        
        if not search_terms:
            return []
        
        # Query products with all filters
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
        
        # Get embeddings for matched products
        product_ids = [p.product_id for p in matched_products]
        embeddings = session.query(ProductEmbedding).filter(
            ProductEmbedding.product_id.in_(product_ids)
        ).all()
        
        # If no embeddings, return basic search results
        if not embeddings:
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
        
        # Calculate similarity scores
        product_scores = calculate_similarity_scores(query, embeddings, matched_products)
        
        # Sort products by score
        product_scores.sort(key=lambda x: x[1], reverse=True)
        
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
            for product, score in product_scores[:15]
        ]

def suggest_products_for_item(item_id, user_id=None):  # [SEARC-005-450]
    """Generate recommendations using hybrid content-based and collaborative approach"""
    with get_session() as session:
        current_embedding = session.query(ProductEmbedding).filter_by(
            product_id=item_id
        ).first()
        if not current_embedding:
            return []

        current_vector = np.frombuffer(current_embedding.embedding)
        other_embeddings = session.query(ProductEmbedding).filter(
            ProductEmbedding.product_id != item_id
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

def get_user_activity_vector(user_id, time_window_days=30):  # [SEARC-006-550]
    """Generate time-weighted user activity vector"""
    with get_session() as session:
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

def get_similar_users(user_id, min_similarity=0.2):  # [SEARC-008-650]
    """Find similar users based on activity patterns"""
    with get_session() as session:
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
