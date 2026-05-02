"""
Authentication module demonstrating secure credential handling.
All sensitive data is loaded from environment variables.
"""
import os
import hashlib
import hmac
import jwt
from datetime import datetime, timedelta

# Load authentication credentials from environment variables
api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('API_SECRET')
jwt_secret = os.environ.get('JWT_SECRET_KEY')
jwt_algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
jwt_expiration = int(os.environ.get('JWT_EXPIRATION_HOURS', '24'))


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass


def validate_api_key(provided_key):
    """
    Validate an API key against the configured key.
    
    Args:
        provided_key (str): The API key to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        AuthenticationError: If API_KEY is not configured
    """
    if not api_key:
        raise AuthenticationError("API_KEY not configured in environment variables")
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(provided_key, api_key)


def generate_jwt_token(user_id, additional_claims=None):
    """
    Generate a JWT token for a user.
    
    Args:
        user_id (str): The user identifier
        additional_claims (dict, optional): Additional claims to include in the token
        
    Returns:
        str: The encoded JWT token
        
    Raises:
        AuthenticationError: If JWT_SECRET_KEY is not configured
    """
    if not jwt_secret:
        raise AuthenticationError("JWT_SECRET_KEY not configured in environment variables")
    
    # Calculate expiration time
    expiration = datetime.utcnow() + timedelta(hours=jwt_expiration)
    
    # Build token payload
    payload = {
        'user_id': user_id,
        'exp': expiration,
        'iat': datetime.utcnow(),
        'iss': 'sample-clean-repo'
    }
    
    # Add any additional claims
    if additional_claims:
        payload.update(additional_claims)
    
    # Encode and return the token
    token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)
    return token


def verify_jwt_token(token):
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or JWT_SECRET_KEY is not configured
    """
    if not jwt_secret:
        raise AuthenticationError("JWT_SECRET_KEY not configured in environment variables")
    
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def verify_hmac_signature(message, signature):
    """
    Verify an HMAC signature for a message.
    
    Args:
        message (str): The message that was signed
        signature (str): The signature to verify
        
    Returns:
        bool: True if signature is valid, False otherwise
        
    Raises:
        AuthenticationError: If API_SECRET is not configured
    """
    if not api_secret:
        raise AuthenticationError("API_SECRET not configured in environment variables")
    
    # Calculate expected signature
    expected_signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Use constant-time comparison
    return hmac.compare_digest(signature, expected_signature)


def authenticate_request(api_key, signature, message):
    """
    Authenticate a request using API key and HMAC signature.
    
    Args:
        api_key (str): The API key provided in the request
        signature (str): The HMAC signature of the message
        message (str): The message that was signed
        
    Returns:
        bool: True if authentication succeeds
        
    Raises:
        AuthenticationError: If authentication fails
    """
    # Validate API key
    if not validate_api_key(api_key):
        raise AuthenticationError("Invalid API key")
    
    # Verify signature
    if not verify_hmac_signature(message, signature):
        raise AuthenticationError("Invalid signature")
    
    return True


class AuthClient:
    """
    Authentication client for managing user sessions and tokens.
    """
    
    def __init__(self):
        """Initialize the authentication client."""
        if not api_key or not api_secret or not jwt_secret:
            raise AuthenticationError(
                "Missing required environment variables: API_KEY, API_SECRET, JWT_SECRET_KEY"
            )
    
    def login(self, username, password_hash):
        """
        Authenticate a user and generate a session token.
        
        Args:
            username (str): The username
            password_hash (str): The hashed password
            
        Returns:
            str: JWT token for the authenticated session
        """
        # In a real application, verify credentials against a database
        # This is a simplified example
        
        # Generate JWT token
        token = generate_jwt_token(
            user_id=username,
            additional_claims={'auth_method': 'password'}
        )
        
        return token
    
    def verify_session(self, token):
        """
        Verify a session token.
        
        Args:
            token (str): The JWT token to verify
            
        Returns:
            dict: User information from the token
        """
        payload = verify_jwt_token(token)
        return {
            'user_id': payload.get('user_id'),
            'auth_method': payload.get('auth_method'),
            'expires_at': payload.get('exp')
        }
    
    def refresh_token(self, old_token):
        """
        Refresh an existing token.
        
        Args:
            old_token (str): The token to refresh
            
        Returns:
            str: New JWT token
        """
        # Verify the old token
        payload = verify_jwt_token(old_token)
        
        # Generate a new token with the same user_id
        new_token = generate_jwt_token(
            user_id=payload.get('user_id'),
            additional_claims={'auth_method': payload.get('auth_method')}
        )
        
        return new_token


# Example usage (for documentation purposes)
if __name__ == '__main__':
    print("Authentication Module - Secure Credential Handling Example")
    print("=" * 60)
    print("\nThis module demonstrates:")
    print("✓ Loading credentials from environment variables")
    print("✓ No hardcoded secrets in source code")
    print("✓ Secure token generation and validation")
    print("✓ HMAC signature verification")
    print("\nRequired environment variables:")
    print("- API_KEY")
    print("- API_SECRET")
    print("- JWT_SECRET_KEY")
    print("- JWT_ALGORITHM (optional, defaults to HS256)")
    print("- JWT_EXPIRATION_HOURS (optional, defaults to 24)")

# Made with Bob
