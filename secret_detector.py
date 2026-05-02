"""
Secret Detector Module for IBM Bob Dev Day Hackathon
Scans directories for hardcoded secrets including API keys, passwords, tokens, and more.

Author: Bob
Date: 2026-05-01
"""

import os
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directories to skip during scanning
SKIP_DIRECTORIES = {
    '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
    'dist', 'build', '.pytest_cache', '.tox', 'env'
}

# File extensions to scan
SCAN_EXTENSIONS = {
    '.py', '.js', '.env', '.yml', '.yaml', '.json', 
    '.sh', '.dockerfile', '.conf', '.config', '.ini'
}

# Regex patterns for different secret types
SECRET_PATTERNS = {
    'API_KEY': [
        re.compile(r'demo_stripe_live_key_placeholder_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'demo_stripe_test_key_placeholder_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'demo_api_key_prod_placeholder_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'demo_openai_api_key_placeholder_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'API_KEY[_\s]*[:=][_\s]*["\']?([a-zA-Z0-9_\-]{10,})["\']?', re.IGNORECASE),
        re.compile(r'APIKEY[_\s]*[:=][_\s]*["\']?([a-zA-Z0-9_\-]{10,})["\']?', re.IGNORECASE),
        re.compile(r'API[_\-]?KEY[_\-]?PROD[_\s]*[:=][_\s]*["\']?([a-zA-Z0-9_\-]{10,})["\']?', re.IGNORECASE),
    ],
    'PASSWORD': [
        re.compile(r'password[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'passwd[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'pwd[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'DB_PASSWORD[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'DATABASE_PASSWORD[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'MYSQL_PASSWORD[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'POSTGRES_PASSWORD[_\s]*[:=][_\s]*["\']([^"\']{3,})["\']', re.IGNORECASE),
        re.compile(r'demo_[a-zA-Z0-9_]*password[a-zA-Z0-9_]*', re.IGNORECASE),
    ],
    'AWS_KEY': [
        re.compile(r'DEMO_AWS_ACCESS_KEY_PLACEHOLDER', re.IGNORECASE),
        re.compile(r'demo_aws_secret_placeholder_value_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'aws_secret_access_key[_\s]*[:=][_\s]*["\']?([a-zA-Z0-9_\-]{10,})["\']?', re.IGNORECASE),
        re.compile(r'AWS_SECRET_ACCESS_KEY[_\s]*[:=][_\s]*["\']?([a-zA-Z0-9_\-]{10,})["\']?', re.IGNORECASE),
        re.compile(r'aws_access_key_id[_\s]*[:=][_\s]*["\']?(DEMO_AWS_ACCESS_KEY_PLACEHOLDER)["\']?', re.IGNORECASE),
    ],
    'GITHUB_TOKEN': [
        re.compile(r'demo_github_token_placeholder_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'demo_github_oauth_placeholder_[a-zA-Z0-9_]+', re.IGNORECASE),
        re.compile(r'github_token[_\s]*[:=][_\s]*["\']?([a-zA-Z0-9_\-]{10,})["\']?', re.IGNORECASE),
    ],
    'PRIVATE_KEY': [
        re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'),
        re.compile(r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----'),
        re.compile(r'-----BEGIN\s+EC\s+PRIVATE\s+KEY-----'),
        re.compile(r'-----BEGIN\s+DSA\s+PRIVATE\s+KEY-----'),
        re.compile(r'-----BEGIN\s+PGP\s+PRIVATE\s+KEY\s+BLOCK-----'),
    ],
    'JWT_TOKEN': [
        re.compile(r'demo\.jwt\.token\.placeholder', re.IGNORECASE),
    ],
}



def classify_secret_type(secret_value: str) -> str:
    """
    Classify the type of secret based on its value.
    
    Args:
        secret_value: The secret string to classify
        
    Returns:
        str: The secret type (API_KEY, PASSWORD, AWS_KEY, GITHUB_TOKEN, 
             PRIVATE_KEY, JWT_TOKEN, or UNKNOWN)
    """
    if not secret_value:
        return "UNKNOWN"
    
    for secret_type, patterns in SECRET_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(secret_value):
                logger.debug(f"Classified secret as {secret_type}")
                return secret_type
    
    logger.debug("Could not classify secret type")
    return "UNKNOWN"


def _should_skip_directory(dir_name: str) -> bool:
    """
    Check if a directory should be skipped during scanning.
    
    Args:
        dir_name: Name of the directory
        
    Returns:
        bool: True if directory should be skipped, False otherwise
    """
    return dir_name in SKIP_DIRECTORIES or dir_name.startswith('.')


def _should_scan_file(file_path: str) -> bool:
    """
    Check if a file should be scanned based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file should be scanned, False otherwise
    """
    file_name = Path(file_path).name.lower()
    file_ext = Path(file_path).suffix.lower()
    
    # Check for special files without extension or starting with dot
    if not file_ext or file_name.startswith('.'):
        special_files = ['dockerfile', 'makefile', 'jenkinsfile', '.env', '.env.local', '.env.production']
        return file_name in special_files
    
    return file_ext in SCAN_EXTENSIONS


def _get_context(file_path: str, line_number: int, lines: Optional[List[str]] = None) -> str:
    """
    Extract context around a specific line in a file.
    
    Args:
        file_path: Path to the file
        line_number: Line number (1-based)
        lines: Optional pre-read lines from the file
        
    Returns:
        str: Context string with surrounding lines
    """
    try:
        if lines is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        # Get 2 lines before and after (0-based indexing)
        start_line = max(0, line_number - 3)
        end_line = min(len(lines), line_number + 2)
        
        context_lines = []
        for i in range(start_line, end_line):
            line_num = i + 1
            prefix = ">>> " if line_num == line_number else "    "
            context_lines.append(f"{prefix}{line_num}: {lines[i].rstrip()}")
        
        return "\n".join(context_lines)
    
    except Exception as e:
        logger.warning(f"Could not extract context from {file_path}: {e}")
        return f"Line {line_number}: [Context unavailable]"


def _scan_file(file_path: str, repo_path: str) -> List[Dict]:
    """
    Scan a single file for secrets.
    
    Args:
        file_path: Absolute path to the file
        repo_path: Root repository path for relative path calculation
        
    Returns:
        List[Dict]: List of found secrets with metadata
    """
    secrets_found = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        relative_path = os.path.relpath(file_path, repo_path)
        
        for line_num, line in enumerate(lines, start=1):
            # Check each secret type
            for secret_type, patterns in SECRET_PATTERNS.items():
                for pattern in patterns:
                    matches = pattern.finditer(line)
                    for match in matches:
                        secret_value = match.group(0)
                        
                        # Skip common false positives
                        if _is_false_positive(secret_value, line):
                            continue
                        
                        context = _get_context(file_path, line_num, lines)
                        
                        secret_info = {
                            'secret_type': secret_type,
                            'secret_value': secret_value,
                            'file_path': relative_path,
                            'line_number': line_num,
                            'context': context,
                            'severity': 'CRITICAL'
                        }
                        
                        secrets_found.append(secret_info)
                        logger.info(f"Found {secret_type} in {relative_path}:{line_num}")
    
    except PermissionError:
        logger.warning(f"Permission denied: {file_path}")
    except UnicodeDecodeError:
        logger.warning(f"Encoding error: {file_path}")
    except Exception as e:
        logger.error(f"Error scanning {file_path}: {e}")
    
    return secrets_found


def _is_false_positive(secret_value: str, line: str) -> bool:
    """
    Check if a detected secret is likely a false positive.
    
    Args:
        secret_value: The detected secret value
        line: The full line containing the secret
        
    Returns:
        bool: True if likely a false positive, False otherwise
    """
    # Skip example/placeholder values
    false_positive_indicators = [
        'example', 'sample', 'dummy', 'fake',
        'your_', 'your-', 'xxx', '***', '...', 'todo', 'fixme',
        '<', '>', '{', '}', '[', ']', 'null', 'none', 'undefined'
    ]

    
    secret_lower = secret_value.lower()
    line_lower = line.lower()
    
    for indicator in false_positive_indicators:
        if indicator in secret_lower:
            return True
    
    # Skip very short passwords (likely not real)
    if 'password' in line_lower and len(secret_value) < 6:
        return True
    
    return False


def detect_secrets(repo_path: str) -> List[Dict]:
    """
    Scan a directory recursively for hardcoded secrets.
    
    Args:
        repo_path: Path to the repository/directory to scan
        
    Returns:
        List[Dict]: List of found secrets, each containing:
            - secret_type: Type of secret (API_KEY, PASSWORD, etc.)
            - secret_value: The actual secret value
            - file_path: Relative path to the file
            - line_number: Line number where secret was found
            - context: Code context around the secret
            - severity: Always "CRITICAL"
            
    Raises:
        ValueError: If repo_path does not exist
    """
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")
    
    if not os.path.isdir(repo_path):
        raise ValueError(f"Repository path is not a directory: {repo_path}")
    
    logger.info(f"Starting secret detection scan in: {repo_path}")
    all_secrets = []
    files_scanned = 0
    
    try:
        for root, dirs, files in os.walk(repo_path):
            # Filter out directories to skip
            dirs[:] = [d for d in dirs if not _should_skip_directory(d)]
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                if _should_scan_file(file_path):
                    files_scanned += 1
                    secrets = _scan_file(file_path, repo_path)
                    all_secrets.extend(secrets)
    
    except Exception as e:
        logger.error(f"Error during directory traversal: {e}")
    
    logger.info(f"Scan complete. Files scanned: {files_scanned}, Secrets found: {len(all_secrets)}")
    return all_secrets


def find_secret_usages(repo_path: str, secret_value: str) -> List[Dict]:
    """
    Find all locations where a specific secret value appears.
    
    Args:
        repo_path: Path to the repository/directory to scan
        secret_value: The specific secret value to search for
        
    Returns:
        List[Dict]: List of locations where the secret appears, each containing:
            - secret_type: Type of secret (classified)
            - secret_value: The secret value
            - file_path: Relative path to the file
            - line_number: Line number where secret was found
            - context: Code context around the secret
            - severity: Always "CRITICAL"
            
    Raises:
        ValueError: If repo_path does not exist or secret_value is empty
    """
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")
    
    if not secret_value:
        raise ValueError("Secret value cannot be empty")
    
    logger.info(f"Searching for secret usages in: {repo_path}")
    usages = []
    files_scanned = 0
    
    # Classify the secret type
    secret_type = classify_secret_type(secret_value)
    
    try:
        for root, dirs, files in os.walk(repo_path):
            # Filter out directories to skip
            dirs[:] = [d for d in dirs if not _should_skip_directory(d)]
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                if _should_scan_file(file_path):
                    files_scanned += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        relative_path = os.path.relpath(file_path, repo_path)
                        
                        for line_num, line in enumerate(lines, start=1):
                            if secret_value in line:
                                context = _get_context(file_path, line_num, lines)
                                
                                usage_info = {
                                    'secret_type': secret_type,
                                    'secret_value': secret_value,
                                    'file_path': relative_path,
                                    'line_number': line_num,
                                    'context': context,
                                    'severity': 'CRITICAL'
                                }
                                
                                usages.append(usage_info)
                                logger.info(f"Found secret usage in {relative_path}:{line_num}")
                    
                    except Exception as e:
                        logger.warning(f"Error scanning {file_path}: {e}")
    
    except Exception as e:
        logger.error(f"Error during directory traversal: {e}")
    
    logger.info(f"Search complete. Files scanned: {files_scanned}, Usages found: {len(usages)}")
    return usages


def main():
    """
    Example usage of the secret detector module.
    """
    # Example 1: Detect all secrets in current directory
    print("=" * 80)
    print("Example 1: Detecting secrets in current directory")
    print("=" * 80)
    
    try:
        secrets = detect_secrets(".")
        print(f"\nFound {len(secrets)} secret(s):\n")
        
        for i, secret in enumerate(secrets, 1):
            print(f"Secret #{i}:")
            print(f"  Type: {secret['secret_type']}")
            print(f"  File: {secret['file_path']}")
            print(f"  Line: {secret['line_number']}")
            print(f"  Severity: {secret['severity']}")
            print(f"  Value: {secret['secret_value'][:20]}..." if len(secret['secret_value']) > 20 else f"  Value: {secret['secret_value']}")
            print(f"  Context:\n{secret['context']}")
            print()
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Classify a secret
    print("=" * 80)
    print("Example 2: Classifying secret types")
    print("=" * 80)
    
    test_secrets = [
        "demo_stripe_live_key_placeholder_12345",
        "DEMO_AWS_ACCESS_KEY_PLACEHOLDER",
        "demo_github_token_placeholder_12345",
        "-----BEGIN PRIVATE KEY-----",
        "demo.jwt.token.placeholder"
    ]

    
    for secret in test_secrets:
        secret_type = classify_secret_type(secret)
        display_secret = secret[:50] + "..." if len(secret) > 50 else secret
        print(f"Secret: {display_secret}")
        print(f"Type: {secret_type}\n")
    
    # Example 3: Find specific secret usages
    print("=" * 80)
    print("Example 3: Finding specific secret usages")
    print("=" * 80)
    print("\nSearching for AWS key 'DEMO_AWS_ACCESS_KEY_PLACEHOLDER'...")
    
    try:
        usages = find_secret_usages(".", "DEMO_AWS_ACCESS_KEY_PLACEHOLDER")
        print(f"Found {len(usages)} usage(s)\n")
        
        for i, usage in enumerate(usages, 1):
            print(f"Usage #{i}:")
            print(f"  File: {usage['file_path']}")
            print(f"  Line: {usage['line_number']}")
            print()
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

# Made with Bob
