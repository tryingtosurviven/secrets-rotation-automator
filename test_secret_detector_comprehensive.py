"""
Comprehensive pytest unit tests for the secret_detector module.
Covers detect_secrets, find_secret_usages, classify_secret_type,
_is_false_positive, and _should_scan_file functions with both passing and failing cases.

Run with: pytest test_secret_detector_comprehensive.py -v
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from secret_detector import (
    detect_secrets,
    find_secret_usages,
    classify_secret_type,
    _is_false_positive,
    _should_scan_file,
    _should_skip_directory,
    _get_context,
    _scan_file
)


# ============================================================================
# Test classify_secret_type - Passing Cases
# ============================================================================

class TestClassifySecretTypePassing:
    """Test classify_secret_type with valid secret patterns."""
    
    def test_classify_api_key_stripe_live(self):
        """Test Stripe live API key classification."""
        assert classify_secret_type("demo_stripe_live_key_placeholder_abc123") == "API_KEY"
    
    def test_classify_api_key_stripe_test(self):
        """Test Stripe test API key classification."""
        assert classify_secret_type("demo_stripe_test_key_placeholder_xyz789") == "API_KEY"
    
    def test_classify_api_key_prod(self):
        """Test production API key classification."""
        assert classify_secret_type("demo_api_key_prod_placeholder_secret123") == "API_KEY"
    
    def test_classify_api_key_openai(self):
        """Test OpenAI API key classification."""
        assert classify_secret_type("demo_openai_api_key_placeholder_sk123") == "API_KEY"
    
    def test_classify_api_key_generic(self):
        """Test generic API key pattern."""
        assert classify_secret_type("API_KEY=abcdef1234567890") == "API_KEY"
    
    def test_classify_password_basic(self):
        """Test basic password classification."""
        assert classify_secret_type("password='demo_mypassword123'") == "PASSWORD"
    
    def test_classify_password_db(self):
        """Test database password classification."""
        assert classify_secret_type("DB_PASSWORD='demo_dbpass456'") == "PASSWORD"
    
    def test_classify_password_mysql(self):
        """Test MySQL password classification."""
        assert classify_secret_type("MYSQL_PASSWORD='demo_mysql_pass'") == "PASSWORD"
    
    def test_classify_password_postgres(self):
        """Test PostgreSQL password classification."""
        assert classify_secret_type("POSTGRES_PASSWORD='demo_pg_pass'") == "PASSWORD"
    
    def test_classify_aws_access_key(self):
        """Test AWS access key classification."""
        assert classify_secret_type("DEMO_AWS_ACCESS_KEY_PLACEHOLDER") == "AWS_KEY"
    
    def test_classify_aws_secret_key(self):
        """Test AWS secret key classification."""
        assert classify_secret_type("demo_aws_secret_placeholder_value_abc123") == "AWS_KEY"
    
    def test_classify_aws_secret_access_key(self):
        """Test AWS secret access key pattern."""
        assert classify_secret_type("aws_secret_access_key=abcd1234567890") == "AWS_KEY"
    
    def test_classify_github_token(self):
        """Test GitHub token classification."""
        assert classify_secret_type("demo_github_token_placeholder_ghp123") == "GITHUB_TOKEN"
    
    def test_classify_github_oauth(self):
        """Test GitHub OAuth token classification."""
        assert classify_secret_type("demo_github_oauth_placeholder_gho456") == "GITHUB_TOKEN"
    
    def test_classify_private_key_rsa(self):
        """Test RSA private key classification."""
        assert classify_secret_type("-----BEGIN RSA PRIVATE KEY-----") == "PRIVATE_KEY"
    
    def test_classify_private_key_openssh(self):
        """Test OpenSSH private key classification."""
        assert classify_secret_type("-----BEGIN OPENSSH PRIVATE KEY-----") == "PRIVATE_KEY"
    
    def test_classify_private_key_ec(self):
        """Test EC private key classification."""
        assert classify_secret_type("-----BEGIN EC PRIVATE KEY-----") == "PRIVATE_KEY"
    
    def test_classify_private_key_dsa(self):
        """Test DSA private key classification."""
        assert classify_secret_type("-----BEGIN DSA PRIVATE KEY-----") == "PRIVATE_KEY"
    
    def test_classify_private_key_pgp(self):
        """Test PGP private key classification."""
        assert classify_secret_type("-----BEGIN PGP PRIVATE KEY BLOCK-----") == "PRIVATE_KEY"
    
    def test_classify_jwt_token(self):
        """Test JWT token classification."""
        assert classify_secret_type("demo.jwt.token.placeholder") == "JWT_TOKEN"


# ============================================================================
# Test classify_secret_type - Failing Cases
# ============================================================================

class TestClassifySecretTypeFailing:
    """Test classify_secret_type with invalid or unknown patterns."""
    
    def test_classify_empty_string(self):
        """Test empty string returns UNKNOWN."""
        assert classify_secret_type("") == "UNKNOWN"
    
    def test_classify_none_value(self):
        """Test None value returns UNKNOWN."""
        assert classify_secret_type(None) == "UNKNOWN"
    
    def test_classify_random_string(self):
        """Test random string returns UNKNOWN."""
        assert classify_secret_type("random_text_12345") == "UNKNOWN"
    
    def test_classify_number_only(self):
        """Test number-only string returns UNKNOWN."""
        assert classify_secret_type("1234567890") == "UNKNOWN"
    
    def test_classify_special_chars(self):
        """Test special characters only returns UNKNOWN."""
        assert classify_secret_type("!@#$%^&*()") == "UNKNOWN"
    
    def test_classify_whitespace(self):
        """Test whitespace returns UNKNOWN."""
        assert classify_secret_type("   ") == "UNKNOWN"
    
    def test_classify_url(self):
        """Test URL returns UNKNOWN."""
        assert classify_secret_type("https://example.com") == "UNKNOWN"
    
    def test_classify_email(self):
        """Test email returns UNKNOWN."""
        assert classify_secret_type("user@example.com") == "UNKNOWN"


# ============================================================================
# Test _is_false_positive - Passing Cases (True = is false positive)
# ============================================================================

class TestIsFalsePositivePassing:
    """Test _is_false_positive correctly identifies false positives."""
    
    def test_example_keyword(self):
        """Test 'example' keyword is detected as false positive."""
        assert _is_false_positive("example_api_key", "API_KEY=example_api_key") is True
    
    def test_sample_keyword(self):
        """Test 'sample' keyword is detected as false positive."""
        assert _is_false_positive("sample_password", "password=sample_password") is True
    
    def test_dummy_keyword(self):
        """Test 'dummy' keyword is detected as false positive."""
        assert _is_false_positive("dummy_secret", "SECRET=dummy_secret") is True
    
    def test_fake_keyword(self):
        """Test 'fake' keyword is detected as false positive."""
        assert _is_false_positive("fake_token", "TOKEN=fake_token") is True
    
    def test_your_prefix(self):
        """Test 'your_' prefix is detected as false positive."""
        assert _is_false_positive("your_api_key", "API_KEY=your_api_key") is True
    
    def test_your_dash_prefix(self):
        """Test 'your-' prefix is detected as false positive."""
        assert _is_false_positive("your-secret", "SECRET=your-secret") is True
    
    def test_xxx_placeholder(self):
        """Test 'xxx' placeholder is detected as false positive."""
        assert _is_false_positive("xxx_secret", "password=xxx_secret") is True
    
    def test_asterisk_placeholder(self):
        """Test asterisk placeholder is detected as false positive."""
        assert _is_false_positive("***secret", "API_KEY=***secret") is True
    
    def test_ellipsis_placeholder(self):
        """Test ellipsis placeholder is detected as false positive."""
        assert _is_false_positive("...secret", "password=...secret") is True
    
    def test_todo_keyword(self):
        """Test 'todo' keyword is detected as false positive."""
        assert _is_false_positive("todo_add_key", "API_KEY=todo_add_key") is True
    
    def test_fixme_keyword(self):
        """Test 'fixme' keyword is detected as false positive."""
        assert _is_false_positive("fixme_password", "password=fixme_password") is True
    
    def test_angle_brackets(self):
        """Test angle brackets are detected as false positive."""
        assert _is_false_positive("<api_key>", "API_KEY=<api_key>") is True
    
    def test_curly_braces(self):
        """Test curly braces are detected as false positive."""
        assert _is_false_positive("{secret}", "SECRET={secret}") is True
    
    def test_square_brackets(self):
        """Test square brackets are detected as false positive."""
        assert _is_false_positive("[token]", "TOKEN=[token]") is True
    
    def test_null_value(self):
        """Test 'null' value is detected as false positive."""
        assert _is_false_positive("null", "password=null") is True
    
    def test_none_value(self):
        """Test 'none' value is detected as false positive."""
        assert _is_false_positive("none", "API_KEY=none") is True
    
    def test_undefined_value(self):
        """Test 'undefined' value is detected as false positive."""
        assert _is_false_positive("undefined", "SECRET=undefined") is True
    
    def test_short_password(self):
        """Test short password (< 6 chars) is detected as false positive."""
        assert _is_false_positive("abc", "password='abc'") is True
    
    def test_very_short_password(self):
        """Test very short password is detected as false positive."""
        assert _is_false_positive("12", "password='12'") is True


# ============================================================================
# Test _is_false_positive - Failing Cases (False = is real secret)
# ============================================================================

class TestIsFalsePositiveFailing:
    """Test _is_false_positive correctly identifies real secrets."""
    
    def test_real_api_key(self):
        """Test real API key is not flagged as false positive."""
        assert _is_false_positive("sk_live_abc123xyz789", "API_KEY=sk_live_abc123xyz789") is False
    
    def test_real_password(self):
        """Test real password is not flagged as false positive."""
        assert _is_false_positive("MySecureP@ssw0rd", "password='MySecureP@ssw0rd'") is False
    
    def test_real_long_password(self):
        """Test real long password is not flagged as false positive."""
        assert _is_false_positive("SuperSecret123!", "DB_PASSWORD='SuperSecret123!'") is False
    
    def test_real_token(self):
        """Test real token is not flagged as false positive."""
        assert _is_false_positive("ghp_1234567890abcdef", "TOKEN=ghp_1234567890abcdef") is False
    
    def test_real_aws_key(self):
        """Test real AWS key is not flagged as false positive."""
        assert _is_false_positive("AKIAIOSFODNN7REAL123", "AWS_KEY=AKIAIOSFODNN7REAL123") is False
    
    def test_alphanumeric_secret(self):
        """Test alphanumeric secret is not flagged as false positive."""
        assert _is_false_positive("abc123def456", "SECRET=abc123def456") is False
    
    def test_mixed_case_secret(self):
        """Test mixed case secret is not flagged as false positive."""
        assert _is_false_positive("AbCdEf123", "password='AbCdEf123'") is False


# ============================================================================
# Test _should_scan_file - Passing Cases
# ============================================================================

class TestShouldScanFilePassing:
    """Test _should_scan_file correctly identifies scannable files."""
    
    def test_python_file(self):
        """Test Python file should be scanned."""
        assert _should_scan_file("config.py") is True
    
    def test_javascript_file(self):
        """Test JavaScript file should be scanned."""
        assert _should_scan_file("app.js") is True
    
    def test_env_file(self):
        """Test .env file should be scanned."""
        assert _should_scan_file(".env") is True
    
    def test_env_local_file(self):
        """Test .env.local file should be scanned."""
        assert _should_scan_file(".env.local") is True
    
    def test_env_production_file(self):
        """Test .env.production file should be scanned."""
        assert _should_scan_file(".env.production") is True
    
    def test_yaml_file(self):
        """Test YAML file should be scanned."""
        assert _should_scan_file("config.yaml") is True
    
    def test_yml_file(self):
        """Test YML file should be scanned."""
        assert _should_scan_file("docker-compose.yml") is True
    
    def test_json_file(self):
        """Test JSON file should be scanned."""
        assert _should_scan_file("package.json") is True
    
    def test_shell_script(self):
        """Test shell script should be scanned."""
        assert _should_scan_file("deploy.sh") is True
    
    def test_dockerfile(self):
        """Test Dockerfile should be scanned."""
        assert _should_scan_file("Dockerfile") is True
    
    def test_dockerfile_lowercase(self):
        """Test lowercase dockerfile should be scanned."""
        assert _should_scan_file("dockerfile") is True
    
    def test_makefile(self):
        """Test Makefile should be scanned."""
        assert _should_scan_file("Makefile") is True
    
    def test_makefile_lowercase(self):
        """Test lowercase makefile should be scanned."""
        assert _should_scan_file("makefile") is True
    
    def test_jenkinsfile(self):
        """Test Jenkinsfile should be scanned."""
        assert _should_scan_file("Jenkinsfile") is True
    
    def test_conf_file(self):
        """Test .conf file should be scanned."""
        assert _should_scan_file("nginx.conf") is True
    
    def test_config_file(self):
        """Test .config file should be scanned."""
        assert _should_scan_file("app.config") is True
    
    def test_ini_file(self):
        """Test .ini file should be scanned."""
        assert _should_scan_file("settings.ini") is True


# ============================================================================
# Test _should_scan_file - Failing Cases
# ============================================================================

class TestShouldScanFileFailing:
    """Test _should_scan_file correctly identifies non-scannable files."""
    
    def test_image_png(self):
        """Test PNG image should not be scanned."""
        assert _should_scan_file("logo.png") is False
    
    def test_image_jpg(self):
        """Test JPG image should not be scanned."""
        assert _should_scan_file("photo.jpg") is False
    
    def test_image_gif(self):
        """Test GIF image should not be scanned."""
        assert _should_scan_file("animation.gif") is False
    
    def test_pdf_file(self):
        """Test PDF file should not be scanned."""
        assert _should_scan_file("document.pdf") is False
    
    def test_binary_exe(self):
        """Test executable should not be scanned."""
        assert _should_scan_file("program.exe") is False
    
    def test_markdown_file(self):
        """Test Markdown file should not be scanned."""
        assert _should_scan_file("README.md") is False
    
    def test_text_file(self):
        """Test text file should not be scanned."""
        assert _should_scan_file("notes.txt") is False
    
    def test_zip_file(self):
        """Test ZIP file should not be scanned."""
        assert _should_scan_file("archive.zip") is False
    
    def test_tar_file(self):
        """Test TAR file should not be scanned."""
        assert _should_scan_file("backup.tar") is False
    
    def test_video_file(self):
        """Test video file should not be scanned."""
        assert _should_scan_file("demo.mp4") is False
    
    def test_audio_file(self):
        """Test audio file should not be scanned."""
        assert _should_scan_file("music.mp3") is False
    
    def test_random_extension(self):
        """Test file with random extension should not be scanned."""
        assert _should_scan_file("file.xyz") is False
    
    def test_no_extension(self):
        """Test file without extension (not special) should not be scanned."""
        assert _should_scan_file("randomfile") is False
    
    def test_hidden_file_not_special(self):
        """Test hidden file (not .env) should not be scanned."""
        assert _should_scan_file(".gitignore") is False


# ============================================================================
# Test detect_secrets - Passing Cases
# ============================================================================

class TestDetectSecretsPassing:
    """Test detect_secrets with valid scenarios."""
    
    def test_detect_api_key_in_python_file(self):
        """Test detecting API key in Python file."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text('API_KEY = "demo_stripe_live_key_placeholder_12345"\n')
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 1
            assert any(s['secret_type'] == 'API_KEY' for s in secrets)
            assert any('demo_stripe_live_key_placeholder_12345' in s['secret_value'] for s in secrets)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_multiple_secrets_in_file(self):
        """Test detecting multiple secrets in one file."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text("""
