from sqlalchemy.orm import sessionmaker
from models import Product, engine

# Create a session
Session = sessionmaker(bind=engine)
session = Session()
# Dummy product data

dummy_products = [
    Product(
        title="Inception", description="A mind bending thriller by Christopher Nolan", price=14.99,
        category="Movie", rating=5, tags="['Thriller', 'Sci-Fi', 'Action']", popularity_score=950,
        brand="Warner Bros", release_date="2010-07-16", was_price=14.99, discount=0, link="",
        image="", embedding=None
    ),

    Product(
        title="The Matrix", description="A sci-fi action film about the nature of reality", price=12.34,
        category="Movie", rating=4.5, tags="['Action', 'Sci-Fi', 'Classic']", popularity_score=920,
        brand="Warner Bros", release_date="1999-03-31", was_price=12.99, discount=5, link="",
        image="", embedding=None
    ),

    Product(
        title="Interstellar", description="A space exploration movie by Christopher Nolan", price=14.44,
        category="Movie", rating=4, tags="['Sci-Fi', 'Adventure']", popularity_score=890,
        brand="Paramount Pictures", release_date="2014-11-07", was_price=16.99, discount=15, link="",
        image="", embedding=None
    ),

    Product(
        title="1984", description="Dystopian novel by George Orwell", price=7.99,
        category="Book", rating=3.5, tags="['Dystopia', 'Classic', 'Political']", popularity_score=850, 
        brand="Penguin Books", release_date="1949-06-08", was_price=9.99, discount=20, link="", 
        image="", embedding=None
    ),

    Product(
        title="Dune", description="Science fiction novel by Frank Herbert", price=13.99,
        category="Book", rating=3, tags="['Sci-Fi', 'Adventure']", popularity_score=870,
        brand="Chilton Books", release_date="1965-08-01", was_price=19.99, discount=30, link="",
        image="", embedding=None
    ),
    Product(
        title="The Great Gatsby", description="Classic novel by F. Scott Fitzgerald", price=5.84,
        category="Book", rating=2.5, tags="['Classic', 'Literature', 'Drama']", popularity_score=830,
        brand="Scribner", release_date="1925-04-10", was_price=8.99, discount=35, link="",
        image="", embedding=None
    ),
    Product(
        title="Nike Air Max", description="Comfortable and stylish running shoes by Nike", price=71.99,
        category="Clothing", rating=3.5, tags="['Shoes', 'Running', 'Comfort']", popularity_score=950,
        brand="Nike", release_date="2022-03-01", was_price=89.99, discount=20, link="",
        image="", embedding=None
    ),
    Product(
        title="Levi's 501 Jeans", description="Iconic straight-fit jeans by Levi's", price=50.99,
        category="Clothing", rating=4, tags="['Jeans', 'Casual', 'Denim']", popularity_score=910,
        brand="Levi's", release_date="2021-05-15", was_price=59.99, discount=15, link="",
        image="", embedding=None
    ),
    Product(
        title="Adidas Running Shoes", description="Lightweight running shoes by Adidas", price=52.49,
        category="Clothing", rating=3, tags="['Shoes', 'Running', 'Lightweight']", popularity_score=880,
        brand="Adidas", release_date="2023-06-05", was_price=74.99, discount=30, link="",
        image="", embedding=None
    ),
    Product(
        title="The Catcher in the Rye", description="Classic novel by J.D. Salinger", price=9.34,
        category="Book", rating=4, tags="['Classic', 'Literature', 'Drama']", popularity_score=840,
        brand="Little, Brown and Company", release_date="1951-07-16", was_price=10.99, discount=15, link="",
        image="", embedding=None
    ),
    Product(
        title="The Hobbit", description="Fantasy novel by J.R.R. Tolkien", price=14.24,
        category="Book", rating=4.5, tags="['Fantasy', 'Adventure']", popularity_score=860,
        brand="George Allen & Unwin", release_date="1937-09-21", was_price=14.99, discount=5, link="",
        image="", embedding=None
    ),
    Product(
        title="To Kill a Mockingbird", description="Pulitzer Prize-winning novel by Harper Lee", price=12.99,
        category="Book", rating=5, tags="['Classic', 'Drama', 'Legal']", popularity_score=870,
        brand="J.B. Lippincott & Co.", release_date="1960-07-11", was_price=12.99, discount=0, link="",
        image="", embedding=None
    ),
    Product(
        title="Puma Hoodie", description="Comfortable hoodie for casual wear", price=31.99,
        category="Clothing", rating=3.5, tags="['Hoodie', 'Casual', 'Comfort']", popularity_score=920,
        brand="Puma", release_date="2023-01-10", was_price=39.99, discount=20, link="",
        image="", embedding=None
    ),
    Product(
        title="Zara Denim Jacket", description="Stylish denim jacket for everyday fashion", price=48.99,
        category="Clothing", rating=3, tags="['Denim', 'Jacket', 'Fashion']", popularity_score=910,
        brand="Zara", release_date="2023-03-20", was_price=69.99, discount=30, link="",
        image="", embedding=None
    ),
    Product(
        title="Uniqlo T-Shirt", description="Basic T-shirt, lightweight and breathable", price=16.99,
        category="Clothing", rating=4, tags="['T-shirt', 'Basic', 'Casual']", popularity_score=900,
        brand="Uniqlo", release_date="2022-06-15", was_price=19.99, discount=15, link="",
        image="", embedding=None
    ),
    Product(
        title="Under Armour Shorts", description="Comfortable and durable workout shorts", price=28.49,
        category="Clothing", rating=4.5, tags="['Shorts', 'Sportswear', 'Workout']", popularity_score=930,
        brand="Under Armour", release_date="2022-09-05", was_price=29.99, discount=5, link="",
        image="", embedding=None
    ),
    Product(
        title="Blue Chunky Beanie", description="A stylish and cozy beanie for winter", price=13.59,
        category="Clothing", rating=4.7, tags="['Beanie', 'Winter', 'Wool']", popularity_score=760,
        brand="Uniqlo", release_date="2023-08-22", was_price=15.99, discount=15, link="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-beanie.png",
        image="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-beanie.png", embedding=None
    ),
    Product(
        title="Oversized Alpaca Crew", description="Oversized alpaca crew sweater for cold weather", price=18.74,
        category="Clothing", rating=4.1, tags="['Sweater', 'Casual', 'Alpaca']", popularity_score=880,
        brand="Nike", release_date="2021-07-03", was_price=24.99, discount=25, link="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-alpaca.png",
        image="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-alpaca.png", embedding=None
    ),
    Product(
        title="Diesel V2 Hoodie", description="Diesel V2 hoodie for comfort and style", price=33.99,
        category="Clothing", rating=4.9, tags="['Hoodie', 'Comfort', 'Cotton']", popularity_score=680,
        brand="Uniqlo", release_date="2021-06-12", was_price=39.99, discount=15, link="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-hoodie.png",
        image="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-hoodie.png", embedding=None
    ),
    Product(
        title="Round neck T-shirt", description="Round neck T-shirt for everyday wear", price=11.99,
        category="Clothing", rating=3.4, tags="['T-shirt', 'Casual', 'Cotton']", popularity_score=870,
        brand="Nike", release_date="2022-04-07", was_price=19.99, discount=40, link="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-round-neck.png",
        image="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-round-neck.png", embedding=None
    ),
    
    Product(
        title="Crossback Halter Dress", description="Crossback halter dress for casual and formal occasions", price=17.99,
        category="Clothing", rating=2.9, tags="['Dress', 'Fashion', 'Halter']", popularity_score=530,
        brand="Zara", release_date="2021-04-30", was_price=29.99, discount=40, link="",
        image="https://csimg.nyc3.cdn.digitaloceanspaces.com/Images/MISC/ecomm-halter.png", embedding=None
    ),
]

# Add all products to the session
session.add_all(dummy_products)

# Commit to the database
session.commit()

print("Dummy data inserted successfully.")