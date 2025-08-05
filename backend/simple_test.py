#!/usr/bin/env python
"""
Simple test to verify API endpoints are accessible
"""

import requests

def test_api_endpoints():
    """Test basic API endpoint accessibility"""
    base_url = "http://localhost:8000"
    
    print("🚗 Testing Car Hire API Endpoints")
    print("=" * 40)
    
    # Test admin endpoint
    try:
        response = requests.get(f"{base_url}/admin/", timeout=5)
        print(f"✅ Admin endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin endpoint: {e}")
    
    # Test registration endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/register/", timeout=5)
        print(f"✅ Registration endpoint: {response.status_code}")
        if response.status_code == 200:
            print("   - Registration form accessible")
    except Exception as e:
        print(f"❌ Registration endpoint: {e}")
    
    # Test login endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/login/", timeout=5)
        print(f"✅ Login endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Login endpoint: {e}")
    
    # Test profile endpoint (should require auth)
    try:
        response = requests.get(f"{base_url}/api/auth/profile/", timeout=5)
        print(f"✅ Profile endpoint: {response.status_code}")
        if response.status_code == 401:
            print("   - Correctly requires authentication")
    except Exception as e:
        print(f"❌ Profile endpoint: {e}")
    
    print("\n" + "=" * 40)
    print("🏁 Basic API Test Complete!")

if __name__ == "__main__":
    test_api_endpoints() 