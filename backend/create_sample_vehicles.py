#!/usr/bin/env python3
"""
Create Sample Vehicle Data
Populates the database with sample vehicles, categories, brands, models, and features
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from vehicles.models import (
    VehicleCategory, VehicleBrand, VehicleModel, Vehicle, 
    VehicleFeature, VehicleFeatureAssignment
)
from authentication.models import CustomUser

def create_sample_data():
    """Create comprehensive sample vehicle data"""
    
    print("🚗 Creating Sample Vehicle Data...")
    
    # Create or get admin user
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@petersonscarhire.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('AdminPass123!')
        admin_user.save()
        print("✅ Admin user created")
    else:
        print("ℹ️  Admin user already exists")
    
    # Create Vehicle Categories
    categories_data = [
        {'name': 'Economy', 'description': 'Budget-friendly vehicles with good fuel efficiency', 'icon': 'fa-car', 'sort_order': 1},
        {'name': 'Compact', 'description': 'Small to medium-sized cars perfect for city driving', 'icon': 'fa-car-side', 'sort_order': 2},
        {'name': 'Mid-size', 'description': 'Comfortable vehicles with more space', 'icon': 'fa-car', 'sort_order': 3},
        {'name': 'Full-size', 'description': 'Large, comfortable vehicles for long trips', 'icon': 'fa-car', 'sort_order': 4},
        {'name': 'SUV', 'description': 'Sport Utility Vehicles with high seating position', 'icon': 'fa-truck', 'sort_order': 5},
        {'name': 'Luxury', 'description': 'Premium vehicles with high-end features', 'icon': 'fa-gem', 'sort_order': 6},
        {'name': 'Van', 'description': 'Large vehicles for groups or cargo', 'icon': 'fa-shuttle-van', 'sort_order': 7},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = VehicleCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
        if created:
            print(f"✅ Created category: {cat_data['name']}")
    
    # Create Vehicle Brands
    brands_data = [
        {'name': 'Toyota', 'country_of_origin': 'Japan'},
        {'name': 'Honda', 'country_of_origin': 'Japan'},
        {'name': 'Ford', 'country_of_origin': 'USA'},
        {'name': 'Chevrolet', 'country_of_origin': 'USA'},
        {'name': 'BMW', 'country_of_origin': 'Germany'},
        {'name': 'Mercedes-Benz', 'country_of_origin': 'Germany'},
        {'name': 'Audi', 'country_of_origin': 'Germany'},
        {'name': 'Nissan', 'country_of_origin': 'Japan'},
        {'name': 'Hyundai', 'country_of_origin': 'South Korea'},
        {'name': 'Kia', 'country_of_origin': 'South Korea'},
    ]
    
    brands = {}
    for brand_data in brands_data:
        brand, created = VehicleBrand.objects.get_or_create(
            name=brand_data['name'],
            defaults=brand_data
        )
        brands[brand_data['name']] = brand
        if created:
            print(f"✅ Created brand: {brand_data['name']}")
    
    # Create Vehicle Models
    models_data = [
        # Economy
        {'brand': 'Toyota', 'name': 'Corolla', 'category': 'Economy', 'year_introduced': 2020},
        {'brand': 'Honda', 'name': 'Civic', 'category': 'Economy', 'year_introduced': 2020},
        {'brand': 'Nissan', 'name': 'Sentra', 'category': 'Economy', 'year_introduced': 2020},
        
        # Compact
        {'brand': 'Toyota', 'name': 'Camry', 'category': 'Compact', 'year_introduced': 2021},
        {'brand': 'Honda', 'name': 'Accord', 'category': 'Compact', 'year_introduced': 2021},
        {'brand': 'Hyundai', 'name': 'Elantra', 'category': 'Compact', 'year_introduced': 2021},
        
        # Mid-size
        {'brand': 'Toyota', 'name': 'Avalon', 'category': 'Mid-size', 'year_introduced': 2022},
        {'brand': 'Ford', 'name': 'Fusion', 'category': 'Mid-size', 'year_introduced': 2022},
        {'brand': 'Chevrolet', 'name': 'Malibu', 'category': 'Mid-size', 'year_introduced': 2022},
        
        # SUV
        {'brand': 'Toyota', 'name': 'RAV4', 'category': 'SUV', 'year_introduced': 2022},
        {'brand': 'Honda', 'name': 'CR-V', 'category': 'SUV', 'year_introduced': 2022},
        {'brand': 'Ford', 'name': 'Explorer', 'category': 'SUV', 'year_introduced': 2023},
        {'brand': 'Chevrolet', 'name': 'Tahoe', 'category': 'SUV', 'year_introduced': 2023},
        
        # Luxury
        {'brand': 'BMW', 'name': '3 Series', 'category': 'Luxury', 'year_introduced': 2023},
        {'brand': 'Mercedes-Benz', 'name': 'C-Class', 'category': 'Luxury', 'year_introduced': 2023},
        {'brand': 'Audi', 'name': 'A4', 'category': 'Luxury', 'year_introduced': 2023},
    ]
    
    models = {}
    for model_data in models_data:
        brand = brands[model_data['brand']]
        category = categories[model_data['category']]
        
        model, created = VehicleModel.objects.get_or_create(
            brand=brand,
            name=model_data['name'],
            defaults={
                'category': category,
                'year_introduced': model_data['year_introduced']
            }
        )
        models[f"{model_data['brand']} {model_data['name']}"] = model
        if created:
            print(f"✅ Created model: {model_data['brand']} {model_data['name']}")
    
    # Create Vehicle Features
    features_data = [
        {'name': 'Air Conditioning', 'category': 'Comfort', 'is_premium': False, 'additional_cost': 0},
        {'name': 'GPS Navigation', 'category': 'Technology', 'is_premium': True, 'additional_cost': 10},
        {'name': 'Bluetooth', 'category': 'Technology', 'is_premium': False, 'additional_cost': 0},
        {'name': 'Backup Camera', 'category': 'Safety', 'is_premium': True, 'additional_cost': 5},
        {'name': 'Heated Seats', 'category': 'Comfort', 'is_premium': True, 'additional_cost': 8},
        {'name': 'Sunroof', 'category': 'Comfort', 'is_premium': True, 'additional_cost': 12},
        {'name': 'Leather Seats', 'category': 'Comfort', 'is_premium': True, 'additional_cost': 15},
        {'name': 'WiFi Hotspot', 'category': 'Technology', 'is_premium': True, 'additional_cost': 7},
        {'name': 'Cruise Control', 'category': 'Convenience', 'is_premium': False, 'additional_cost': 0},
        {'name': 'Keyless Entry', 'category': 'Convenience', 'is_premium': False, 'additional_cost': 0},
    ]
    
    features = {}
    for feature_data in features_data:
        feature, created = VehicleFeature.objects.get_or_create(
            name=feature_data['name'],
            defaults=feature_data
        )
        features[feature_data['name']] = feature
        if created:
            print(f"✅ Created feature: {feature_data['name']}")
    
    # Create Sample Vehicles
    vehicles_data = [
        # Economy vehicles
        {
            'model': 'Toyota Corolla', 'year': 2023, 'color': 'White', 
            'license_plate': 'ECO001', 'daily_rate': 45.00, 'seating_capacity': 5,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'Bluetooth', 'Cruise Control', 'Keyless Entry']
        },
        {
            'model': 'Honda Civic', 'year': 2023, 'color': 'Silver', 
            'license_plate': 'ECO002', 'daily_rate': 48.00, 'seating_capacity': 5,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'Bluetooth', 'Backup Camera']
        },
        {
            'model': 'Nissan Sentra', 'year': 2022, 'color': 'Blue', 
            'license_plate': 'ECO003', 'daily_rate': 42.00, 'seating_capacity': 5,
            'fuel_type': 'petrol', 'transmission': 'manual', 'status': 'available',
            'features': ['Air Conditioning', 'Bluetooth']
        },
        
        # Compact vehicles
        {
            'model': 'Toyota Camry', 'year': 2023, 'color': 'Black', 
            'license_plate': 'COM001', 'daily_rate': 65.00, 'seating_capacity': 5,
            'fuel_type': 'hybrid', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'GPS Navigation', 'Bluetooth', 'Backup Camera', 'Heated Seats']
        },
        {
            'model': 'Honda Accord', 'year': 2023, 'color': 'Red', 
            'license_plate': 'COM002', 'daily_rate': 68.00, 'seating_capacity': 5,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'rented',
            'features': ['Air Conditioning', 'Bluetooth', 'Sunroof', 'Cruise Control']
        },
        
        # SUV vehicles
        {
            'model': 'Toyota RAV4', 'year': 2023, 'color': 'Gray', 
            'license_plate': 'SUV001', 'daily_rate': 85.00, 'seating_capacity': 7,
            'fuel_type': 'hybrid', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'GPS Navigation', 'Bluetooth', 'Backup Camera', 'WiFi Hotspot']
        },
        {
            'model': 'Honda CR-V', 'year': 2023, 'color': 'White', 
            'license_plate': 'SUV002', 'daily_rate': 82.00, 'seating_capacity': 7,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'Bluetooth', 'Backup Camera', 'Heated Seats']
        },
        {
            'model': 'Ford Explorer', 'year': 2023, 'color': 'Blue', 
            'license_plate': 'SUV003', 'daily_rate': 95.00, 'seating_capacity': 8,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'maintenance',
            'features': ['Air Conditioning', 'GPS Navigation', 'Bluetooth', 'Leather Seats', 'Sunroof']
        },
        
        # Luxury vehicles
        {
            'model': 'BMW 3 Series', 'year': 2024, 'color': 'Black', 
            'license_plate': 'LUX001', 'daily_rate': 150.00, 'seating_capacity': 5,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'GPS Navigation', 'Bluetooth', 'Leather Seats', 'Heated Seats', 'Sunroof', 'WiFi Hotspot']
        },
        {
            'model': 'Mercedes-Benz C-Class', 'year': 2024, 'color': 'Silver', 
            'license_plate': 'LUX002', 'daily_rate': 165.00, 'seating_capacity': 5,
            'fuel_type': 'petrol', 'transmission': 'automatic', 'status': 'available',
            'features': ['Air Conditioning', 'GPS Navigation', 'Bluetooth', 'Leather Seats', 'Heated Seats', 'Backup Camera']
        },
    ]
    
    created_vehicles = []
    for vehicle_data in vehicles_data:
        model = models[vehicle_data['model']]
        
        # Check if vehicle already exists
        existing_vehicle = Vehicle.objects.filter(license_plate=vehicle_data['license_plate']).first()
        if existing_vehicle:
            print(f"ℹ️  Vehicle {vehicle_data['license_plate']} already exists")
            continue
        
        vehicle = Vehicle.objects.create(
            model=model,
            year=vehicle_data['year'],
            color=vehicle_data['color'],
            license_plate=vehicle_data['license_plate'],
            daily_rate=Decimal(str(vehicle_data['daily_rate'])),
            seating_capacity=vehicle_data['seating_capacity'],
            fuel_type=vehicle_data['fuel_type'],
            transmission=vehicle_data['transmission'],
            status=vehicle_data['status'],
            created_by=admin_user
        )
        
        # Add features to vehicle
        for feature_name in vehicle_data['features']:
            if feature_name in features:
                VehicleFeatureAssignment.objects.create(
                    vehicle=vehicle,
                    feature=features[feature_name]
                )
        
        created_vehicles.append(vehicle)
        print(f"✅ Created vehicle: {vehicle_data['year']} {vehicle_data['model']} ({vehicle_data['license_plate']})")
    
    # Summary
    print(f"\n📊 Sample Data Creation Summary:")
    print(f"   - Categories: {VehicleCategory.objects.count()}")
    print(f"   - Brands: {VehicleBrand.objects.count()}")
    print(f"   - Models: {VehicleModel.objects.count()}")
    print(f"   - Features: {VehicleFeature.objects.count()}")
    print(f"   - Vehicles: {Vehicle.objects.count()}")
    print(f"   - Available Vehicles: {Vehicle.objects.filter(status='available').count()}")
    
    print(f"\n🏁 Sample data creation completed!")
    return True

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
