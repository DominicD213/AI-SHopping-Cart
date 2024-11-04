"""
AI-Powered Shopping Tool - Flask Backend
======================================

Version History:
---------------
v0.1 - Initial Release
    - Basic Flask application setup
    - Simple user authentication

v0.2 - Authentication Enhancement
    - Added password hashing
    - Session management
    - User registration

v0.3 - 10-14-24 - Jakub Bartkowiak
    - Migrated to MySQL database
    - Enhanced security with werkzeug
    - Improved session handling

v0.4 - 10-28-24
    - Added CORS support for React frontend
    - Implemented activity tracking system
    - Added weighted importance for different activities
    - New endpoints for cart and purchase tracking
    - API versioning with /api prefix
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

from models import User, Activity, Product, engine
from search import search_products
from flask_sqlalchemy import SQLAlchemy

# ==================== APPLICATION SETUP ======================== #

load_dotenv()  # Load environment variables

app = Flask("__name__")
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://jbart:your_password@localhost/ASCdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# CORS Configuration
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],  # React development server
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True
    }
})

# ==================== HELPER FUNCTIONS ======================== #

def log_activity(db_session, user_id, activity_type, search_query=None, product_id=None):
    """
    Helper function to log user activities
    
    Parameters:
        db_session: SQLAlchemy session
        user_id: ID of the user performing the action
        activity_type: Type of activity (search/view/cart/purchase)
        search_query: Optional search term
        product_id: Optional product ID for views/cart/purchases
    """
    try:
        activity = Activity(
            user_id=user_id,
            activity_type=activity_type,
            search_query=search_query,
            product_id=product_id
        )
        db_session.add(activity)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        print(f"Error logging {activity_type} activity: {e}")
        raise

# ==================== API ROUTES ======================== #

@app.route("/")
def home():
    """Home route - renders main page with optional username"""
    return render_template('home.html', username=session.get('username'))

@app.route('/api/search', methods=['POST'])
def search():
    if 'username' not in session:
        return jsonify({'error': 'User must be logged in'}), 401

    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    results = search_products(query)

    # Log search activity
    db_session = db.session
    try:
        user = db_session.query(User).filter_by(username=session['username']).first()
        log_activity(db_session, user.user_id, 'search', search_query=query)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': 'Error processing search'}), 500

@app.route('/api/product/<int:product_id>', methods=['GET'])
def view_product(product_id):
    if 'username' not in session:
        return jsonify({'error': 'User must be logged in'}), 401

    db_session = db.session
    try:
        product = db_session.query(Product).get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        user = db_session.query(User).filter_by(username=session['username']).first()
        log_activity(db_session, user.user_id, 'view', product_id=product_id)

        return jsonify({
            'id': product.product_id,
            'title': product.title,
            'description': product.description,
            'brand': product.brand,
            'category': product.category,
            'ratings': product.ratings
        })
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'username' not in session:
        return jsonify({'error': 'User must be logged in'}), 401

    db_session = db.session
    try:
        user = db_session.query(User).filter_by(username=session['username']).first()
        log_activity(db_session, user.user_id, 'cart', product_id=product_id)
        return jsonify({'message': 'Product added to cart successfully'})
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/purchase', methods=['POST'])
def purchase():
    if 'username' not in session:
        return jsonify({'error': 'User must be logged in'}), 401

    product_ids = request.json.get('product_ids', [])
    if not product_ids:
        return jsonify({'error': 'No products specified'}), 400

    db_session = db.session
    try:
        user = db_session.query(User).filter_by(username=session['username']).first()
        for product_id in product_ids:
            log_activity(db_session, user.user_id, 'purchase', product_id=product_id)
        return jsonify({'message': 'Purchase logged successfully'})
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# ==================== AUTH ROUTES ======================== #

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    db_session = db.session
    try:
        user = db_session.query(User).filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            return jsonify({'message': 'Login successful', 'username': user.username})
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    finally:
        db_session.close()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not all([username, password, email]):
        return jsonify({'error': 'All fields are required'}), 400

    db_session = db.session
    try:
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db_session.add(new_user)
        db_session.commit()
        return jsonify({'message': 'Registration successful'})
    except Exception as e:
        db_session.rollback()
        print(f"Error during registration: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'})

# ==================== APPLICATION ENTRY ======================== #

if __name__ == "__main__":
    app.run(debug=True)
