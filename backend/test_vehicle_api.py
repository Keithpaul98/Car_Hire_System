#!/usr/bin/env python
"""
Vehicle API Test Script for the Car Hire Management System
Tests all vehicle-related endpoints to verify functionality
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token for testing"""
    try:
        # Try to login with existing user or create one
        login_data = {
            "username": "admin_car",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print("❌ Could not get authentication token")
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
    
    # Test vehicle search endpoint
    print("\n🔍 Testing Vehicle Search Endpoint...")
    try:
        search_data = {
            "available_only": True,
            "order_by": "-created_at"
        }
        response = requests.post(f"{BASE_URL}/api/vehicles/search/", 
                               json=search_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle search endpoint accessible")
            data = response.json()
            print(f"   - Search results: {len(data.get('results', data))}")
        else:
            print(f"❌ Vehicle search endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Vehicle search error: {e}")

def test_vehicle_creation():
    """Test vehicle creation (if we have brands and models)"""
    print("\n➕ Testing Vehicle Creation...")
    
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First, let's check if we have brands and models
    try:
        brands_response = requests.get(f"{BASE_URL}/api/vehicles/brands/", headers=headers, timeout=10)
        models_response = requests.get(f"{BASE_URL}/api/vehicles/models/", headers=headers, timeout=10)
        
        if brands_response.status_code == 200 and models_response.status_code == 200:
            brands = brands_response.json().get('results', brands_response.json())
            models = models_response.json().get('results', models_response.json())
            
            if brands and models:
                # Create a test vehicle
                test_vehicle_data = {
                    "model_id": models[0]['id'],
                    "year": 2023,
                    "color": "White",
                    "license_plate": "TEST123",
                    "fuel_type": "petrol",
                    "transmission": "automatic",
                    "seating_capacity": 5,
                    "doors": 4,
                    "status": "available",
                    "condition": "good",
                    "current_mileage": 15000,
                    "daily_rate": "150.00",
                    "current_location": "Test Location"
                }
                
                response = requests.post(f"{BASE_URL}/api/vehicles/", 
                                       json=test_vehicle_data, headers=headers, timeout=10)
                
                if response.status_code == 201:
                    print("✅ Vehicle creation successful!")
                    data = response.json()
                    print(f"   - Vehicle ID: {data.get('id')}")
                    print(f"   - License Plate: {data.get('license_plate')}")
                    return data.get('id')
                else:
                    print(f"❌ Vehicle creation failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print("⚠️ No brands or models available for testing vehicle creation")
        else:
            print("⚠️ Could not fetch brands/models for testing")
            
    except Exception as e:
        print(f"❌ Vehicle creation test error: {e}")
    
    return None

def test_vehicle_detail(vehicle_id):
    """Test vehicle detail endpoint"""
    if not vehicle_id:
        return
    
    print(f"\n📄 Testing Vehicle Detail Endpoint (ID: {vehicle_id})...")
    
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Vehicle detail endpoint accessible")
            data = response.json()
            print(f"   - Vehicle: {data.get('display_name', 'N/A')}")
            print(f"   - Status: {data.get('status', 'N/A')}")
            print(f"   - Daily Rate: ${data.get('daily_rate', 'N/A')}")
        else:
            print(f"❌ Vehicle detail endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle detail error: {e}")

def main():
    """Main test function"""
    print("🚗 Car Hire Management System - Vehicle API Testing")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test all vehicle endpoints
    test_vehicle_endpoints()
    
    # Test vehicle creation
    vehicle_id = test_vehicle_creation()
    
    # Test vehicle detail if we created one
    if vehicle_id:
        test_vehicle_detail(vehicle_id)
    
    print("\n" + "=" * 60)
    print("🏁 Vehicle API Testing Complete!")

if __name__ == "__main__":
    main() 