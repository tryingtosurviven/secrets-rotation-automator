# Secret Detector Module

A comprehensive Python module for detecting hardcoded secrets in codebases, built for the IBM Bob Dev Day Hackathon.

## Features

- 🔍 **Comprehensive Detection**: Scans for API keys, passwords, AWS-style credentials, GitHub-style tokens, private keys, and JWT-style tokens

- 📁 **Smart Filtering**: Automatically skips common directories like `.git`, `node_modules`, `__pycache__`
- 🎯 **Precise Classification**: Identifies the type of each detected secret
- 📊 **Detailed Context**: Provides surrounding code lines for each finding
- 🚨 **Severity Marking**: All detected secrets marked as CRITICAL
- 🛡️ **Error Handling**: Robust error handling for file permissions and encoding issues
- 📝 **Comprehensive Logging**: Detailed logging for debugging and auditing

## Supported Secret Types

| Secret Type | Examples | Detection Patterns |
|------------|----------|-------------------|
| **API_KEY** | `demo_stripe_live_key_placeholder_12345`, `API_KEY_PROD` | Demo API keys, generic API keys |
| **PASSWORD** | `DB_PASSWORD`, `password=` | Database passwords, generic passwords |
| **AWS_KEY** | `DEMO_AWS_ACCESS_KEY_PLACEHOLDER`, `demo_aws_secret_placeholder_value_12345` | Demo AWS-style access keys and secrets |
| **GITHUB_TOKEN** | `demo_github_token_placeholder_12345`, `demo_github_oauth_placeholder_12345` | Demo GitHub-style tokens |
| **PRIVATE_KEY** | `-----BEGIN PRIVATE KEY-----` | PEM format private keys |
| **JWT_TOKEN** | `demo.jwt.token.placeholder` | Demo JWT-style tokens |



## Installation

No additional dependencies required beyond Python standard library!

```bash
# Simply copy secret_detector.py to your project
cp secret_detector.py /path/to/your/project/
```

## Usage

### 1. Detect All Secrets in a Directory

```python
from secret_detector import detect_secrets

# Scan current directory
secrets = detect_secrets(".")

# Scan specific directory
secrets = detect_secrets("/path/to/repository")

# Process results
for secret in secrets:
    print(f"Found {secret['secret_type']} in {secret['file_path']}:{secret['line_number']}")
    print(f"Value: {secret['secret_value']}")
    print(f"Context:\n{secret['context']}\n")
```

### 2. Find Specific Secret Usages

```python
from secret_detector import find_secret_usages

# Find all occurrences of a specific secret
usages = find_secret_usages(".", "DEMO_AWS_ACCESS_KEY_PLACEHOLDER")

for usage in usages:
    print(f"Found in {usage['file_path']} at line {usage['line_number']}")
```

### 3. Classify Secret Type

```python
from secret_detector import classify_secret_type

# Classify a secret value
secret_type = classify_secret_type("demo_github_token_placeholder_12345")
print(f"Secret type: {secret_type}")  # Output: GITHUB_TOKEN
```

## API Reference

### `detect_secrets(repo_path: str) -> List[Dict]`

Scan a directory recursively for hardcoded secrets.

**Parameters:**
- `repo_path` (str): Path to the repository/directory to scan

**Returns:**
- List[Dict]: List of found secrets with the following structure:
  ```python
  {
      'secret_type': str,      # API_KEY, PASSWORD, AWS_KEY, etc.
      'secret_value': str,     # The detected secret value
      'file_path': str,        # Relative path from repo_path
      'line_number': int,      # Line number (1-based)
      'context': str,          # Surrounding code lines
      'severity': 'CRITICAL'   # Always CRITICAL
  }
  ```

**Raises:**
- `ValueError`: If repo_path does not exist or is not a directory

**Example:**
```python
secrets = detect_secrets("/path/to/repo")
print(f"Found {len(secrets)} secrets")
```

---

### `find_secret_usages(repo_path: str, secret_value: str) -> List[Dict]`

Find all locations where a specific secret value appears.