API_KEY = "demo_api_key_prod_placeholder_abc123"
DB_PASSWORD = "demo_db_password_secure123"
AWS_ACCESS_KEY_ID = "DEMO_AWS_ACCESS_KEY_PLACEHOLDER"
""")
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 3
            secret_types = [s['secret_type'] for s in secrets]
            assert 'API_KEY' in secret_types
            assert 'PASSWORD' in secret_types
            assert 'AWS_KEY' in secret_types
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_in_multiple_files(self):
        """Test detecting secrets across multiple files."""
        temp_dir = tempfile.mkdtemp()
        try:
            file1 = Path(temp_dir) / "config1.py"
            file1.write_text('API_KEY = "demo_api_key_prod_placeholder_file1"\n')
            
            file2 = Path(temp_dir) / "config2.py"
            file2.write_text('PASSWORD = "demo_password_file2"\n')
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 2
            file_paths = [s['file_path'] for s in secrets]
            assert any('config1.py' in fp for fp in file_paths)
            assert any('config2.py' in fp for fp in file_paths)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_with_context(self):
        """Test that secrets include context information."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text("""
# Configuration
API_KEY = "demo_api_key_prod_placeholder_context"
# End config
""")
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 1
            secret = secrets[0]
            assert 'context' in secret
            assert 'API_KEY' in secret['context']
            assert secret['severity'] == 'CRITICAL'
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_skips_excluded_directories(self):
        """Test that excluded directories are properly skipped."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create excluded directory with secret
            excluded_dir = Path(temp_dir) / ".git"
            excluded_dir.mkdir()
            (excluded_dir / "config").write_text('SECRET = "should_be_skipped"\n')
            
            # Create normal file with secret
            (Path(temp_dir) / "config.py").write_text('API_KEY = "demo_api_key_prod_placeholder_found"\n')
            
            secrets = detect_secrets(temp_dir)
            
            # Should find secret in config.py but not in .git
            assert len(secrets) >= 1
            for secret in secrets:
                assert '.git' not in secret['file_path']
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_in_env_file(self):
        """Test detecting secrets in .env file."""
        temp_dir = tempfile.mkdtemp()
        try:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text('DATABASE_PASSWORD="demo_db_pass_env"\n')
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 1
            assert any(s['secret_type'] == 'PASSWORD' for s in secrets)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_in_yaml_file(self):
        """Test detecting secrets in YAML file."""
        temp_dir = tempfile.mkdtemp()
        try:
            yaml_file = Path(temp_dir) / "config.yml"
            yaml_file.write_text('api_key: demo_api_key_prod_placeholder_yaml\n')
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 1
            assert any('demo_api_key_prod_placeholder_yaml' in s['secret_value'] for s in secrets)
        finally:
            shutil.rmtree(temp_dir)


