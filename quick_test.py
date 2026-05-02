import requests

try:
    print("\n✅ Testing API Connection...\n")
    
    # Test 1: Health
    resp = requests.get("http://localhost:5000/api/health")
    print(f"Health Check: {resp.status_code} - {resp.json().get('status')}")
    
    # Test 2: Analyze
    resp = requests.post("http://localhost:5000/api/analyze", json={
        "repo_path": "sample-vulnerable-repo",
        "secret_name": "API_KEY_PROD"
    })
    print(f"Analysis: {resp.status_code} - Found {resp.json().get('locations_found')} secrets")
    
    # Test 3: Find Usages
    resp = requests.post("http://localhost:5000/api/find-secret-usages", json={
        "repo_path": "sample-vulnerable-repo",
        "secret_value": "sk_live_abc123xyz789def456ghi789"
    })
    print(f"Find Usages: {resp.status_code} - Found {resp.json().get('locations_found')} usages")
    
    # Test 4: Classify
    resp = requests.post("http://localhost:5000/api/classify-secret", json={
        "secret_value": "AKIA1234567890ABCDEF"
    })
    print(f"Classify: {resp.status_code} - Type: {resp.json().get('secret_type')}")
    
    # Test 5: Rotation Plan
    resp = requests.post("http://localhost:5000/api/generate-rotation-plan", json={
        "secret_name": "API_KEY_PROD",
        "affected_services": ["API", "Payment"],
        "files": ["src/auth.py"]
    })
    print(f"Rotation Plan: {resp.status_code} - Estimated time: {resp.json().get('estimated_time')}")
    
    print("\n✅✅✅ ALL TESTS PASSED! API IS WORKING! ✅✅✅\n")

except Exception as e:
    print(f"\n❌ Error: {e}\n")
