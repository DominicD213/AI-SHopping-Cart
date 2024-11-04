
# Jakub Bartkowiak - v0.1 - 9-28-24
# Jakub Bartkowiak - v0.3 - 10-14-24
# [add your name and version number if you change stuff - even if using github]


"""
Code for Search, with Embeddings for products and Reranking of search results
-----------------------------------------------------------------------------

This code uses SQLite and SQLAlchemy to store and manage products and their embeddings.
Products are embedded using spaCy (300-dimensional vectors) and stored in the database.

The search retrieves products by comparing cosine similarity between query and product embeddings.
If fewer than 5 results are found, the cosine similarity threshold is relaxed iteratively.

The final set of results is reranked based on cosine similarity [60%], popularity (0-1000) [20%], and ratings (0.0-5.0) [20%].
This ensures the results are relevant while considering product popularity and quality.
""" 


import spacy
import numpy as np
import pickle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product, ProductEmbedding, Base

# Load spaCy model for generating embeddings
nlp = spacy.load("en_core_web_md")

# Database setup
engine = create_engine('sqlite:///products.db')
Session = sessionmaker(bind=engine)
session = Session()

# ----------------------------- #
# 1. Database Preparation Functions
# ----------------------------- #

# Function: generate_product_embedding(product)
# Purpose: Generate an embedding for a product using its attributes (Title, Tags, Category, Description, Brand).
def generate_product_embedding(product):
    # Combine relevant product attributes (Title, Tags, Category, Description, Brand)
    text = f"{product.title} {product.tags} {product.category} {product.description} {product.brand}"
    
    # Generate embedding using spaCy
    product_embedding = nlp(text).vector
    return product_embedding

# Function: store_product_embeddings_in_db()
# Purpose: Precompute embeddings for all products and store them in the database.
def store_product_embeddings_in_db():
    # Fetch all products from the database
    products = session.query(Product).all()
    
    # For each product, generate embedding and store it in the database
    for product in products:
        embedding = generate_product_embedding(product)
        
        # Store the embedding as binary data in SQLite
        binary_embedding = pickle.dumps(embedding)  # Convert embedding to binary
        embedding_entry = ProductEmbedding(product_id=product.product_id, embedding=binary_embedding)
        
        # Check if embedding already exists, update if needed
        existing_entry = session.query(ProductEmbedding).filter_by(product_id=product.product_id).first()
        if existing_entry:
            existing_entry.embedding = binary_embedding  # Update existing embedding
        else:
            session.add(embedding_entry)  # Add new embedding
        
        # Commit the transaction
        session.commit()

# Function: get_product_embeddings_from_db()
# Purpose: Retrieve precomputed product embeddings from the database for similarity comparison.
def get_product_embeddings_from_db():
    # Fetch all product embeddings from the database
    embeddings = session.query(ProductEmbedding).all()
    
    product_embeddings = []
    for entry in embeddings:
        # Convert binary data back to numpy array
        product_embedding = pickle.loads(entry.embedding)
        
        # Fetch corresponding product data
        product = session.query(Product).filter_by(product_id=entry.product_id).first()
        product_embeddings.append({
            'product_id': product.product_id,
            'title': product.title,
            'popularity': product.popularity,
            'ratings': product.ratings,
            'embedding': product_embedding
        })
    
    return product_embeddings

# ----------------------------- #
# 2. Query Processing Functions
# ----------------------------- #

# Function: preprocess_query(query)
# Purpose: Preprocess the user search query (lowercase, lemmatize).
def preprocess_query(query):
    # Lowercase and lemmatize the query using spaCy
    doc = nlp(query.lower())
    lemmatized_query = " ".join([token.lemma_ for token in doc])
    return lemmatized_query

# Function: generate_embedding(query)
# Purpose: Convert the preprocessed query into an embedding.
def generate_embedding(query):
    # Use spaCy to generate the embedding for the preprocessed query
    query_embedding = nlp(query).vector
    return query_embedding

# ----------------------------- #
# 3. Search and Similarity Functions
# ----------------------------- #

# Function: cosine_similarity(embedding1, embedding2)
# Purpose: Compute cosine similarity between two embedding vectors.
def cosine_similarity(embedding1, embedding2):
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0  # Handle case where one of the embeddings has zero magnitude
    return dot_product / (norm1 * norm2)

# Function: normalize(value, min_value, max_value)
# Purpose: Normalize a value between 0 and 1.
def normalize(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0

# Function: search_products(query)
# Purpose: Perform the actual search by comparing the query embedding with the product embeddings and return a list of 5+ relevant products.
def search_products(query):
    # Step 1: Preprocess the query
    query = preprocess_query(query)  # Lowercase, lemmatize
    query_embedding = generate_embedding(query)  # Convert query to an embedding
    
    # Step 2: Retrieve precomputed product embeddings from the database
    product_embeddings = get_product_embeddings_from_db()  # Precomputed embeddings
    
    # Step 3: Initialize similarity threshold and results
    threshold = 0.8  # Start with a high similarity threshold
    results = []
    
    # Step 4: Perform search, relaxing the threshold if needed
    while len(results) < 5 and threshold > 0:
        results = []
        for product in product_embeddings:
            similarity = cosine_similarity(query_embedding, product['embedding'])
            if similarity >= threshold:
                results.append((product, similarity))
        
        # Lower the threshold if fewer than 5 products are found
        threshold -= 0.05
    
    # Step 5: Rerank the products based on combined score (cosine similarity, popularity, and ratings)
    if results:
        # Assume min/max values for normalization
        min_popularity = 0
        max_popularity = 1000
        min_ratings = 0.0
        max_ratings = 5.0
        
        reranked_results = []
        for product, similarity in results:
            # Normalize popularity and ratings
            normalized_popularity = normalize(product['popularity'], min_popularity, max_popularity)
            normalized_ratings = normalize(product['ratings'], min_ratings, max_ratings)
            
            # Calculate the final score using weights (e.g., 60% similarity, 20% popularity, 20% ratings)
            final_score = (0.6 * similarity) + (0.2 * normalized_popularity) + (0.2 * normalized_ratings)
            
            # Append the product and final score
            reranked_results.append((product, final_score))
        
        # Sort products by final score (highest score first)
        reranked_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return only the products, discarding the scores
        return [product for product, score in reranked_results]
    
    return results  # Return original results if reranking isn't needed
