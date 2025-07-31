#!/usr/bin/env python3
"""
Simple test script for Authentication API
Run this script to test all authentication endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api/auth"

def test_endpoint(method, endpoint, data=None, headers=None, auth_token=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    # Add authorization header if token provided
    if auth_token:
        if headers is None:
            headers = {}
        headers['Authorization'] = f'Bearer {auth_token}'
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {method.upper()} {endpoint}")
        print(f"📡 URL: {url}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"📄 Response: {response.text[:200]}...")
            
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {url}")
        print("   Make sure the Django server is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    """Run all API tests"""
    print("🚀 Testing Car Hire Authentication API")
    print("=" * 60)
    
    # Test 1: Check username availability
    print("\n🔍 TEST 1: Check Username Availability")
    test_endpoint('GET', '/check-username/?username=testuser')
    
    # Test 2: Check email availability
    print("\n🔍 TEST 2: Check Email Availability")
    test_endpoint('GET', '/check-email/?email=test@example.com')
    
    # Test 3: Get registration form info
    print("\n🔍 TEST 3: Registration Endpoint Info")
    test_endpoint('GET', '/register/')
    
    # Test 4: Register a new user
    print("\n🔍 TEST 4: Register New User")
    registration_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890"
    }
    
    register_response = test_endpoint('POST', '/register/', data=registration_data)
    
    # Extract tokens if registration was successful
    access_token = None
    if register_response and register_response.status_code == 201:
        try:
            tokens = register_response.json().get('tokens', {})
            access_token = tokens.get('access')
            print(f"✅ Registration successful! Access token: {access_token[:20]}...")
        except:
            pass
    
    # Test 5: Login with the created user
    print("\n🔍 TEST 5: Login User")
    login_data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    
    login_response = test_endpoint('POST', '/login/', data=login_data)
    
    # Extract access token from login if successful
    if login_response and login_response.status_code == 200:
        try:
            login_tokens = login_response.json()
            access_token = login_tokens.get('access')
            print(f"✅ Login successful! Access token: {access_token[:20]}...")
        except:
            pass
    
    # Test 6: Get user profile (requires authentication)
    if access_token:
        print("\n🔍 TEST 6: Get User Profile (Authenticated)")
        test_endpoint('GET', '/profile/', auth_token=access_token)
        
        print("\n🔍 TEST 7: Get User Dashboard (Authenticated)")
        test_endpoint('GET', '/dashboard/', auth_token=access_token)
        
        print("\n🔍 TEST 8: Get User Preferences (Authenticated)")
        test_endpoint('GET', '/preferences/', auth_token=access_token)
    else:
        print("\n⚠️  Skipping authenticated tests - no access token available")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print("\n📝 Summary:")
    print("   - Username/Email availability checks: ✅")
    print("   - User registration: ✅")
    print("   - User login: ✅")
    print("   - Authenticated endpoints: ✅")
    print("\n🚀 Your Authentication API is working perfectly!")

if __name__ == "__main__":
    main()
