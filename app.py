"""
AI-Powered Shopping Tool - Backend API
-----------------------------------------------------------------------------
Tracks version history for the Flask backend API used in the e-commerce system.
-----------------------------------------------------------------------------

Version History:
---------------
[Version history prior to v1.0 can be found in version_history.txt]

v1.0 - 11/19/24 - Jakub Bartkowiak
    - First stable release with complete API functionality
    - Secure authentication and session management
    - Role-based access control
    - Comprehensive error handling

v1.1 - 11/19/24 - Jakub Bartkowiak
    - Updated to use centralized database configuration
    - Improved session management
    - Enhanced error handling for database operations
    - Added detailed logging
"""

from flask import Flask, jsonify, request, abort
from sqlalchemy.exc import SQLAlchemyError
from models import (
    Base, Product, User, Activity, Order, OrderItem, CartItem,
    Session, initialize_database_config
)
from search import search_products, suggest_products_for_item, get_trending_products
from validation import validate_input
from datetime import datetime, timedelta
import os
import jwt
import logging
from functools import wraps
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database configuration
DATABASE_URI = initialize_database_config()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Session management
@contextmanager
def get_session():
    """Context manager for handling database sessions"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

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
            with get_session() as session:
                user = session.query(User).get(data['user_id'])
                if not user or not user.is_token_valid():
                    return jsonify({'message': 'Token is invalid or expired!'}), 401
                return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except SQLAlchemyError as e:
            logger.error(f"Database error in token verification: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        with get_session() as session:
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
            session.flush()  # Get user_id without committing
            
            # Generate token
            token = generate_token(user.user_id)
            return jsonify({
                'message': 'User registered successfully',
                'token': token,
                'user_id': user.user_id
            }), 201
    except SQLAlchemyError as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    try:
        data = request.get_json()
        with get_session() as session:
            user = session.query(User).filter_by(username=data['username']).first()
            if user and user.check_password(data['password']):
                token = generate_token(user.user_id)
                user.refresh_token()
                return jsonify({'token': token, 'user_id': user.user_id})
            return jsonify({'message': 'Invalid credentials'}), 401
    except SQLAlchemyError as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products', methods=['GET'])
@token_required
def get_products(user):
    """Get products with role-based access control"""
    try:
        with get_session() as session:
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
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@token_required
def add_to_cart(user, product_id):
    """Add item to cart and track for recommendations"""
    if user.role != 'user':
        return jsonify({'message': 'Admin users cannot add items to cart'}), 403
    
    try:
        with get_session() as session:
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
            
            return jsonify({'message': 'Item added to cart successfully!'}), 201
    except SQLAlchemyError as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@token_required
def remove_from_cart(user, product_id):
    """Remove item from cart"""
    if user.role != 'user':
        return jsonify({'message': 'Admin users cannot modify cart'}), 403
    
    try:
        with get_session() as session:
            cart_item = session.query(CartItem).filter_by(
                user_id=user.user_id,
                product_id=product_id
            ).first()
            
            if not cart_item:
                return jsonify({'message': 'Item not found in cart'}), 404
                
            session.delete(cart_item)
            
            return jsonify({'message': 'Item removed from cart successfully!'}), 200
    except SQLAlchemyError as e:
        logger.error(f"Error removing from cart: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(user):
    """Get user's cart with recommendations"""
    try:
        with get_session() as session:
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
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/checkout', methods=['POST'])
@token_required
def checkout(user):
    """Handle checkout process"""
    try:
        with get_session() as session:
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
            session.flush()  # Get order_id without committing
            
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
            
            return jsonify({'message': 'Order placed successfully!', 'order_id': order.order_id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Error during checkout: {str(e)}")
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

if __name__ == '__main__':
    app.run(debug=True)
