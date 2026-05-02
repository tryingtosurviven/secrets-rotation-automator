"""
Authentication module for user management.
Handles user authentication and profile retrieval.
"""

# [WARNING] SECURITY VULNERABILITY: Hardcoded API key in source code
API_KEY_PROD = "sk_live_abc123xyz789def456ghi789"

import requests
from flask import Flask, request, jsonify
from typing import Dict, Optional


app = Flask(__name__)


def authenticate(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user against external API.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        User data if authentication successful, None otherwise
    """
    # [WARNING] VULNERABILITY: Using hardcoded API key for authentication
    headers = {
        'Authorization': f'Bearer {API_KEY_PROD}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(
            'https://api.example.com/auth/login',
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Authentication error: {e}")
        return None


def get_user_profile(user_id: int) -> Optional[Dict]:
    """
    Retrieve user profile from external API.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        User profile data if found, None otherwise
    """
    # [WARNING] VULNERABILITY: Reusing hardcoded API key
    headers = {
        'Authorization': f'Bearer {API_KEY_PROD}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'https://api.example.com/users/{user_id}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Profile retrieval error: {e}")
        return None


def refresh_token(refresh_token: str) -> Optional[str]:
    """
    Refresh authentication token.
    
    Args:
        refresh_token: Current refresh token
        
    Returns:
        New access token if successful, None otherwise
    """
    # [WARNING] VULNERABILITY: Yet another usage of hardcoded API key
    headers = {
        'Authorization': f'Bearer {API_KEY_PROD}',
        'Content-Type': 'application/json'
    }
    
    payload = {'refresh_token': refresh_token}
    
    try:
        response = requests.post(
            'https://api.example.com/auth/refresh',
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    except requests.RequestException as e:
        print(f"Token refresh error: {e}")
        return None


@app.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    
    user_data = authenticate(username, password)
    
    if user_data:
        return jsonify(user_data), 200
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    """User profile endpoint."""
    user_profile = get_user_profile(user_id)
    
    if user_profile:
        return jsonify(user_profile), 200
    return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    # [WARNING] VULNERABILITY: Running in debug mode with hardcoded secrets
    print(f"Starting auth service with API key: {API_KEY_PROD}")
    app.run(host='0.0.0.0', port=5000, debug=True)
