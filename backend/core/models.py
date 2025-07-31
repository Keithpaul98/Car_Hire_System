from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from authentication.models import CustomUser
from vehicles.models import Vehicle
from bookings.models import Booking
import uuid


class Review(models.Model):
    """Customer reviews and ratings"""
    
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews')
    
    # Review Content
    overall_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    vehicle_condition_rating = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    service_rating = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    value_for_money_rating = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    title = models.CharField(max_length=200, null=True, blank=True)
    comment = models.TextField()
    pros = models.TextField(null=True, blank=True)
    cons = models.TextField(null=True, blank=True)
    
    # Verification and Moderation
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    moderation_notes = models.TextField(null=True, blank=True)
    moderated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reviews')
    
    # Engagement
    helpful_votes = models.PositiveIntegerField(default=0)
    total_votes = models.PositiveIntegerField(default=0)
    
    # Response from Company
    company_response = models.TextField(null=True, blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_responses')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        indexes = [
            models.Index(fields=['vehicle', 'is_approved']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['overall_rating', 'is_approved']),
            models.Index(fields=['is_featured', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.username} - {self.vehicle} ({self.overall_rating} stars)"


class LoyaltyProgram(models.Model):
    """Loyalty program configuration"""
    
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    min_points_required = models.PositiveIntegerField()
    points_per_dollar = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    benefits = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loyalty_programs'
        verbose_name = 'Loyalty Program'
        verbose_name_plural = 'Loyalty Programs'
        ordering = ['min_points_required']
    
    def __str__(self):
        return f"{self.get_tier_display()} ({self.min_points_required} points)"


class Promotion(models.Model):
    """Promotional campaigns and discount codes"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
        ('free_days', 'Free Days'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    
    # Discount Configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Validity and Usage
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    per_customer_limit = models.PositiveIntegerField(default=1)
    
    # Conditions
    min_booking_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    min_rental_days = models.PositiveIntegerField(null=True, blank=True)
    applicable_vehicle_categories = models.JSONField(default=list, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'promotions'
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active', 'is_public']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class IssueReport(models.Model):
    """Customer issue reports and complaints"""
    
    ISSUE_TYPES = [
        ('vehicle_problem', 'Vehicle Problem'),
        ('service_complaint', 'Service Complaint'),
        ('billing_issue', 'Billing Issue'),
        ('booking_problem', 'Booking Problem'),
        ('accident_report', 'Accident Report'),
        ('breakdown', 'Vehicle Breakdown'),
        ('other', 'Other'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='issue_reports')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='issue_reports')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='issue_reports')
    
    # Issue Details
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, null=True, blank=True)
    
    # Verification and Response
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_issues')
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(null=True, blank=True)
    
    # Assignment and Resolution
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    resolution = models.TextField(null=True, blank=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_issues')
    
    # Customer Satisfaction
    customer_satisfaction = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        null=True, blank=True
    )
    customer_feedback = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'issue_reports'
        verbose_name = 'Issue Report'
        verbose_name_plural = 'Issue Reports'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"


class Penalty(models.Model):
    """Penalties and additional charges"""
    
    PENALTY_TYPES = [
        ('late_return', 'Late Return'),
        ('fuel_shortage', 'Fuel Shortage'),
        ('damage', 'Vehicle Damage'),
        ('cleaning_fee', 'Cleaning Fee'),
        ('smoking_fee', 'Smoking Fee'),
        ('mileage_overage', 'Mileage Overage'),
        ('traffic_violation', 'Traffic Violation'),
        ('lost_key', 'Lost Key'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('disputed', 'Disputed'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='penalties')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='penalties')
    
    # Penalty Details
    penalty_type = models.CharField(max_length=30, choices=PENALTY_TYPES)
    description = models.TextField()
    amount = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Evidence and Documentation
    evidence_photos = models.JSONField(default=list, null=True, blank=True)
    supporting_documents = models.JSONField(default=list, null=True, blank=True)
    
    # Dispute Information
    is_disputed = models.BooleanField(default=False)
    dispute_reason = models.TextField(null=True, blank=True)
    dispute_date = models.DateTimeField(null=True, blank=True)
    dispute_resolution = models.TextField(null=True, blank=True)
    
    # Processing
    assessed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessed_penalties')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_penalties')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'penalties'
        verbose_name = 'Penalty'
        verbose_name_plural = 'Penalties'
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['penalty_type', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_penalty_type_display()} - {self.amount} ({self.booking.booking_reference})"
