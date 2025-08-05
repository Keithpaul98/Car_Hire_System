#!/usr/bin/env python3
"""
Comprehensive Vehicle API Test Script
Tests all vehicle-related endpoints with authentication
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class VehicleAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_user_data = {
            "username": "vehicletester",
            "email": "vehicletester@test.com",
            "password": "TestPass123!",
            "first_name": "Vehicle",
            "last_name": "Tester",
            "phone_number": "+1234567890"
        }
        
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🚗 {title}")
        print(f"{'='*60}")
        
    def print_result(self, endpoint, method, status_code, success=True):
        """Print test result"""
        icon = "✅" if success else "❌"
        print(f"{icon} {method} {endpoint}: {status_code}")
        
    def setup_authentication(self):
        """Register user and get JWT tokens"""
        self.print_header("Setting Up Authentication")
        
        # Try to register user (might fail if already exists)
        try:
            response = self.session.post(
                f"{API_BASE}/auth/register/",
                json=self.test_user_data
            )
            if response.status_code == 201:
                print("✅ User registered successfully")
            elif response.status_code == 400:
                print("ℹ️  User already exists, proceeding to login")
        except Exception as e:
            print(f"❌ Registration error: {e}")
            
        # Login to get tokens
        login_data = {
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login/", json=login_data)
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens.get('access')
                self.refresh_token = tokens.get('refresh')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
            
    def test_vehicle_categories(self):
        """Test vehicle categories endpoint"""
        self.print_header("Testing Vehicle Categories")
        
        try:
            response = self.session.get(f"{API_BASE}/vehicles/categories/")
            self.print_result("/vehicles/categories/", "GET", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                categories = response.json()
                print(f"📊 Found {len(categories)} categories")
                for category in categories[:3]:  # Show first 3
                    print(f"   - {category.get('name', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ Categories test error: {e}")
            
    def test_vehicle_brands(self):
        """Test vehicle brands endpoint"""
        self.print_header("Testing Vehicle Brands")
        
        try:
            response = self.session.get(f"{API_BASE}/vehicles/brands/")
            self.print_result("/vehicles/brands/", "GET", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                brands = response.json()
                print(f"📊 Found {len(brands)} brands")
                for brand in brands[:3]:  # Show first 3
                    print(f"   - {brand.get('name', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ Brands test error: {e}")
            
    def test_vehicle_models(self):
        """Test vehicle models endpoint"""
        self.print_header("Testing Vehicle Models")
        
        try:
            response = self.session.get(f"{API_BASE}/vehicles/models/")
            self.print_result("/vehicles/models/", "GET", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                models = response.json()
                print(f"📊 Found {len(models)} models")
                for model in models[:3]:  # Show first 3
                    brand_name = model.get('brand', {}).get('name', 'N/A')
                    model_name = model.get('name', 'N/A')
                    print(f"   - {brand_name} {model_name}")
                    
        except Exception as e:
            print(f"❌ Models test error: {e}")
            
    def test_vehicle_features(self):
        """Test vehicle features endpoint"""
        self.print_header("Testing Vehicle Features")
        
        try:
            response = self.session.get(f"{API_BASE}/vehicles/features/")
            self.print_result("/vehicles/features/", "GET", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                features = response.json()
                print(f"📊 Found {len(features)} features")
                for feature in features[:3]:  # Show first 3
                    print(f"   - {feature.get('name', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ Features test error: {e}")
            
    def test_vehicle_list(self):
        """Test vehicle list endpoint"""
        self.print_header("Testing Vehicle List")
        
        try:
            # Test basic list
            response = self.session.get(f"{API_BASE}/vehicles/")
            self.print_result("/vehicles/", "GET", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                vehicles = response.json()
                if isinstance(vehicles, dict) and 'results' in vehicles:
                    vehicles = vehicles['results']
                    
                print(f"📊 Found {len(vehicles)} vehicles")
                for vehicle in vehicles[:2]:  # Show first 2
                    model_info = vehicle.get('model', {})
                    brand_name = model_info.get('brand', {}).get('name', 'N/A')
                    model_name = model_info.get('name', 'N/A')
                    year = vehicle.get('year', 'N/A')
                    rate = vehicle.get('daily_rate', 'N/A')
                    print(f"   - {year} {brand_name} {model_name} - ${rate}/day")
                    
            # Test with filters
            print("\n🔍 Testing with filters:")
            
            # Filter by availability
            response = self.session.get(f"{API_BASE}/vehicles/?available_only=true")
            self.print_result("/vehicles/?available_only=true", "GET", response.status_code, 
                            response.status_code == 200)
            
            # Filter by price range
            response = self.session.get(f"{API_BASE}/vehicles/?min_price=50&max_price=200")
            self.print_result("/vehicles/?min_price=50&max_price=200", "GET", response.status_code, 
                            response.status_code == 200)
                            
        except Exception as e:
            print(f"❌ Vehicle list test error: {e}")
            
    def test_vehicle_search(self):
        """Test vehicle search endpoint"""
        self.print_header("Testing Vehicle Search")
        
        search_criteria = {
            "available_only": True,
            "fuel_type": "petrol",
            "min_seats": 4,
            "max_price": 150
        }
        
        try:
            response = self.session.post(f"{API_BASE}/vehicles/search/", json=search_criteria)
            self.print_result("/vehicles/search/", "POST", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                results = response.json()
                vehicles = results.get('vehicles', [])
                print(f"📊 Search found {len(vehicles)} matching vehicles")
                print(f"🔍 Search criteria: {search_criteria}")
                
        except Exception as e:
            print(f"❌ Vehicle search test error: {e}")
            
    def test_vehicle_statistics(self):
        """Test vehicle statistics endpoint"""
        self.print_header("Testing Vehicle Statistics")
        
        try:
            response = self.session.get(f"{API_BASE}/vehicles/statistics/")
            self.print_result("/vehicles/statistics/", "GET", response.status_code, 
                            response.status_code == 200)
            
            if response.status_code == 200:
                stats = response.json()
                print("📊 Fleet Statistics:")
                print(f"   - Total Vehicles: {stats.get('total_vehicles', 'N/A')}")
                print(f"   - Available: {stats.get('available_vehicles', 'N/A')}")
                print(f"   - Rented: {stats.get('rented_vehicles', 'N/A')}")
                print(f"   - In Maintenance: {stats.get('maintenance_vehicles', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Statistics test error: {e}")
            
    def test_vehicle_detail(self):
        """Test vehicle detail endpoint"""
        self.print_header("Testing Vehicle Detail")
        
        try:
            # First get a vehicle ID from the list
            response = self.session.get(f"{API_BASE}/vehicles/")
            if response.status_code == 200:
                vehicles = response.json()
                if isinstance(vehicles, dict) and 'results' in vehicles:
                    vehicles = vehicles['results']
                    
                if vehicles:
                    vehicle_id = vehicles[0]['id']
                    
                    # Test vehicle detail
                    response = self.session.get(f"{API_BASE}/vehicles/{vehicle_id}/")
                    self.print_result(f"/vehicles/{vehicle_id}/", "GET", response.status_code, 
                                    response.status_code == 200)
                    
                    if response.status_code == 200:
                        vehicle = response.json()
                        model_info = vehicle.get('model', {})
                        brand_name = model_info.get('brand', {}).get('name', 'N/A')
                        model_name = model_info.get('name', 'N/A')
                        print(f"📋 Vehicle Details: {vehicle.get('year')} {brand_name} {model_name}")
                        print(f"   - Status: {vehicle.get('status', 'N/A')}")
                        print(f"   - Daily Rate: ${vehicle.get('daily_rate', 'N/A')}")
                        print(f"   - Seating: {vehicle.get('seating_capacity', 'N/A')} seats")
                else:
                    print("ℹ️  No vehicles found to test detail endpoint")
                    
        except Exception as e:
            print(f"❌ Vehicle detail test error: {e}")
            
    def run_all_tests(self):
        """Run all vehicle API tests"""
        print("🚗 Starting Comprehensive Vehicle API Tests")
        print(f"🌐 Base URL: {BASE_URL}")
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
            
        # Run all tests
        self.test_vehicle_categories()
        self.test_vehicle_brands()
        self.test_vehicle_models()
        self.test_vehicle_features()
        self.test_vehicle_list()
        self.test_vehicle_search()
        self.test_vehicle_statistics()
        self.test_vehicle_detail()
        
        # Summary
        self.print_header("Test Summary")
        print("🏁 Vehicle API tests completed!")
        print("📝 Check the results above for any failed endpoints")
        print("💡 Make sure the Django server is running on localhost:8000")
        
        return True

if __name__ == "__main__":
    tester = VehicleAPITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
