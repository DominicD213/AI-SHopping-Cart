'''
AI-Powered Shopping Tool - Backend API
-----------------------------------------------------------------------------
Tracks version history for the Flask backend API used in the e-commerce system.
-----------------------------------------------------------------------------
# [please add your name and version number if you change stuff - even if using github]

Version History:
---------------
v0.1 - 9-28-24 - Jakub Bartkowiak
    - Initial implementation with basic product and user endpoints

v0.2 - 10-05-24 - Nya James & Mariam Lafi
    - Added authentication routes for login and registration
    - User roles (user/admin) were added to restrict access

v0.3 - 10-15-24 - Jakub Bartkowiak
    - Migrated from SQLite to MySQL
    - Integrated token-based authentication

v0.4 - 10-30-24 - Talon Jasper
    - Added activity tracking routes for viewing, cart addition, and purchase
    - Implemented detailed logging for user activities

v0.5 - 11-08-24 - Jakub Bartkowiak
    - Refined activity endpoints to include importance weights for tracking
    - Introduced error handling and custom exception classes

v0.6 - 11-10-24 - Jakub Bartkowiak
    - Added CartItem and OrderItem endpoints
    - Implemented product recommendations based on user activity
    - Introduced role-based access control for admin operations
    - Added consistent documentation headers and extensive comments

v0.7 - 11-11-24 - Jakub Bartkowiak
    - Enhanced error handling and logging
    - Added token expiry validation
    - Improved cart management endpoints

v0.8 - 11-12-24 - Jakub Bartkowiak
    - Added trending products endpoint
    - Enhanced recommendation system
    - Improved search functionality with filters
    - Added comprehensive error logging
'''

from flask import Flask, jsonify, request, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Base, Product, User, Activity, Order, OrderItem, CartItem
from search import search_products, suggest_products_for_item, get_trending_products
from validation import validate_input
from datetime import datetime, timedelta
import os
import jwt
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
Session = sessionmaker(bind=create_engine(os.getenv('DATABASE_URI')))
session = Session()

def generate_token(user_id):
    """Generate JWT token with 24-hour expiry"""
    expiry = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({'user_id': user_id, 'exp': expiry}, app.secret_key, algorithm='HS256')

def token_required(f):
    """Decorator to check for valid authentication tokens"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            data = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            user = session.query(User).get(data['user_id'])
            if not user or not user.is_token_valid():
                return jsonify({'message': 'Token is invalid or expired!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except SQLAlchemyError as e:
            logger.error(f"Database error in token verification: {str(e)}")
            session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
        return f(user, *args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Check if user already exists
        if session.query(User).filter(
            (User.username == data['username']) | 
            (User.email == data['email'])
        ).first():
            return jsonify({'message': 'Username or email already exists'}), 400
            
        # Create new user
        user = User(
            username=data['username'],
            password=data['password'],
            email=data['email']
        )
        session.add(user)
        session.commit()
        
        # Generate token
        token = generate_token(user.user_id)
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': user.user_id
        }), 201
    except SQLAlchemyError as e:
        logger.error(f"Registration error: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        user = session.query(User).filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = generate_token(user.user_id)
            user.refresh_token()
            session.commit()
            return jsonify({'token': token, 'user_id': user.user_id})
        return jsonify({'message': 'Invalid credentials'}), 401
    except SQLAlchemyError as e:
        logger.error(f"Login error: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products', methods=['GET'])
@token_required
def get_products(user):
    """Get products with role-based access control"""
    try:
        products = session.query(Product).all()
        output = []
        for p in products:
            product_data = {
                'product_id': p.product_id,
                'title': p.title,
                'category': p.category,
                'price': p.price,
                'ratings': p.ratings
            }
            if user.is_admin():
                product_data.update({
                    'popularity': p.popularity,
                    'tags': p.tags
                })
            output.append(product_data)
        return jsonify(output)
    except SQLAlchemyError as e:
        logger.error(f"Error fetching products: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@token_required
def add_to_cart(user, product_id):
    """Add item to cart and track for recommendations"""
    if user.role != 'user':
        return jsonify({'message': 'Admin users cannot add items to cart'}), 403
    
    try:
        product = session.query(Product).get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
            
        cart_item = session.query(CartItem).filter_by(
            user_id=user.user_id,
            product_id=product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=user.user_id, product_id=product_id)
            session.add(cart_item)
            
        activity = Activity(
            user_id=user.user_id,
            activity_type='cart',
            product_id=product_id
        )
        session.add(activity)
        session.commit()
        
        return jsonify({'message': 'Item added to cart successfully!'}), 201
    except SQLAlchemyError as e:
        logger.error(f"Error adding to cart: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@token_required
def remove_from_cart(user, product_id):
    """Remove item from cart"""
    if user.role != 'user':
        return jsonify({'message': 'Admin users cannot modify cart'}), 403
    
    try:
        cart_item = session.query(CartItem).filter_by(
            user_id=user.user_id,
            product_id=product_id
        ).first()
        
        if not cart_item:
            return jsonify({'message': 'Item not found in cart'}), 404
            
        session.delete(cart_item)
        session.commit()
        
        return jsonify({'message': 'Item removed from cart successfully!'}), 200
    except SQLAlchemyError as e:
        logger.error(f"Error removing from cart: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(user):
    """Get user's cart with recommendations"""
    try:
        cart_items = session.query(CartItem).filter_by(user_id=user.user_id).all()
        output = []
        
        for item in cart_items:
            product = session.query(Product).get(item.product_id)
            if product:
                output.append({
                    'product_id': product.product_id,
                    'title': product.title,
                    'quantity': item.quantity,
                    'price': product.price,
                    'added_date': item.added_date.isoformat()
                })
        
        recommendations = []
        if cart_items:
            latest_item = max(cart_items, key=lambda x: x.added_date)
            recommendations = suggest_products_for_item(
                latest_item.product_id,
                user.user_id
            )
        
        return jsonify({
            'cart_items': output,
            'recommendations': recommendations
        })
    except SQLAlchemyError as e:
        logger.error(f"Error fetching cart: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/checkout', methods=['POST'])
@token_required
def checkout(user):
    """Handle checkout process"""
    try:
        cart_items = session.query(CartItem).filter_by(user_id=user.user_id).all()
        if not cart_items:
            return jsonify({'message': 'Your cart is empty'}), 400
        
        total = 0
        for item in cart_items:
            product = session.query(Product).get(item.product_id)
            if product:
                total += product.price * item.quantity
        
        order = Order(
            user_id=user.user_id,
            total=total,
            order_date=datetime.utcnow()
        )
        session.add(order)
        session.commit()
        
        # Create order items
        for item in cart_items:
            product = session.query(Product).get(item.product_id)
            if product:
                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=product.price
                )
                session.add(order_item)
        
        # Clear the cart
        session.query(CartItem).filter_by(user_id=user.user_id).delete()
        session.commit()
        
        return jsonify({'message': 'Order placed successfully!', 'order_id': order.order_id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Error during checkout: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search', methods=['GET'])
def search():
    """Search for products by title or category"""
    query = request.args.get('query')
    if not query:
        return jsonify({'message': 'Search query missing'}), 400
    
    try:
        results = search_products(query)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending():
    """Get trending products"""
    try:
        trending_products = get_trending_products()
        return jsonify(trending_products)
    except Exception as e:
        logger.error(f"Trending error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
