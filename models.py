# =================== DATA LOG ============================== #
"""
Version History:
---------------
v0.1 - 9-28-24 - Jakub Bartkowiak
    - Initial implementation of basic models
    - Created Product and User tables

v0.2 - 10-02-24 - Nya James & Mariam Lafi
    - Added user authentication features
    - Enhanced product model with additional fields

v0.3 - 10-14-24 - Jakub Bartkowiak
    - Migrated from SQLite to MySQL
    - Implemented password hashing using werkzeug.security
    - Added length specifications for MySQL columns

v0.4 - 10-28-24 - Jakub Bartkowiak
    - Added Activity tracking system
    - Implemented weighted importance for different activities
    - Added support for tracking searches, views, cart adds, and purchases
"""

# =================== IMPORTS & BASE ======================== #
from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, CHAR, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Database configuration
# TODO: Move these to environment variables for security
user = 'jbart'
password = 'root99'
host = 'localhost'
database = 'ASCdb'

Base = declarative_base()

# ==================== PRODUCT TABLE ======================== #
class Product(Base):
    """
    Product Model
    ------------
    Represents products in the e-commerce system.
    
    Attributes:
        product_id (int): Primary key
        title (str): Product name/title (max 255 chars)
        tags (str): Searchable tags/keywords (max 255 chars)
        category (str): Product category (max 100 chars)
        description (str): Product description (max 500 chars)
        brand (str): Product brand name (max 100 chars)
        popularity (int): Product popularity score
        ratings (float): Average product rating (0.0-5.0)
    """
    __tablename__ = 'products'
    product_id = Column("product_id", Integer, primary_key=True)
    title = Column("title", String(255))
    tags = Column("tags", String(255))
    category = Column("category", String(100))
    description = Column("description", String(500))
    brand = Column("brand", String(100))
    popularity = Column("popularity", Integer)
    ratings = Column("ratings", Float)

    def __init__(self, title, tags, category, description, brand, popularity, ratings):
        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self.brand = brand
        self.popularity = popularity
        self.ratings = ratings

# ==================== USER TABLE ======================== #
class User(Base):
    """
    User Model
    ----------
    Represents system users with authentication capabilities.
    
    Attributes:
        user_id (int): Primary key
        username (str): Unique username (max 50 chars)
        password_hash (str): Hashed password (max 255 chars)
        email (str): Unique email address (max 100 chars)
    
    Methods:
        check_password(password): Verifies if provided password matches hash
    """
    __tablename__ = 'user'
    user_id = Column("user_id", Integer, primary_key=True)
    username = Column("username", String(50), unique=True, nullable=False)
    password_hash = Column("password_hash", String(255), nullable=False)
    email = Column("email", String(100), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

# ==================== ACTIVITY TABLE ======================== #
class Activity(Base):
    """
    Activity Model
    -------------
    Tracks user interactions with the system for analytics and recommendations.
    
    Activity Types and Weights:
        - search (0.2): Lowest impact, tracks search queries
        - view (0.4): Medium-low impact, tracks product views
        - cart (0.7): Medium-high impact, tracks cart additions
        - purchase (1.0): Highest impact, tracks completed purchases
    
    Attributes:
        activity_id (int): Primary key
        user_id (int): Foreign key to User
        activity_type (str): Type of activity (search/view/cart/purchase)
        search_query (str): Search term if activity_type is 'search'
        product_id (int): Foreign key to Product for views/cart/purchases
        timestamp (datetime): When the activity occurred
        importance_weight (float): Weight for recommendation system
    """
    __tablename__ = 'activity'
    activity_id = Column("activity_id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey('user.user_id'), nullable=False)
    activity_type = Column("activity_type", String(20), nullable=False)
    search_query = Column("search_query", String(255), nullable=True)
    product_id = Column("product_id", Integer, ForeignKey('products.product_id'), nullable=True)
    timestamp = Column("timestamp", DateTime, nullable=False, default=datetime.utcnow)
    importance_weight = Column("importance_weight", Float, nullable=False)

    # Define relationships for easy access to related data
    user = relationship("User")
    product = relationship("Product")

    def __init__(self, user_id, activity_type, search_query=None, product_id=None):
        """
        Initialize activity with appropriate weight based on type.
        Weights determine impact on recommendation system:
        - Higher weights (purchases) have stronger influence
        - Lower weights (searches) have lesser influence
        """
        self.user_id = user_id
        self.activity_type = activity_type
        self.search_query = search_query
        self.product_id = product_id
        self.timestamp = datetime.utcnow()
        
        # Activity weights for recommendation system
        self.importance_weight = {
            'search': 0.2,    # Lowest impact
            'view': 0.4,      # Medium-low impact
            'cart': 0.7,      # Medium-high impact
            'purchase': 1.0   # Highest impact
        }.get(activity_type, 0.1)  # Default weight for unknown types

# ================== DATABASE SETUP ======================= #
# Set up MySQL database connection
DATABASE_URI = os.getenv("DATABASE_URI", "mysql+pymysql:{user}:{password}@{host}/{database}")
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
