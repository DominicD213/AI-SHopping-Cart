"""
AI-Powered Shopping Tool - Data Import
-----------------------------------------------------------------------------
Handles importing CSV files into database tables to pre-populate databases with product data as well as synthetic data for other tables for testing purposes
-----------------------------------------------------------------------------


Version History:
---------------
[please please remember to add your name, date, and version number if you change anything, even when using Github  - thanks, JB]
---------------

75%, 6/8, all of CSVs/product data/synthetic data

v0.1 - 9-28-24 - Jakub Bartkowiak
    - Initial version with basic CSV import functionality
    - Implemented product and user data import

v0.2 - 10-08-24 - Mariam Lafi
    - Added error handling and logging for import failures
    - Improved validation for CSV format and content

v0.3 - 11-01-24 - Nya James
    - Updated for MySQL compatibility
    - Enhanced schema matching for user activity data
    - Added support for timestamp handling

v0.4 - 11-12-24 - Jakub Bartkowiak
    - Updated to match new database schemas
    - Added retry mechanism for interrupted imports
    - Modified activity type mapping to match CSV values
    - Added proper handling for all activity types (search, view, cart, purchase)

v0.5 - 11-14-24 - Jakub Bartkowiak
    - Added create_tables function to ensure tables exist
    - Added drop_tables option for clean slate imports
    - Improved import order to handle foreign key dependencies
    - Enhanced logging for import progress and issues

v0.6-V-0.8 - 11-15 to 11-16-24 - Jakub Bartkowiak
    - Introduced batch processing for large datasets to improve scalability
    - Modified data loading to use chunked reading, reducing memory usage for large files
    - Added support for 50-dimensional product embeddings, ensuring compatibility with updated models
    - Enhanced tracking of imported IDs to maintain referential integrity across tables
    - Improved handling of CSV parsing errors, providing detailed feedback for debugging
    - Implemented efficient binary storage for embeddings to optimize space and retrieval times
"""

import os
import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging
import glob
from datetime import datetime

# Add parent directory to Python path for relative imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import models after adding parent directory to path
from models import Base, Product, User, Activity, ProductEmbedding, Session

# Set up logging with both file and console handlers
logger = logging.getLogger('import_data')
logger.setLevel(logging.INFO)

