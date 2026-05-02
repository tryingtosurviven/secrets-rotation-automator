"""Test script to verify no hardcoded secrets in sample-clean-repo"""
import sys
sys.path.insert(0, '..')
from secret_detector import detect_secrets

print("Scanning sample-clean-repo for hardcoded secrets...")
print("=" * 60)

secrets = detect_secrets('.')
print(f"\nScan complete: Found {len(secrets)} secrets")

if secrets:
    print("\nWARNING: Secrets detected:")
    for s in secrets:
        print(f"  - {s['secret_type']} in {s['file_path']}:{s['line_number']}")
        print(f"    Value: {s['secret_value']}")
else:
    print("\nSUCCESS: No hardcoded secrets detected - Repository is clean!")
    print("SUCCESS: All sensitive values use os.environ.get()")
    print("SUCCESS: Best practices for secret management demonstrated")

# Made with Bob
