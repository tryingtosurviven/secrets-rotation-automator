"""
Sample Vulnerable Repository Generator
Creates a realistic repository with intentionally hardcoded demo secrets for testing and demo purposes.

WARNING: This script creates files with DEMO placeholders for TESTING ONLY.
These are NOT real credentials and should NEVER be used in production.
"""

import base64
from pathlib import Path

TEST_SECRETS = {
    "API_KEY_PROD": "demo_stripe_live_key_placeholder_12345",
    "DB_PASSWORD": "demo_db_password_placeholder_12345",
    "DATABASE_HOST": "prod-db.example.com",
    "DATABASE_USER": "payment_user",
    "AWS_ACCESS_KEY": "DEMO_AWS_ACCESS_KEY_PLACEHOLDER",
    "AWS_SECRET_KEY": "demo_aws_secret_placeholder_value_12345",
    "GITHUB_TOKEN": "demo_github_token_placeholder_12345",
    "JWT_SECRET": "demo.jwt.token.placeholder",
    "STRIPE_KEY": "demo_stripe_key_placeholder_12345",
    "SENDGRID_API_KEY": "demo_sendgrid_api_key_placeholder_12345",
    "MYSQL_ROOT_PASSWORD": "demo_mysql_root_password_placeholder",
}

def create_directory_structure(base_path: Path) -> None:
    directories = [
        base_path,
        base_path / "src",
        base_path / "config",
        base_path / "k8s",
        base_path / ".github" / "workflows",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    print("[+] Created directory structure")

def create_auth_py(base_path: Path) -> None:
    content = f'''"""
Authentication module for user management.
Handles user authentication and profile retrieval.
"""

API_KEY_PROD = "{TEST_SECRETS["API_KEY_PROD"]}"

import requests
from flask import Flask, request, jsonify
from typing import Dict, Optional

app = Flask(__name__)

def authenticate(username: str, password: str) -> Optional[Dict]:
    headers = {{
        "Authorization": f"Bearer {{API_KEY_PROD}}",
        "Content-Type": "application/json"
    }}
    payload = {{
        "username": username,
        "password": password
    }}
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
        print(f"Authentication error: {{e}}")
        return None

def get_user_profile(user_id: int) -> Optional[Dict]:
    headers = {{
        "Authorization": f"Bearer {{API_KEY_PROD}}",
        "Content-Type": "application/json"
    }}
    try:
        response = requests.get(
            f"https://api.example.com/users/{{user_id}}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        print(f"Profile retrieval error: {{e}}")
        return None

def refresh_token(refresh_token: str) -> Optional[str]:
    headers = {{
        "Authorization": f"Bearer {{API_KEY_PROD}}",
        "Content-Type": "application/json"
    }}
    payload = {{"refresh_token": refresh_token}}
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
        print(f"Token refresh error: {{e}}")
        return None

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({{"error": "Missing credentials"}}), 400

    user_data = authenticate(username, password)

    if user_data:
        return jsonify(user_data), 200
    return jsonify({{"error": "Invalid credentials"}}), 401

@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    user_profile = get_user_profile(user_id)
    if user_profile:
        return jsonify(user_profile), 200
    return jsonify({{"error": "User not found"}}), 404

if __name__ == "__main__":
    print(f"Starting auth service with API key: {{API_KEY_PROD}}")
    app.run(host="0.0.0.0", port=5000, debug=True)
'''
    file_path = base_path / "src" / "auth.py"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created src/auth.py (with hardcoded demo API key)")

def create_payment_py(base_path: Path) -> None:
    content = f'''"""
Payment processing module.
Handles payment transactions and refunds.
"""

DB_PASSWORD = "{TEST_SECRETS["DB_PASSWORD"]}"
DATABASE_HOST = "{TEST_SECRETS["DATABASE_HOST"]}"
DATABASE_USER = "{TEST_SECRETS["DATABASE_USER"]}"

import mysql.connector
from mysql.connector import Error
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime

class PaymentProcessor:
    def __init__(self):
        self.connection = None
        self.connect_to_database()

    def connect_to_database(self) -> None:
        try:
            self.connection = mysql.connector.connect(
                host=DATABASE_HOST,
                user=DATABASE_USER,
                password=DB_PASSWORD,
                database="payments_db",
                port=3306
            )
            if self.connection.is_connected():
                print(f"Connected to MySQL database at {{DATABASE_HOST}}")
                print(f"Using credentials: {{DATABASE_USER}}:{{DB_PASSWORD}}")
        except Error as e:
            print(f"Database connection error: {{e}}")
            self.connection = None

    def process_payment(self, card_number: str, amount: Decimal, customer_id: int) -> Optional[Dict]:
        if not self.connection or not self.connection.is_connected():
            self.connect_to_database()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                INSERT INTO transactions
                (customer_id, card_number, amount, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                customer_id,
                card_number,
                float(amount),
                "completed",
                datetime.now()
            )
            cursor.execute(query, values)
            self.connection.commit()

            transaction_id = cursor.lastrowid
            cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Payment processing error: {{e}}")
            if self.connection:
                self.connection.rollback()
            return None

    def refund_payment(self, transaction_id: int) -> bool:
        if not self.connection or not self.connection.is_connected():
            print(f"Reconnecting to database with password: {{DB_PASSWORD}}")
            self.connect_to_database()
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE transactions
                SET status = 'refunded', refunded_at = %s
                WHERE id = %s
            """
            cursor.execute(query, (datetime.now(), transaction_id))
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected > 0
        except Error as e:
            print(f"Refund processing error: {{e}}")
            if self.connection:
                self.connection.rollback()
            return False

    def get_transaction_history(self, customer_id: int) -> List[Dict]:
        if not self.connection or not self.connection.is_connected():
            self.connect_to_database()
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM transactions
                WHERE customer_id = %s
                ORDER BY created_at DESC
            """
            cursor.execute(query, (customer_id,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Transaction history error: {{e}}")
            return []

    def close_connection(self) -> None:
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

def main():
    print("Initializing payment processor...")
    print(f"Database: {{DATABASE_HOST}}")
    print(f"User: {{DATABASE_USER}}")
    print(f"Password: {{DB_PASSWORD}}")

    processor = PaymentProcessor()
    result = processor.process_payment(
        card_number="4532123456789012",
        amount=Decimal("99.99"),
        customer_id=12345
    )
    if result:
        print(f"Payment processed: {{result}}")

    processor.close_connection()

if __name__ == "__main__":
    main()
'''
    file_path = base_path / "src" / "payment.py"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created src/payment.py (with hardcoded demo DB password)")

def create_production_env(base_path: Path) -> None:
    content = f'''# Production Environment Configuration
# WARNING: This file contains demo placeholder secrets for testing only.

API_KEY_PROD={TEST_SECRETS["API_KEY_PROD"]}
API_ENDPOINT=https://api.example.com/v1

DB_PASSWORD={TEST_SECRETS["DB_PASSWORD"]}
DATABASE_HOST={TEST_SECRETS["DATABASE_HOST"]}
DATABASE_USER={TEST_SECRETS["DATABASE_USER"]}
DATABASE_PORT=3306
DATABASE_NAME=payments_db

AWS_ACCESS_KEY={TEST_SECRETS["AWS_ACCESS_KEY"]}
AWS_SECRET_KEY={TEST_SECRETS["AWS_SECRET_KEY"]}
AWS_REGION=us-east-1
AWS_S3_BUCKET=prod-payment-files

GITHUB_TOKEN={TEST_SECRETS["GITHUB_TOKEN"]}
GITHUB_REPO=company/payment-service

JWT_SECRET={TEST_SECRETS["JWT_SECRET"]}
JWT_EXPIRATION=3600

STRIPE_KEY={TEST_SECRETS["STRIPE_KEY"]}
SENDGRID_API_KEY={TEST_SECRETS["SENDGRID_API_KEY"]}

APP_ENV=production
DEBUG=false
LOG_LEVEL=info
PORT=5000
'''
    file_path = base_path / "config" / "production.env"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created config/production.env (with demo placeholder secrets)")

def create_docker_compose(base_path: Path) -> None:
    content = f'''version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: payment-api
    ports:
      - "5000:5000"
    environment:
      - API_KEY_PROD={TEST_SECRETS["API_KEY_PROD"]}
      - DB_PASSWORD={TEST_SECRETS["DB_PASSWORD"]}
      - DATABASE_HOST=db
      - DATABASE_USER={TEST_SECRETS["DATABASE_USER"]}
      - AWS_ACCESS_KEY={TEST_SECRETS["AWS_ACCESS_KEY"]}
      - AWS_SECRET_KEY={TEST_SECRETS["AWS_SECRET_KEY"]}
      - GITHUB_TOKEN={TEST_SECRETS["GITHUB_TOKEN"]}
      - JWT_SECRET={TEST_SECRETS["JWT_SECRET"]}
      - STRIPE_KEY={TEST_SECRETS["STRIPE_KEY"]}
      - APP_ENV=production
    depends_on:
      - db
      - redis
    networks:
      - payment-network
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    container_name: payment-worker
    environment:
      - API_KEY_PROD={TEST_SECRETS["API_KEY_PROD"]}
      - DB_PASSWORD={TEST_SECRETS["DB_PASSWORD"]}
      - DATABASE_HOST=db
      - DATABASE_USER={TEST_SECRETS["DATABASE_USER"]}
      - AWS_ACCESS_KEY={TEST_SECRETS["AWS_ACCESS_KEY"]}
      - AWS_SECRET_KEY={TEST_SECRETS["AWS_SECRET_KEY"]}
      - SENDGRID_API_KEY={TEST_SECRETS["SENDGRID_API_KEY"]}
    depends_on:
      - db
      - redis
    networks:
      - payment-network
    restart: unless-stopped

  db:
    image: mysql:8.0
    container_name: payment-db
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD={TEST_SECRETS["MYSQL_ROOT_PASSWORD"]}
      - MYSQL_DATABASE=payments_db
      - MYSQL_USER={TEST_SECRETS["DATABASE_USER"]}
      - MYSQL_PASSWORD={TEST_SECRETS["DB_PASSWORD"]}
    volumes:
      - db-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - payment-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: payment-redis
    ports:
      - "6379:6379"
    networks:
      - payment-network
    restart: unless-stopped

networks:
  payment-network:
    driver: bridge

volumes:
  db-data:
    driver: local
'''
    file_path = base_path / "docker-compose.yml"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created docker-compose.yml (with demo placeholder secrets)")

def create_k8s_secrets(base_path: Path) -> None:
    secrets_encoded = {
        "api-key": base64.b64encode(TEST_SECRETS["API_KEY_PROD"].encode()).decode(),
        "db-password": base64.b64encode(TEST_SECRETS["DB_PASSWORD"].encode()).decode(),
        "github-token": base64.b64encode(TEST_SECRETS["GITHUB_TOKEN"].encode()).decode(),
        "aws-secret": base64.b64encode(TEST_SECRETS["AWS_SECRET_KEY"].encode()).decode(),
        "jwt-secret": base64.b64encode(TEST_SECRETS["JWT_SECRET"].encode()).decode(),
        "stripe-key": base64.b64encode(TEST_SECRETS["STRIPE_KEY"].encode()).decode(),
    }

    content = f'''apiVersion: v1
kind: Secret
metadata:
  name: payment-service-secrets
  namespace: production
  labels:
    app: payment-service
    environment: production
type: Opaque
data:
  api-key: {secrets_encoded["api-key"]}
  db-password: {secrets_encoded["db-password"]}
  github-token: {secrets_encoded["github-token"]}
  aws-secret-key: {secrets_encoded["aws-secret"]}
  jwt-secret: {secrets_encoded["jwt-secret"]}
  stripe-key: {secrets_encoded["stripe-key"]}

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-service-config
  namespace: production
data:
  DATABASE_HOST: "{TEST_SECRETS["DATABASE_HOST"]}"
  DATABASE_USER: "{TEST_SECRETS["DATABASE_USER"]}"
  AWS_REGION: "us-east-1"
  APP_ENV: "production"
'''
    file_path = base_path / "k8s" / "secrets.yaml"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created k8s/secrets.yaml (with encoded demo placeholders)")

def create_github_workflow(base_path: Path) -> None:
    content = f'''name: Deploy to Production

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy Payment Service
    runs-on: ubuntu-latest

    env:
      API_KEY_PROD: {TEST_SECRETS["API_KEY_PROD"]}
      DB_PASSWORD: {TEST_SECRETS["DB_PASSWORD"]}
      AWS_ACCESS_KEY: {TEST_SECRETS["AWS_ACCESS_KEY"]}
      AWS_SECRET_KEY: {TEST_SECRETS["AWS_SECRET_KEY"]}
      GITHUB_TOKEN: {TEST_SECRETS["GITHUB_TOKEN"]}
      STRIPE_KEY: {TEST_SECRETS["STRIPE_KEY"]}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/ -v
        env:
          API_KEY: \${{{{ env.API_KEY_PROD }}}}
          DB_PASS: \${{{{ env.DB_PASSWORD }}}}

      - name: Build Docker image
        run: |
          echo "Building Docker image..."
          docker build -t payment-service:latest .

      - name: Configure AWS credentials
        run: |
          echo "Configuring demo AWS credentials"
          echo "\${{{{ env.AWS_ACCESS_KEY }}}}"
          echo "\${{{{ env.AWS_SECRET_KEY }}}}"

      - name: Deploy to ECS
        run: |
          echo "Deploying to production..."
          echo "Using API key: \${{{{ env.API_KEY_PROD }}}}"
          echo "Database password: \${{{{ env.DB_PASSWORD }}}}"

      - name: Update Kubernetes secrets
        run: |
          kubectl apply -f k8s/secrets.yaml
          kubectl rollout restart deployment/payment-service -n production
        env:
          KUBECONFIG: /tmp/kubeconfig

      - name: Notify deployment
        run: |
          echo "Deployment notification sent"

      - name: Health check
        run: |
          echo "Running health check..."
'''
    file_path = base_path / ".github" / "workflows" / "deploy.yml"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created .github/workflows/deploy.yml (with demo placeholder secrets)")

def create_readme(base_path: Path) -> None:
    content = '''# Sample Vulnerable Repository

WARNING: This repository contains intentionally hardcoded demo placeholder secrets for TESTING and DEMONSTRATION purposes only.

## Purpose
This repository demonstrates common security vulnerabilities related to hardcoded secrets in source code. It is designed to be used with the Secret Detector tool for testing and educational purposes.

## Disclaimer
All secrets in this repository are DEMO placeholders and for TESTING PURPOSES ONLY.
'''
    file_path = base_path / "README.md"
    file_path.write_text(content, encoding="utf-8")
    print("[+] Created README.md (documentation)")

def main():
    print("\\n" + "=" * 70)
    print("[*] Creating Sample Vulnerable Repository")
    print("=" * 70 + "\\n")

    base_path = Path("sample-vulnerable-repo")

    create_directory_structure(base_path)
    create_auth_py(base_path)
    create_payment_py(base_path)
    create_production_env(base_path)
    create_docker_compose(base_path)
    create_k8s_secrets(base_path)
    create_github_workflow(base_path)
    create_readme(base_path)

    print("\\n" + "=" * 70)
    print("[SUCCESS] Sample vulnerable repository created successfully!")
    print("=" * 70)
    print(f"\\nLocation: {base_path.absolute()}")
    print("\\n[WARNING] This repository contains DEMO placeholders for TESTING ONLY")
    print("=" * 70 + "\\n")

if __name__ == "__main__":
    main()
