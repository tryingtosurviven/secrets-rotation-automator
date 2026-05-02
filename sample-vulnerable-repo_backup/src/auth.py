"""
Authentication module for user management.
Handles user authentication and profile retrieval.
"""

import os
API_KEY_PROD = "os.getenv("API_KEY_6")"

import requests
from flask import Flask, request, jsonify
from typing import Dict, Optional

app = Flask(__name__)

def authenticate(username: str, password: str) -> Optional[Dict]:
    headers = {
        "Authorization": f"Bearer {API_KEY_PROD}",
        "Content-Type": "application/json"
    }
    payload = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(
            "https://api.example.com/auth/login",
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
    headers = {
        "Authorization": f"Bearer {API_KEY_PROD}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(
            f"https://api.example.com/users/{user_id}",
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
    headers = {
        "Authorization": f"Bearer {API_KEY_PROD}",
        "Content-Type": "application/json"
    }
    payload = {"refresh_token": refresh_token}
    try:
        response = requests.post(
            "https://api.example.com/auth/refresh",
            json=payload,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except requests.RequestException as e:
        print(f"Token refresh error: {e}")
        return None

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user_data = authenticate(username, password)

    if user_data:
        return jsonify(user_data), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    user_profile = get_user_profile(user_id)
    if user_profile:
        return jsonify(user_profile), 200
    return jsonify({"error": "User not found"}), 404

if __name__ == "__main__":
    print(f"Starting auth service with API key: {API_KEY_PROD}")
    app.run(host="0.0.0.0", port=5000, debug=True)
