#!/usr/bin/env python
"""
Simple Authentication Test Script
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    """Test authentication endpoint"""
    print("🔐 Testing Authentication...")
    print("=" * 40)
    
    # Test login
    login_data = {
        "username": "AdminCarHire",
        "password": "1234567kp"
    }
    
    try:
        print(f"Attempting login with: {login_data['username']}")
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=login_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentication successful!")
            print(f"Access Token: {data.get('access', 'Not found')[:50]}...")
            return data.get('access')
        else:
            print("❌ Authentication failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_vehicle_endpoint(token):
    """Test vehicle endpoint with token"""
    if not token:
        print("❌ No token available")
        return
    
    print("\n🚗 Testing Vehicle Endpoint...")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Vehicle endpoint accessible!")
        else:
            print("❌ Vehicle endpoint failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    token = test_auth()
    if token:
        test_vehicle_endpoint(token) 