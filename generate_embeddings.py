"""
Generate Embeddings Script
--------------------------
This script generates 300-dimensional embeddings for all products in the database
and stores them in the ProductEmbedding table. Embeddings are generated on first run
and stored in the database.

Version History:
---------------
v1.0 - Initial implementation
v1.1 - Updated to use centralized database configuration
v1.2 - Added proper session management
v1.3 - Improved embedding dimension handling
v1.4 - Added ML/AI documentation references
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from models import Base, Product, ProductEmbedding, Session, initialize_database_config
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database configuration
DATABASE_URI = initialize_database_config()

# Load Sentence Transformer model  # [GENER-001-020]
MODEL_NAME = 'all-MiniLM-L6-v2'
EMBEDDING_DIMENSIONS = 300  # Production embedding size

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

def check_embeddings_exist():  # [GENER-002-045]
    """Check if embeddings already exist in the database"""
    try:
        with get_session() as session:
            count = session.query(ProductEmbedding).count()
            return count > 0
    except Exception as e:
        logger.error(f"Error checking embeddings: {e}")
        return False

def generate_product_embeddings():  # [GENER-003-065]
    """Generate embeddings for all products using sentence transformer model"""
    if check_embeddings_exist():
        logger.info("Embeddings already exist in the database.")
        return

    logger.info(f"Starting embedding generation using model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    try:
        with get_session() as session:
            products = session.query(Product).all()
            logger.info(f"Found {len(products)} products in the database.")

            for product in products:
                # Generate embedding for the product
                text_to_embed = f"{product.title} {product.category} {product.tags}"
                embedding = model.encode(text_to_embed)

                # Store the embedding in the database
                new_embedding = ProductEmbedding(
                    product_id=product.product_id,
                    embedding=embedding.tobytes(),
                    dimensions=EMBEDDING_DIMENSIONS
                )
                session.add(new_embedding)
                logger.info(f"Generated and stored embedding for product_id: {product.product_id}")

            logger.info("Embedding generation and storage completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during embedding generation: {e}")
        raise

def ensure_embeddings():  # [GENER-004-120]
    """Ensure all products have corresponding embeddings"""
    try:
        with get_session() as session:
            products_without_embeddings = session.query(Product).outerjoin(
                ProductEmbedding
            ).filter(
                ProductEmbedding.product_id.is_(None)
            ).count()

            if products_without_embeddings > 0:
                logger.info(f"Found {products_without_embeddings} products without embeddings. Generating...")
                generate_product_embeddings()
            else:
                logger.info("All products have embeddings.")

    except Exception as e:
        logger.error(f"Error ensuring embeddings: {e}")
        raise

if __name__ == "__main__":
    generate_product_embeddings()
