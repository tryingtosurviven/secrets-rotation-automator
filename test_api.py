import requests
import json

BASE_URL = "http://localhost:5000"

print("\n" + "="*80)
print("Testing Secrets Rotation Automator API")
print("="*80 + "\n")

# Test 1: Health Check
print("TEST 1: Health Check")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/api/health")
    print(json.dumps(response.json(), indent=2))
    print("✅ PASSED\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 2: Analyze Secrets
print("TEST 2: Analyze Secrets in Sample Repo")
print("-" * 40)
try:
    response = requests.post(f"{BASE_URL}/api/analyze", json={
        "repo_path": "sample-vulnerable-repo",
        "secret_name": "API_KEY_PROD"
    })
    result = response.json()
    print(f"Secret Name: {result.get('secret_name')}")
    print(f"Locations Found: {result.get('locations_found')}")
    print(f"Affected Services: {result.get('affected_services')}")
    print(f"Time to Fix: {result.get('time_to_fix_estimate')}")
    print("✅ PASSED\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 3: Find Secret Usages
print("TEST 3: Find Secret Usages")
print("-" * 40)
try:
    response = requests.post(f"{BASE_URL}/api/find-secret-usages", json={
        "repo_path": "sample-vulnerable-repo",
        "secret_value": "demo_stripe_live_key_placeholder_12345"
    })
    result = response.json()
    print(f"Secret Value: {result.get('secret_value')}")
    print(f"Locations Found: {result.get('locations_found')}")
    for loc in result.get('locations', [])[:3]:
        print(f" - {loc['file']}:{loc['line']}")
    print("✅ PASSED\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 4: Classify Secret
print("TEST 4: Classify Secret Type")
print("-" * 40)
try:
    response = requests.post(f"{BASE_URL}/api/classify-secret", json={
        "secret_value": "DEMO_AWS_ACCESS_KEY_PLACEHOLDER"
    })
    result = response.json()
    print(f"Secret Type: {result.get('secret_type')}")
    print(f"Confidence: {result.get('confidence')}")
    print("✅ PASSED\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 5: Generate Rotation Plan
print("TEST 5: Generate Rotation Plan")
print("-" * 40)
try:
    response = requests.post(f"{BASE_URL}/api/generate-rotation-plan", json={
        "secret_name": "API_KEY_PROD",
        "affected_services": ["API", "Payment"],
        "files": ["src/auth.py", "src/payment.py"]
    })
    result = response.json()
    print(f"Secret Name: {result.get('secret_name')}")
    print(f"Affected Services: {result.get('affected_services')}")
    print(f"Estimated Time: {result.get('estimated_time')}")
    print(f"Steps: {len(result.get('step_by_step_plan', []))}")
    print("✅ PASSED\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

print("="*80)
print("All Tests Complete!")
print("="*80 + "\n")
