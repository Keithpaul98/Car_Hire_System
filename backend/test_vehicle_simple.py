#!/usr/bin/env python3
"""
Simple Vehicle API Test Script
Tests vehicle endpoints with existing authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_vehicle_endpoints():
    """Test vehicle endpoints without authentication first"""
    
    print("🚗 Testing Vehicle API Endpoints")
    print("="*50)
    
    session = requests.Session()
    
    # Test endpoints that might work without authentication or return proper errors
    endpoints_to_test = [
        ("/vehicles/", "GET", "Vehicle List"),
        ("/vehicles/categories/", "GET", "Vehicle Categories"),
        ("/vehicles/brands/", "GET", "Vehicle Brands"),
        ("/vehicles/models/", "GET", "Vehicle Models"),
        ("/vehicles/features/", "GET", "Vehicle Features"),
        ("/vehicles/statistics/", "GET", "Vehicle Statistics"),
    ]
    
    for endpoint, method, description in endpoints_to_test:
        try:
            url = f"{API_BASE}{endpoint}"
            response = session.request(method, url)
            
            if response.status_code == 200:
                icon = "✅"
                status_text = "SUCCESS"
                
                # Try to parse JSON and show some data
                try:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                        print(f"{icon} {description}: {response.status_code} ({count} items)")
                    elif isinstance(data, dict):
                        if 'results' in data:
                            count = len(data['results'])
                            print(f"{icon} {description}: {response.status_code} ({count} items)")
                        else:
                            print(f"{icon} {description}: {response.status_code} (data returned)")
                    else:
                        print(f"{icon} {description}: {response.status_code}")
                except:
                    print(f"{icon} {description}: {response.status_code}")
                    
            elif response.status_code == 401:
                icon = "🔒"
                print(f"{icon} {description}: {response.status_code} (Authentication Required)")
            elif response.status_code == 403:
                icon = "🚫"
                print(f"{icon} {description}: {response.status_code} (Forbidden)")
            elif response.status_code == 404:
                icon = "❓"
                print(f"{icon} {description}: {response.status_code} (Not Found)")
            elif response.status_code == 405:
                icon = "⚠️"
                print(f"{icon} {description}: {response.status_code} (Method Not Allowed)")
            else:
                icon = "❌"
                print(f"{icon} {description}: {response.status_code} (Error)")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Connection Error (Is server running?)")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    print("="*50)
    print("🏁 Vehicle API endpoint test completed!")
    print("💡 If you see 401 errors, that's normal - endpoints require authentication")
    print("💡 If you see 200 responses, the endpoints are working correctly!")

if __name__ == "__main__":
    test_vehicle_endpoints()
