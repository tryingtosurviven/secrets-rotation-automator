"""
Sample Vulnerable Repository Generator
Creates a realistic repository with intentionally hardcoded secrets for testing and demo purposes.

[WARNING] WARNING: This script creates files with FAKE hardcoded secrets for TESTING ONLY.
These are NOT real credentials and should NEVER be used in production.

Author: Bob
Date: 2026-05-01
"""

import os
import base64
from pathlib import Path
from typing import Dict


# Consistent test secrets used across multiple files
TEST_SECRETS = {
    'API_KEY_PROD': 'sk_live_abc123xyz789def456ghi789',
    'DB_PASSWORD': 'super_secret_password_123!@#',
    'DATABASE_HOST': 'prod-db.example.com',
    'DATABASE_USER': 'payment_user',
    'AWS_ACCESS_KEY': 'AKIAIOSFODNN7EXAMPLE',
    'AWS_SECRET_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    'GITHUB_TOKEN': 'ghp_1234567890abcdefghijklmnopqrstuvwxyz',
    'JWT_SECRET': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
    'STRIPE_KEY': 'sk_live_stripe_secret_key_here',
    'SENDGRID_API_KEY': 'SG.sendgrid_api_key_12345678901234567890',
    'MYSQL_ROOT_PASSWORD': 'mysql_root_pass_2024_prod'
}


