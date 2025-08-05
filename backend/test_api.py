#!/usr/bin/env python
"""
Simple API test script for the Car Hire Management System
Tests the authentication endpoints to verify they're working
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not accessible: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication Endpoints...")
    
    # Test registration endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/auth/register/", timeout=5)
        if response.status_code == 200:
            print("✅ Registration endpoint is accessible")
            data = response.json()
            print(f"   - Endpoint provides registration form")
        else:
            print(f"❌ Registration endpoint returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration endpoint error: {e}")
    
    # Test login endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login/", timeout=5)
        if response.status_code == 200:
            print("✅ Login endpoint is accessible")
        else:
            print(f"❌ Login endpoint returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Login endpoint error: {e}")
    
    # Test profile endpoint (should require authentication)
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile/", timeout=5)
        if response.status_code == 401:
            print("✅ Profile endpoint correctly requires authentication")
        else:
            print(f"⚠️  Profile endpoint returned unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Profile endpoint error: {e}")

def test_user_registration():
    """Test actual user registration"""
    print("\n👤 Testing User Registration...")
    
    test_user_data = {
        "username": "testuser_api",
        "email": "testapi@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "API",
        "phone_number": "+1234567890"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json=test_user_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ User registration successful!")
            data = response.json()
            print(f"   - User created: {data.get('user', {}).get('username')}")
            print(f"   - Tokens received: {'access' in data.get('tokens', {})}")
            return data.get('tokens', {}).get('access')
        else:
            print(f"❌ Registration failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration request failed: {e}")
        return None

def test_authenticated_endpoints(access_token):
    """Test endpoints that require authentication"""
    if not access_token:
        print("⚠️  Skipping authenticated endpoint tests (no access token)")
        return
    
    print("\n🔒 Testing Authenticated Endpoints...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test profile endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Profile endpoint accessible with token")
            data = response.json()
            print(f"   - User: {data.get('username')}")
        else:
            print(f"❌ Profile endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Profile request failed: {e}")
    
    # Test dashboard endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/auth/dashboard/", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard endpoint accessible with token")
        else:
            print(f"❌ Dashboard endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard request failed: {e}")

def main():
    """Main test function"""
    print("🚗 Car Hire Management System - API Testing")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Cannot proceed with API tests - server not accessible")
        return
    
    # Test authentication endpoints
    test_auth_endpoints()
    
    # Test user registration
    access_token = test_user_registration()
    
    # Test authenticated endpoints
    test_authenticated_endpoints(access_token)
    
    print("\n" + "=" * 50)
    print("🏁 API Testing Complete!")

if __name__ == "__main__":
    main() 