# 🔐 Secrets Rotation Automator

A powerful Flask-based web application and API for detecting hardcoded secrets in codebases and automating the secret rotation process. Built to enhance security by identifying exposed credentials and providing actionable rotation plans.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [What It Does](#what-it-does)
- [Why It Matters](#why-it-matters)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Web Interface](#web-interface)
- [Screenshots](#screenshots)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 What It Does

Secrets Rotation Automator is a comprehensive security tool that:

1. **Scans codebases** for hardcoded secrets (API keys, passwords, tokens, private keys)
2. **Identifies secret locations** across multiple files and services
3. **Classifies secret types** (AWS keys, GitHub tokens, JWT tokens, etc.)
4. **Generates rotation plans** with step-by-step instructions
5. **Estimates remediation time** based on affected services and locations
6. **Provides both Web UI and REST API** for flexible integration

## 🔒 Why It Matters for Security

Hardcoded secrets in source code are a **critical security vulnerability** that can lead to:

- **Data Breaches**: Exposed credentials can grant unauthorized access to sensitive systems
- **Compliance Violations**: Regulations like GDPR, PCI-DSS, and SOC 2 require proper secret management
- **Financial Loss**: Security incidents can cost millions in remediation and legal fees
- **Reputation Damage**: Public exposure of secrets can severely harm brand trust

### The Problem

- 🚨 **6 million+ secrets** are leaked on GitHub annually
- 💰 Average cost of a data breach: **$4.45 million** (IBM Security Report 2023)
- ⏱️ Average time to identify a breach: **277 days**

### Our Solution

Secrets Rotation Automator helps you:
- ✅ **Detect secrets early** before they reach production
- ✅ **Automate rotation planning** to reduce manual effort
- ✅ **Track affected services** for comprehensive remediation
- ✅ **Integrate into CI/CD** pipelines for continuous security

## ✨ Features

### 🔍 Secret Detection
- Detects **6 types of secrets**: API keys, passwords, AWS keys, GitHub tokens, private keys, JWT tokens
- **Smart filtering** to skip common directories (`.git`, `node_modules`, `.venv`)
- **Context-aware** detection with surrounding code lines
- **False positive filtering** for example/placeholder values

### 📊 Impact Analysis
- Identifies **affected services** (Authentication, Payment, Database, etc.)
- Calculates **time-to-fix estimates** based on complexity
- Provides **detailed file locations** with line numbers

### 🔄 Rotation Planning
- Generates **step-by-step rotation plans**
- Includes **rollback procedures** for safe deployment
- Provides **verification checklists** for post-rotation validation

### 🌐 Dual Interface
- **Web UI**: User-friendly interface for manual analysis
- **REST API**: Programmatic access for automation and integration

### 📝 Comprehensive Logging
- Detailed application logs for debugging
- Audit trail for security compliance

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/secrets-rotation-automator.git
cd secrets-rotation-automator
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python app.py
```

The application should start on `http://localhost:5000`

## 🎬 Quick Start

### Running the Application

```bash
# Development mode with debug enabled
set FLASK_DEBUG=true  # Windows
export FLASK_DEBUG=true  # macOS/Linux

python app.py
```

### Using the Web Interface

1. Open your browser to `http://localhost:5000`
2. Enter the repository path to scan
3. Specify the secret name to search for
4. View results with affected files and rotation plan

### Using the API

```python
import requests

# Analyze secrets in a repository
response = requests.post('http://localhost:5000/api/analyze', json={
    "repo_path": "./my-project",
    "secret_name": "API_KEY"
})

print(response.json())
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

---

#### 2. Get Version

Get application version information.

**Endpoint:** `GET /api/version`

**Response:**
```json
{
  "version": "1.0.0",
  "name": "Secrets Rotation Automator",
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

---

#### 3. Analyze Secrets

Scan a repository for a specific secret and get a rotation plan.

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
{
  "repo_path": "./sample-vulnerable-repo",
  "secret_name": "API_KEY_PROD"
}
```

**Response:**
```json
{
  "secret_name": "API_KEY_PROD",
  "locations_found": 3,
  "files": [
    {
      "file": "src/auth.py",
      "line": 15,
      "context": ">>> 15: API_KEY_PROD = \"demo_api_key_prod_placeholder_12345\"",
      "secret_type": "API_KEY"
    }
  ],
  "affected_services": ["Authentication", "API"],
  "time_to_fix_estimate": "35 minutes",
  "rotation_plan": {
    "step_by_step_plan": [
      "Backup current configuration and affected files",
      "Generate a new value for API_KEY_PROD",
      "Update secret management or environment configuration",
      "Update 3 affected file(s)",
      "Deploy changes to staging and run tests",
      "Deploy safely to production",
      "Verify all affected services are healthy",
      "Revoke the old secret after verification"
    ],
    "rollback_plan": [
      "Restore previous configuration",
      "Redeploy previous known-good version",
      "Verify service recovery",
      "Investigate and retry rotation safely"
    ],
    "verification_checks": [
      "Check service health endpoints",
      "Review application logs for errors",
      "Verify integrations still work",
      "Run automated tests"
    ],
    "estimated_time": "35 minutes"
  },
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

---

#### 4. Find Secret Usages

Find all locations where a specific secret value appears.

**Endpoint:** `POST /api/find-secret-usages`

**Request Body:**
```json
{
  "repo_path": "./sample-vulnerable-repo",
  "secret_value": "demo_stripe_live_key_placeholder_12345"
}
```

**Response:**
```json
{
  "secret_value": "demo_stripe_live_key_placeholder_12345",
  "locations_found": 2,
  "locations": [
    {
      "secret_type": "API_KEY",
      "secret_value": "demo_stripe_live_key_placeholder_12345",
      "file_path": "src/payment.py",
      "line_number": 8,
      "context": ">>> 8: STRIPE_KEY = \"demo_stripe_live_key_placeholder_12345\"",
      "severity": "CRITICAL"
    }
  ],
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

---

#### 5. Classify Secret

Classify the type of a secret based on its value.

**Endpoint:** `POST /api/classify-secret`

**Request Body:**
```json
{
  "secret_value": "DEMO_AWS_ACCESS_KEY_PLACEHOLDER"
}
```

**Response:**
```json
{
  "secret_type": "AWS_KEY",
  "confidence": "HIGH",
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

---

#### 6. Generate Rotation Plan

Generate a detailed rotation plan for a secret.

**Endpoint:** `POST /api/generate-rotation-plan`

**Request Body:**
```json
{
  "secret_name": "DATABASE_PASSWORD",
  "affected_services": ["Database", "API"],
  "files": ["config/production.env", "src/db.py"]
}
```

**Response:**
```json
{
  "secret_name": "DATABASE_PASSWORD",
  "affected_services": ["Database", "API"],
  "affected_files": ["config/production.env", "src/db.py"],
  "step_by_step_plan": [
    "Backup current configuration and affected files",
    "Generate a new value for DATABASE_PASSWORD",
    "Update secret management or environment configuration",
    "Update 2 affected file(s)",
    "Deploy changes to staging and run tests",
    "Deploy safely to production",
    "Verify all affected services are healthy",
    "Revoke the old secret after verification"
  ],
  "rollback_plan": [
    "Restore previous configuration",
    "Redeploy previous known-good version",
    "Verify service recovery",
    "Investigate and retry rotation safely"
  ],
  "verification_checks": [
    "Check service health endpoints",
    "Review application logs for errors",
    "Verify integrations still work",
    "Run automated tests"
  ],
  "estimated_time": "30 minutes",
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

### Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "timestamp": "2026-05-02T10:00:00.000Z"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (invalid endpoint)
- `500` - Internal Server Error

## 🖥️ Web Interface

### Home Page
Access the main interface at `http://localhost:5000`

### Analyze Secrets
- **Route:** `/analyze-ui` (POST)
- **Form Fields:**
  - Repository Path
  - Secret Name
- **Output:** Detailed analysis with rotation plan

### Find Usages
- **Route:** `/usages` (GET/POST)
- **Form Fields:**
  - Repository Path
  - Secret Value
- **Output:** All locations where the secret appears

## 📸 Screenshots

### 1. Home Page
*The main landing page with navigation to analysis tools*

![Home Page](docs/screenshots/home.png)

### 2. Secret Analysis Results
*Detailed view showing detected secrets, affected services, and rotation plan*

![Analysis Results](docs/screenshots/analysis-results.png)

### 3. Secret Usages View
*List of all locations where a specific secret value is found*

![Secret Usages](docs/screenshots/usages.png)

### 4. API Response Example
*JSON response from the analyze endpoint*

![API Response](docs/screenshots/api-response.png)

> **Note:** Screenshots will be added to the `docs/screenshots/` directory. Run the application and capture screenshots of the web interface for documentation purposes.

## ⚙️ Configuration

### Environment Variables

```bash
# Enable debug mode (development only)
FLASK_DEBUG=true

# Custom port (default: 5000)
PORT=8080

# Custom host (default: 0.0.0.0)
HOST=127.0.0.1
```

### Logging

Logs are written to:
- **Console**: Real-time output
- **File**: `app.log` in the project root

Log level can be adjusted in `app.py`:
```python
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for verbose output
```

### Scanned File Types

The detector scans these file extensions:
- `.py`, `.js` - Source code
- `.env`, `.yml`, `.yaml` - Configuration
- `.json` - JSON configs
- `.sh` - Shell scripts
- `.dockerfile` - Docker files
- `.conf`, `.config`, `.ini` - Config files

### Excluded Directories

These directories are automatically skipped:
- `.git`, `.venv`, `venv`, `env`
- `node_modules`, `__pycache__`
- `dist`, `build`
- `.pytest_cache`, `.tox`

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_secret_detector.py
```

### Testing the API

Use the provided test script:

```bash
# Make sure the app is running first
python app.py

# In another terminal
python test_api.py
```

### Project Structure

```
secrets-rotation-automator/
├── app.py                      # Main Flask application
├── secret_detector.py          # Core detection logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── app.log                     # Application logs
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   └── usages.html
├── static/                     # CSS and static assets
│   └── style.css
├── sample-vulnerable-repo/     # Sample repo for testing
└── tests/                      # Test files
    ├── test_api.py
    ├── test_secret_detector.py
    └── test_sample_repo.py
```

### Adding New Secret Patterns

Edit `secret_detector.py` and add patterns to `SECRET_PATTERNS`:

```python
SECRET_PATTERNS = {
    'NEW_SECRET_TYPE': [
        re.compile(r'your_pattern_here', re.IGNORECASE),
    ],
    # ... existing patterns
}
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the IBM Bob Dev Day Hackathon
- Inspired by security best practices from OWASP and NIST
- Thanks to the open-source community for Flask and related libraries

## 📞 Support

For issues, questions, or contributions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/secrets-rotation-automator/issues)
- **Documentation**: See `README_SECRET_DETECTOR.md` for detailed module documentation
- **Email**: support@example.com

## 🔐 Security Notice

**Important:** This tool helps identify hardcoded secrets but should be part of a comprehensive security strategy. Always:

- ✅ Use proper secret management solutions (AWS Secrets Manager, HashiCorp Vault, etc.)
- ✅ Rotate secrets immediately after detection
- ✅ Never commit secrets to version control
- ✅ Use environment variables for configuration
- ✅ Implement least-privilege access controls
- ✅ Enable audit logging for secret access

---

**Made with ❤️ by Bob | Version 1.0.0**