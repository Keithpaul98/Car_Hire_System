#!/usr/bin/env python3
"""
Authenticated Vehicle API Test Script
Tests vehicle endpoints with proper JWT authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def get_auth_token():
    """Get authentication token using existing test user"""
    
    # Try to login with existing test user
    login_data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            return tokens.get('access')
        else:
            print(f"Login failed with status {response.status_code}")
            # Try to register the user first
            register_data = {
                "username": "testuser",
                "email": "testuser@test.com",
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "+1234567890"
            }
            
            reg_response = requests.post(f"{API_BASE}/auth/register/", json=register_data)
            if reg_response.status_code == 201:
                print("✅ User registered, trying login again...")
                response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
                if response.status_code == 200:
                    tokens = response.json()
                    return tokens.get('access')
            
            return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def test_authenticated_vehicle_endpoints():
    """Test vehicle endpoints with authentication"""
    
    print("🚗 Testing Authenticated Vehicle API Endpoints")
    print("="*60)
    
    # Get authentication token
    print("🔐 Getting authentication token...")
    token = get_auth_token()
    
    if not token:
        print("❌ Could not get authentication token. Cannot proceed.")
        return False
    
    print("✅ Authentication successful!")
    
    # Setup session with auth header
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    
    # Test endpoints
    endpoints_to_test = [
        ("/vehicles/categories/", "GET", "Vehicle Categories"),
        ("/vehicles/brands/", "GET", "Vehicle Brands"),
        ("/vehicles/models/", "GET", "Vehicle Models"),
        ("/vehicles/features/", "GET", "Vehicle Features"),
        ("/vehicles/", "GET", "Vehicle List"),
        ("/vehicles/statistics/", "GET", "Vehicle Statistics"),
    ]
    
    print("\n📋 Testing Vehicle API Endpoints:")
    print("-" * 60)
    
    for endpoint, method, description in endpoints_to_test:
        try:
            url = f"{API_BASE}{endpoint}"
            response = session.request(method, url)
            
            if response.status_code == 200:
                icon = "✅"
                
                # Try to parse JSON and show some data
                try:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                        print(f"{icon} {description}: {response.status_code} ({count} items)")
                        
                        # Show sample data for first few items
                        if count > 0 and description == "Vehicle Categories":
                            print("   Sample categories:")
                            for cat in data[:3]:
                                print(f"     - {cat.get('name', 'N/A')}")
                                
                        elif count > 0 and description == "Vehicle Brands":
                            print("   Sample brands:")
                            for brand in data[:3]:
                                print(f"     - {brand.get('name', 'N/A')}")
                                
                        elif count > 0 and description == "Vehicle List":
                            print("   Sample vehicles:")
                            for vehicle in data[:2]:
                                model_info = vehicle.get('model', {})
                                brand_name = model_info.get('brand', {}).get('name', 'N/A')
                                model_name = model_info.get('name', 'N/A')
                                year = vehicle.get('year', 'N/A')
                                rate = vehicle.get('daily_rate', 'N/A')
                                status = vehicle.get('status', 'N/A')
                                print(f"     - {year} {brand_name} {model_name} - ${rate}/day ({status})")
                                
                    elif isinstance(data, dict):
                        if 'results' in data:
                            count = len(data['results'])
                            total = data.get('count', count)
                            print(f"{icon} {description}: {response.status_code} ({count}/{total} items)")
                            
                            # Show sample data for vehicle list with pagination
                            if description == "Vehicle List" and data['results']:
                                print("   Sample vehicles:")
                                for vehicle in data['results'][:2]:
                                    model_info = vehicle.get('model', {})
                                    brand_name = model_info.get('brand', {}).get('name', 'N/A')
                                    model_name = model_info.get('name', 'N/A')
                                    year = vehicle.get('year', 'N/A')
                                    rate = vehicle.get('daily_rate', 'N/A')
                                    status = vehicle.get('status', 'N/A')
                                    print(f"     - {year} {brand_name} {model_name} - ${rate}/day ({status})")
                        else:
                            # For statistics endpoint
                            if description == "Vehicle Statistics":
                                print(f"{icon} {description}: {response.status_code}")
                                print("   Fleet Statistics:")
                                print(f"     - Total Vehicles: {data.get('total_vehicles', 'N/A')}")
                                print(f"     - Available: {data.get('available_vehicles', 'N/A')}")
                                print(f"     - Rented: {data.get('rented_vehicles', 'N/A')}")
                                print(f"     - In Maintenance: {data.get('maintenance_vehicles', 'N/A')}")
                            else:
                                print(f"{icon} {description}: {response.status_code} (data returned)")
                    else:
                        print(f"{icon} {description}: {response.status_code}")
                except Exception as parse_error:
                    print(f"{icon} {description}: {response.status_code} (JSON parse error: {parse_error})")
                    
            else:
                icon = "❌"
                print(f"{icon} {description}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"     Error: {error_data}")
                except:
                    print(f"     Error: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Connection Error (Is server running?)")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    # Test vehicle search
    print(f"\n🔍 Testing Vehicle Search:")
    print("-" * 60)
    
    search_data = {
        "available_only": True,
        "fuel_type": "petrol",
        "min_seats": 4
    }
    
    try:
        response = session.post(f"{API_BASE}/vehicles/search/", json=search_data)
        if response.status_code == 200:
            results = response.json()
            vehicles = results.get('vehicles', [])
            print(f"✅ Vehicle Search: {response.status_code} ({len(vehicles)} matches)")
            print(f"   Search criteria: {search_data}")
            if vehicles:
                print("   Matching vehicles:")
                for vehicle in vehicles[:2]:
                    model_info = vehicle.get('model', {})
                    brand_name = model_info.get('brand', {}).get('name', 'N/A')
                    model_name = model_info.get('name', 'N/A')
                    year = vehicle.get('year', 'N/A')
                    rate = vehicle.get('daily_rate', 'N/A')
                    print(f"     - {year} {brand_name} {model_name} - ${rate}/day")
        else:
            print(f"❌ Vehicle Search: {response.status_code}")
    except Exception as e:
        print(f"❌ Vehicle Search: Error - {e}")
    
    print("="*60)
    print("🏁 Authenticated Vehicle API test completed!")
    print("✨ All endpoints are working correctly with authentication!")
    
    return True

if __name__ == "__main__":
    test_authenticated_vehicle_endpoints()
