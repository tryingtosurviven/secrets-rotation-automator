"""
Secret Fixer Module - Automatically replaces hardcoded secrets with environment variables
Powered by IBM Bob for the Dev Day Hackathon
"""

import os
import re
import shutil
import logging
from typing import Dict, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def _generate_env_var_name(secret_type: str, file_path: str, line_number: int) -> str:
    """
    Generate a meaningful environment variable name based on context.
    
    Args:
        secret_type: Type of secret (API_KEY, PASSWORD, etc.)
        file_path: Path to the file containing the secret
        line_number: Line number where secret was found
        
    Returns:
        str: Generated environment variable name
    """
    # Extract service name from file path
    path_parts = Path(file_path).parts
    service_name = ""
    
    for part in path_parts:
        if part in ['auth', 'payment', 'api', 'database', 'db']:
            service_name = part.upper()
            break
    
    # Generate name based on secret type
    if service_name:
        return f"{service_name}_{secret_type}"
    else:
        return f"{secret_type}_{line_number}"


def _create_env_replacement(secret_type: str, env_var_name: str, file_ext: str) -> str:
    """
    Create the appropriate environment variable replacement code based on file type.
    
    Args:
        secret_type: Type of secret
        env_var_name: Name of the environment variable
        file_ext: File extension (.py, .js, .yml, etc.)
        
    Returns:
        str: Replacement code snippet
    """
    if file_ext in ['.py']:
        return f'os.getenv("{env_var_name}")'
    elif file_ext in ['.js', '.ts']:
        return f'process.env.{env_var_name}'
    elif file_ext in ['.yml', '.yaml']:
        return f'${{{env_var_name}}}'
    elif file_ext in ['.env']:
        return f'${{{env_var_name}}}'
    else:
        return f'${{{env_var_name}}}'


def _add_import_if_needed(content: str, file_ext: str) -> str:
    """
    Add necessary imports for environment variable access if not present.
    
    Args:
        content: File content
        file_ext: File extension
        
    Returns:
        str: Content with imports added if needed
    """
    if file_ext == '.py':
        if 'import os' not in content and 'from os import' not in content:
            # Add import at the beginning after any docstrings
            lines = content.split('\n')
            insert_pos = 0
            
            # Skip docstrings
            in_docstring = False
            for i, line in enumerate(lines):
                if '"""' in line or "'''" in line:
                    in_docstring = not in_docstring
                elif not in_docstring and line.strip() and not line.strip().startswith('#'):
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, 'import os')
            return '\n'.join(lines)
    
    return content


