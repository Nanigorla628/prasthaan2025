# server.py (Python Backend for Login Authentication)

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging

# Set up basic logging to capture print statements in a structured way
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# This file MUST exist and contain 'email' and 'password' columns
USER_DATA_FILENAME = 'registration_data.xlsx' 

# --- Flask Setup ---
app = Flask(__name__)
# Enable CORS for local development compatibility
CORS(app) 

def load_user_data():
    """Loads and returns the DataFrame from the Excel file."""
    if not os.path.exists(USER_DATA_FILENAME):
        logging.error(f"User data file '{USER_DATA_FILENAME}' not found. Ensure it exists.")
        return None

    try:
        # Explicitly read data types as strings to ensure consistent comparison
        df = pd.read_excel(USER_DATA_FILENAME, dtype={'email': str, 'password': str})
        
        required_cols = ['email', 'password']
        # 'fullName' is nice to have but not strictly required for authentication
        
        # Check for required columns
        if not all(col in df.columns for col in required_cols):
            logging.error(f"'{USER_DATA_FILENAME}' is missing one or more required columns ({', '.join(required_cols)}).")
            return None
            
        # Strip leading/trailing whitespace from crucial columns
        df['email'] = df['email'].str.strip()
        df['password'] = df['password'].str.strip()

        return df
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}", exc_info=True)
        return None


@app.route('/login', methods=['POST'])
def login():
    """Authenticates the user against the data in the Excel file."""
    try:
        data = request.get_json() 
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Missing username or password'}), 400

        user_df = load_user_data()
        
        if user_df is None:
            # 503 Service Unavailable: The authentication data source is missing/corrupt
            return jsonify({'message': 'Authentication service is unavailable.'}), 503

        # Filter the DataFrame to find a matching email (username). Use .strip() for safety.
        user_match = user_df[user_df['email'] == username.strip()]
        
        if user_match.empty:
            # 401 Unauthorized: Failed attempt - use generic message
            return jsonify({'message': 'Invalid username or password.'}), 401
        
        # --- SECURITY WARNING ---
        # The comparison below is highly UNSECURE. In a production application, 
        # passwords MUST be hashed (e.g., using bcrypt) and stored securely.
        # DO NOT USE PLAINTEXT PASSWORDS IN PRODUCTION.
        stored_password = user_match['password'].iloc[0]
        
        # Safely get the full name
        full_name = user_match['fullName'].iloc[0] if 'fullName' in user_match.columns else 'User'
        
        # Use simple string comparison for this demonstration
        if stored_password == password:
            # Success
            logging.info(f"User {username} logged in successfully.")
            return jsonify({
                'message': 'Login successful',
                'user': full_name
            }), 200
        else:
            # Failure (Password mismatch) - use generic message
            return jsonify({'message': 'Invalid username or password.'}), 401

    except Exception as e:
        # Catch unexpected errors during the process
        logging.error(f"An unexpected error occurred during login: {e}", exc_info=True)
        return jsonify({'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    logging.info(f"Starting Authentication Server. It will use: {USER_DATA_FILENAME}")
    # Running in debug mode reloads the server on code changes
    app.run(port=8000, debug=True)