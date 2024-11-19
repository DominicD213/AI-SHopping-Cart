"""
Generate Embeddings Script
--------------------------
This script generates 300-dimensional embeddings for all products in the database
and stores them in the ProductEmbedding table. Embeddings are generated on first run
and stored in the database.

WARNING: importing the entire database into memory can be memory-intensive and especially compute-intensive (depends heavily on your system's GPU and if it can handle CUDA natively). Ensure you adjust the import limits (IMPORT_LIMITS) to suit your system resources when testing (I'd recommend around 250 products, 25 users, 500 activity logs so it doesnt take more than 2-3 minutes on CPU [TO BE CONFIRMED])

Version History:
---------------
[Version history prior to v1.0 can be found in version_history.txt]

v1.0 - 11/19/24 - Jakub Bartkowiak
    - First stable release with sentence transformer model
    - Efficient batch processing implementation
    - Memory-optimized embedding generation
    - Comprehensive progress tracking

v1.1 - 11/19/24 - Jakub Bartkowiak
    - Added some basic performance metrics and logging to see how much compute/memory it's eating
    - Added batch size and import limits configurations to help with the above in testing
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from models import Base, Product, ProductEmbedding, Session, initialize_database_config
from contextlib import contextmanager
import logging
import time
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database configuration
DATABASE_URI = initialize_database_config()

# Configuration
MODEL_NAME = 'all-MiniLM-L6-v2'  # [GENER-001-020]
EMBEDDING_DIMENSIONS = 300  # Production embedding size
BATCH_SIZE = 100  # Number of products to process in each batch
COMMIT_FREQUENCY = 1000  # How often to commit to database

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

def log_memory_usage():
    """Log current memory usage"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        logger.info(f"Current memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
    except ImportError:
        pass

def generate_product_embeddings():  # [GENER-003-065]
    """Generate embeddings for all products using sentence transformer model"""
    if check_embeddings_exist():
        logger.info("Embeddings already exist in the database.")
        return

    logger.info(f"Starting embedding generation using model: {MODEL_NAME}")
    start_time = time.time()
    
    try:
        # Load model and log initial memory usage
        model = SentenceTransformer(MODEL_NAME)
        log_memory_usage()
        
        with get_session() as session:
            # Get total number of products
            total_products = session.query(Product).count()
            logger.info(f"Found {total_products} products in the database.")
            
            # Calculate and log estimates
            estimated_time_cpu = total_products * 0.1  # 0.1s per product on CPU
            estimated_time_gpu = total_products * 0.02  # 0.02s per product on GPU
            estimated_storage = total_products * 1.2  # 1.2KB per product
            
            logger.info("Estimated processing time:")
            logger.info(f"  CPU: {estimated_time_cpu/60:.1f} minutes")
            logger.info(f"  GPU: {estimated_time_gpu/60:.1f} minutes")
            logger.info(f"Estimated storage required: {estimated_storage/1024:.1f} MB")

            # Process products in batches
            products_processed = 0
            embeddings_to_add = []
            batch_times = []
            
            # Create progress bar
            with tqdm(total=total_products, desc="Generating embeddings") as pbar:
                for offset in range(0, total_products, BATCH_SIZE):
                    batch_start = time.time()
                    
                    # Get batch of products
                    products = session.query(Product).offset(offset).limit(BATCH_SIZE).all()
                    
                    # Generate embeddings for batch
                    for product in products:
                        text_to_embed = f"{product.title} {product.category} {product.tags}"
                        embedding = model.encode(text_to_embed)

                        new_embedding = ProductEmbedding(
                            product_id=product.product_id,
                            embedding=embedding.tobytes(),
                            dimensions=EMBEDDING_DIMENSIONS
                        )
                        embeddings_to_add.append(new_embedding)
                        products_processed += 1
                        pbar.update(1)
                    
                    # Commit batch if reached frequency
                    if len(embeddings_to_add) >= COMMIT_FREQUENCY:
                        session.bulk_save_objects(embeddings_to_add)
                        session.commit()
                        embeddings_to_add = []
                        log_memory_usage()
                    
                    # Track batch performance
                    batch_time = time.time() - batch_start
                    batch_times.append(batch_time)
                    avg_time_per_product = batch_time / len(products)
                    logger.debug(f"Batch processing time: {batch_time:.2f}s ({avg_time_per_product:.3f}s per product)")

            # Commit any remaining embeddings
            if embeddings_to_add:
                session.bulk_save_objects(embeddings_to_add)
                session.commit()

            # Log final statistics
            total_time = time.time() - start_time
            avg_time = total_time / total_products
            avg_batch_time = sum(batch_times) / len(batch_times)
            
            logger.info("\nEmbedding Generation Statistics:")
            logger.info(f"Total products processed: {products_processed}")
            logger.info(f"Total processing time: {total_time/60:.1f} minutes")
            logger.info(f"Average time per product: {avg_time:.3f} seconds")
            logger.info(f"Average batch time: {avg_batch_time:.3f} seconds")
            log_memory_usage()

    except Exception as e:
        logger.error(f"An error occurred during embedding generation: {e}")
        raise

def ensure_embeddings():  # [GENER-004-120]
    """Ensure all products have corresponding embeddings"""
    try:
        with get_session() as session:
            # Check for products without embeddings
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
