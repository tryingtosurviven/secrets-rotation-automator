"""
Unit tests for the secret_detector module.
Run with: pytest test_secret_detector.py -v
"""

import os
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
    assert classify_secret_type("sk_live_51H8xyzABCDEF123456789") == "API_KEY"
    assert classify_secret_type("sk_test_4eC39HqLyjWDarjtT1zdp7dc") == "API_KEY"


def test_classify_secret_type_aws_key():
    """Test AWS key classification."""
    assert classify_secret_type("AKIA1234567890ABCDEF") == "AWS_KEY"
    assert classify_secret_type("AKIAIOSFODNN7EXAMPLE") == "AWS_KEY"


def test_classify_secret_type_github_token():
    """Test GitHub token classification."""
    assert classify_secret_type("ghp_1234567890abcdefghijklmnopqrstuvwxyz") == "GITHUB_TOKEN"
    assert classify_secret_type("gho_abcdefghijklmnopqrstuvwxyz1234567890") == "GITHUB_TOKEN"
    assert classify_secret_type("ghs_1234567890abcdefghijklmnopqrstuvwxyz") == "GITHUB_TOKEN"
    assert classify_secret_type("ghr_1234567890abcdefghijklmnopqrstuvwxyz") == "GITHUB_TOKEN"


def test_classify_secret_type_private_key():
    """Test private key classification."""
    assert classify_secret_type("-----BEGIN PRIVATE KEY-----") == "PRIVATE_KEY"
    assert classify_secret_type("-----BEGIN RSA PRIVATE KEY-----") == "PRIVATE_KEY"
    assert classify_secret_type("-----BEGIN OPENSSH PRIVATE KEY-----") == "PRIVATE_KEY"


def test_classify_secret_type_jwt():
    """Test JWT token classification."""
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    assert classify_secret_type(jwt) == "JWT_TOKEN"


def test_classify_secret_type_unknown():
    """Test unknown secret classification."""
    assert classify_secret_type("random_string_123") == "UNKNOWN"
    assert classify_secret_type("") == "UNKNOWN"


def test_should_skip_directory():
    """Test directory skip logic."""
    assert _should_skip_directory(".git") == True
    assert _should_skip_directory("__pycache__") == True
    assert _should_skip_directory("node_modules") == True
    assert _should_skip_directory(".venv") == True
    assert _should_skip_directory("venv") == True
    assert _should_skip_directory("dist") == True
    assert _should_skip_directory("build") == True
    assert _should_skip_directory(".hidden") == True
    assert _should_skip_directory("src") == False
    assert _should_skip_directory("tests") == False


def test_should_scan_file():
    """Test file scanning logic."""
    # Should scan
    assert _should_scan_file("config.py") == True
    assert _should_scan_file("script.js") == True
    assert _should_scan_file(".env") == True
    assert _should_scan_file("config.yml") == True
    assert _should_scan_file("config.yaml") == True
    assert _should_scan_file("package.json") == True
    assert _should_scan_file("deploy.sh") == True
    assert _should_scan_file("app.conf") == True
    assert _should_scan_file("settings.ini") == True
    assert _should_scan_file("settings.config") == True
    
    # Should not scan
    assert _should_scan_file("image.png") == False
    assert _should_scan_file("document.pdf") == False
    assert _should_scan_file("binary.exe") == False
    assert _should_scan_file("README.md") == False


def test_detect_secrets_with_temp_directory():
    """Test secret detection in a temporary directory."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test file with secrets
        test_file = Path(temp_dir) / "config.py"
        test_file.write_text("""
# Configuration file
API_KEY = "sk_live_51H8xyzABCDEF123456789"
DB_PASSWORD = "my_secret_password_123"
AWS_ACCESS_KEY_ID = "AKIA1234567890ABCDEF"
""")
        
        # Run detection
        secrets = detect_secrets(temp_dir)
        
        # Verify results
        assert len(secrets) >= 3
        
        secret_types = [s['secret_type'] for s in secrets]
        assert 'API_KEY' in secret_types
        assert 'PASSWORD' in secret_types
        assert 'AWS_KEY' in secret_types
        
        # Check that all secrets have required fields
        for secret in secrets:
            assert 'secret_type' in secret
            assert 'secret_value' in secret
            assert 'file_path' in secret
            assert 'line_number' in secret
            assert 'context' in secret
            assert secret['severity'] == 'CRITICAL'
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_find_secret_usages_with_temp_directory():
    """Test finding specific secret usages."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test files with the same secret
        file1 = Path(temp_dir) / "config1.py"
        file1.write_text('API_KEY = "test_secret_key_123"\n')
        
        file2 = Path(temp_dir) / "config2.py"
        file2.write_text('SECRET = "test_secret_key_123"\n')
        
        # Find usages
        usages = find_secret_usages(temp_dir, "test_secret_key_123")
        
        # Verify results
        assert len(usages) == 2
        
        file_paths = [u['file_path'] for u in usages]
        assert any('config1.py' in fp for fp in file_paths)
        assert any('config2.py' in fp for fp in file_paths)
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_detect_secrets_skips_excluded_directories():
    """Test that excluded directories are skipped."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create excluded directory with secrets
        excluded_dir = Path(temp_dir) / ".git"
        excluded_dir.mkdir()
        (excluded_dir / "config").write_text('SECRET = "should_be_skipped"\n')
        
        # Create normal file with secret
        (Path(temp_dir) / "config.py").write_text('API_KEY = "should_be_found"\n')
        
        # Run detection
        secrets = detect_secrets(temp_dir)
        
        # Verify .git directory was skipped
        for secret in secrets:
            assert '.git' not in secret['file_path']
    
    finally:
        # Cleanup
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
    # Run tests manually
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

# Made with Bob
