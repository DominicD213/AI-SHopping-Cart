"""
AI-Powered Shopping Tool - Data Models
----------------------------------------------------------------------------- 
Tracks version history for the database models used in the e-commerce system.
----------------------------------------------------------------------------- 

Version History:
---------------
[please please remember to add your name, date, and version number if you change anything, even when using Github  - thanks, JB]
---------------

85%, 11/13


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

v0.5 - 11-08-24 - Talon Jasper
    - Added admin role to User model with role-based access

v0.6-0.9 - 11-11 to 11-12-24 - Jakub Bartkowiak
    - Expanded API endpoints for cart management and product recommendations
    - Integrated role-based access control
    - Added consistent documentation headers and extensive comments
    - Modified misunderstanding by TM, finishing move from SQLite to MySQL 
    - Ensured MySQL consistency across all modules
    - Added detailed front-end reference IDs for API integration
    - Enhanced error handling for data imports and search functionalities
    - Added CartItems and OrderItems tables
    - Expanded API endpoints for cart management and product recommendations
    - Added consistent documentation headers and extensive comments

v1.0-v1.3 - 11-15 to 11-17-24 - Jakub Bartkowiak
    - Removed automatic seed data execution
    - Made seed_data function optional for testing
    - Refined ProductEmbedding model for dynamic-dimensional product embeddings
    - Added dimension tracking for flexible embedding sizes (intent: 50 for testing, 300 for production)
    - Enhanced embedding storage with proper dimension tracking
    - Added dimensions field to ProductEmbedding for dynamic size support
    - Added price field to Product model for compatibility with import_data
    - Added was_price and discount fields for full product data supporu
    - TBD 11-17
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, Enum, DateTime, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# Database configuration - Now with fallbacks
DATABASE_URI = os.getenv('DATABASE_URI', f"mysql+pymysql://{os.getenv('MYSQL_USER', 'jbart')}:{os.getenv('MYSQL_PASSWORD', 'root99')}@{os.getenv('MYSQL_HOST', 'localhost')}/{os.getenv('MYSQL_DB', 'ASCdb')}")

Base = declarative_base()

class Product(Base):
    """
    Product Model
    ------------
    Represents products in the e-commerce system.
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
    price = Column(Float)  # Current price
    was_price = Column(Float)  # Original price before discount
    discount = Column(Float)  # Discount percentage

    def __init__(self, title, tags, category, description, brand, popularity, ratings, price=None, was_price=None, discount=None):
        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self.brand = brand
        self.popularity = popularity
        self.ratings = ratings
        self.price = price
        self.was_price = was_price
        self.discount = discount

    def __repr__(self):
        return (f"Product(title={self.title}, tags={self.tags}, category={self.category}, "
                f"description={self.description}, brand={self.brand}, popularity={self.popularity}, "
                f"ratings={self.ratings}, price={self.price}, was_price={self.was_price}, "
                f"discount={self.discount})")

class ProductEmbedding(Base):
    """
    Product Embedding Model
    ---------------------
    Stores dynamic-dimensional embeddings for products to enable semantic search and recommendations.
    Supports both testing (50-dimensional) and production (300-dimensional) environments.
    """
    __tablename__ = 'product_embeddings'
    
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'), primary_key=True)
    embedding = Column(LargeBinary, nullable=False)  # Stores vector as binary
    dimensions = Column(Integer, nullable=False)  # Stores the number of dimensions (50 or 300)
    
    product = relationship("Product")

    def __repr__(self):
        return f"ProductEmbedding(product_id={self.product_id}, dimensions={self.dimensions})"

class User(Base):
    """
    Represents system users with authentication capabilities and role-based access.
    """
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(Enum('user', 'admin'), default='user', nullable=False)

    activities = relationship("Activity", back_populates="user")
    orders = relationship("Order", back_populates="user")

    def __init__(self, username, password, email, role='user'):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.role = role

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if the user has admin privileges"""
        return self.role == 'admin'

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, role={self.role})"

class Activity(Base):
    """
    Tracks user interactions with the system for analytics and recommendations.
    """
    __tablename__ = 'activity'
    
    activity_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'), nullable=True)
    action = Column(Enum('viewed', 'added_to_cart', 'purchased'), nullable=False, default='viewed')    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activities")
    product = relationship("Product")

    def __init__(self, user_id, action, product_id=None):
        self.user_id = user_id
        self.action = action
        self.product_id = product_id

    def __repr__(self):
        return (f"Activity(user_id={self.user_id}, product_id={self.product_id}, "
                f"action={self.action}, timestamp={self.timestamp})")

class Order(Base):
    """
    Tracks customer orders for AI analysis.
    """
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'))
    total_amount = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('processing', 'completed', 'cancelled'), nullable=False, default='processing')

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

    def __init__(self, user_id, total_amount, status):
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status

    def __repr__(self):
        return (f"Order(user_id={self.user_id}, total_amount={self.total_amount}, "
                f"order_date={self.order_date}, status={self.status})")

class OrderItem(Base):
    __tablename__ = 'orderitems'
    
    orderitem_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey('products.product_id', ondelete='CASCADE'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return (f"OrderItem(order_id={self.order_id}, product_id={self.product_id}, "
                f"quantity={self.quantity}, price={self.price})")

# Database setup
engine = create_engine(DATABASE_URI, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def seed_data(session):
    """Seed sample user and product data for testing"""
    try:
        sample_user = User(username="sampleuser", password="password123", email="user@example.com")
        session.add(sample_user)
        session.commit()

        sample_product = Product(
            title="Sample Product", 
            tags="electronics, gadgets", 
            category="Gadgets", 
            description="An example product", 
            brand="BrandX",
            popularity=500, 
            ratings=4.5,
            price=99.99,
            was_price=129.99,
            discount=23.08
        )
        session.add(sample_product)
        session.commit()

        print("Dummy data has been added.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {str(e)}")
