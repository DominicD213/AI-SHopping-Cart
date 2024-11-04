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

from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Database configuration
user = os.environ.get('DB_USER', 'jbart')
password = os.environ.get('DB_PASSWORD', 'root99')
host = os.environ.get('DB_HOST', 'localhost')
database = os.environ.get('DB_NAME', 'ASCdb')

DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{database}"
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
    
    product_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    tags = Column(String(255))
    category = Column(String(100))
    description = Column(String(500))
    brand = Column(String(100))
    popularity = Column(Integer)  # Popularity score out of 1000
    ratings = Column(Float)  # Ratings out of 5.0

    def __init__(self, title, tags, category, description, brand, popularity, ratings):
        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self.brand = brand
        self.popularity = popularity
        self.ratings = ratings

    def __repr__(self):
        return (f"Product(title={self.title}, tags={self.tags}, category={self.category}, "
                f"description={self.description}, brand={self.brand}, popularity={self.popularity}, "
                f"ratings={self.ratings})")

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
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User(username={self.username}, email={self.email})"

# ==================== ACTIVITY TABLE ======================== #
class Activity(Base):
    """
    Activity Model
    -------------
    Tracks user interactions with the system for analytics and recommendations.
    
    Attributes:
        activity_id (int): Primary key
        user_id (int): Foreign key to User
        product_id (int): Foreign key to Product for views/cart/purchases
        action (str): Type of activity (search/view/cart/purchase)
        timestamp (datetime): When the activity occurred
    """
    __tablename__ = 'activity'
    
    activity_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'), nullable=True)
    action = Column(Enum('viewed', 'added_to_cart', 'purchased'), nullable=False, default='viewed')    
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    product = relationship("Product")

    def __init__(self, user_id, action, product_id=None):
        self.user_id = user_id
        self.action = action
        self.product_id = product_id

    def __repr__(self):
        return (f"Activity(user_id={self.user_id}, product_id={self.product_id}, "
                f"action={self.action}, timestamp={self.timestamp})")

# ======================= ORDER TABLE ========================== #
class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    total_amount = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('processing', 'completed', 'cancelled'), nullable=False, default='processing')

    user = relationship("User")

    def __init__(self, user_id, total_amount, status):
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status

    def __repr__(self):
        return (f"Order(user_id={self.user_id}, total_amount={self.total_amount}, "
                f"order_date={self.order_date}, status={self.status})")

# ======================= ORDER ITEMS TABLE ==================== #
class Orderitems(Base):
    __tablename__ = 'orderitems'
    
    orderitem_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order")

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return (f"OrderItem(order_id={self.order_id}, product_id={self.product_id}, "
                f"quantity={self.quantity}, price={self.price})")

# ==================== SET UP DATABASE INFO ==================== #
# Setup the database engine and session
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ==================== DUMMY INFO ADDED ======================== #
def seed_data(session):
    # Example: Add dummy products and users
    sample_user = User(username="sampleuser", password="password123", email="user@example.com")
    sample_product = Product(title="Sample Product", tags="sample, product", category="General", description="A sample product", brand="SampleBrand", popularity=100, ratings=4.5)

    session.add(sample_user)
    session.add(sample_product)
    session.commit()

# Uncomment to seed the database
# seed_data(session)
