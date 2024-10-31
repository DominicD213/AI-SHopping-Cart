"""
Data Import Helper for MySQL Database
===================================

Version History:
---------------
v0.1 - Initial version with basic CSV import
v0.2 - Added error handling and logging
v0.3 - Updated for MySQL compatibility
v0.4 - Updated to match new database schemas and activity tracking

This script scans a directory for CSV files and loads them into corresponding MySQL tables.
File names should match table names (e.g., products.csv loads into products table).

Database Tables:
---------------
- products: Product information
- user: User accounts
- activity: User activity tracking
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from models import Base, Product, User, Activity, Session

# Database connection configuration
# TODO: Move to environment variables
user = 'jbart'
password = 'root99'
host = 'localhost'
database = 'ASCdb'

# Create database connection
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Directory where CSV files are stored
directory = 'C:/Users/JMBar/Desktop/SHOPPING/data'

def import_products(file_path, session):
    """
    Import product data from CSV
    
    Expected CSV columns:
    - title: Product name (str, max 255 chars)
    - tags: Search keywords (str, max 255 chars)
    - category: Product category (str, max 100 chars)
    - description: Product details (str, max 500 chars)
    - brand: Product brand (str, max 100 chars)
    - popularity: Popularity score (int)
    - ratings: Average rating (float)
    """
    try:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            product = Product(
                title=row['title'],
                tags=row['tags'],
                category=row['category'],
                description=row['description'],
                brand=row['brand'],
                popularity=int(row['popularity']),
                ratings=float(row['ratings'])
            )
            session.add(product)
        session.commit()
        print(f"Successfully imported products from {file_path}")
    except Exception as e:
        session.rollback()
        print(f"Error importing products: {e}")

def import_users(file_path, session):
    """
    Import user data from CSV
    
    Expected CSV columns:
    - username: Unique username (str, max 50 chars)
    - password: Plain password to be hashed (str)
    - email: Unique email (str, max 100 chars)
    """
    try:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            user = User(
                username=row['username'],
                password=row['password'],  # Will be hashed by User model
                email=row['email']
            )
            session.add(user)
        session.commit()
        print(f"Successfully imported users from {file_path}")
    except Exception as e:
        session.rollback()
        print(f"Error importing users: {e}")

def import_activities(file_path, session):
    """
    Import activity data from CSV
    
    Expected CSV columns:
    - user_id: ID of user (int)
    - activity_type: Type of activity (str: search/view/cart/purchase)
    - search_query: Search term if applicable (str, max 255 chars)
    - product_id: Product ID if applicable (int)
    - timestamp: Activity timestamp (datetime)
    """
    try:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            activity = Activity(
                user_id=int(row['user_id']),
                activity_type=row['activity_type'],
                search_query=row['search_query'] if 'search_query' in row else None,
                product_id=int(row['product_id']) if 'product_id' in row else None
            )
            if 'timestamp' in row:
                activity.timestamp = pd.to_datetime(row['timestamp'])
            session.add(activity)
        session.commit()
        print(f"Successfully imported activities from {file_path}")
    except Exception as e:
        session.rollback()
        print(f"Error importing activities: {e}")

def main():
    """
    Main function to process all CSV files in the data directory
    """
    # Create database session
    session = Session()
    
    try:
        # Process each CSV file in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory, filename)
                table_name = filename.replace('.csv', '')
                
                print(f"\nProcessing {filename}...")
                
                # Import data based on table name
                if table_name == 'products':
                    import_products(file_path, session)
                elif table_name == 'user':
                    import_users(file_path, session)
                elif table_name == 'activity':
                    import_activities(file_path, session)
                else:
                    print(f"Unknown table: {table_name}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()
        print("\nImport process completed.")

if __name__ == "__main__":
    main()