def create_directory_structure(base_path: Path) -> None:
    """
    Create the directory structure for the sample repository.
    
    Args:
        base_path: Base path for the repository
    """
    directories = [
        base_path,
        base_path / 'src',
        base_path / 'config',
        base_path / 'k8s',
        base_path / '.github' / 'workflows'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("[+] Created directory structure")


def create_auth_py(base_path: Path) -> None:
    """
    Create src/auth.py with hardcoded API key vulnerabilities.
    
    Args:
        base_path: Base path for the repository
    """
    content = f'''"""
Authentication module for user management.
Handles user authentication and profile retrieval.
"""

# [WARNING] SECURITY VULNERABILITY: Hardcoded API key in source code
API_KEY_PROD = "{TEST_SECRETS['API_KEY_PROD']}"

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
    headers = {{
        'Authorization': f'Bearer {{API_KEY_PROD}}',
        'Content-Type': 'application/json'
    }}
    
    payload = {{
        'username': username,
        'password': password
    }}
    
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
        print(f"Authentication error: {{e}}")
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
    headers = {{
        'Authorization': f'Bearer {{API_KEY_PROD}}',
        'Content-Type': 'application/json'
    }}
    
    try:
        response = requests.get(
            f'https://api.example.com/users/{{user_id}}',
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
    """
    Refresh authentication token.
    
    Args:
        refresh_token: Current refresh token
        
    Returns:
        New access token if successful, None otherwise
    """
    # [WARNING] VULNERABILITY: Yet another usage of hardcoded API key
    headers = {{
        'Authorization': f'Bearer {{API_KEY_PROD}}',
        'Content-Type': 'application/json'
    }}
    
    payload = {{'refresh_token': refresh_token}}
    
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
        print(f"Token refresh error: {{e}}")
        return None


@app.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({{'error': 'Missing credentials'}}), 400
    
    user_data = authenticate(username, password)
    
    if user_data:
        return jsonify(user_data), 200
    return jsonify({{'error': 'Invalid credentials'}}), 401


@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    """User profile endpoint."""
    user_profile = get_user_profile(user_id)
    
    if user_profile:
        return jsonify(user_profile), 200
    return jsonify({{'error': 'User not found'}}), 404


if __name__ == '__main__':
    # [WARNING] VULNERABILITY: Running in debug mode with hardcoded secrets
    print(f"Starting auth service with API key: {{API_KEY_PROD}}")
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    file_path = base_path / 'src' / 'auth.py'
    file_path.write_text(content, encoding='utf-8')
    print(f"[+] Created src/auth.py (with hardcoded API key)")


def create_payment_py(base_path: Path) -> None:
    """
    Create src/payment.py with hardcoded database credentials.
    
    Args:
        base_path: Base path for the repository
    """
    content = f'''"""
Payment processing module.
Handles payment transactions and refunds.
"""

# [WARNING] SECURITY VULNERABILITY: Hardcoded database credentials
DB_PASSWORD = "{TEST_SECRETS['DB_PASSWORD']}"
DATABASE_HOST = "{TEST_SECRETS['DATABASE_HOST']}"
DATABASE_USER = "{TEST_SECRETS['DATABASE_USER']}"

import mysql.connector
from mysql.connector import Error
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime


class PaymentProcessor:
    """Payment processing class with database operations."""
    
    def __init__(self):
        """Initialize payment processor with database connection."""
        self.connection = None
        self.connect_to_database()
    
    def connect_to_database(self) -> None:
        """
        Establish database connection.
        [WARNING] VULNERABILITY: Using hardcoded credentials
        """
        try:
            # [WARNING] CRITICAL VULNERABILITY: Hardcoded database password
            self.connection = mysql.connector.connect(
                host=DATABASE_HOST,
                user=DATABASE_USER,
                password=DB_PASSWORD,
                database='payments_db',
                port=3306
            )
            
            if self.connection.is_connected():
                print(f"Connected to MySQL database at {{DATABASE_HOST}}")
                print(f"Using credentials: {{DATABASE_USER}}:{{DB_PASSWORD}}")
        
        except Error as e:
            print(f"Database connection error: {{e}}")
            self.connection = None
    
    def process_payment(self, card_number: str, amount: Decimal, 
                       customer_id: int) -> Optional[Dict]:
        """
        Process a payment transaction.
        
        Args:
            card_number: Customer's card number
            amount: Payment amount
            customer_id: Customer's unique identifier
            
        Returns:
            Transaction details if successful, None otherwise
        """
        if not self.connection or not self.connection.is_connected():
            # [WARNING] VULNERABILITY: Reconnecting with hardcoded credentials
            self.connect_to_database()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Insert payment transaction
            query = """
                INSERT INTO transactions 
                (customer_id, card_number, amount, status, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                customer_id,
                card_number,
                float(amount),
                'completed',
                datetime.now()
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            
            transaction_id = cursor.lastrowid
            
            # Retrieve transaction details
            cursor.execute(
                "SELECT * FROM transactions WHERE id = %s",
                (transaction_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            
            return result
        
        except Error as e:
            print(f"Payment processing error: {{e}}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def refund_payment(self, transaction_id: int) -> bool:
        """
        Process a refund for a transaction.
        
        Args:
            transaction_id: Transaction to refund
            
        Returns:
            True if refund successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            # [WARNING] VULNERABILITY: Another reconnection with hardcoded password
            print(f"Reconnecting to database with password: {{DB_PASSWORD}}")
            self.connect_to_database()
        
        try:
            cursor = self.connection.cursor()
            
            # Update transaction status
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
        """
        Retrieve transaction history for a customer.
        
        Args:
            customer_id: Customer's unique identifier
            
        Returns:
            List of transactions
        """
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
        """Close database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")


def main():
    """Main function for testing payment processor."""
    # [WARNING] VULNERABILITY: Printing database credentials
    print(f"Initializing payment processor...")
    print(f"Database: {{DATABASE_HOST}}")
    print(f"User: {{DATABASE_USER}}")
    print(f"Password: {{DB_PASSWORD}}")
    
    processor = PaymentProcessor()
    
    # Test payment processing
    result = processor.process_payment(
        card_number="4532123456789012",
        amount=Decimal("99.99"),
        customer_id=12345
    )
    
    if result:
        print(f"Payment processed: {{result}}")
    
    processor.close_connection()


if __name__ == '__main__':
    main()
'''
    
    file_path = base_path / 'src' / 'payment.py'
    file_path.write_text(content, encoding='utf-8')
    print(f"[+] Created src/payment.py (with hardcoded DB password)")


def create_production_env(base_path: Path) -> None:
    """
    Create config/production.env with multiple hardcoded secrets.
    
    Args:
        base_path: Base path for the repository
    """
    content = f'''# Production Environment Configuration
# [WARNING] WARNING: This file contains hardcoded secrets - DO NOT COMMIT TO VERSION CONTROL

# API Configuration
API_KEY_PROD={TEST_SECRETS['API_KEY_PROD']}
API_ENDPOINT=https://api.example.com/v1

# Database Configuration
DB_PASSWORD={TEST_SECRETS['DB_PASSWORD']}
DATABASE_HOST={TEST_SECRETS['DATABASE_HOST']}
DATABASE_USER={TEST_SECRETS['DATABASE_USER']}
DATABASE_PORT=3306
DATABASE_NAME=payments_db

# AWS Configuration
AWS_ACCESS_KEY={TEST_SECRETS['AWS_ACCESS_KEY']}
AWS_SECRET_KEY={TEST_SECRETS['AWS_SECRET_KEY']}
AWS_REGION=us-east-1
AWS_S3_BUCKET=prod-payment-files

# GitHub Configuration
GITHUB_TOKEN={TEST_SECRETS['GITHUB_TOKEN']}
GITHUB_REPO=company/payment-service

# JWT Configuration
JWT_SECRET={TEST_SECRETS['JWT_SECRET']}
JWT_EXPIRATION=3600

# Third-party Services
STRIPE_KEY={TEST_SECRETS['STRIPE_KEY']}
SENDGRID_API_KEY={TEST_SECRETS['SENDGRID_API_KEY']}

# Application Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=info
PORT=5000
'''
    
    file_path = base_path / 'config' / 'production.env'
    file_path.write_text(content, encoding='utf-8')
    print(f"[+] Created config/production.env (with multiple secrets)")


def create_docker_compose(base_path: Path) -> None:
    """
    Create docker-compose.yml with secrets in environment variables.
    
    Args:
        base_path: Base path for the repository
    """
    content = f'''version: '3.8'

services:
  # API Service
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: payment-api
    ports:
      - "5000:5000"
    environment:
      # [WARNING] SECURITY VULNERABILITY: Hardcoded secrets in docker-compose
      - API_KEY_PROD={TEST_SECRETS['API_KEY_PROD']}
      - DB_PASSWORD={TEST_SECRETS['DB_PASSWORD']}
      - DATABASE_HOST=db
      - DATABASE_USER={TEST_SECRETS['DATABASE_USER']}
      - AWS_ACCESS_KEY={TEST_SECRETS['AWS_ACCESS_KEY']}
      - AWS_SECRET_KEY={TEST_SECRETS['AWS_SECRET_KEY']}
      - GITHUB_TOKEN={TEST_SECRETS['GITHUB_TOKEN']}
      - JWT_SECRET={TEST_SECRETS['JWT_SECRET']}
      - STRIPE_KEY={TEST_SECRETS['STRIPE_KEY']}
      - APP_ENV=production
    depends_on:
      - db
      - redis
    networks:
      - payment-network
    restart: unless-stopped

  # Worker Service
  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    container_name: payment-worker
    environment:
      # [WARNING] VULNERABILITY: Same secrets exposed in worker service
      - API_KEY_PROD={TEST_SECRETS['API_KEY_PROD']}
      - DB_PASSWORD={TEST_SECRETS['DB_PASSWORD']}
      - DATABASE_HOST=db
      - DATABASE_USER={TEST_SECRETS['DATABASE_USER']}
      - AWS_ACCESS_KEY={TEST_SECRETS['AWS_ACCESS_KEY']}
      - AWS_SECRET_KEY={TEST_SECRETS['AWS_SECRET_KEY']}
      - SENDGRID_API_KEY={TEST_SECRETS['SENDGRID_API_KEY']}
    depends_on:
      - db
      - redis
    networks:
      - payment-network
    restart: unless-stopped

  # Database Service
  db:
    image: mysql:8.0
    container_name: payment-db
    ports:
      - "3306:3306"
    environment:
      # [WARNING] VULNERABILITY: Hardcoded database root password
      - MYSQL_ROOT_PASSWORD={TEST_SECRETS['MYSQL_ROOT_PASSWORD']}
      - MYSQL_DATABASE=payments_db
      - MYSQL_USER={TEST_SECRETS['DATABASE_USER']}
      - MYSQL_PASSWORD={TEST_SECRETS['DB_PASSWORD']}
    volumes:
      - db-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - payment-network
    restart: unless-stopped

  # Redis Service
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
    
    file_path = base_path / 'docker-compose.yml'
    file_path.write_text(content, encoding='utf-8')
    print(f"[+] Created docker-compose.yml (with secrets in env)")


def create_k8s_secrets(base_path: Path) -> None:
    """
    Create k8s/secrets.yaml with base64-encoded secrets.
    
    Args:
        base_path: Base path for the repository
    """
    # Base64 encode secrets
    secrets_encoded = {
        'api-key': base64.b64encode(TEST_SECRETS['API_KEY_PROD'].encode()).decode(),
        'db-password': base64.b64encode(TEST_SECRETS['DB_PASSWORD'].encode()).decode(),
        'github-token': base64.b64encode(TEST_SECRETS['GITHUB_TOKEN'].encode()).decode(),
        'aws-secret': base64.b64encode(TEST_SECRETS['AWS_SECRET_KEY'].encode()).decode(),
        'jwt-secret': base64.b64encode(TEST_SECRETS['JWT_SECRET'].encode()).decode(),
        'stripe-key': base64.b64encode(TEST_SECRETS['STRIPE_KEY'].encode()).decode()
    }
    
    content = f'''# Kubernetes Secrets Configuration
# [WARNING] SECURITY VULNERABILITY: Secrets stored in version control
# Even though base64 encoded, these are NOT encrypted and easily decoded

apiVersion: v1
kind: Secret
metadata:
  name: payment-service-secrets
  namespace: production
  labels:
    app: payment-service
    environment: production
type: Opaque
data:
  # [WARNING] VULNERABILITY: Base64 is NOT encryption - these can be easily decoded
  # Decode with: echo "<value>" | base64 -d
  
  # API Key: {TEST_SECRETS['API_KEY_PROD']}
  api-key: {secrets_encoded['api-key']}
  
  # Database Password: {TEST_SECRETS['DB_PASSWORD']}
  db-password: {secrets_encoded['db-password']}
  
  # GitHub Token: {TEST_SECRETS['GITHUB_TOKEN']}
  github-token: {secrets_encoded['github-token']}
  
  # AWS Secret Key: {TEST_SECRETS['AWS_SECRET_KEY']}
  aws-secret-key: {secrets_encoded['aws-secret']}
  
  # JWT Secret: {TEST_SECRETS['JWT_SECRET']}
  jwt-secret: {secrets_encoded['jwt-secret']}
  
  # Stripe Key: {TEST_SECRETS['STRIPE_KEY']}
  stripe-key: {secrets_encoded['stripe-key']}

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-service-config
  namespace: production
data:
  DATABASE_HOST: "{TEST_SECRETS['DATABASE_HOST']}"
  DATABASE_USER: "{TEST_SECRETS['DATABASE_USER']}"
  AWS_REGION: "us-east-1"
  APP_ENV: "production"
'''
    
    file_path = base_path / 'k8s' / 'secrets.yaml'
    file_path.write_text(content, encoding='utf-8')
    print(f"[+] Created k8s/secrets.yaml (with encoded secrets)")


def create_github_workflow(base_path: Path) -> None:
    """
    Create .github/workflows/deploy.yml with secrets in environment variables.
    
    Args:
        base_path: Base path for the repository
    """
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
    
    # [WARNING] SECURITY VULNERABILITY: Hardcoded secrets in workflow file
    env:
      API_KEY_PROD: {TEST_SECRETS['API_KEY_PROD']}
      DB_PASSWORD: {TEST_SECRETS['DB_PASSWORD']}
      AWS_ACCESS_KEY: {TEST_SECRETS['AWS_ACCESS_KEY']}
      AWS_SECRET_KEY: {TEST_SECRETS['AWS_SECRET_KEY']}
      GITHUB_TOKEN: {TEST_SECRETS['GITHUB_TOKEN']}
      STRIPE_KEY: {TEST_SECRETS['STRIPE_KEY']}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v
        env:
          # [WARNING] VULNERABILITY: Exposing secrets to test environment
          API_KEY: ${{{{ env.API_KEY_PROD }}}}
          DB_PASS: ${{{{ env.DB_PASSWORD }}}}
      
      - name: Build Docker image
        run: |
          echo "Building Docker image..."
          docker build -t payment-service:latest .
        env:
          # [WARNING] VULNERABILITY: Secrets available during build
          BUILDKIT_PROGRESS: plain
      
      - name: Configure AWS credentials
        run: |
          # [WARNING] CRITICAL VULNERABILITY: Hardcoded AWS credentials
          aws configure set aws_access_key_id ${{{{ env.AWS_ACCESS_KEY }}}}
          aws configure set aws_secret_access_key ${{{{ env.AWS_SECRET_KEY }}}}
          aws configure set region us-east-1
      
      - name: Deploy to ECS
        run: |
          echo "Deploying to production..."
          echo "Using API key: ${{{{ env.API_KEY_PROD }}}}"
          echo "Database password: ${{{{ env.DB_PASSWORD }}}}"
          
          # Deploy application
          aws ecs update-service \\
            --cluster production-cluster \\
            --service payment-service \\
            --force-new-deployment
      
      - name: Update Kubernetes secrets
        run: |
          # [WARNING] VULNERABILITY: Applying secrets from file
          kubectl apply -f k8s/secrets.yaml
          kubectl rollout restart deployment/payment-service -n production
        env:
          KUBECONFIG: /tmp/kubeconfig
      
      - name: Notify deployment
        run: |
          # [WARNING] VULNERABILITY: Secrets in notification
          curl -X POST https://hooks.slack.com/services/XXX/YYY/ZZZ \\
            -H 'Content-Type: application/json' \\
            -d '{{"text": "Deployed with API key: ${{{{ env.API_KEY_PROD }}}}" }}'
      
      - name: Health check
        run: |
          echo "Running health check..."
          curl -H "Authorization: Bearer ${{{{ env.API_KEY_PROD }}}}" \\
            https://api.example.com/health
'''
    
    file_path = base_path / '.github' / 'workflows' / 'deploy.yml'
    file_path.write_text(content, encoding='utf-8')
    print(f"[+] Created .github/workflows/deploy.yml (with secrets in env)")


def create_readme(base_path: Path) -> None:
    """
    Create README.md for the sample repository.
    
    Args:
        base_path: Base path for the repository
    """
    content = '''# Sample Vulnerable Repository

[WARNING] **WARNING: This repository contains intentionally hardcoded secrets for TESTING and DEMONSTRATION purposes only.**

## Purpose

This repository demonstrates common security vulnerabilities related to hardcoded secrets in source code. It is designed to be used with the Secret Detector tool for testing and educational purposes.

## Vulnerabilities Included

### 1. Hardcoded API Keys
- **Location**: `src/auth.py` (lines 5-6)
- **Type**: Production API key hardcoded in source code
- **Risk**: CRITICAL - Allows unauthorized access to external services

### 2. Hardcoded Database Credentials
- **Location**: `src/payment.py` (lines 4-6)
- **Type**: Database password, host, and username in source code
- **Risk**: CRITICAL - Direct database access possible

### 3. Environment File with Secrets
- **Location**: `config/production.env`
- **Type**: Multiple secrets in environment configuration
- **Risk**: CRITICAL - Complete system compromise possible

### 4. Docker Compose Secrets
- **Location**: `docker-compose.yml`
- **Type**: Secrets in container environment variables
- **Risk**: HIGH - Container compromise exposes all secrets

### 5. Kubernetes Secrets in Version Control
- **Location**: `k8s/secrets.yaml`
- **Type**: Base64-encoded secrets (not encrypted)
- **Risk**: CRITICAL - Easy to decode and exploit

### 6. GitHub Actions Workflow Secrets
- **Location**: `.github/workflows/deploy.yml`
- **Type**: Hardcoded secrets in CI/CD pipeline
- **Risk**: CRITICAL - Workflow logs may expose secrets

## Testing with Secret Detector

```bash
# Run secret detector on this repository
python secret_detector.py

# Or import and use programmatically
from secret_detector import detect_secrets

secrets = detect_secrets("sample-vulnerable-repo")
print(f"Found {len(secrets)} secrets")
```

## Expected Findings

The Secret Detector should find approximately **30+ secret occurrences** across all files, including:
- API keys (multiple occurrences)
- Database passwords (multiple occurrences)
- AWS credentials
- GitHub tokens
- JWT secrets
- Stripe keys
- SendGrid API keys

## Remediation

**DO NOT** use this code in production. Proper secret management should use:
- Environment variables (not committed to version control)
- Secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)
- Kubernetes secrets (with encryption at rest)
- GitHub Secrets (for CI/CD workflows)

## Disclaimer

All secrets in this repository are **FAKE** and for **TESTING PURPOSES ONLY**. They are not real credentials and should never be used in any production environment.
'''
    
    file_path = base_path / 'README.md'
    file_path.write_text(content, encoding='utf-8')
    print("[+] Created README.md (documentation)")


def main():
    """
    Main function to create the sample vulnerable repository.
    """
    print("\n" + "="*70)
    print("[*] Creating Sample Vulnerable Repository")
    print("="*70 + "\n")
    
    # Define base path
    base_path = Path('sample-vulnerable-repo')
    
    try:
        # Create directory structure
        create_directory_structure(base_path)
        
        # Create source files
        create_auth_py(base_path)
        create_payment_py(base_path)
        
        # Create configuration files
        create_production_env(base_path)
        create_docker_compose(base_path)
        create_k8s_secrets(base_path)
        create_github_workflow(base_path)
        
        # Create documentation
        create_readme(base_path)
        
        print("\n" + "="*70)
        print("[SUCCESS] Sample vulnerable repository created successfully!")
        print("="*70)
        print(f"\nLocation: {base_path.absolute()}")
        print(f"\nTest with: python secret_detector.py")
        print(f"   Or: from secret_detector import detect_secrets")
        print(f"       secrets = detect_secrets('{base_path}')")
        print("\n[WARNING] This repository contains FAKE secrets for TESTING ONLY")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error creating repository: {e}")
        raise


if __name__ == '__main__':
    main()

# Made with Bob
