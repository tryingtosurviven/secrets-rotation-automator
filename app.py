"""
Secrets Rotation Automator - Flask REST API
Production-ready Flask 3.x application for secret detection and rotation planning.

Author: Bob
Date: 2026-05-01
Version: 1.0.0
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import secret detector functions
from secret_detector import (
    detect_secrets,
    find_secret_usages,
    classify_secret_type
)

# Configuration constants
DEBUG = True
PORT = 5000
HOST = '0.0.0.0'
VERSION = '1.0.0'
APP_NAME = 'Secrets Rotation Automator'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Flask
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


# ============================================================================
# Helper Functions
# ============================================================================

def _validate_repo_path(path: str) -> bool:
    """
    Validate that a repository path exists and is a directory.
    
    Args:
        path: Path to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not path:
        return False
    
    if not os.path.exists(path):
        logger.warning(f"Repository path does not exist: {path}")
        return False
    
    if not os.path.isdir(path):
        logger.warning(f"Repository path is not a directory: {path}")
        return False
    
    return True


def _validate_secret_value(value: str) -> bool:
    """
    Validate that a secret value is not empty.
    
    Args:
        value: Secret value to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not value or not value.strip():
        logger.warning("Secret value is empty or whitespace")
        return False
    
    return True


def _format_response(data: Any, status: int = 200) -> Tuple[Dict, int]:
    """
    Format API response with consistent structure.
    
    Args:
        data: Response data
        status: HTTP status code
        
    Returns:
        Tuple[Dict, int]: Formatted response and status code
    """
    return data, status


def _format_error_response(error: str, message: str, status: int = 500) -> Tuple[Dict, int]:
    """
    Format error response with consistent structure.
    
    Args:
        error: Error type/title
        message: Detailed error message
        status: HTTP status code
        
    Returns:
        Tuple[Dict, int]: Formatted error response and status code
    """
    return {
        'error': error,
        'message': message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }, status


def _extract_affected_services(files: List[Dict]) -> List[str]:
    """
    Extract affected services from file paths.
    
    Args:
        files: List of file dictionaries with file_path
        
    Returns:
        List[str]: List of affected service names
    """
    services = set()
    
    for file_info in files:
        file_path = file_info.get('file_path', '')
        
        # Extract service name from path
        if 'auth' in file_path.lower():
            services.add('Authentication')
        if 'payment' in file_path.lower():
            services.add('Payment')
        if 'api' in file_path.lower():
            services.add('API')
        if 'database' in file_path.lower() or 'db' in file_path.lower():
            services.add('Database')
        if 'config' in file_path.lower():
            services.add('Configuration')
        if 'k8s' in file_path.lower() or 'kubernetes' in file_path.lower():
            services.add('Kubernetes')
        if 'docker' in file_path.lower():
            services.add('Docker')
    
    return sorted(list(services)) if services else ['Unknown']


def _estimate_time_to_fix(locations_count: int, affected_services: List[str]) -> str:
    """
    Estimate time required to fix secret rotation.
    
    Args:
        locations_count: Number of locations where secret is used
        affected_services: List of affected services
        
    Returns:
        str: Time estimate
    """
    # Base time: 5 minutes per location
    base_time = locations_count * 5
    
    # Add time for each service (10 minutes per service)
    service_time = len(affected_services) * 10
    
    total_minutes = base_time + service_time
    
    if total_minutes < 60:
        return f"{total_minutes} minutes"
    else:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if minutes > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''}"


def _generate_rotation_plan_text(
    secret_name: str,
    affected_services: List[str],
    files: List[str]
) -> str:
    """
    Generate a comprehensive rotation plan text.
    
    Args:
        secret_name: Name of the secret
        affected_services: List of affected services
        files: List of affected files
        
    Returns:
        str: Rotation plan text
    """
    plan = f"""
# Secret Rotation Plan for {secret_name}

## Overview
This plan outlines the steps to safely rotate the secret '{secret_name}' across {len(affected_services)} service(s) and {len(files)} file(s).

## Affected Services
{chr(10).join(f'- {service}' for service in affected_services)}

## Affected Files
{chr(10).join(f'- {file}' for file in files)}

## Pre-Rotation Checklist
1. ✓ Backup current configuration
2. ✓ Notify team members
3. ✓ Schedule maintenance window
4. ✓ Prepare rollback plan

