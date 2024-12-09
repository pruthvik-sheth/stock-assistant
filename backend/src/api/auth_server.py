from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import pbkdf2_sha256
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from logging import getLogger
from pythonjsonlogger import jsonlogger

# Initialize Flask app
app = Flask(__name__)
CORS(app, methods=["GET","POST"])

# Load environment variables
load_dotenv()

# Configure logging
logger = getLogger()
logHandler = jsonlogger.JsonFormatter()

# MongoDB connection
def get_db_connection():
    client = MongoClient(os.getenv('MONGO_URI'))
    return client[os.getenv('MONGO_DB_NAME')]

# Initialize MongoDB collections
def init_auth_db():
    try:
        db = get_db_connection()
        
        # Create users collection if it doesn't exist
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            
            # Create unique index on email
            db.users.create_index('email', unique=True)
            
        print("Auth database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing auth database: {e}")
        logger.error(f"Auth database initialization error: {str(e)}")
        raise

# Generate JWT token
def generate_token(user_id, email):
    try:
        payload = {
            'user_id': str(user_id),  # Convert ObjectId to string
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(
            payload,
            os.getenv('JWT_SECRET_KEY'),
            algorithm=os.getenv('JWT_ALGORITHM')
        )
        return token
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        return None

# Middleware to verify JWT token
def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET_KEY'),
            algorithms=[os.getenv('JWT_ALGORITHM')]
        )
        return payload
    except:
        return None

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Hash the password
        hashed_password = pbkdf2_sha256.hash(password)

        db = get_db_connection()

        # Check if user already exists
        if db.users.find_one({'email': email}):
            return jsonify({'error': 'User already exists'}), 409

        # Create new user document
        user = {
            'email': email,
            'password': hashed_password,
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow()
        }

        # Insert new user
        result = db.users.insert_one(user)
        user_id = result.inserted_id

        # Generate token
        token = generate_token(user_id, email)
        if not token:
            return jsonify({'error': 'Error generating token'}), 500

        return jsonify({
            'message': 'User created successfully',
            'token': token
        }), 201

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        db = get_db_connection()

        # Get user from database
        user = db.users.find_one({'email': email})

        if not user or not pbkdf2_sha256.verify(password, user['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate token
        token = generate_token(user['_id'], user['email'])
        if not token:
            return jsonify({'error': 'Error generating token'}), 500

        return jsonify({
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'message': 'Login successful',
            'token': token
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/validate', methods=['GET'])
def validate():
    try:
        # Check JWT token in header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401

        email = payload['email']
        db = get_db_connection()

        # Get user from database
        user = db.users.find_one({'email': email})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'message': 'Valid Token'
        }), 200

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_auth_db()
    app.run(debug=True, port=5000)