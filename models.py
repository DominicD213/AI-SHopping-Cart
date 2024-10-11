# =================== DATA LOG ============================== #

# Jakub Bartkowiak - v0.1 - 9-28-24
# Nya James & Mariam Lafi - v0.2 - 10-02-24
# [please add your name and version number (make sure to sync with the backend functions) if you change stuff - even if using github]

# =================== IMPORTS & BASE ======================== #

from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary, ForeignKey, CHAR, Enum # [Nya: New ForeignKey, Char, Enum]
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

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
