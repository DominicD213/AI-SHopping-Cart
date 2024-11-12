"""
AI-Powered Shopping Tool - Data Import
Handles importing CSV files into database tables.
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI)

def import_csv_to_table(csv_path, table_name):
    """
    Import data from a CSV file into the specified database table.
    
    Args:
        csv_path (str): Path to the CSV file
        table_name (str): Name of the target database table
    """
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Import to database
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        
        logger.info(f"Successfully imported {csv_path} to {table_name}")
        
    except Exception as e:
        logger.error(f"Error importing {csv_path} to {table_name}: {str(e)}")
        raise

def import_all_data():
    """Import all CSV files to their corresponding tables."""
    try:
        # Map CSV files to table names
        csv_tables = {
            'Products_Table.csv': 'Products_Table',
            'Users_Table.csv': 'Users_Table',
            'Activity_Table.csv': 'Activity_Table',
            'Orders_Table.csv': 'Orders_Table',
            'OrderItems_Table.csv': 'OrderItems_Table',
            'CartItems_Table.csv': 'CartItems_Table',
            'ProductEmbeddings_Table.csv': 'ProductEmbeddings_Table'
        }
        
        # Import each CSV file
        for csv_file, table_name in csv_tables.items():
            if os.path.exists(csv_file):
                import_csv_to_table(csv_file, table_name)
            else:
                logger.info(f"Skipping {csv_file} - file not found")
                
    except Exception as e:
        logger.error(f"Error during data import: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        import_all_data()
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
