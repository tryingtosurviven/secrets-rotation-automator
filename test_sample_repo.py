"""
Test script to demonstrate secret detection on the sample vulnerable repository.
"""

from secret_detector import detect_secrets, find_secret_usages

print("\n" + "="*70)
print("Testing Secret Detector on Sample Vulnerable Repository")
print("="*70 + "\n")

# Test 1: Detect all secrets
print("Test 1: Detecting all secrets...")
secrets = detect_secrets('sample-vulnerable-repo')
print(f"Found {len(secrets)} total secrets\n")

# Count by type
types = {}
for s in secrets:
    types[s['secret_type']] = types.get(s['secret_type'], 0) + 1

print("Breakdown by type:")
for secret_type, count in sorted(types.items()):
    print(f"  {secret_type}: {count}")

# Test 2: Find specific secret usages
print("\n" + "="*70)
print("Test 2: Finding usages of specific API key...")
print("="*70 + "\n")

api_key = 'sk_live_abc123xyz789def456ghi789'
usages = find_secret_usages('sample-vulnerable-repo', api_key)
print(f"Found {len(usages)} usages of API key: {api_key}\n")

for usage in usages:
    print(f"  - {usage['file_path']}:{usage['line_number']}")

# Test 3: Find database password usages
print("\n" + "="*70)
print("Test 3: Finding usages of database password...")
print("="*70 + "\n")

db_password = 'super_secret_password_123!@#'
usages = find_secret_usages('sample-vulnerable-repo', db_password)
print(f"Found {len(usages)} usages of DB password\n")

for usage in usages:
    print(f"  - {usage['file_path']}:{usage['line_number']}")

print("\n" + "="*70)
print("Testing Complete!")
print("="*70 + "\n")

# Made with Bob