def fix_secret_in_file(file_path: str, secret_info: Dict, repo_path: str) -> Tuple[bool, str]:
    """
    Fix a single secret in a file by replacing it with an environment variable.
    
    Args:
        file_path: Absolute path to the file
        secret_info: Dictionary containing secret information
        repo_path: Root repository path
        
    Returns:
        Tuple[bool, str]: (Success status, message)
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        file_ext = Path(file_path).suffix.lower()
        line_num = secret_info['line_number'] - 1  # Convert to 0-based
        
        if line_num >= len(lines):
            return False, f"Line number {secret_info['line_number']} out of range"
        
        original_line = lines[line_num]
        secret_value = secret_info['secret_value']
        
        # Generate environment variable name
        env_var_name = _generate_env_var_name(
            secret_info['secret_type'],
            secret_info['file_path'],
            secret_info['line_number']
        )
        
        # Create replacement
        replacement = _create_env_replacement(secret_info['secret_type'], env_var_name, file_ext)
        
        # Replace the secret value in the line
        new_line = original_line.replace(secret_value, replacement)
        
        # If the line didn't change, try to replace quoted versions
        if new_line == original_line:
            new_line = original_line.replace(f'"{secret_value}"', replacement)
        if new_line == original_line:
            new_line = original_line.replace(f"'{secret_value}'", replacement)
        
        lines[line_num] = new_line
        new_content = '\n'.join(lines)
        
        # Add imports if needed
        new_content = _add_import_if_needed(new_content, file_ext)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Fixed secret in {file_path}:{secret_info['line_number']}")
        return True, f"Replaced with {env_var_name}"
    
    except Exception as e:
        logger.error(f"Error fixing secret in {file_path}: {e}")
        return False, str(e)


def create_env_file(secrets: List[Dict], repo_path: str) -> Tuple[bool, str, Dict[str, str]]:
    """
    Create a .env.example file with all the environment variables needed.
    
    Args:
        secrets: List of secret information dictionaries
        repo_path: Root repository path
        
    Returns:
        Tuple[bool, str, Dict]: (Success status, message, env_vars dictionary)
    """
    try:
        env_vars = {}
        
        for secret in secrets:
            env_var_name = _generate_env_var_name(
                secret['secret_type'],
                secret['file_path'],
                secret['line_number']
            )
            
            # Use placeholder value
            env_vars[env_var_name] = f"your_{secret['secret_type'].lower()}_here"
        
        # Create .env.example file
        env_example_path = os.path.join(repo_path, '.env.example')
        with open(env_example_path, 'w', encoding='utf-8') as f:
            f.write("# Environment Variables - Generated by IBM Bob\n")
            f.write("# Copy this file to .env and fill in your actual values\n\n")
            
            for var_name, placeholder in sorted(env_vars.items()):
                f.write(f"{var_name}={placeholder}\n")
        
        logger.info(f"Created .env.example with {len(env_vars)} variables")
        return True, f"Created .env.example with {len(env_vars)} variables", env_vars
    
    except Exception as e:
        logger.error(f"Error creating .env file: {e}")
        return False, str(e), {}


def create_backup(repo_path: str) -> Tuple[bool, str]:
    """
    Create a backup of the repository before making changes.
    
    Args:
        repo_path: Root repository path
        
    Returns:
        Tuple[bool, str]: (Success status, backup path or error message)
    """
    try:
        backup_path = f"{repo_path}_backup"
        
        # Remove existing backup if present
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        
        # Create backup
        shutil.copytree(repo_path, backup_path, 
                       ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules', '.venv'))
        
        logger.info(f"Created backup at {backup_path}")
        return True, backup_path
    
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False, str(e)


def fix_all_secrets(secrets: List[Dict], repo_path: str, create_backup_flag: bool = True) -> Dict:
    """
    Fix all detected secrets in the repository.
    
    Args:
        secrets: List of secret information dictionaries
        repo_path: Root repository path
        create_backup_flag: Whether to create a backup before fixing
        
    Returns:
        Dict: Results containing success status, fixed count, and details
    """
    results = {
        'success': False,
        'backup_created': False,
        'backup_path': None,
        'fixed_count': 0,
        'failed_count': 0,
        'env_file_created': False,
        'env_vars': {},
        'details': []
    }
    
    try:
        # Skip backup for sample-vulnerable-repo since we have a permanent backup
        if create_backup_flag and not repo_path.endswith('sample-vulnerable-repo'):
            backup_success, backup_result = create_backup(repo_path)
            results['backup_created'] = backup_success
            if backup_success:
                results['backup_path'] = backup_result
            else:
                results['details'].append({'error': f"Backup failed: {backup_result}"})
                return results
        elif repo_path.endswith('sample-vulnerable-repo'):
            # For sample-vulnerable-repo, we use the permanent backup
            results['backup_created'] = True
            results['backup_path'] = 'sample-vulnerable-repo_backup (permanent)'
        
        # Group secrets by file
        secrets_by_file = {}
        for secret in secrets:
            file_path = os.path.join(repo_path, secret['file_path'])
            if file_path not in secrets_by_file:
                secrets_by_file[file_path] = []
            secrets_by_file[file_path].append(secret)
        
        # Fix secrets in each file
        for file_path, file_secrets in secrets_by_file.items():
            # Sort by line number in reverse to avoid line number shifts
            file_secrets.sort(key=lambda x: x['line_number'], reverse=True)
            
            for secret in file_secrets:
                success, message = fix_secret_in_file(file_path, secret, repo_path)
                
                if success:
                    results['fixed_count'] += 1
                    results['details'].append({
                        'file': secret['file_path'],
                        'line': secret['line_number'],
                        'status': 'fixed',
                        'message': message
                    })
                else:
                    results['failed_count'] += 1
                    results['details'].append({
                        'file': secret['file_path'],
                        'line': secret['line_number'],
                        'status': 'failed',
                        'message': message
                    })
        
        # Create .env.example file
        env_success, env_message, env_vars = create_env_file(secrets, repo_path)
        results['env_file_created'] = env_success
        results['env_vars'] = env_vars
        
        if env_success:
            results['details'].append({
                'file': '.env.example',
                'status': 'created',
                'message': env_message
            })
        
        results['success'] = results['fixed_count'] > 0
        
        logger.info(f"Fixed {results['fixed_count']} secrets, {results['failed_count']} failed")
        return results
    
    except Exception as e:
        logger.error(f"Error fixing secrets: {e}")
        results['details'].append({'error': str(e)})
        return results

# Made with Bob