**Parameters:**
- `repo_path` (str): Path to the repository/directory to scan
- `secret_value` (str): The specific secret value to search for

**Returns:**
- List[Dict]: List of locations with the same structure as `detect_secrets()`

**Raises:**
- `ValueError`: If repo_path does not exist or secret_value is empty

**Example:**
```python
usages = find_secret_usages(".", "demo_api_key_prod_placeholder_12345")
for usage in usages:
    print(f"Found at {usage['file_path']}:{usage['line_number']}")
```

---

### `classify_secret_type(secret_value: str) -> str`

Classify the type of secret based on its value.

**Parameters:**
- `secret_value` (str): The secret string to classify

**Returns:**
- str: Secret type (API_KEY, PASSWORD, AWS_KEY, GITHUB_TOKEN, PRIVATE_KEY, JWT_TOKEN, or UNKNOWN)

**Example:**
```python
secret_type = classify_secret_type("DEMO_AWS_ACCESS_KEY_PLACEHOLDER")
print(secret_type)  # Output: AWS_KEY
```

## Configuration

### Skipped Directories

The following directories are automatically skipped:
- `.git`
- `__pycache__`
- `node_modules`
- `.venv`, `venv`, `env`
- `dist`, `build`
- `.pytest_cache`, `.tox`

### Scanned File Extensions

The module scans files with these extensions:
- `.py` - Python
- `.js` - JavaScript
- `.env` - Environment files
- `.yml`, `.yaml` - YAML configs
- `.json` - JSON configs
- `.sh` - Shell scripts
- `.dockerfile` - Docker files
- `.conf`, `.config` - Configuration files
- `.ini` - INI files

## Example Output

```
2026-05-02 00:53:31,788 - __main__ - INFO - Starting secret detection scan in: .
2026-05-02 00:53:31,793 - __main__ - INFO - Found AWS_KEY in config.py:15
2026-05-02 00:53:31,794 - __main__ - INFO - Found GITHUB_TOKEN in deploy.sh:42
2026-05-02 00:53:31,794 - __main__ - INFO - Scan complete. Files scanned: 25, Secrets found: 8

Found 8 secret(s):

Secret #1:
  Type: AWS_KEY
  File: config.py
  Line: 15
  Severity: CRITICAL
  Value: DEMO_AWS_ACCESS_KEY_PLACEHOLDER
  Context:
    13: # AWS Configuration
    14: AWS_REGION = "us-east-1"
>>> 15: AWS_ACCESS_KEY_ID = "DEMO_AWS_ACCESS_KEY_PLACEHOLDER"
    16: AWS_SECRET_ACCESS_KEY = "demo_aws_secret_placeholder_value_12345"
    17:
```

## Best Practices

1. **Run Before Commits**: Integrate into pre-commit hooks
2. **CI/CD Integration**: Add to your CI/CD pipeline
3. **Regular Scans**: Schedule periodic scans of your codebase
4. **Review Findings**: Manually review all detected secrets
5. **Rotate Exposed Secrets**: Immediately rotate any exposed credentials
6. **Use Secret Management**: Store secrets in proper secret management systems

## Integration Examples

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python secret_detector.py
if [ $? -ne 0 ]; then
    echo "❌ Secrets detected! Commit aborted."
    exit 1
fi
```

### GitHub Actions

```yaml
name: Secret Detection
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Secret Detector
        run: python secret_detector.py
```

### Jenkins Pipeline

```groovy
stage('Secret Detection') {
    steps {
        sh 'python secret_detector.py'
    }
}
```

## Limitations

- **False Positives**: May detect example/placeholder values (filtered automatically)
- **Obfuscated Secrets**: Cannot detect heavily obfuscated or encrypted secrets
- **Binary Files**: Does not scan binary files
- **Performance**: Large repositories may take time to scan

## Contributing

This module was created for the IBM Bob Dev Day Hackathon. Contributions and improvements are welcome!

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or questions, please refer to the module documentation or contact the development team.

---

**⚠️ Security Notice**: This tool helps identify hardcoded secrets but should be part of a comprehensive security strategy. Always use proper secret management solutions in production environments.