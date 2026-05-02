# Clean Repository Example

This is a **clean repository example** demonstrating best practices for secret management in software projects.

## 🔒 Security Best Practices

This repository showcases how to properly handle sensitive information without hardcoding secrets in your codebase.

### Key Principles Demonstrated

1. **Environment Variables**: All sensitive data is loaded from environment variables using `os.environ.get()`
2. **No Hardcoded Secrets**: Zero hardcoded API keys, passwords, tokens, or credentials in the source code
3. **Example Configuration**: `.env.example` file shows required variables without exposing real values
4. **Separation of Concerns**: Configuration is centralized and separate from business logic

## 📁 Repository Structure

```
sample-clean-repo/
├── config.py           # Central configuration using environment variables
├── .env.example        # Template showing required environment variables
├── README.md           # This file - documentation
├── src/
│   ├── auth.py        # Authentication module using env vars
│   └── payment.py     # Payment processing using env vars
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sample-clean-repo
```

### 2. Set Up Environment Variables

Copy the example environment file and fill in your actual values:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```bash
# Example - DO NOT commit this file
API_KEY=your_actual_api_key_here
DB_PASSWORD=your_actual_password_here
# ... etc
```

**Important**: Add `.env` to your `.gitignore` file to prevent committing secrets!

### 3. Load Environment Variables

#### Option A: Using python-dotenv

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()

import config
# Now config.API_KEY will have your actual value
```

#### Option B: Export Manually

```bash
export API_KEY=your_actual_api_key
export DB_PASSWORD=your_actual_password
# ... etc
```

#### Option C: Use a Secret Manager

For production environments, use proper secret management:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Cloud Secret Manager

## 📝 Configuration

All configuration is centralized in `config.py`. This file:

- Uses `os.environ.get()` for all sensitive values
- Provides sensible defaults for non-sensitive settings
- Includes a `validate_config()` function to check required variables

### Example Usage

```python
from config import API_KEY, DB_PASSWORD, validate_config

# Validate all required environment variables are set
validate_config()

# Use configuration values
api_client = APIClient(api_key=API_KEY)
db_connection = connect(password=DB_PASSWORD)
```

## 🔐 What NOT to Do

❌ **Never do this:**

```python
# BAD - Hardcoded secret
API_KEY = "sk_live_abc123xyz789"

# BAD - Secret in code
password = "MySecretPassword123!"

# BAD - Committed credentials
aws_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

✅ **Always do this:**

```python
# GOOD - Load from environment
API_KEY = os.environ.get('API_KEY')

# GOOD - Use environment variables
password = os.environ.get('DB_PASSWORD')

# GOOD - Never hardcode credentials
aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
```

## 🛡️ Security Checklist

- [x] All secrets loaded from environment variables
- [x] No hardcoded credentials in source code
- [x] `.env.example` provided with placeholder values
- [x] `.env` added to `.gitignore`
- [x] Configuration validation implemented
- [x] Documentation explains setup process
- [x] Separate configs for different environments

## 📚 Additional Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

## 🤝 Contributing

When contributing to this repository:

1. Never commit actual secrets or credentials
2. Use `.env.example` to document new required variables
3. Update this README if adding new configuration options
4. Test with environment variables before submitting PR

## 📄 License

This is an example repository for educational purposes.

## ⚠️ Important Notes

- **Never commit `.env` files** - Add them to `.gitignore`
- **Rotate secrets regularly** - Change credentials periodically
- **Use different secrets per environment** - Dev, staging, and production should have different credentials
- **Audit access** - Monitor who has access to production secrets
- **Use secret managers in production** - Don't rely solely on environment variables for production systems

---

**Remember**: The best way to keep secrets safe is to never put them in your code in the first place! 🔐