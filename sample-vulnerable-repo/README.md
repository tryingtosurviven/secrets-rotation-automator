# Sample Vulnerable Repository

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
