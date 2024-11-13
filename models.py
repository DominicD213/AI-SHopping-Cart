"""
AI-Powered Shopping Tool - Data Models
======================================
Tracks version history for the database models used in the e-commerce system.
"""

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

v0.5 - 11-08-24 - Talon Jasper
    - Added admin role to User model with role-based access

v0.9 - 11-12-24 - System Update
    - Added additional fields for MoSCoW requirements
    - Enhanced user profile capabilities
    - Added product metadata fields
"""

# =================== IMPORTS & BASE ======================== #
from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, Enum, DateTime, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# Database configuration - Now with fallbacks
DATABASE_URI = os.getenv('DATABASE_URI', f"mysql+pymysql://{os.getenv('DB_USER', 'jbart')}:{os.getenv('DB_PASSWORD', 'root99')}@{os.getenv('DB_HOST', 'localhost')}/{os.getenv('DB_NAME', 'ASCdb')}")

Base = declarative_base()

# ==================== PRODUCT TABLE ======================== #
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

# ==================== ACTIVITY TABLE ======================== #
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

# ======================= ORDER TABLE ========================== #
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

# ======================= ORDER ITEMS TABLE ==================== #
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

# ================== DATABASE SETUP ===================== #
engine = create_engine(DATABASE_URI, echo=True)

Base.metadata.create_all(engine)

# ===================== DATABASE SESSION ================= #
Session = sessionmaker(bind=engine)
session = Session()

# Seed sample data
def seed_data(session):
    """Seed sample user and product data for testing"""
    sample_user = User(username="sampleuser", password="password123", email="user@example.com")
    session.add(sample_user)
    session.commit()

    sample_product = Product(title="Sample Product", tags="electronics, gadgets", 
                             category="Gadgets", description="An example product", brand="BrandX",
                             popularity=500, ratings=4.5)
    session.add(sample_product)
    session.commit()

    print("Dummy data has been added.")

# Run the seed function to add sample data
seed_data(session)
