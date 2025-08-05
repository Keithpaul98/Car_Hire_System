#!/usr/bin/env python
"""
Vehicle API Test Script with Correct Credentials
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token with correct credentials"""
    try:
        login_data = {
            "username": "AdminCarHire",
            "password": "1234567kp"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authentication successful!")
            return data.get('access')
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_vehicle_endpoints():
    """Test all vehicle API endpoints"""
    print("🚗 Testing Vehicle API Endpoints")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test vehicle list endpoint
    print("\n📋 Testing Vehicle List Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle list endpoint accessible")
            data = response.json()
            print(f"   - Vehicles found: {len(data.get('results', data))}")
        else:
            print(f"❌ Vehicle list endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Vehicle list error: {e}")
    
    # Test vehicle categories endpoint
    print("\n🏷️ Testing Vehicle Categories Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/categories/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle categories endpoint accessible")
            data = response.json()
            print(f"   - Categories found: {len(data.get('results', data))}")
        else:
            print(f"❌ Vehicle categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle categories error: {e}")
    
    # Test vehicle brands endpoint
    print("\n🏭 Testing Vehicle Brands Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/brands/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle brands endpoint accessible")
            data = response.json()
            print(f"   - Brands found: {len(data.get('results', data))}")
        else:
            print(f"❌ Vehicle brands endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle brands error: {e}")
    
    # Test vehicle models endpoint
    print("\n🚙 Testing Vehicle Models Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/models/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle models endpoint accessible")
            data = response.json()
            print(f"   - Models found: {len(data.get('results', data))}")
        else:
            print(f"❌ Vehicle models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle models error: {e}")
    
    # Test vehicle features endpoint
    print("\n⚙️ Testing Vehicle Features Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/features/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle features endpoint accessible")
            data = response.json()
            print(f"   - Features found: {len(data.get('results', data))}")
        else:
            print(f"❌ Vehicle features endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle features error: {e}")
    
    # Test vehicle statistics endpoint
    print("\n📊 Testing Vehicle Statistics Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/statistics/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle statistics endpoint accessible")
            data = response.json()
            print(f"   - Total vehicles: {data.get('total_vehicles', 0)}")
            print(f"   - Available vehicles: {data.get('available_vehicles', 0)}")
        else:
            print(f"❌ Vehicle statistics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle statistics error: {e}")

def main():
    """Main test function"""
    print("🚗 Car Hire Management System - Vehicle API Testing")
    print("=" * 60)
    
    # Test all vehicle endpoints
    test_vehicle_endpoints()
    
    print("\n" + "=" * 60)
    print("🏁 Vehicle API Testing Complete!")

if __name__ == "__main__":
    main() 