# File handler
fh = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'data_import.log'))
fh.setLevel(logging.INFO)
fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch_formatter = logging.Formatter('%(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

# Load environment variables from the .env file in parent directory
env_path = os.path.join(parent_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    logger.error(f".env file not found at {env_path}")
    raise FileNotFoundError(f".env file not found at {env_path}")

# Get MySQL configuration from environment variables
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_db = os.getenv('MYSQL_DB')

# Validate required environment variables
required_vars = {
    'MYSQL_USER': mysql_user,
    'MYSQL_PASSWORD': mysql_password,
    'MYSQL_HOST': mysql_host,
    'MYSQL_DB': mysql_db
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg)
    raise ValueError(error_msg)

# Construct DATABASE_URI from MySQL environment variables
DATABASE_URI = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"

try:
    engine = create_engine(DATABASE_URI)
    # Test the connection
    with engine.connect() as conn:
        logger.info("Successfully connected to database")
except Exception as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise

def get_newest_embedding_file(directory):  # [IMPOR-001-150]
    """
    Get the newest ProductEmbeddings file in the specified directory.
    Removes any characters after 'Table' in the filename.
    
    Args:
        directory (str): Directory to search for embedding files
        
    Returns:
        str: Path to the newest embedding file
    """
    try:
        # Get all files matching the pattern
        pattern = os.path.join(directory, "ProductEmbeddings_Table*")
        embedding_files = glob.glob(pattern)
        
        if not embedding_files:
            logger.error("No embedding files found")
            return None
            
        # Get the newest file based on creation time
        newest_file = max(embedding_files, key=os.path.getctime)
        logger.info(f"Found newest embedding file: {newest_file}")
        
        return newest_file
        
    except Exception as e:
        logger.error(f"Error finding newest embedding file: {str(e)}")
        return None

def import_product_embeddings(file_path, session, imported_product_ids, embedding_size=10, skip_embeddings=False):  # [IMPOR-001-150]
    """Import product embeddings from CSV using chunked processing"""
    if skip_embeddings:
        logger.info("Skipping product embeddings import (testing mode)")
        return

    try:
        # Get the newest embedding file
        directory = os.path.dirname(file_path)
        newest_file = get_newest_embedding_file(directory)
        if not newest_file:
            logger.error("No embedding file found")
            return
            
        logger.info(f"\nImporting product embeddings from {newest_file}")
        
        # Get total number of records without loading entire file
        total_records = sum(1 for _ in open(newest_file)) - 1  # subtract header row
        logger.info(f"Found {total_records} embeddings in CSV")
        
        processed_count = 0
        imported_count = 0
        chunk_size = 1000
        
        for chunk in pd.read_csv(newest_file, chunksize=chunk_size):
            # Filter embeddings for imported products
            chunk = chunk[chunk['product_id'].isin(imported_product_ids)]
            
            for _, row in chunk.iterrows():
                # Convert embedding string to numpy array and resize
                embedding_values = [float(x) for x in row['embedding'].split(',')]
                
                # Handle different embedding sizes
                if len(embedding_values) > embedding_size:
                    embedding_values = embedding_values[:embedding_size]  # Take first n dimensions
                elif len(embedding_values) < embedding_size:
                    # Pad with zeros if less than desired dimensions
                    embedding_values.extend([0.0] * (embedding_size - len(embedding_values)))
                
                embedding_array = np.array(embedding_values, dtype=np.float32)
                # Normalize the vector
                embedding_array = embedding_array / np.linalg.norm(embedding_array)
                
                embedding = ProductEmbedding(
                    product_id=int(row['product_id']),
                    embedding=embedding_array.tobytes(),
                    dimensions=embedding_size
                )
                
                session.add(embedding)
                imported_count += 1
                processed_count += 1
                
                # Commit every 100 records to avoid memory issues
                if imported_count % 100 == 0:
                    session.commit()
                    logger.info(f"Processed {processed_count} embeddings...")
            
            session.commit()
            
        logger.info(f"Successfully imported {imported_count} embeddings")
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing product embeddings: {e}")

def create_tables(drop_existing=True):  # [IMPOR-003-250]
    """Create database tables"""
    try:
        if drop_existing:
            logger.info("Dropping existing tables...")
            Base.metadata.drop_all(engine)
        
        logger.info("Creating tables...")
        Base.metadata.create_all(engine)
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

def add_product(session, title, tags, category, description, brand, popularity, ratings, 
                embedding_size=50, skip_embeddings=False, price=None, was_price=None, discount=None):  # [IMPOR-004-300]
    """
    Add a new product to the database with its embedding.
    
    Args:
        session: SQLAlchemy session
        title (str): Product title
        tags (str): Product tags
        category (str): Product category
        description (str): Product description
        brand (str): Product brand
        popularity (int): Product popularity score (0-1000)
        ratings (float): Product ratings (0-5)
        embedding_size (int): Size of embedding vector (50 for testing, 300 for production)
        skip_embeddings (bool): If True, skip embedding generation (for testing)
        price (float): Current product price
        was_price (float): Original price before discount
        discount (float): Discount percentage
    
    Returns:
        tuple: (product_id, success_flag)
    """
    try:
        # Create and add product
        product = Product(
            title=title,
            tags=tags,
            category=category,
            description=description,
            brand=brand,
            popularity=popularity,
            ratings=ratings,
            price=price,
            was_price=was_price,
            discount=discount
        )
        session.add(product)
        session.flush()  # Get product_id without committing

        if not skip_embeddings:
            # Generate embedding based on product attributes
            # Combine all text fields for embedding calculation
            text_content = f"{title} {tags} {category} {description} {brand}"
            
            # Generate embedding using a simple method (for demonstration)
            # In production, you'd use a proper embedding model
            np.random.seed(hash(text_content) % 2**32)  # Deterministic based on content
            embedding_vector = np.random.randn(embedding_size)
            # Normalize the vector
            embedding_vector = embedding_vector / np.linalg.norm(embedding_vector)

            # Create and add embedding
            product_embedding = ProductEmbedding(
                product_id=product.product_id,
                embedding=embedding_vector.tobytes(),
                dimensions=embedding_size
            )
            session.add(product_embedding)
            
        session.commit()
        logger.info(f"Successfully added product: {title}{' without embedding' if skip_embeddings else f' with {embedding_size}-dimensional embedding'}")
        return product.product_id, True
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding product: {str(e)}")
        return None, False

def import_products(file_path, session, entry_limit=None, skip_embeddings=False):  # [IMPOR-002-200]
    """Import product data from CSV using chunked processing"""
    try:
        logger.info(f"\nImporting products from {file_path}")
        
        # Get total number of records without loading entire file
        total_records = sum(1 for _ in open(file_path)) - 1  # subtract header row
        logger.info(f"Found {total_records} products in CSV")
        
        # Base chunk size is always 5 items
        chunk_size = 5
        
        # If entry_limit is provided, ensure it's a multiple of chunk_size
        if entry_limit:
            # Round up to nearest multiple of chunk_size
            entry_limit = ((entry_limit + chunk_size - 1) // chunk_size) * chunk_size
            logger.info(f"Adjusted entry limit to {entry_limit} to maintain chunk size of {chunk_size}")
            
        logger.info(f"Using chunk size of {chunk_size} items")
        
        imported_product_ids = set()
        processed_count = 0
        
        # Read CSV in chunks of 5 items
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            if entry_limit and processed_count >= entry_limit:
                break
                
            if entry_limit:
                remaining = entry_limit - processed_count
                if remaining < chunk_size:
                    chunk = chunk.head(remaining)
            
            for _, row in chunk.iterrows():
                try:
                    # Convert price strings to floats
                    price = float(str(row['price']).replace('$', '').replace(',', '').strip()) if pd.notna(row['price']) else None
                    was_price = float(str(row['was_price']).replace('$', '').replace(',', '').strip()) if pd.notna(row['was_price']) else None
                    discount = float(str(row['discount']).strip()) if pd.notna(row['discount']) else None
                    
                    product = Product(
                        title=str(row['product_name']),  # Changed from 'title' to 'product_name'
                        tags=str(row['tags']),
                        category=str(row['category']),
                        description=str(row['description']),
                        brand=str(row['brand/manufacturer']),  # Updated to match CSV column name
                        popularity=int(row['popularity_score']),
                        ratings=float(row['rating']),
                        price=price,
                        was_price=was_price,
                        discount=discount
                    )
                    session.add(product)
                    session.flush()
                    imported_product_ids.add(product.product_id)
                    processed_count += 1
                    
                    # Commit after each chunk
                    if len(imported_product_ids) % chunk_size == 0:
                        session.commit()
                        logger.info(f"Processed {processed_count} products...")
                except Exception as row_error:
                    logger.error(f"Error processing product row: {row_error}")
                    continue
            
            session.commit()
            
        logger.info(f"Successfully imported {len(imported_product_ids)} products")
        return imported_product_ids
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing products: {e}")
        return set()

def import_users(file_path, session, entry_limit=None):  # [IMPOR-002-200]
    """Import user data from CSV using chunked processing"""
    try:
        logger.info(f"\nImporting users from {file_path}")
        
        # Get total number of records without loading entire file
        total_records = sum(1 for _ in open(file_path)) - 1  # subtract header row
        logger.info(f"Found {total_records} users in CSV")
        
        imported_user_ids = set()
        processed_count = 0
        chunk_size = min(1000, entry_limit if entry_limit else 1000)
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            if entry_limit and processed_count >= entry_limit:
                break
                
            if entry_limit:
                chunk = chunk.head(entry_limit - processed_count)
            
            for _, row in chunk.iterrows():
                user = User(
                    username=row['username'],
                    password="temp",  # Temporary password
                    email=row['email'],
                    role=row['role']
                )
                user.password_hash = row['password_hash']
                
                session.add(user)
                session.flush()
                imported_user_ids.add(user.user_id)
                processed_count += 1
                
                # Commit every 100 records to avoid memory issues
                if len(imported_user_ids) % 100 == 0:
                    session.commit()
                    logger.info(f"Processed {processed_count} users...")
            
            session.commit()
            
        logger.info(f"Successfully imported {len(imported_user_ids)} users")
        return imported_user_ids
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing users: {e}")
        return set()

def import_activities(file_path, session, imported_user_ids, imported_product_ids, entry_limit=None):  # [IMPOR-003-250]
    """Import activity data from CSV using chunked processing"""
    try:
        logger.info(f"\nImporting activities from {file_path}")
        
        # Get total number of records without loading entire file
        total_records = sum(1 for _ in open(file_path)) - 1  # subtract header row
        logger.info(f"Found {total_records} activities in CSV")
        
        processed_count = 0
        imported_count = 0
        chunk_size = min(1000, entry_limit if entry_limit else 1000)
        
        activity_type_map = {
            'view': 'viewed',
            'cart': 'added_to_cart',
            'purchase': 'purchased'
        }
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            if entry_limit and processed_count >= entry_limit:
                break
            
            # Filter activities within the chunk
            chunk = chunk[
                (chunk['user_id'].isin(imported_user_ids)) & 
                ((chunk['product_id'].isin(imported_product_ids)) | (chunk['product_id'].isna()))
            ]
            
            if entry_limit:
                chunk = chunk.head(entry_limit - processed_count)
            
            for _, row in chunk.iterrows():
                action = activity_type_map.get(row['activity_type'], 'viewed')
                
                product_id = None
                if pd.notna(row['product_id']):
                    product_id = int(row['product_id'])
                
                activity = Activity(
                    user_id=int(row['user_id']),
                    action=action,
                    product_id=product_id
                )
                if 'timestamp' in row:
                    activity.timestamp = pd.to_datetime(row['timestamp'])
                
                session.add(activity)
                imported_count += 1
                processed_count += 1
                
                # Commit every 100 records to avoid memory issues
                if imported_count % 100 == 0:
                    session.commit()
                    logger.info(f"Processed {processed_count} activities...")
            
            session.commit()
            
        logger.info(f"Successfully imported {imported_count} activities")
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing activities: {e}")

def import_csv_to_table(csv_path, table_name, session, entry_limit=None, imported_ids=None, skip_embeddings=False):  # [IMPOR-004-300]
    """
    Import data from a CSV file into the specified database table.
    
    Args:
        csv_path (str): Path to the CSV file
        table_name (str): Name of the target database table
        session (Session): The SQLAlchemy session object
        entry_limit (int, optional): Limit number of entries to import
        imported_ids (dict): Dictionary containing imported user and product IDs
        skip_embeddings (bool): If True, skip embedding processing (for testing)
    """
    try:
        table_map = {
            'product': 'products',
            'products': 'products',
            'activity': 'activity',
            'users': 'users',
            'productembeddings': 'product_embeddings'
        }
        
        correct_table = table_map.get(table_name.lower(), table_name.lower())
        
        if correct_table == 'products':
            return {'product_ids': import_products(csv_path, session, entry_limit, skip_embeddings)}
        elif correct_table == 'users':
            return {'user_ids': import_users(csv_path, session, entry_limit)}
        elif correct_table == 'activity':
            import_activities(csv_path, session, 
                            imported_ids.get('user_ids', set()),
                            imported_ids.get('product_ids', set()),
                            entry_limit)
            return {}
        elif correct_table == 'product_embeddings' and not skip_embeddings:
            import_product_embeddings(csv_path, session,
                                   imported_ids.get('product_ids', set()),
                                   entry_limit)
            return {}
        else:
            if correct_table == 'product_embeddings' and skip_embeddings:
                logger.info("Skipping product embeddings import (testing mode)")
            else:
                logger.error(f"Unknown table: {table_name}")
            return {}
        
    except Exception as e:
        logger.error(f"Error importing {csv_path} to {table_name}: {str(e)}")
        session.rollback()
        raise

def main(entry_limit=15, skip_embeddings=False):  # [IMPOR-005-350]
    """
    Main function to process all CSV files in the data directory
    
    Args:
        entry_limit (int, optional): Limit number of entries to import from each CSV.
                                   Defaults to 15 entries per table.
        skip_embeddings (bool): If True, skip embedding processing (for testing)
    """
    try:
        logger.info("\n=== Starting Data Import Process ===")
        logger.info(f"Running with {entry_limit} entry limit per table")
        if skip_embeddings:
            logger.info("Running in testing mode (skipping embeddings)")
        
        create_tables(drop_existing=True)
        
        with Session() as session:
            try:
                # Updated to match exact CSV file names
                table_files = {
                    'Product': 'Product_Table.csv',
                    'Users': 'Users_Table.csv',
                    'Activity': 'Activity_Table.csv',
                    'ProductEmbeddings': 'ProductEmbeddings_Table.csv'
                }
                
                imported_ids = {}
                
                # Process products first to get product IDs for embeddings
                if os.path.exists(os.path.join(os.path.dirname(__file__), table_files['Product'])):
                    logger.info(f"\nProcessing {table_files['Product']}...")
                    result = import_csv_to_table(
                        os.path.join(os.path.dirname(__file__), table_files['Product']),
                        'products', session, entry_limit, skip_embeddings=skip_embeddings
                    )
                    imported_ids.update(result)
                
                # Then process embeddings using the imported product IDs (if not skipping)
                if not skip_embeddings and os.path.exists(os.path.join(os.path.dirname(__file__), table_files['ProductEmbeddings'])):
                    logger.info(f"\nProcessing {table_files['ProductEmbeddings']}...")
                    import_csv_to_table(
                        os.path.join(os.path.dirname(__file__), table_files['ProductEmbeddings']),
                        'product_embeddings', session, entry_limit, imported_ids
                    )
                
                # Process remaining tables
                for table, filename in table_files.items():
                    if table not in ['Product', 'ProductEmbeddings']:
                        file_path = os.path.join(os.path.dirname(__file__), filename)
                        if os.path.exists(file_path):
                            table_name = filename.replace('_Table.csv', '').lower()
                            logger.info(f"\nProcessing {filename}...")
                            result = import_csv_to_table(file_path, table_name, session, entry_limit, imported_ids)
                            imported_ids.update(result)
                        else:
                            logger.warning(f"File not found: {filename}")
            
            except Exception as e:
                logger.error(f"An error occurred: {e}")
            
            logger.info("\n=== Import Process Completed ===")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    try: 
        main(skip_embeddings=True)  # use 15 entries per table when run in testing mode, used by default
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
