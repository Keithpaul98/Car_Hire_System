from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from authentication.models import CustomUser
from vehicles.models import Vehicle
import uuid
from datetime import datetime, timedelta


class Booking(models.Model):
    """Main booking model for vehicle rentals"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active Rental'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Payment Failed'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_reference = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking Dates and Times
    pickup_date = models.DateTimeField()
    return_date = models.DateTimeField()
    actual_pickup_date = models.DateTimeField(null=True, blank=True)
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    # Location Information
    pickup_location = models.CharField(max_length=200)
    return_location = models.CharField(max_length=200)
    pickup_address = models.TextField(null=True, blank=True)
    return_address = models.TextField(null=True, blank=True)
    
    # Status and Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing Information
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    total_days = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    additional_fees = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Driver Information
    primary_driver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_driver_bookings')
    additional_drivers = models.ManyToManyField(CustomUser, through='BookingAdditionalDriver', blank=True)
    
    # Vehicle Condition
    pickup_mileage = models.PositiveIntegerField(null=True, blank=True)
    return_mileage = models.PositiveIntegerField(null=True, blank=True)
    pickup_fuel_level = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # 0.0 to 1.0
    return_fuel_level = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    # Special Requests and Notes
    special_requests = models.TextField(null=True, blank=True)
    customer_notes = models.TextField(null=True, blank=True)
    staff_notes = models.TextField(null=True, blank=True)
    
    # Insurance and Add-ons
    insurance_selected = models.BooleanField(default=False)
    insurance_type = models.CharField(max_length=50, null=True, blank=True)
    insurance_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Loyalty and Promotions
    loyalty_points_used = models.PositiveIntegerField(default=0)
    loyalty_points_earned = models.PositiveIntegerField(default=0)
    promotion_code = models.CharField(max_length=50, null=True, blank=True)
    
    # Communication
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    pickup_notification_sent = models.BooleanField(default=False)
    return_notification_sent = models.BooleanField(default=False)
    
    # Staff Assignment
    assigned_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    pickup_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='pickup_bookings')
    return_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_bookings')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['vehicle', 'pickup_date']),
            models.Index(fields=['status', 'pickup_date']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_reference} - {self.customer.username} ({self.vehicle})"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate unique booking reference"""
        import random
        import string
        prefix = 'BK'
        timestamp = datetime.now().strftime('%y%m%d')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"
    
    def calculate_total_days(self):
        """Calculate total rental days"""
        delta = self.return_date - self.pickup_date
        return max(1, delta.days)
    
    def is_overdue(self):
        """Check if booking is overdue"""
        if self.status == 'active' and self.return_date < datetime.now():
            return True
        return False
    
    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.status in ['pending', 'confirmed'] and self.pickup_date > datetime.now()


class BookingAdditionalDriver(models.Model):
    """Additional drivers for a booking"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='additional_driver_assignments')
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    additional_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_approved = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_additional_drivers'
        verbose_name = 'Booking Additional Driver'
        verbose_name_plural = 'Booking Additional Drivers'
        unique_together = ['booking', 'driver']
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.driver.username}"


class BookingAddOn(models.Model):
    """Add-on services for bookings"""
    
    ADDON_TYPES = [
        ('gps', 'GPS Navigation'),
        ('child_seat', 'Child Seat'),
        ('additional_driver', 'Additional Driver'),
        ('wifi', 'WiFi Hotspot'),
        ('ski_rack', 'Ski Rack'),
        ('bike_rack', 'Bike Rack'),
        ('roadside_assistance', 'Roadside Assistance'),
        ('fuel_service', 'Fuel Service'),
        ('cleaning', 'Vehicle Cleaning'),
        ('delivery', 'Vehicle Delivery'),
        ('other', 'Other'),
    ]
    
    PRICING_TYPES = [
        ('per_day', 'Per Day'),
        ('per_booking', 'Per Booking'),
        ('percentage', 'Percentage of Rental'),
    ]
    
    name = models.CharField(max_length=100)
    addon_type = models.CharField(max_length=30, choices=ADDON_TYPES)
    description = models.TextField(null=True, blank=True)
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='per_day')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_addons'
        verbose_name = 'Booking Add-on'
        verbose_name_plural = 'Booking Add-ons'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BookingAddOnAssignment(models.Model):
    """Assignment of add-ons to bookings"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='addon_assignments')
    addon = models.ForeignKey(BookingAddOn, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_addon_assignments'
        verbose_name = 'Booking Add-on Assignment'
        verbose_name_plural = 'Booking Add-on Assignments'
        unique_together = ['booking', 'addon']
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.addon.name}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
