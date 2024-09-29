from sqlalchemy import create_engine, Column, Integer, String, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    title = Column(String)
    tags = Column(String)
    category = Column(String)
    description = Column(String)
    brand = Column(String)
    popularity = Column(Integer)  # Popularity score out of 1000
    ratings = Column(Float)  # Ratings out of 5.0

class ProductEmbedding(Base):
    __tablename__ = 'product_embeddings'
    product_id = Column(Integer, primary_key=True)
    embedding = Column(LargeBinary)  # Store the embedding as binary data

# Setup the database engine and session
engine = create_engine('sqlite:///products.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