# ============================================================================
# Test detect_secrets - Failing Cases
# ============================================================================

class TestDetectSecretsFailing:
    """Test detect_secrets error handling and edge cases."""
    
    def test_detect_secrets_nonexistent_path(self):
        """Test error when path doesn't exist."""
        with pytest.raises(ValueError, match="does not exist"):
            detect_secrets("/nonexistent/path/12345")
    
    def test_detect_secrets_file_not_directory(self):
        """Test error when path is a file, not directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test")
            
            with pytest.raises(ValueError, match="not a directory"):
                detect_secrets(str(test_file))
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_empty_directory(self):
        """Test scanning empty directory returns empty list."""
        temp_dir = tempfile.mkdtemp()
        try:
            secrets = detect_secrets(temp_dir)
            assert secrets == []
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_no_scannable_files(self):
        """Test directory with only non-scannable files."""
        temp_dir = tempfile.mkdtemp()
        try:
            (Path(temp_dir) / "image.png").write_bytes(b'\x89PNG')
            (Path(temp_dir) / "README.md").write_text("# README")
            
            secrets = detect_secrets(temp_dir)
            assert secrets == []
        finally:
            shutil.rmtree(temp_dir)
    
    def test_detect_secrets_filters_false_positives(self):
        """Test that false positives are filtered out."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text("""
