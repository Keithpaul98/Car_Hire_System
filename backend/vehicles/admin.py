from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import (
    VehicleCategory, VehicleBrand, VehicleModel, Vehicle,
    VehicleFeature, VehicleFeatureAssignment, VehicleImage,
    VehicleMaintenanceRecord, VehicleSafetyEquipment
)


class VehicleImageInline(admin.TabularInline):
    """Inline for vehicle images"""
    model = VehicleImage
    extra = 1
    fields = ['image', 'image_type', 'caption', 'is_primary', 'sort_order']
    readonly_fields = ['uploaded_by']


class VehicleFeatureAssignmentInline(admin.TabularInline):
    """Inline for vehicle features"""
    model = VehicleFeatureAssignment
    extra = 1
    fields = ['feature', 'is_working', 'notes']
    readonly_fields = ['assigned_date']


class VehicleSafetyEquipmentInline(admin.TabularInline):
    """Inline for safety equipment"""
    model = VehicleSafetyEquipment
    extra = 1
    fields = ['equipment_type', 'status', 'expiry_date', 'next_inspection_due']
    readonly_fields = ['created_at']


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    """Admin for vehicle categories"""
    
    list_display = ['name', 'description', 'sort_order', 'is_active', 'vehicle_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']
    
    def vehicle_count(self, obj):
        """Count vehicles in this category"""
        count = obj.vehiclemodel_set.aggregate(
            total=Count('vehicles')
        )['total'] or 0
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    vehicle_count.short_description = 'Vehicles'


@admin.register(VehicleBrand)
class VehicleBrandAdmin(admin.ModelAdmin):
    """Admin for vehicle brands"""
    
    list_display = ['name', 'country_of_origin', 'is_active', 'model_count', 'created_at']
    list_filter = ['is_active', 'country_of_origin', 'created_at']
    search_fields = ['name', 'country_of_origin']
    readonly_fields = ['created_at']
    
    def model_count(self, obj):
        """Count models for this brand"""
        return obj.models.count()
    model_count.short_description = 'Models'


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    """Admin for vehicle models"""
    
    list_display = ['name', 'brand', 'category', 'year_introduced', 'is_active', 'vehicle_count']
    list_filter = ['brand', 'category', 'is_active', 'year_introduced']
    search_fields = ['name', 'brand__name']
    ordering = ['brand__name', 'name']
    
    def vehicle_count(self, obj):
        """Count vehicles of this model"""
        return obj.vehicles.count()
    vehicle_count.short_description = 'Vehicles'


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Comprehensive admin for vehicles"""
    
    list_display = [
        'license_plate', 'get_display_name', 'year', 'color',
        'status', 'condition', 'daily_rate', 'current_mileage',
        'is_featured', 'is_active'
    ]
    
    list_filter = [
        'status', 'condition', 'fuel_type', 'transmission',
        'model__brand', 'model__category', 'is_featured', 'is_active',
        'gps_enabled', 'year'
    ]
    
    search_fields = [
        'license_plate', 'vin_number', 'model__name', 
        'model__brand__name', 'color'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'created_by'
    ]
    
    inlines = [VehicleImageInline, VehicleFeatureAssignmentInline, VehicleSafetyEquipmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('model', 'year', 'color', 'license_plate', 'vin_number')
        }),
        ('Technical Specifications', {
            'fields': ('engine_size', 'fuel_type', 'transmission', 
                      'seating_capacity', 'doors', 'fuel_tank_capacity')
        }),
        ('Status & Condition', {
            'fields': ('status', 'condition', 'is_featured', 'is_active')
        }),
        ('Mileage & Usage', {
            'fields': ('current_mileage', 'last_service_mileage', 'next_service_due')
        }),
        ('Pricing', {
            'fields': ('daily_rate', 'weekly_rate', 'monthly_rate', 'security_deposit')
        }),
        ('Location & Tracking', {
            'fields': ('current_location', 'gps_enabled', 'last_gps_update', 
                      'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Purchase & Registration', {
            'fields': ('purchase_date', 'purchase_price', 'registration_date', 
                      'registration_expiry'),
            'classes': ('collapse',)
        }),
        ('Insurance', {
            'fields': ('insurance_company', 'insurance_policy_number', 
                      'insurance_expiry', 'insurance_value'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_available', 'mark_maintenance', 'feature_vehicles', 'unfeature_vehicles']
    
    def mark_available(self, request, queryset):
        """Mark vehicles as available"""
        updated = queryset.update(status='available')
        self.message_user(request, f'{updated} vehicles marked as available.')
    mark_available.short_description = "Mark as available"
    
    def mark_maintenance(self, request, queryset):
        """Mark vehicles for maintenance"""
        updated = queryset.update(status='maintenance')
        self.message_user(request, f'{updated} vehicles marked for maintenance.')
    mark_maintenance.short_description = "Mark for maintenance"
    
    def feature_vehicles(self, request, queryset):
        """Feature selected vehicles"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} vehicles featured.')
    feature_vehicles.short_description = "Feature vehicles"
    
    def unfeature_vehicles(self, request, queryset):
        """Unfeature selected vehicles"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} vehicles unfeatured.')
    unfeature_vehicles.short_description = "Unfeature vehicles"
    
    def save_model(self, request, obj, form, change):
        """Set created_by when saving"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(VehicleFeature)
