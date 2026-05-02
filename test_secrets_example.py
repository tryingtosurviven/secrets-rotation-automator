"""
Example file with various types of demo secrets for testing the secret detector.
WARNING: These are demo placeholders only.
"""

# API Keys
STRIPE_API_KEY = "demo_stripe_live_key_placeholder_67890"
API_KEY_PROD = "demo_api_key_prod_placeholder_12345"
OPENAI_API_KEY = "demo_openai_api_key_placeholder_12345"

# Database Passwords
DB_PASSWORD = "demo_db_password_placeholder_12345"
MYSQL_PASSWORD = "demo_mysql_password_placeholder_12345"
POSTGRES_PASSWORD = "demo_postgres_password_placeholder_12345"
password = "demo_password_placeholder_12345"

# AWS Credentials
AWS_ACCESS_KEY_ID = "DEMO_AWS_ACCESS_KEY_PLACEHOLDER"
aws_secret_access_key = "demo_aws_secret_placeholder_value_12345"

# GitHub Tokens
GITHUB_TOKEN = "demo_github_token_placeholder_12345"
github_oauth_token = "demo_github_oauth_placeholder_12345"

# JWT Token
jwt_token = "demo.jwt.token.placeholder"

# Private Key (example)
private_key = """
-----BEGIN PRIVATE KEY-----
DEMO_PRIVATE_KEY_PLACEHOLDER_LINE_1
DEMO_PRIVATE_KEY_PLACEHOLDER_LINE_2
-----END PRIVATE KEY-----
"""

config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "username": "admin",
        "password": "demo_db_password_placeholder_12345"
    },
    "api": {
        "key": "demo_api_key_prod_placeholder_12345",
        "secret": "demo_api_secret_placeholder_12345"
    }
}

def connect_to_database():
    connection_string = "postgresql://user:demo_password_placeholder_12345@localhost:5432/mydb"
    return connection_string

def get_api_client():
    api_key = "demo_stripe_test_key_placeholder_12345"
    return api_key
