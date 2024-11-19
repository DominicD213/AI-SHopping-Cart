"""
AI-Powered Shopping Tool - Data Import
Handles importing CSV files into database tables.

Version History:
---------------
v1.0 - Initial implementation
v1.1 - Updated to use centralized database configuration from models.py
v1.2 - Improved CSV import handling:
       - Added proper NaN handling
       - Removed artificial grouping limitations
       - Made batch size configurable
       - Enhanced logging for import progress
v1.3 - Added ML/AI documentation markers
"""

import os
import pandas as pd
import numpy as np
from models import Base, Product, User, Activity, Session, initialize_database_config
import logging
from datetime import datetime

# Initialize database configuration
DATABASE_URI = initialize_database_config()

# Configuration
BATCH_SIZE = 20  # Number of records to process in each batch
LOG_FREQUENCY = 1000  # How often to log progress (number of records)

# Set up logging
logging.basicConfig(
    filename='data/data_import.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def handle_nan_value(value, default=0):  # [IMPOR-004-300]
    """Handle NaN values with appropriate defaults for ML features"""
    if pd.isna(value):
        return default
    return value

def import_products(file_path, session):  # [IMPOR-001-150]
    """Import product data from CSV with ML feature preparation"""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        total_records = len(df)
        logging.info(f"Starting import of {total_records} products from {file_path}")
        
        required_columns = ['title', 'tags', 'category', 'description', 'brand', 'popularity', 'ratings']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return
        
        # Process records
        records_processed = 0
        products_to_add = []
        
        for _, row in df.iterrows():
            product = Product(
                title=handle_nan_value(row['title'], ''),
                tags=handle_nan_value(row['tags'], ''),
                category=handle_nan_value(row['category'], 'Uncategorized'),
                description=handle_nan_value(row['description'], ''),
                brand=handle_nan_value(row['brand'], 'Unknown'),
                popularity=int(handle_nan_value(row['popularity'], 0)),
                ratings=float(handle_nan_value(row['ratings'], 0.0)),
                price=float(handle_nan_value(row.get('price'), 0.0)),
                was_price=float(handle_nan_value(row.get('was_price'), 0.0)),
                discount=float(handle_nan_value(row.get('discount'), 0.0))
            )
            products_to_add.append(product)
            records_processed += 1
            
            # Batch commit
            if len(products_to_add) >= BATCH_SIZE:
                session.bulk_save_objects(products_to_add)
                session.commit()
                products_to_add = []
            
            # Log progress
            if records_processed % LOG_FREQUENCY == 0:
                logging.info(f"Processed {records_processed}/{total_records} products")
        
        # Commit any remaining records
        if products_to_add:
            session.bulk_save_objects(products_to_add)
            session.commit()
        
        logging.info(f"Successfully imported {records_processed} products from {file_path}")
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing products from {file_path}: {e}")
        raise

def import_users(file_path, session):  # [IMPOR-002-200]
    """Import user data for ML-based recommendation system"""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        total_records = len(df)
        logging.info(f"Starting import of {total_records} users from {file_path}")
        
        required_columns = ['username', 'password', 'email']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return
        
        # Process records
        records_processed = 0
        users_to_add = []
        
        for _, row in df.iterrows():
            user = User(
                username=handle_nan_value(row['username'], f'user_{records_processed}'),
                password=handle_nan_value(row['password'], 'default_password'),
                email=handle_nan_value(row['email'], f'user_{records_processed}@example.com')
            )
            users_to_add.append(user)
            records_processed += 1
            
            # Batch commit
            if len(users_to_add) >= BATCH_SIZE:
                session.bulk_save_objects(users_to_add)
                session.commit()
                users_to_add = []
            
            # Log progress
            if records_processed % LOG_FREQUENCY == 0:
                logging.info(f"Processed {records_processed}/{total_records} users")
        
        # Commit any remaining records
        if users_to_add:
            session.bulk_save_objects(users_to_add)
            session.commit()
        
        logging.info(f"Successfully imported {records_processed} users from {file_path}")
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing users from {file_path}: {e}")
        raise

def import_activities(file_path, session):  # [IMPOR-003-250]
    """Import activity data for ML analysis and recommendations"""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        total_records = len(df)
        logging.info(f"Starting import of {total_records} activities from {file_path}")
        
        required_columns = ['user_id', 'activity_type']
        
        if not all(col in df.columns for col in required_columns):
            logging.error(f"Missing columns in {file_path}: {set(required_columns) - set(df.columns)}")
            return
        
        # Process records
        records_processed = 0
        activities_to_add = []
        
        for _, row in df.iterrows():
            activity = Activity(
                user_id=int(handle_nan_value(row['user_id'], 0)),
                action=handle_nan_value(row['activity_type'], 'viewed'),
                product_id=handle_nan_value(row.get('product_id'), None)
            )
            
            # Handle timestamp if present
            if 'timestamp' in row:
                timestamp = handle_nan_value(row['timestamp'], datetime.utcnow())
                if isinstance(timestamp, str):
                    activity.timestamp = pd.to_datetime(timestamp)
                else:
                    activity.timestamp = timestamp
            
            activities_to_add.append(activity)
            records_processed += 1
            
            # Batch commit
            if len(activities_to_add) >= BATCH_SIZE:
                session.bulk_save_objects(activities_to_add)
                session.commit()
                activities_to_add = []
            
            # Log progress
            if records_processed % LOG_FREQUENCY == 0:
                logging.info(f"Processed {records_processed}/{total_records} activities")
        
        # Commit any remaining records
        if activities_to_add:
            session.bulk_save_objects(activities_to_add)
            session.commit()
        
        logging.info(f"Successfully imported {records_processed} activities from {file_path}")
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error importing activities from {file_path}: {e}")
        raise

def import_csv_to_table(csv_path, table_name, session):  # [IMPOR-005-350]
    """
    Import data from a CSV file into the specified database table.
    Coordinates ML data preparation and storage.
    """
    try:
        logging.info(f"Starting import for {table_name} from {csv_path}")
        
        # Import to database based on table name
        if table_name == 'products':
            import_products(csv_path, session)
        elif table_name == 'users':
            import_users(csv_path, session)
        elif table_name == 'activity':
            import_activities(csv_path, session)
        else:
            logging.error(f"Unknown table: {table_name}")
            return
        
        logging.info(f"Successfully completed import of {table_name} from {csv_path}")
        
    except Exception as e:
        logging.error(f"Error importing {csv_path} to {table_name}: {str(e)}")
        raise

def main():
    """Main function to process all CSV files in the data directory"""
    start_time = datetime.now()
    logging.info(f"Starting import process at {start_time}")
    
    # Create database session
    session = Session()
    try:
        # Get the data directory path
        directory = os.path.join(os.path.dirname(__file__), 'data')
        
        # Process each CSV file in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory, filename)
                table_name = filename.replace('.csv', '').lower()  # Normalize to lowercase
                
                logging.info(f"\nProcessing {filename}...")
                import_csv_to_table(file_path, table_name, session)
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        session.close()
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"\nImport process completed at {end_time}")
        logging.info(f"Total duration: {duration}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
