from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserSession, UserPreference


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Enhanced admin interface for CustomUser"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'user_type', 'is_verified', 'loyalty_tier', 
        'loyalty_points', 'is_active', 'date_joined'
    ]
    
    list_filter = [
        'user_type', 'is_verified', 'loyalty_tier', 
        'is_active', 'is_staff', 'is_superuser',
        'marketing_consent', 'date_joined'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name',
        'phone_number', 'company_name', 'drivers_license_number'
    ]
    
    readonly_fields = [
        'date_joined', 'last_login', 'created_at', 'updated_at',
        'verification_date', 'loyalty_points_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name')
        }),
        ('User Type & Status', {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 
                      'is_verified', 'verification_date', 'is_suspended', 'suspension_reason')
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'gender', 'bio'),
            'classes': ('collapse',)
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 
                      'state_province', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Driver Information', {
            'fields': ('drivers_license_number', 'license_expiry_date', 
                      'license_class', 'license_country'),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 
                      'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': ('company_name', 'company_registration', 'tax_number'),
            'classes': ('collapse',)
        }),
        ('Loyalty Program', {
            'fields': ('loyalty_tier', 'loyalty_points_display', 'marketing_consent')
        }),
        ('Preferences', {
            'fields': ('preferred_language',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number'),
        }),
    )
    
    def loyalty_points_display(self, obj):
        """Display loyalty points with tier information"""
        if obj.loyalty_points > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} points ({})</span>',
                obj.loyalty_points, obj.loyalty_tier
            )
        return format_html('<span style="color: #6c757d;">0 points</span>')
    loyalty_points_display.short_description = 'Loyalty Status'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related()
    
    actions = ['verify_users', 'suspend_users', 'activate_users']
    
    def verify_users(self, request, queryset):
        """Bulk verify users"""
        from django.utils import timezone
        updated = queryset.update(is_verified=True, verification_date=timezone.now())
        self.message_user(request, f'{updated} users were verified.')
    verify_users.short_description = "Verify selected users"
    
    def suspend_users(self, request, queryset):
        """Bulk suspend users"""
        updated = queryset.update(is_suspended=True, is_active=False)
        self.message_user(request, f'{updated} users were suspended.')
    suspend_users.short_description = "Suspend selected users"
    
    def activate_users(self, request, queryset):
        """Bulk activate users"""
        updated = queryset.update(is_suspended=False, is_active=True)
        self.message_user(request, f'{updated} users were activated.')
    activate_users.short_description = "Activate selected users"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for user sessions"""
    
    list_display = [
        'user', 'ip_address', 'device_type', 'location', 
        'is_active', 'created_at', 'last_activity'
    ]
    
    list_filter = [
        'is_active', 'device_type', 'created_at', 'last_activity'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'ip_address', 'location'
    ]
    
    readonly_fields = [
        'session_key', 'created_at', 'last_activity'
    ]
    
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for user preferences"""
    
    list_display = [
        'user', 'email_notifications', 'sms_notifications', 
        'marketing_emails', 'currency', 'created_at'
    ]
    
    list_filter = [
        'email_notifications', 'sms_notifications', 'push_notifications',
        'marketing_emails', 'currency', 'auto_insurance'
    ]
    
    search_fields = ['user__username', 'user__email']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Communication Preferences', {
            'fields': ('email_notifications', 'sms_notifications', 
                      'push_notifications', 'marketing_emails')
        }),
        ('Booking Preferences', {
            'fields': ('preferred_pickup_time', 'preferred_return_time',
                      'auto_insurance', 'preferred_fuel_policy')
        }),
        ('Display Preferences', {
            'fields': ('currency', 'date_format', 'time_format')
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'share_booking_history')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
