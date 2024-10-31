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

# Jakub Bartkowiak - v0.1 - 9-28-24
# Nya James & Mariam Lafi - v0.2 - 10-02-24
# [please add your name and version number (make sure to sync with the backend functions) if you change stuff - even if using github]

# =================== IMPORTS & BASE ======================== #

from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, CHAR, Enum # [Nya: New ForeignKey, Char, Enum]
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
    
# =================== PRODUCT TABLE ======================== #

# [Nya: added name of columns in product_id, title, tags, category, description, brand, popularity, ratings]
# [Nya: added __init__ function for Product]
# [Nya: added __repr__ function for Product]

class Product(Base):

    __tablename__ = 'products'
    product_id = Column("product_id", Integer, primary_key=True)
    title = Column("title", String)
    tags = Column("tags", String)
    category = Column("category", String)
    description = Column("description", String)
    brand = Column("brand", String)
    popularity = Column("popularity", Integer)  # Popularity score out of 1000
    ratings = Column("ratings", Float)  # Ratings out of 5.0

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
    def __repr__(self):
        return f"Product(title={self.title}, tags={self.tags}, category={self.category}, description={self.description}, brand={self.brand}, popularity={self.popularity}, ratings={self.ratings})"


# =================== PRODUCT_EMBEDDING TABLE ==================== #

# [Nya: added name of columns in product_id, embedding]

class ProductEmbedding(Base):
    __tablename__ = 'product_embeddings'
    product_id = Column("product_id", Integer, primary_key=True)
    embedding = Column("embedding", LargeBinary)  # Store the embedding as binary data


# ======================= USER TABLE ============================ #

# [Nya: New Tables in Activity, Order, Orderitems, account]
# [Nya: added name of columns in user_id, username, password, email]
# [Nya: added __init__ function for User]
# [Nya: added __repr__ function for User]
class User(Base):

    __tablename__ = 'users'

    user_id = Column("user_id", Integer, primary_key=True)
    username = Column("username", String)
    password = Column("password", String)
    email = Column("email", String)

    def __init__(self, username, password, email):
        
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f"User(username={self.username}, password={self.password}, email={self.email})"


# ======================= ACTIVITY TABLE ======================== #
# - Tracks users actions such as viewing, added to cart, and purchased

# [v02: added name of columns in user_id, activity_id, product_id, action, timestamp]
# [Nya: added __init__ function for Activity]
# [Nya: added __repr__ function for Activity]
class Activity(Base):

    __tablename__ = 'activity'
    activity_id = Column("activity_id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey('users.user_id'))
    product_id = Column("product_id", Integer, ForeignKey('products.product_id'))
    action = Column("action", Enum('viewed', 'added_to_cart', 'purchased'), nullable=False, default=['viewed', 'added_to_cart', 'purchased'])    
    timestamp = Column("timestamp", CHAR(20))


    def __init__(self, user_id, product_id, action, timestamp):

        self.user_id = user_id
        self.product_id = product_id
        self.action = action
        self.timestamp = timestamp


    def __repr__(self):
        return f"Activity(user_id={self.user_id}, product_id={self.product_id}, action={self.action}, timestamp={self.timestamp})"

# ======================= ORDER TABLE ========================== #
# Nya: added name of columns in user_id, total_amount, order_date, status
# Nya: added __init__ function for Order
# Nya: added __repr__ function for Order
class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    total_amount = Column(Integer)
    order_date = Column(CHAR(20))
    status = Column(Enum('processing', 'completed', 'cancelled'), nullable=False, default=['processing', 'completed', 'cancelled'])

    def __init__(self, user_id, total_amount, order_date, status):
        self.user_id = user_id
        self.total_amount = total_amount
        self.order_date = order_date
        self.status = status

    def __repr__(self):
        return f"Order(user_id={self.user_id}, total_amount={self.total_amount}, order_date={self.order_date}, status={self.status})"
    
# ======================= ORDER_ITEMS TABLE ==================== #
# Nya: added name of columns in order_id, product_id, quantity, price
# Nya: added __init__ function for Orderitems
# Nya: added __repr__ function for Orderitems
class Orderitems(Base):
    __tablename__ = 'orderitems'
    orderitem_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    price = Column(Integer)

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f"Orderitem(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity}, price={self.price})"

# ==================== SET UP DATABASE INFO ==================== #

# Setup the database engine and session

engine = create_engine('sqlite:///products.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ==================== DUMMY INFO ADDED ======================== #
