"""
AI-Powered Shopping Tool - Data Import
Handles importing CSV files into database tables and generating embeddings.
"""
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from models import Base, Product, User, Activity, ProductEmbedding, Session
from dotenv import load_dotenv
import logging
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename='data_import.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection configuration
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')

# Initialize database connection
DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI)

# Directory where CSV files are stored - using relative path
directory = 'data'

# Initialize the sentence transformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions, good balance of speed/quality

def generate_product_embedding(product):
    """Generate embedding for a product using its text fields"""
    # Combine relevant text fields
    text = f"{product.title} {product.description} {product.category} {product.brand} {product.tags}"
    
    # Generate embedding
    embedding = model.encode(text)
    return embedding

def clean_price(price_str):
    """Clean price string by removing $ and , characters"""
    if pd.isna(price_str):
        return None
    return float(price_str.replace('$', '').replace(',', '').strip())

def clean_tags(tags_str):
    """Clean tags string by removing list characters and quotes"""
    if pd.isna(tags_str):
        return None
    return tags_str.replace("['", "").replace("']", "").replace("'", "")

def import_products(file_path, session):
    """
    Import product data from CSV and generate embeddings. Skips rows with missing critical fields.
    """
    try:
        df = pd.read_csv(file_path)
        
        # Map CSV columns to model fields
        column_mapping = {
            'product_name': 'title',
            'description': 'description',
            'category': 'category',
            'brand/manufacturer': 'brand',
            'popularity_score': 'popularity',
            'rating': 'ratings',
            'price': 'price',
            'was_price': 'was_price',
            'discount': 'discount',
            'tags': 'tags'
        }

        skipped_rows = []  # To track skipped rows
        
        for index, row in df.iterrows():
            # Skip rows with missing critical fields
            if pd.isna(row['product_name']) or pd.isna(row['description']) or pd.isna(row['category']):
                skipped_rows.append(index)
                continue

            # Create product object
            product = Product(
                title=row['product_name'],
                description=row['description'],
                category=row['category'],
                brand=row['brand/manufacturer'],
                popularity=int(row['popularity_score']),
                ratings=float(row['rating']),
                price=clean_price(row['price']),
                was_price=clean_price(row['was_price']),
                discount=float(row['discount']),
                tags=clean_tags(row['tags'])
            )
            session.add(product)
            session.flush()  # Flush to get the product_id

            # Generate and store embedding
            embedding = generate_product_embedding(product)
            product_embedding = ProductEmbedding(
                product_id=product.product_id,
                embedding=embedding.tobytes(),
                dimensions=len(embedding)
            )
            session.add(product_embedding)

        session.commit()
        
        # Log skipped rows
        if skipped_rows:
            logging.warning(f"Skipped rows with missing critical fields: {skipped_rows}")

        logging.info(f"Successfully imported products and generated embeddings from {file_path}")
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing products from {file_path}: {e}")

def create_dummy_users(session, user_ids):
    """Create dummy users for the given user IDs, skipping existing users"""
    created_count = 0
    skipped_count = 0
    
    for user_id in user_ids:
        username = f"user_{user_id}"
        # Check if user already exists
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user is None:
            user = User(
                username=username,
                password="dummy_password",
                email=f"user_{user_id}@example.com"
            )
            session.add(user)
            created_count += 1
        else:
            skipped_count += 1
    
    try:
        session.commit()
        logging.info(f"Created {created_count} new users, skipped {skipped_count} existing users")
    except Exception as e:
        session.rollback()
        logging.error(f"Error creating users: {e}")
        raise

def import_activities(file_path, session):
    """Import activity data from CSV"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['user_id', 'action']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return

        # Create dummy users first
        unique_user_ids = df['user_id'].unique()
        create_dummy_users(session, unique_user_ids)
        
        for _, row in df.iterrows():
            activity = Activity(
                user_id=int(row['user_id']),
                action=row['action'],
                product_id=int(row['product_id']) if pd.notna(row['product_id']) else None
            )
            if 'timestamp' in row:
                activity.timestamp = pd.to_datetime(row['timestamp'])
            session.add(activity)
        session.commit()
        logging.info(f"Successfully imported activities from {file_path}")
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing activities from {file_path}: {e}")

def main():
    """Main function to process all CSV files in the data directory"""
    # Create database session
    with Session() as session:
        try:
            # First, import products from Product_Table.csv
            products_path = os.path.join(directory, 'Product_Table.csv')
            if os.path.exists(products_path):
                logging.info(f"\nProcessing {products_path}...")
                import_products(products_path, session)
            else:
                logging.error(f"Product file not found: {products_path}")
            
            # Then, import activities from Activity_Table.csv
            activity_path = os.path.join(directory, 'Activity_Table.csv')
            if os.path.exists(activity_path):
                logging.info(f"\nProcessing {activity_path}...")
                import_activities(activity_path, session)
            else:
                logging.error(f"Activity file not found: {activity_path}")
        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        
        logging.info("\nImport process completed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
