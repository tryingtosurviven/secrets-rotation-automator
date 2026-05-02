"""
Unit tests for the secret_detector module.
Run with: pytest test_secret_detector.py -v
"""

import tempfile
import shutil
from pathlib import Path
from secret_detector import (
    detect_secrets,
    find_secret_usages,
    classify_secret_type,
    _should_skip_directory,
    _should_scan_file
)

def test_classify_secret_type_api_key():
    """Test API key classification."""
    assert classify_secret_type("demo_stripe_live_key_placeholder_12345") == "API_KEY"
    assert classify_secret_type("demo_stripe_test_key_placeholder_12345") == "API_KEY"

def test_classify_secret_type_aws_key():
    """Test AWS key classification."""
    assert classify_secret_type("DEMO_AWS_ACCESS_KEY_PLACEHOLDER") == "AWS_KEY"
    assert classify_secret_type("demo_aws_secret_placeholder_value_12345") == "AWS_KEY"

def test_classify_secret_type_github_token():
    """Test GitHub token classification."""
    assert classify_secret_type("demo_github_token_placeholder_12345") == "GITHUB_TOKEN"
    assert classify_secret_type("demo_github_oauth_placeholder_12345") == "GITHUB_TOKEN"

def test_classify_secret_type_private_key():
    """Test private key classification."""
    assert classify_secret_type("-----BEGIN PRIVATE KEY-----") == "PRIVATE_KEY"
    assert classify_secret_type("-----BEGIN RSA PRIVATE KEY-----") == "PRIVATE_KEY"
    assert classify_secret_type("-----BEGIN OPENSSH PRIVATE KEY-----") == "PRIVATE_KEY"

def test_classify_secret_type_jwt():
    """Test JWT token classification."""
    assert classify_secret_type("demo.jwt.token.placeholder") == "JWT_TOKEN"

def test_classify_secret_type_unknown():
    """Test unknown secret classification."""
    assert classify_secret_type("random_string_123") == "UNKNOWN"
    assert classify_secret_type("") == "UNKNOWN"

def test_should_skip_directory():
    """Test directory skip logic."""
    assert _should_skip_directory(".git") is True
    assert _should_skip_directory("__pycache__") is True
    assert _should_skip_directory("node_modules") is True
    assert _should_skip_directory(".venv") is True
    assert _should_skip_directory("venv") is True
    assert _should_skip_directory("dist") is True
    assert _should_skip_directory("build") is True
    assert _should_skip_directory(".hidden") is True
    assert _should_skip_directory("src") is False
    assert _should_skip_directory("tests") is False

def test_should_scan_file():
    """Test file scanning logic."""
    assert _should_scan_file("config.py") is True
    assert _should_scan_file("script.js") is True
    assert _should_scan_file(".env") is True
    assert _should_scan_file("config.yml") is True
    assert _should_scan_file("config.yaml") is True
    assert _should_scan_file("package.json") is True
    assert _should_scan_file("deploy.sh") is True
    assert _should_scan_file("app.conf") is True
    assert _should_scan_file("settings.ini") is True
    assert _should_scan_file("settings.config") is True

    assert _should_scan_file("image.png") is False
    assert _should_scan_file("document.pdf") is False
    assert _should_scan_file("binary.exe") is False
    assert _should_scan_file("README.md") is False

def test_detect_secrets_with_temp_directory():
    """Test secret detection in a temporary directory."""
    temp_dir = tempfile.mkdtemp()

    try:
        test_file = Path(temp_dir) / "config.py"
        test_file.write_text("""
# Configuration file
API_KEY = "demo_stripe_live_key_placeholder_12345"
DB_PASSWORD = "demo_db_password_placeholder_12345"
AWS_ACCESS_KEY_ID = "DEMO_AWS_ACCESS_KEY_PLACEHOLDER"
""")

        secrets = detect_secrets(temp_dir)

        assert len(secrets) >= 3

        secret_types = [s["secret_type"] for s in secrets]
        assert "API_KEY" in secret_types
        assert "PASSWORD" in secret_types
        assert "AWS_KEY" in secret_types

        for secret in secrets:
            assert "secret_type" in secret
            assert "secret_value" in secret
            assert "file_path" in secret
            assert "line_number" in secret
            assert "context" in secret
            assert secret["severity"] == "CRITICAL"

    finally:
        shutil.rmtree(temp_dir)

def test_find_secret_usages_with_temp_directory():
    """Test finding specific secret usages."""
    temp_dir = tempfile.mkdtemp()

    try:
        file1 = Path(temp_dir) / "config1.py"
        file1.write_text('API_KEY = "demo_api_key_prod_placeholder_12345"\n')

        file2 = Path(temp_dir) / "config2.py"
        file2.write_text('SECRET = "demo_api_key_prod_placeholder_12345"\n')

        usages = find_secret_usages(temp_dir, "demo_api_key_prod_placeholder_12345")

        assert len(usages) == 2

        file_paths = [u["file_path"] for u in usages]
        assert any("config1.py" in fp for fp in file_paths)
        assert any("config2.py" in fp for fp in file_paths)

    finally:
        shutil.rmtree(temp_dir)

def test_detect_secrets_skips_excluded_directories():
    """Test that excluded directories are skipped."""
    temp_dir = tempfile.mkdtemp()

    try:
        excluded_dir = Path(temp_dir) / ".git"
        excluded_dir.mkdir()
        (excluded_dir / "config").write_text('SECRET = "should_be_skipped"\n')

        (Path(temp_dir) / "config.py").write_text('API_KEY = "demo_api_key_prod_placeholder_12345"\n')

        secrets = detect_secrets(temp_dir)

        for secret in secrets:
            assert ".git" not in secret["file_path"]

    finally:
        shutil.rmtree(temp_dir)

def test_detect_secrets_invalid_path():
    """Test error handling for invalid paths."""
    try:
        detect_secrets("/nonexistent/path/12345")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "does not exist" in str(e)

def test_find_secret_usages_empty_secret():
    """Test error handling for empty secret value."""
    try:
        find_secret_usages(".", "")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "cannot be empty" in str(e)

if __name__ == "__main__":
    print("Running secret_detector tests...\n")

    tests = [
        ("API Key Classification", test_classify_secret_type_api_key),
        ("AWS Key Classification", test_classify_secret_type_aws_key),
        ("GitHub Token Classification", test_classify_secret_type_github_token),
        ("Private Key Classification", test_classify_secret_type_private_key),
        ("JWT Classification", test_classify_secret_type_jwt),
        ("Unknown Classification", test_classify_secret_type_unknown),
        ("Directory Skip Logic", test_should_skip_directory),
        ("File Scan Logic", test_should_scan_file),
        ("Secret Detection", test_detect_secrets_with_temp_directory),
        ("Secret Usage Finding", test_find_secret_usages_with_temp_directory),
        ("Excluded Directory Skip", test_detect_secrets_skips_excluded_directories),
        ("Invalid Path Handling", test_detect_secrets_invalid_path),
        ("Empty Secret Handling", test_find_secret_usages_empty_secret),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"[PASS] {test_name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test_name}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'='*60}")