API_KEY = "example_api_key"
PASSWORD = "your_password_here"
SECRET = "dummy_secret"
""")
            
            secrets = detect_secrets(temp_dir)
            
            # Should not detect any of these false positives
            assert len(secrets) == 0
        finally:
            shutil.rmtree(temp_dir)


# ============================================================================
# Test find_secret_usages - Passing Cases
# ============================================================================

class TestFindSecretUsagesPassing:
    """Test find_secret_usages with valid scenarios."""
    
    def test_find_usages_single_file(self):
        """Test finding secret usage in single file."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text('API_KEY = "demo_api_key_prod_placeholder_search"\n')
            
            usages = find_secret_usages(temp_dir, "demo_api_key_prod_placeholder_search")
            
            assert len(usages) == 1
            assert usages[0]['secret_value'] == "demo_api_key_prod_placeholder_search"
            assert 'config.py' in usages[0]['file_path']
        finally:
            shutil.rmtree(temp_dir)
    
    def test_find_usages_multiple_files(self):
        """Test finding secret usage across multiple files."""
        temp_dir = tempfile.mkdtemp()
        try:
            secret = "demo_shared_secret_12345"
            
            file1 = Path(temp_dir) / "config1.py"
            file1.write_text(f'SECRET = "{secret}"\n')
            
            file2 = Path(temp_dir) / "config2.py"
            file2.write_text(f'API_KEY = "{secret}"\n')
            
            usages = find_secret_usages(temp_dir, secret)
            
            assert len(usages) == 2
            file_paths = [u['file_path'] for u in usages]
            assert any('config1.py' in fp for fp in file_paths)
            assert any('config2.py' in fp for fp in file_paths)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_find_usages_multiple_occurrences_same_file(self):
        """Test finding multiple occurrences in same file."""
        temp_dir = tempfile.mkdtemp()
        try:
            secret = "demo_repeated_secret"
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text(f"""
PRIMARY_KEY = "{secret}"
BACKUP_KEY = "{secret}"
""")
            
            usages = find_secret_usages(temp_dir, secret)
            
            assert len(usages) == 2
            assert all(u['secret_value'] == secret for u in usages)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_find_usages_classifies_secret_type(self):
        """Test that found usages include classified secret type."""
        temp_dir = tempfile.mkdtemp()
        try:
            secret = "demo_stripe_live_key_placeholder_classify"
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text(f'KEY = "{secret}"\n')
            
            usages = find_secret_usages(temp_dir, secret)
            
            assert len(usages) == 1
            assert usages[0]['secret_type'] == 'API_KEY'
        finally:
            shutil.rmtree(temp_dir)
    
    def test_find_usages_includes_context(self):
        """Test that usages include context information."""
        temp_dir = tempfile.mkdtemp()
        try:
            secret = "demo_context_secret"
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text(f"""
# Configuration
SECRET = "{secret}"
# End
""")
            
            usages = find_secret_usages(temp_dir, secret)
            
            assert len(usages) == 1
            assert 'context' in usages[0]
            assert secret in usages[0]['context']
        finally:
            shutil.rmtree(temp_dir)


