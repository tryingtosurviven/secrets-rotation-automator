"""
Example file with various types of secrets for testing the secret detector.
WARNING: These are example secrets only - not real credentials!
"""

# API Keys
STRIPE_API_KEY = "sk_live_51H8xyzABCDEF1234567890123456789"
API_KEY_PROD = "prod_api_key_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
OPENAI_API_KEY = "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"

# Database Passwords
DB_PASSWORD = "MySecureP@ssw0rd123"
MYSQL_PASSWORD = "mysql_root_password_2024"
POSTGRES_PASSWORD = "postgres_admin_pass"
password = "hardcoded_password"

# AWS Credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# GitHub Tokens
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz1234"
github_oauth_token = "gho_abcdefghijklmnopqrstuvwxyz1234567890ab"

# JWT Token
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Private Key (example - not a real key)
private_key = """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKj
MzEfYyjiWA4R4/M2bS1+fWIcPm15A8+raZ4Q
-----END PRIVATE KEY-----
"""

# Configuration with secrets
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "username": "admin",
        "password": "db_secret_password_123"
    },
    "api": {
        "key": "api_key_1234567890abcdefghijklmnop",
        "secret": "api_secret_9876543210zyxwvutsrqponmlk"
    }
}

def connect_to_database():
    """Example function with hardcoded credentials."""
    connection_string = "postgresql://user:MyP@ssw0rd@localhost:5432/mydb"
    return connection_string

def get_api_client():
    """Example function with API key."""
    api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
    return api_key

# Made with Bob
