'''
AI-Powered Shopping Tool - Data Models
----------------------------------------------------------------------------- 
Tracks version history for the database models used in the e-commerce system.
----------------------------------------------------------------------------- 
# [please add your name and version number if you change stuff - even if using github]

[Previous version history remains unchanged...]

v0.9 - 11-12-24 - System Update
    - Added additional fields for MoSCoW requirements
    - Enhanced user profile capabilities
    - Added product metadata fields
'''

from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, Enum, DateTime, Index, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

Base = declarative_base()

class Product(Base):
    """
    Product Model
    ------------
    Core product information with AI-optimized fields.
    
    AI Integration Points:
    - title and tags fields are used for semantic search via embeddings
    - popularity and ratings influence search result ranking
    - category field enables domain-specific embeddings training
    """
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    title = Column(String(255), index=True)  # Indexed for text search
    tags = Column(String(255))
    category = Column(String(100), index=True)  # Indexed for category filtering
    description = Column(String(500))
    brand = Column(String(100), index=True)  # Indexed for brand filtering
    popularity = Column(Integer)
    ratings = Column(Float, index=True)  # Indexed for rating-based filtering
    price = Column(Float, index=True)  # Added price field with index
    image_url = Column(String(500))  # Product image URL
    barcode = Column(String(100), index=True)  # For barcode scanning feature
    release_date = Column(DateTime)  # Product release date
    was_price = Column(Float)  # Original price for discount tracking
    discount = Column(Float)  # Current discount percentage
    link = Column(String(500))  # External product link

    # Create composite index for common filter combinations
    __table_args__ = (
        Index('idx_category_brand', 'category', 'brand'),
        Index('idx_price_rating', 'price', 'ratings'),
        Index('idx_barcode', 'barcode')
    )

    def __init__(self, title, tags, category, description, brand, popularity, ratings, price, 
                 image_url=None, barcode=None, release_date=None, was_price=None, discount=0, link=None):
        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self.brand = brand
        self.popularity = popularity
        self.ratings = ratings
        self.price = price
        self.image_url = image_url
        self.barcode = barcode
        self.release_date = release_date or datetime.utcnow()
        self.was_price = was_price or price
        self.discount = discount
        self.link = link

    def __repr__(self):
        return f"Product(title={self.title}, category={self.category}, brand={self.brand}, price={self.price})"

class User(Base):
    """
    User Model
    ----------
    User management with AI-enhanced security.
    
    AI Integration Points:
    - User activities are tracked for personalized recommendations
    - Role-based access controls recommendation algorithm access
    - Token expiry enables secure AI model access
    """
    __tablename__ = 'user'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(Enum('user', 'admin'), default='user', nullable=False)
    token_expiry = Column(DateTime)  # Added token expiry field
    profile_picture = Column(String(500))  # Profile picture URL
    last_login = Column(DateTime)  # Track last login time
    preferences = Column(JSON)  # Store user preferences as JSON
    is_active = Column(Boolean, default=True)  # Account status
    created_at = Column(DateTime, default=datetime.utcnow)
    social_auth_id = Column(String(100))  # For social media login

    def __init__(self, username, password, email, role='user', profile_picture=None, preferences=None):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email
        self.role = role
        self.profile_picture = profile_picture
        self.preferences = preferences or {}
        self.refresh_token()
        self.last_login = datetime.utcnow()

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if the user has admin privileges"""
        return self.role == 'admin'

    def refresh_token(self):
        """Refresh token expiry (24 hours from now)"""
        self.token_expiry = datetime.utcnow() + timedelta(hours=24)

    def is_token_valid(self):
        """Check if the user's token is still valid"""
        return self.token_expiry and self.token_expiry > datetime.utcnow()

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, role={self.role})"