# ============================================================================
# Test find_secret_usages - Failing Cases
# ============================================================================

class TestFindSecretUsagesFailing:
    """Test find_secret_usages error handling and edge cases."""
    
    def test_find_usages_nonexistent_path(self):
        """Test error when path doesn't exist."""
        with pytest.raises(ValueError, match="does not exist"):
            find_secret_usages("/nonexistent/path", "secret")
    
    def test_find_usages_empty_secret(self):
        """Test error when secret value is empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            find_secret_usages(".", "")
    
    def test_find_usages_none_secret(self):
        """Test error when secret value is None."""
        with pytest.raises(ValueError, match="cannot be empty"):
            find_secret_usages(".", None)
    
    def test_find_usages_secret_not_found(self):
        """Test finding non-existent secret returns empty list."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text('API_KEY = "different_secret"\n')
            
            usages = find_secret_usages(temp_dir, "nonexistent_secret")
            
            assert usages == []
        finally:
            shutil.rmtree(temp_dir)
    
    def test_find_usages_empty_directory(self):
        """Test finding secret in empty directory returns empty list."""
        temp_dir = tempfile.mkdtemp()
        try:
            usages = find_secret_usages(temp_dir, "any_secret")
            assert usages == []
        finally:
            shutil.rmtree(temp_dir)


