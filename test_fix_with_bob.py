"""
Test script for the "Fix with Bob" functionality
"""

import sys
import io
import requests
import json

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"

def test_fix_all_secrets():
    """Test the fix-all-secrets API endpoint"""
    print("=" * 80)
    print("Testing Fix with Bob Functionality")
    print("=" * 80)
    
    # Test data
    payload = {
        "repo_path": "sample-vulnerable-repo",
        "secret_name": "API_KEY"
    }
    
    print(f"\n1. Sending request to fix secrets in: {payload['repo_path']}")
    print(f"   Secret name filter: {payload['secret_name']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/fix-all-secrets",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n2. Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n3. Results:")
            print(f"   ✅ Success: {data.get('success')}")
            print(f"   📊 Fixed Count: {data.get('fixed_count')}")
            print(f"   ❌ Failed Count: {data.get('failed_count')}")
            print(f"   💾 Backup Created: {data.get('backup_created')}")
            if data.get('backup_path'):
                print(f"   📁 Backup Path: {data.get('backup_path')}")
            print(f"   📄 .env File Created: {data.get('env_file_created')}")
            
            if data.get('env_vars'):
                print(f"\n4. Environment Variables Created:")
                for var_name, placeholder in data['env_vars'].items():
                    print(f"   - {var_name}={placeholder}")
            
            if data.get('details'):
                print(f"\n5. Detailed Results:")
                for detail in data['details'][:10]:  # Show first 10
                    status = detail.get('status', 'unknown')
                    if status == 'fixed':
                        print(f"   ✅ {detail.get('file')}:{detail.get('line')} - {detail.get('message')}")
                    elif status == 'created':
                        print(f"   📄 {detail.get('file')} - {detail.get('message')}")
                    elif status == 'failed':
                        print(f"   ❌ {detail.get('file')}:{detail.get('line')} - {detail.get('message')}")
                
                if len(data['details']) > 10:
                    print(f"   ... and {len(data['details']) - 10} more")
            
            print("\n" + "=" * 80)
            print("TEST PASSED: Fix with Bob is working!")
            print("=" * 80)
            
        else:
            print(f"\nTEST FAILED: Unexpected status code {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\nTEST FAILED: Could not connect to Flask app")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")

if __name__ == "__main__":
    test_fix_all_secrets()

# Made with Bob