class VehicleFeatureAdmin(admin.ModelAdmin):
    """Admin for vehicle features"""
    
    list_display = [
        'name', 'category', 'is_premium', 'additional_cost', 
        'is_active', 'vehicle_count'
    ]
    
    list_filter = ['category', 'is_premium', 'is_active']
    search_fields = ['name', 'description', 'category']
    ordering = ['category', 'name']
    
    def vehicle_count(self, obj):
        """Count vehicles with this feature"""
        return obj.vehicle_assignments.count()
    vehicle_count.short_description = 'Vehicles'


@admin.register(VehicleMaintenanceRecord)
class VehicleMaintenanceRecordAdmin(admin.ModelAdmin):
    """Admin for maintenance records"""
    
    list_display = [
        'vehicle', 'maintenance_type', 'scheduled_date', 
        'status', 'actual_cost', 'service_provider'
    ]
    
    list_filter = [
        'maintenance_type', 'status', 'scheduled_date', 
        'service_provider'
    ]
    
    search_fields = [
        'vehicle__license_plate', 'description', 
        'service_provider', 'technician_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vehicle', 'maintenance_type', 'description', 'status')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'completed_date')
        }),
        ('Service Details', {
            'fields': ('service_provider', 'technician_name', 'mileage_at_service')
        }),
        ('Cost Information', {
            'fields': ('estimated_cost', 'actual_cost', 'labor_hours')
        }),
        ('Parts and Documentation', {
            'fields': ('parts_used', 'invoice_number', 'warranty_expiry'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by when saving"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(VehicleSafetyEquipment)
class VehicleSafetyEquipmentAdmin(admin.ModelAdmin):
    """Admin for safety equipment"""
    
    list_display = [
        'vehicle', 'equipment_type', 'status', 'expiry_date', 
        'next_inspection_due', 'needs_attention'
    ]
    
    list_filter = [
        'equipment_type', 'status', 'expiry_date', 
        'next_inspection_due'
    ]
    
    search_fields = [
        'vehicle__license_plate', 'brand', 'model_number', 'serial_number'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    def needs_attention(self, obj):
        """Check if equipment needs attention"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if obj.status in ['missing', 'damaged', 'expired']:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Yes</span>')
        elif obj.expiry_date and obj.expiry_date <= today:
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ Expired</span>')
        elif obj.next_inspection_due and obj.next_inspection_due <= today:
            return format_html('<span style="color: orange;">📅 Inspection Due</span>')
        return format_html('<span style="color: green;">✅ OK</span>')
    needs_attention.short_description = 'Status'
    
    actions = ['mark_inspected', 'mark_missing', 'mark_present']
    
    def mark_inspected(self, request, queryset):
        """Mark equipment as inspected"""
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        next_inspection = today + timedelta(days=90)  # 3 months
        
        updated = queryset.update(
            last_inspection_date=today,
            next_inspection_due=next_inspection,
            status='present'
        )
        self.message_user(request, f'{updated} equipment marked as inspected.')
    mark_inspected.short_description = "Mark as inspected"
    
    def mark_missing(self, request, queryset):
        """Mark equipment as missing"""
        updated = queryset.update(status='missing')
        self.message_user(request, f'{updated} equipment marked as missing.')
    mark_missing.short_description = "Mark as missing"
    
    def mark_present(self, request, queryset):
        """Mark equipment as present"""
        updated = queryset.update(status='present')
        self.message_user(request, f'{updated} equipment marked as present.')
    mark_present.short_description = "Mark as present"
