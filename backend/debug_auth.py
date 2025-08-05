#!/usr/bin/env python
"""
Debug Authentication Script
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def debug_auth():
    """Debug authentication with detailed error reporting"""
    print("🔍 Debugging Authentication...")
    print("=" * 50)
    
    # Test login
    login_data = {
        "username": "AdminCarHire",
        "password": "1234567kp"
    }
    
    try:
        print(f"Attempting login with: {login_data['username']}")
        print(f"Request URL: {BASE_URL}/api/auth/login/")
        print(f"Request Data: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=login_data,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Response Length: {len(response.text)} characters")
        
        # Check if response is HTML (debug page) or JSON
        if 'text/html' in response.headers.get('content-type', ''):
            print("\n❌ Received HTML response (Django debug page)")
            print("This indicates an unhandled exception in the view.")
            print("\nFirst 500 characters of response:")
            print(response.text[:500])
            print("\n" + "="*50)
            print("To see the full error, visit: http://localhost:8000/api/auth/login/")
            print("in your browser and submit the form.")
        else:
            print("\n✅ Received JSON response")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Network/Request Error: {e}")

def test_simple_endpoint():
    """Test a simple endpoint to ensure server is working"""
    print("\n🌐 Testing Server Connectivity...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=10)
        print(f"Admin endpoint status: {response.status_code}")
        
        response = requests.get(f"{BASE_URL}/api/auth/", timeout=10)
        print(f"Auth API root status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Server connectivity error: {e}")

if __name__ == "__main__":
    test_simple_endpoint()
    debug_auth() 