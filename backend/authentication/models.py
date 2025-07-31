from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image
import os


class CustomUser(AbstractUser):
    """Extended User model with comprehensive profile information"""
    
    USER_TYPES = [
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    # Basic Information
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Profile Information
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state_province = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True, default='Malawi')
    
    # Driver's License Information
    drivers_license_number = models.CharField(max_length=50, null=True, blank=True, unique=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    license_class = models.CharField(max_length=10, null=True, blank=True)  # e.g., 'B', 'C1', etc.
    license_country = models.CharField(max_length=100, null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, null=True, blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en', null=True, blank=True)
    notification_preferences = models.JSONField(default=dict, null=True, blank=True)  # Email, SMS, Push notifications
    marketing_consent = models.BooleanField(default=False)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(null=True, blank=True)
    
    # Loyalty Program
    loyalty_points = models.PositiveIntegerField(default=0)
    loyalty_tier = models.CharField(max_length=20, default='Bronze', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Business Information (for corporate customers)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    company_registration = models.CharField(max_length=50, null=True, blank=True)
    tax_number = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'auth_user_extended'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['user_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['loyalty_tier']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [self.address_line_1, self.address_line_2, self.city, 
                        self.state_province, self.postal_code, self.country]
        return ', '.join([part for part in address_parts if part])
    
    def save(self, *args, **kwargs):
        # Resize profile picture if too large
        super().save(*args, **kwargs)
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)


class UserSession(models.Model):
    """Track user sessions for security and analytics"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)  # City, Country
    device_type = models.CharField(max_length=50, null=True, blank=True)  # Mobile, Desktop, Tablet
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.created_at})"


class UserPreference(models.Model):
    """Store user preferences and settings"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    
    # Communication Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Booking Preferences
    preferred_pickup_time = models.TimeField(null=True, blank=True)
    preferred_return_time = models.TimeField(null=True, blank=True)
    auto_insurance = models.BooleanField(default=True)
    preferred_fuel_policy = models.CharField(max_length=20, default='full_to_full', null=True, blank=True)
    
    # Display Preferences
    currency = models.CharField(max_length=3, default='ZAR')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')
    time_format = models.CharField(max_length=10, default='24h')
    
    # Privacy Settings
    profile_visibility = models.CharField(max_length=20, default='private')
    share_booking_history = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.username} Preferences"