# ============================================================================
# Additional Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_get_context_first_line(self):
        """Test context extraction for first line of file."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("line1\nline2\nline3\n")
            
            context = _get_context(str(test_file), 1)
            
            assert "1:" in context
            assert "line1" in context
        finally:
            shutil.rmtree(temp_dir)
    
    def test_get_context_last_line(self):
        """Test context extraction for last line of file."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("line1\nline2\nline3\n")
            
            context = _get_context(str(test_file), 3)
            
            assert "3:" in context
            assert "line3" in context
        finally:
            shutil.rmtree(temp_dir)
    
    def test_should_skip_directory_hidden(self):
        """Test that hidden directories are skipped."""
        assert _should_skip_directory(".hidden") is True
        assert _should_skip_directory(".cache") is True
    
    def test_should_skip_directory_normal(self):
        """Test that normal directories are not skipped."""
        assert _should_skip_directory("src") is False
        assert _should_skip_directory("tests") is False
        assert _should_skip_directory("lib") is False
    
    def test_detect_secrets_with_subdirectories(self):
        """Test detecting secrets in nested subdirectories."""
        temp_dir = tempfile.mkdtemp()
        try:
            subdir = Path(temp_dir) / "src" / "config"
            subdir.mkdir(parents=True)
            
            test_file = subdir / "settings.py"
            test_file.write_text('API_KEY = "demo_api_key_prod_placeholder_nested"\n')
            
            secrets = detect_secrets(temp_dir)
            
            assert len(secrets) >= 1
            assert any('src' in s['file_path'] and 'config' in s['file_path'] for s in secrets)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_scan_file_with_unicode(self):
        """Test scanning file with unicode characters."""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "config.py"
            test_file.write_text('# Configuración\nAPI_KEY = "demo_api_key_prod_placeholder_unicode"\n', encoding='utf-8')
            
            secrets = _scan_file(str(test_file), temp_dir)
            
            assert len(secrets) >= 1
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# Made with Bob
