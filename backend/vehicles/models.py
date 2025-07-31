from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from authentication.models import CustomUser
import uuid


class VehicleCategory(models.Model):
    """Vehicle categories (Economy, Compact, SUV, Luxury, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)  # FontAwesome icon class
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicle_categories'
        verbose_name = 'Vehicle Category'
        verbose_name_plural = 'Vehicle Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class VehicleBrand(models.Model):
    """Vehicle brands (Toyota, BMW, Mercedes, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True)
    country_of_origin = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicle_brands'
        verbose_name = 'Vehicle Brand'
        verbose_name_plural = 'Vehicle Brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    """Vehicle models (Corolla, X5, C-Class, etc.)"""
    brand = models.ForeignKey(VehicleBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    category = models.ForeignKey(VehicleCategory, on_delete=models.SET_NULL, null=True, blank=True)
    year_introduced = models.PositiveIntegerField(null=True, blank=True)
    year_discontinued = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicle_models'
        verbose_name = 'Vehicle Model'
        verbose_name_plural = 'Vehicle Models'
        unique_together = ['brand', 'name']
        ordering = ['brand__name', 'name']
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Vehicle(models.Model):
    """Individual vehicles in the fleet"""
    
    FUEL_TYPES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
        ('lpg', 'LPG'),
    ]
    
    TRANSMISSION_TYPES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Under Repair'),
        ('retired', 'Retired'),
        ('sold', 'Sold'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name='vehicles')
    year = models.PositiveIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2030)])
    color = models.CharField(max_length=50, null=True, blank=True)
    license_plate = models.CharField(max_length=20, unique=True)
    vin_number = models.CharField(max_length=17, unique=True, null=True, blank=True)
    
    # Technical Specifications
    engine_size = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # in liters
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, default='petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_TYPES, default='manual')
    seating_capacity = models.PositiveIntegerField(default=5)
    doors = models.PositiveIntegerField(default=4)
    fuel_tank_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in liters
    
    # Status and Condition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    # Mileage and Usage
    current_mileage = models.PositiveIntegerField(default=0)  # in kilometers
    last_service_mileage = models.PositiveIntegerField(null=True, blank=True)
    next_service_due = models.PositiveIntegerField(null=True, blank=True)
    
    # Pricing
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    weekly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Location and Tracking
    current_location = models.CharField(max_length=200, null=True, blank=True)
    gps_enabled = models.BooleanField(default=False)
    last_gps_update = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Purchase and Registration
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)
    
    # Insurance
    insurance_company = models.CharField(max_length=100, null=True, blank=True)
    insurance_policy_number = models.CharField(max_length=50, null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    insurance_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles_created')
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['model', 'year']),
            models.Index(fields=['daily_rate']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.model} ({self.year}) - {self.license_plate}"
    
    def get_display_name(self):
        return f"{self.model.brand.name} {self.model.name} {self.year}"
    
    def is_available_for_booking(self):
        return self.status == 'available' and self.is_active
    
    def calculate_weekly_rate(self):
        if self.weekly_rate:
            return self.weekly_rate
        return self.daily_rate * Decimal('6.5')  # 10% discount for weekly
    
    def calculate_monthly_rate(self):
        if self.monthly_rate:
            return self.monthly_rate
        return self.daily_rate * Decimal('25')  # 20% discount for monthly


class VehicleFeature(models.Model):
    """Features available for vehicles (GPS, Bluetooth, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)  # Safety, Comfort, Technology
    is_premium = models.BooleanField(default=False)
    additional_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicle_features'
        verbose_name = 'Vehicle Feature'
        verbose_name_plural = 'Vehicle Features'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class VehicleFeatureAssignment(models.Model):
    """Many-to-many relationship between vehicles and features"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='feature_assignments')
    feature = models.ForeignKey(VehicleFeature, on_delete=models.CASCADE, related_name='vehicle_assignments')
    is_working = models.BooleanField(default=True)
    notes = models.TextField(null=True, blank=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicle_feature_assignments'
        verbose_name = 'Vehicle Feature Assignment'
        verbose_name_plural = 'Vehicle Feature Assignments'
        unique_together = ['vehicle', 'feature']
    
    def __str__(self):
        return f"{self.vehicle} - {self.feature}"


class VehicleImage(models.Model):
    """Images for vehicles"""
    
    IMAGE_TYPES = [
        ('exterior', 'Exterior'),
        ('interior', 'Interior'),
        ('engine', 'Engine'),
        ('trunk', 'Trunk'),
        ('damage', 'Damage'),
        ('other', 'Other'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicle_images/')
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default='exterior')
    caption = models.CharField(max_length=200, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vehicle_images'
        verbose_name = 'Vehicle Image'
        verbose_name_plural = 'Vehicle Images'
        ordering = ['vehicle', 'sort_order']
    
    def __str__(self):
        return f"{self.vehicle} - {self.get_image_type_display()}"


class VehicleMaintenanceRecord(models.Model):
    """Maintenance and service records for vehicles"""
    
    MAINTENANCE_TYPES = [
        ('routine', 'Routine Service'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('cleaning', 'Cleaning'),
        ('tire_change', 'Tire Change'),
        ('oil_change', 'Oil Change'),
        ('brake_service', 'Brake Service'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Service Details
    service_provider = models.CharField(max_length=200, null=True, blank=True)
    technician_name = models.CharField(max_length=100, null=True, blank=True)
    mileage_at_service = models.PositiveIntegerField(null=True, blank=True)
    
    # Cost Information
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Parts and Labor
    parts_used = models.JSONField(default=list, null=True, blank=True)  # List of parts
    labor_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Documentation
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    # Tracking
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicle_maintenance_records'
        verbose_name = 'Vehicle Maintenance Record'
        verbose_name_plural = 'Vehicle Maintenance Records'
        indexes = [
            models.Index(fields=['vehicle', 'status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['maintenance_type']),
        ]
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.vehicle} - {self.get_maintenance_type_display()} ({self.scheduled_date.date()})"


class VehicleSafetyEquipment(models.Model):
    """Safety equipment tracking for vehicles"""
    
    EQUIPMENT_TYPES = [
        ('fire_extinguisher', 'Fire Extinguisher'),
        ('first_aid_kit', 'First Aid Kit'),
        ('warning_triangle', 'Warning Triangle'),
        ('spare_tire', 'Spare Tire'),
        ('jack', 'Jack'),
        ('jumper_cables', 'Jumper Cables'),
        ('emergency_kit', 'Emergency Kit'),
        ('reflective_vest', 'Reflective Vest'),
    ]
    
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('missing', 'Missing'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='safety_equipment')
    equipment_type = models.CharField(max_length=30, choices=EQUIPMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    brand = models.CharField(max_length=50, null=True, blank=True)
    model_number = models.CharField(max_length=50, null=True, blank=True)
    serial_number = models.CharField(max_length=50, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_due = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicle_safety_equipment'
        verbose_name = 'Vehicle Safety Equipment'
        verbose_name_plural = 'Vehicle Safety Equipment'
        unique_together = ['vehicle', 'equipment_type']
        indexes = [
            models.Index(fields=['vehicle', 'status']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['next_inspection_due']),
        ]
    
    def __str__(self):
        return f"{self.vehicle} - {self.get_equipment_type_display()}"
