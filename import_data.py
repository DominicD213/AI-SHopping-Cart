import os
import pandas as pd
from sqlalchemy import create_engine
from models import Base, Product, User, Activity, Session
from dotenv import load_dotenv
import logging

# Load environment variables from the .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='data_import.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection configuration
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')

# Create database connection
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Directory where CSV files are stored
directory = os.getenv('CSV_DATA_DIRECTORY', 'C:/Users/JMBar/Desktop/SHOPPING/data')

def import_products(file_path, session):
    """Import product data from CSV"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['title', 'tags', 'category', 'description', 'brand', 'popularity', 'ratings']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return
        
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
        logging.info(f"Successfully imported products from {file_path}")
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing products from {file_path}: {e}")

def import_users(file_path, session):
    """Import user data from CSV"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['username', 'password', 'email']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return
        
        for _, row in df.iterrows():
            user = User(
                username=row['username'],
                password=row['password'],  # Will be hashed by User model
                email=row['email']
            )
            session.add(user)
        session.commit()
        logging.info(f"Successfully imported users from {file_path}")
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing users from {file_path}: {e}")

def import_activities(file_path, session):
    """Import activity data from CSV"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['user_id', 'activity_type']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return
        
        for _, row in df.iterrows():
            activity = Activity(
                user_id=int(row['user_id']),
                activity_type=row['activity_type'],
                search_query=row.get('search_query'),
                product_id=row.get('product_id')
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
            # Process each CSV file in the directory
            for filename in os.listdir(directory):
                if filename.endswith('.csv'):
                    file_path = os.path.join(directory, filename)
                    table_name = filename.replace('.csv', '')
                    
                    logging.info(f"\nProcessing {filename}...")
                    
                    # Import data based on table name
                    if table_name == 'products':
                        import_products(file_path, session)
                    elif table_name == 'user':
                        import_users(file_path, session)
                    elif table_name == 'activity':
                        import_activities(file_path, session)
                    else:
                        logging.error(f"Unknown table: {table_name}")
        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        
        logging.info("\nImport process completed.")

if __name__ == "__main__":
    main()
