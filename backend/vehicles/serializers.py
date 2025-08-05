from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .models import (
    Vehicle, VehicleCategory, VehicleBrand, VehicleModel, 
    VehicleFeature, VehicleImage, VehicleMaintenanceRecord,
    VehicleFeatureAssignment, VehicleSafetyEquipment
)
from authentication.serializers import UserProfileSerializer


class VehicleCategorySerializer(serializers.ModelSerializer):
    """Serializer for vehicle categories"""
    
    class Meta:
        model = VehicleCategory
        fields = [
            'id', 'name', 'description', 'icon', 'sort_order', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleBrandSerializer(serializers.ModelSerializer):
    """Serializer for vehicle brands"""
    
    class Meta:
        model = VehicleBrand
        fields = [
            'id', 'name', 'logo', 'country_of_origin', 'website', 
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VehicleModelSerializer(serializers.ModelSerializer):
    """Serializer for vehicle models"""
    brand = VehicleBrandSerializer(read_only=True)
    category = VehicleCategorySerializer(read_only=True)
    brand_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = VehicleModel
        fields = [
            'id', 'brand', 'brand_id', 'name', 'category', 'category_id',
            'year_introduced', 'year_discontinued', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VehicleFeatureSerializer(serializers.ModelSerializer):
    """Serializer for vehicle features"""
    
    class Meta:
        model = VehicleFeature
        fields = [
            'id', 'name', 'description', 'icon', 'category', 'is_premium',
            'additional_cost', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VehicleFeatureAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for vehicle feature assignments"""
    feature = VehicleFeatureSerializer(read_only=True)
    feature_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = VehicleFeatureAssignment
        fields = [
            'id', 'feature', 'feature_id', 'is_working', 'notes', 'assigned_date'
        ]
        read_only_fields = ['id', 'assigned_date']


class VehicleImageSerializer(serializers.ModelSerializer):
    """Serializer for vehicle images"""
    uploaded_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = VehicleImage
        fields = [
            'id', 'image', 'image_type', 'caption', 'is_primary', 
            'sort_order', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class VehicleMaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for vehicle maintenance records"""
    created_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = VehicleMaintenanceRecord
        fields = [
            'id', 'maintenance_type', 'description', 'scheduled_date',
            'completed_date', 'status', 'service_provider', 'technician_name',
            'mileage_at_service', 'estimated_cost', 'actual_cost', 'parts_used',
            'labor_hours', 'invoice_number', 'warranty_expiry', 'notes',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class VehicleSafetyEquipmentSerializer(serializers.ModelSerializer):
    """Serializer for vehicle safety equipment"""
    
    class Meta:
        model = VehicleSafetyEquipment
        fields = [
            'id', 'equipment_type', 'status', 'brand', 'model_number',
            'serial_number', 'purchase_date', 'expiry_date', 'last_inspection_date',
            'next_inspection_due', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VehicleSerializer(serializers.ModelSerializer):
    """Main serializer for vehicles with nested relationships"""
    model = VehicleModelSerializer(read_only=True)
    model_id = serializers.IntegerField(write_only=True)
    images = VehicleImageSerializer(many=True, read_only=True)
    feature_assignments = VehicleFeatureAssignmentSerializer(many=True, read_only=True)
    safety_equipment = VehicleSafetyEquipmentSerializer(many=True, read_only=True)
    created_by = UserProfileSerializer(read_only=True)
    
    # Computed fields
    display_name = serializers.CharField(read_only=True)
    is_available_for_booking = serializers.BooleanField(read_only=True)
    weekly_rate = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    monthly_rate = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'model', 'model_id', 'year', 'color', 'license_plate', 'vin_number',
            'engine_size', 'fuel_type', 'transmission', 'seating_capacity', 'doors',
            'fuel_tank_capacity', 'status', 'condition', 'current_mileage',
            'last_service_mileage', 'next_service_due', 'daily_rate', 'weekly_rate',
            'monthly_rate', 'security_deposit', 'current_location', 'gps_enabled',
            'last_gps_update', 'latitude', 'longitude', 'purchase_date', 'purchase_price',
            'registration_date', 'registration_expiry', 'insurance_company',
            'insurance_policy_number', 'insurance_expiry', 'insurance_value',
            'notes', 'is_featured', 'is_active', 'created_at', 'updated_at',
            'created_by', 'images', 'feature_assignments', 'safety_equipment',
            'display_name', 'is_available_for_booking'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'display_name',
            'is_available_for_booking', 'weekly_rate', 'monthly_rate'
        ]
    
    def validate_daily_rate(self, value):
        """Validate daily rate is positive"""
        if value <= 0:
            raise serializers.ValidationError("Daily rate must be greater than zero.")
        return value
    
    def validate_year(self, value):
        """Validate year is reasonable"""
        if value < 1900 or value > 2030:
            raise serializers.ValidationError("Year must be between 1900 and 2030.")
        return value
    
    def validate_seating_capacity(self, value):
        """Validate seating capacity"""
        if value < 1 or value > 20:
            raise serializers.ValidationError("Seating capacity must be between 1 and 20.")
        return value
    
    def validate_license_plate(self, value):
        """Validate license plate format"""
        if len(value) < 3 or len(value) > 20:
            raise serializers.ValidationError("License plate must be between 3 and 20 characters.")
        return value.upper()
    
    def to_representation(self, instance):
        """Add computed fields to representation"""
        data = super().to_representation(instance)
        data['display_name'] = instance.get_display_name()
        data['is_available_for_booking'] = instance.is_available_for_booking()
        data['weekly_rate'] = instance.calculate_weekly_rate()
        data['monthly_rate'] = instance.calculate_monthly_rate()
        return data


class VehicleSearchSerializer(serializers.Serializer):
    """Serializer for vehicle search criteria"""
    brand = serializers.CharField(required=False, max_length=100)
    model = serializers.CharField(required=False, max_length=100)
    category = serializers.CharField(required=False, max_length=100)
    fuel_type = serializers.ChoiceField(choices=Vehicle.FUEL_TYPES, required=False)
    transmission = serializers.ChoiceField(choices=Vehicle.TRANSMISSION_TYPES, required=False)
    min_seats = serializers.IntegerField(required=False, min_value=1, max_value=20)
    max_seats = serializers.IntegerField(required=False, min_value=1, max_value=20)
    min_price = serializers.DecimalField(required=False, max_digits=8, decimal_places=2, min_value=0)
    max_price = serializers.DecimalField(required=False, max_digits=8, decimal_places=2, min_value=0)
    available_only = serializers.BooleanField(required=False, default=False)
    features = serializers.ListField(child=serializers.CharField(), required=False)
    order_by = serializers.CharField(required=False, default='-created_at')
    
    def validate(self, data):
        """Validate search criteria"""
        if 'min_seats' in data and 'max_seats' in data:
            if data['min_seats'] > data['max_seats']:
                raise serializers.ValidationError("min_seats cannot be greater than max_seats.")
        
        if 'min_price' in data and 'max_price' in data:
            if data['min_price'] > data['max_price']:
                raise serializers.ValidationError("min_price cannot be greater than max_price.")
        
        return data


class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vehicles with validation"""
    model_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'model_id', 'year', 'color', 'license_plate', 'vin_number',
            'engine_size', 'fuel_type', 'transmission', 'seating_capacity',
            'doors', 'fuel_tank_capacity', 'status', 'condition',
            'current_mileage', 'daily_rate', 'security_deposit',
            'current_location', 'notes', 'is_featured'
        ]
    
    def validate_license_plate(self, value):
        """Ensure license plate is unique"""
        if Vehicle.objects.filter(license_plate=value.upper()).exists():
            raise serializers.ValidationError("A vehicle with this license plate already exists.")
        return value.upper()
    
    def validate_vin_number(self, value):
        """Ensure VIN number is unique if provided"""
        if value and Vehicle.objects.filter(vin_number=value).exists():
            raise serializers.ValidationError("A vehicle with this VIN number already exists.")
        return value


class VehicleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating vehicles"""
    
    class Meta:
        model = Vehicle
        fields = [
            'color', 'status', 'condition', 'current_mileage',
            'daily_rate', 'security_deposit', 'current_location',
            'notes', 'is_featured', 'is_active'
        ]
    
    def validate_current_mileage(self, value):
        """Ensure mileage doesn't decrease"""
        instance = self.instance
        if instance and value < instance.current_mileage:
            raise serializers.ValidationError("Current mileage cannot be less than previous mileage.")
        return value 