class Activity(Base):
    """
    Activity Model
    -------------
    Tracks user interactions for AI-powered analytics.
    
    AI Integration Points:
    - Importance weights influence recommendation algorithms
    - Timestamp enables time-decay in recommendation relevance
    - Activity types guide different recommendation strategies
    - Search queries help train and improve search models
    """
    __tablename__ = 'activity'
    
    activity_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    activity_type = Column(String(20), nullable=False)
    search_query = Column(String(255), nullable=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    importance_weight = Column(Float, nullable=False)

    # Create indexes for frequent queries
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_product_activity', 'product_id', 'activity_type')
    )

    user = relationship("User")
    product = relationship("Product")

    def __init__(self, user_id, activity_type, search_query=None, product_id=None):
        self.user_id = user_id
        self.activity_type = activity_type
        self.search_query = search_query
        self.product_id = product_id
        self.timestamp = datetime.utcnow()
        self.importance_weight = {
            'search': 0.2,    # Lowest impact
            'view': 0.4,      # Medium-low impact
            'cart': 0.7,      # Medium-high impact
            'purchase': 1.0   # Highest impact
        }.get(activity_type, 0.1)

    def __repr__(self):
        return f"Activity(user_id={self.user_id}, activity_type={self.activity_type}, product_id={self.product_id})"

class ProductEmbedding(Base):
    """
    Product Embedding Model
    -----------------------
    Stores precomputed embeddings for AI-powered search.
    
    AI Integration Points:
    - Embeddings enable semantic similarity search
    - Vector representations support content-based recommendations
    - Facilitates real-time similarity computations
    """
    __tablename__ = 'product_embeddings'
    
    product_id = Column(Integer, ForeignKey('products.product_id'), primary_key=True)
    embedding = Column(LargeBinary)  # Stores 300-dimensional vector as binary

    product = relationship("Product")

class Order(Base):
    """
    Order Model
    -----------
    Tracks customer orders for AI analysis.
    
    AI Integration Points:
    - Order history influences recommendation weights
    - Purchase patterns help train prediction models
    - Order status affects recommendation timing
    """
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    total_amount = Column(Float)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('processing', 'completed', 'cancelled'), nullable=False)

    # Create index for user order history queries
    __table_args__ = (
        Index('idx_user_order_date', 'user_id', 'order_date'),
    )

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")

    def __init__(self, user_id, total_amount, status='processing'):
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status

    def __repr__(self):
        return f"Order(user_id={self.user_id}, total_amount={self.total_amount}, status={self.status})"

class OrderItem(Base):
    """
    OrderItem Model
    ---------------
    Represents items within orders for AI analysis.
    
    AI Integration Points:
    - Item combinations inform bundle recommendations
    - Quantity data helps predict inventory needs
    - Price points guide personalized pricing
    """
    __tablename__ = 'orderitems'
    
    orderitem_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    price = Column(Float)

    # Create index for product purchase history
    __table_args__ = (
        Index('idx_product_order', 'product_id', 'order_id'),
    )

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return f"OrderItem(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})"

class CartItem(Base):
    """
    CartItem Model
    --------------
    Tracks items in shopping carts for AI analysis.
    
    AI Integration Points:
    - Cart contents influence real-time recommendations
    - Abandoned cart analysis for retention strategies
    - Cart combination patterns for bundle suggestions
    """
    __tablename__ = 'cartitems'
    
    cartitem_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, default=1)
    added_date = Column(DateTime, default=datetime.utcnow)

    # Create indexes for frequent cart operations
    __table_args__ = (
        Index('idx_user_cart', 'user_id'),  # For retrieving user's cart
        Index('idx_cart_product', 'product_id'),  # For product-based cart queries
        Index('idx_user_product_cart', 'user_id', 'product_id', unique=True)  # Ensure unique user-product combinations
    )

    user = relationship("User")
    product = relationship("Product")

    def __init__(self, user_id, product_id, quantity=1):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
        self.added_date = datetime.utcnow()

    def __repr__(self):
        return f"CartItem(user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})"

# Database setup
DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