## Rotation Steps
1. Generate new secret value
2. Update secret in secret management system (e.g., AWS Secrets Manager, HashiCorp Vault)
3. Deploy new secret to staging environment
4. Test all affected services in staging
5. Deploy to production with zero-downtime strategy
6. Verify all services are functioning correctly
7. Revoke old secret after confirmation period (24-48 hours)

## Post-Rotation Verification
- Monitor application logs for authentication errors
- Check service health endpoints
- Verify API integrations
- Run automated test suite
"""
    return plan.strip()


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check() -> Tuple[Dict, int]:
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    logger.info("Health check requested")
    return _format_response({
        'status': 'healthy',
        'version': VERSION,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@app.route('/api/version', methods=['GET'])
def get_version() -> Tuple[Dict, int]:
    """
    Get API version information.
    
    Returns:
        JSON response with version details
    """
    logger.info("Version information requested")
    return _format_response({
        'version': VERSION,
        'name': APP_NAME,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_secrets() -> Tuple[Dict, int]:
    """
    Analyze repository for a specific secret and generate rotation plan.
    
    Request Body:
        {
            "repo_path": ".",
            "secret_name": "API_KEY_PROD"
        }
    
    Returns:
        JSON response with analysis results and rotation plan
    """
    start_time = datetime.utcnow()
    logger.info(f"POST /api/analyze - Request received at {start_time.isoformat()}")
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided")
            return _format_error_response(
                'Bad Request',
                'Request body must be valid JSON',
                400
            )
        
        repo_path = data.get('repo_path', '.')
        secret_name = data.get('secret_name', '')
        
        # Validate inputs
        if not _validate_repo_path(repo_path):
            return _format_error_response(
                'Invalid Repository Path',
                f'Repository path does not exist or is not a directory: {repo_path}',
                400
            )
        
        if not secret_name:
            return _format_error_response(
                'Missing Secret Name',
                'secret_name is required',
                400
            )
        
        logger.info(f"Analyzing secrets in {repo_path} for secret: {secret_name}")
        
        # Detect all secrets in repository
        all_secrets = detect_secrets(repo_path)
        
        # Filter secrets matching the secret name
        matching_secrets = [
            s for s in all_secrets
            if secret_name.lower() in s.get('file_path', '').lower() or
               secret_name.lower() in s.get('context', '').lower()
        ]
        
        # Format file information
        files = []
        for secret in matching_secrets:
            files.append({
                'file': secret['file_path'],
                'line': secret['line_number'],
                'context': secret['context'],
                'secret_type': secret['secret_type']
            })
        
        # Extract affected services
        affected_services = _extract_affected_services(matching_secrets)
        
        # Estimate time to fix
        time_estimate = _estimate_time_to_fix(len(matching_secrets), affected_services)
        
        # Generate rotation plan
        file_paths = [f['file'] for f in files]
        rotation_plan = _generate_rotation_plan_text(
            secret_name,
            affected_services,
            file_paths
        )
        
        # Build response
        response = {
            'secret_name': secret_name,
            'locations_found': len(matching_secrets),
            'files': files,
            'affected_services': affected_services,
            'time_to_fix_estimate': time_estimate,
            'rotation_plan': rotation_plan,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Analysis completed in {duration:.2f} seconds. Found {len(matching_secrets)} locations")
        
        return _format_response(response)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return _format_error_response('Validation Error', str(e), 400)
    
    except Exception as e:
        logger.error(f"Error analyzing secrets: {e}", exc_info=True)
        return _format_error_response(
            'Internal Server Error',
            f'An error occurred while analyzing secrets: {str(e)}',
            500
        )


@app.route('/api/find-secret-usages', methods=['POST'])
def find_usages() -> Tuple[Dict, int]:
    """
    Find all usages of a specific secret value in the repository.
    
    Request Body:
        {
            "repo_path": ".",
            "secret_value": "sk_live_abc123..."
        }
    
    Returns:
        JSON response with list of all locations where secret is used
    """
    start_time = datetime.utcnow()
    logger.info(f"POST /api/find-secret-usages - Request received at {start_time.isoformat()}")
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided")
            return _format_error_response(
                'Bad Request',
                'Request body must be valid JSON',
                400
            )
        
        repo_path = data.get('repo_path', '.')
        secret_value = data.get('secret_value', '')
        
        # Validate inputs
        if not _validate_repo_path(repo_path):
            return _format_error_response(
                'Invalid Repository Path',
                f'Repository path does not exist or is not a directory: {repo_path}',
                400
            )
        
        if not _validate_secret_value(secret_value):
            return _format_error_response(
                'Invalid Secret Value',
                'secret_value cannot be empty',
                400
            )
        
        logger.info(f"Finding usages of secret in {repo_path}")
        
        # Find all usages
        usages = find_secret_usages(repo_path, secret_value)
        
        # Format response
        locations = []
        for usage in usages:
            locations.append({
                'file': usage['file_path'],
                'line': usage['line_number'],
                'context': usage['context'],
                'secret_type': usage['secret_type'],
                'severity': usage['severity']
            })
        
        response = {
            'secret_value': secret_value[:20] + '...' if len(secret_value) > 20 else secret_value,
            'locations_found': len(usages),
            'locations': locations,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Found {len(usages)} usages in {duration:.2f} seconds")
        
        return _format_response(response)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return _format_error_response('Validation Error', str(e), 400)
    
    except Exception as e:
        logger.error(f"Error finding secret usages: {e}", exc_info=True)
        return _format_error_response(
            'Internal Server Error',
            f'An error occurred while finding secret usages: {str(e)}',
            500
        )


@app.route('/api/classify-secret', methods=['POST'])
def classify_secret() -> Tuple[Dict, int]:
    """
    Classify the type of a secret based on its value.
    
    Request Body:
        {
            "secret_value": "sk_live_abc123..."
        }
    
    Returns:
        JSON response with secret type and confidence level
    """
    start_time = datetime.utcnow()
    logger.info(f"POST /api/classify-secret - Request received at {start_time.isoformat()}")
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided")
            return _format_error_response(
                'Bad Request',
                'Request body must be valid JSON',
                400
            )
        
        secret_value = data.get('secret_value', '')
        
        # Validate input
        if not _validate_secret_value(secret_value):
            return _format_error_response(
                'Invalid Secret Value',
                'secret_value cannot be empty',
                400
            )
        
        logger.info("Classifying secret type")
        
        # Classify the secret
        secret_type = classify_secret_type(secret_value)
        
        # Determine confidence level
        confidence = 'HIGH' if secret_type != 'UNKNOWN' else 'LOW'
        
        response = {
            'secret_type': secret_type,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Secret classified as {secret_type} in {duration:.2f} seconds")
        
        return _format_response(response)
    
    except Exception as e:
        logger.error(f"Error classifying secret: {e}", exc_info=True)
        return _format_error_response(
            'Internal Server Error',
            f'An error occurred while classifying secret: {str(e)}',
            500
        )


@app.route('/api/generate-rotation-plan', methods=['POST'])
def generate_rotation_plan() -> Tuple[Dict, int]:
    """
    Generate a comprehensive rotation plan for a secret.
    
    Request Body:
        {
            "secret_name": "API_KEY_PROD",
            "affected_services": ["API", "Payment"],
            "files": ["src/auth.py", "src/payment.py"]
        }
    
    Returns:
        JSON response with detailed rotation plan
    """
    start_time = datetime.utcnow()
    logger.info(f"POST /api/generate-rotation-plan - Request received at {start_time.isoformat()}")
    
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided")
            return _format_error_response(
                'Bad Request',
                'Request body must be valid JSON',
                400
            )
        
        secret_name = data.get('secret_name', '')
        affected_services = data.get('affected_services', [])
        files = data.get('files', [])
        
        # Validate inputs
        if not secret_name:
            return _format_error_response(
                'Missing Secret Name',
                'secret_name is required',
                400
            )
        
        if not affected_services:
            affected_services = ['Unknown']
        
        if not files:
            files = []
        
        logger.info(f"Generating rotation plan for {secret_name}")
        
        # Generate step-by-step plan
        step_by_step_plan = [
            {
                'step': 1,
                'action': 'Backup Current Configuration',
                'description': 'Create backups of all configuration files and current secret values',
                'estimated_time': '5 minutes'
            },
            {
                'step': 2,
                'action': 'Generate New Secret',
                'description': f'Generate a new secure value for {secret_name}',
                'estimated_time': '2 minutes'
            },
            {
                'step': 3,
                'action': 'Update Secret Management System',
                'description': 'Store new secret in your secret management system (AWS Secrets Manager, Vault, etc.)',
                'estimated_time': '5 minutes'
            },
            {
                'step': 4,
                'action': 'Update Application Code',
                'description': f'Update {len(files)} file(s) to reference the new secret',
                'estimated_time': f'{len(files) * 3} minutes'
            },
            {
                'step': 5,
                'action': 'Deploy to Staging',
                'description': 'Deploy changes to staging environment and run tests',
                'estimated_time': '15 minutes'
            },
            {
                'step': 6,
                'action': 'Deploy to Production',
                'description': 'Deploy to production using blue-green or canary deployment',
                'estimated_time': '20 minutes'
            },
            {
                'step': 7,
                'action': 'Verify Services',
                'description': f'Verify all {len(affected_services)} affected service(s) are functioning correctly',
                'estimated_time': '10 minutes'
            },
            {
                'step': 8,
                'action': 'Revoke Old Secret',
                'description': 'After 24-48 hours, revoke the old secret value',
                'estimated_time': '5 minutes'
            }
        ]
        
        # Deployment order
        deployment_order = []
        for i, service in enumerate(affected_services, 1):
            deployment_order.append({
                'order': i,
                'service': service,
                'strategy': 'Blue-Green Deployment',
                'rollback_time': '5 minutes'
            })
        
        # Rollback plan
        rollback_plan = {
            'trigger_conditions': [
                'Authentication failures increase by >10%',
                'Service health checks fail',
                'Critical errors in application logs',
                'User-reported issues'
            ],
            'rollback_steps': [
                'Immediately revert to previous secret value',
                'Redeploy previous configuration',
                'Verify service restoration',
                'Investigate root cause'
            ],
            'estimated_rollback_time': '10 minutes'
        }
        
        # Verification checks
        verification_checks = [
            {
                'check': 'Service Health',
                'method': 'GET /health endpoint',
                'expected': '200 OK'
            },
            {
                'check': 'Authentication',
                'method': 'Test API calls with new secret',
                'expected': 'Successful authentication'
            },
            {
                'check': 'Application Logs',
                'method': 'Monitor for errors',
                'expected': 'No authentication errors'
            },
            {
                'check': 'Metrics',
                'method': 'Check error rates and latency',
                'expected': 'Normal baseline metrics'
            }
        ]
        
        # Calculate total estimated time
        total_time = sum(
            int(step['estimated_time'].split()[0])
            for step in step_by_step_plan
        )
        
        response = {
            'secret_name': secret_name,
            'affected_services': affected_services,
            'affected_files': files,
            'step_by_step_plan': step_by_step_plan,
            'deployment_order': deployment_order,
            'rollback_plan': rollback_plan,
            'verification_checks': verification_checks,
            'estimated_time': f'{total_time} minutes',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Rotation plan generated in {duration:.2f} seconds")
        
        return _format_response(response)
    
    except Exception as e:
        logger.error(f"Error generating rotation plan: {e}", exc_info=True)
        return _format_error_response(
            'Internal Server Error',
            f'An error occurred while generating rotation plan: {str(e)}',
            500
        )


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error) -> Tuple[Dict, int]:
    """Handle 404 errors."""
    logger.warning(f"404 Not Found: {request.path}")
    return _format_error_response(
        'Not Found',
        f'The requested endpoint {request.path} does not exist',
        404
    )


@app.errorhandler(405)
def method_not_allowed(error) -> Tuple[Dict, int]:
    """Handle 405 errors."""
    logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
    return _format_error_response(
        'Method Not Allowed',
        f'The method {request.method} is not allowed for {request.path}',
        405
    )


@app.errorhandler(500)
def internal_error(error) -> Tuple[Dict, int]:
    """Handle 500 errors."""
    logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    return _format_error_response(
        'Internal Server Error',
        'An unexpected error occurred. Please try again later.',
        500
    )


# ============================================================================
# Request/Response Logging
# ============================================================================

@app.before_request
def log_request():
    """Log all incoming requests."""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")


@app.after_request
def log_response(response):
    """Log all outgoing responses."""
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info(f"Starting {APP_NAME} v{VERSION}")
    logger.info(f"Host: {HOST}")
    logger.info(f"Port: {PORT}")
    logger.info(f"Debug: {DEBUG}")
    logger.info("=" * 80)
    
    app.run(host=HOST, port=PORT, debug=DEBUG)

# Made with Bob
