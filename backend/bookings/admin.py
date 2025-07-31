from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.utils import timezone
from .models import (
    Booking, BookingAdditionalDriver, BookingAddOn, BookingAddOnAssignment
)


class BookingAdditionalDriverInline(admin.TabularInline):
    """Inline for additional drivers"""
    model = BookingAdditionalDriver
    extra = 0
    fields = [
        'driver', 'additional_fee', 'is_approved', 'added_at'
    ]
    readonly_fields = ['added_at']


class BookingAddOnAssignmentInline(admin.TabularInline):
    """Inline for booking add-ons"""
    model = BookingAddOnAssignment
    extra = 0
    fields = ['addon', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price', 'added_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Comprehensive admin for bookings"""
    
    list_display = [
        'booking_reference', 'customer', 'vehicle', 'pickup_date',
        'return_date', 'status', 'total_amount', 'payment_status',
        'days_count', 'created_at'
    ]
    
    list_filter = [
        'status', 'pickup_date', 'return_date', 'payment_status',
        'vehicle__model__brand', 'vehicle__model__category',
        'insurance_type', 'created_at'
    ]
    
    search_fields = [
        'booking_reference', 'customer__username', 'customer__email',
        'customer__first_name', 'customer__last_name',
        'vehicle__license_plate', 'vehicle__model__name'
    ]
    
    readonly_fields = [
        'id', 'booking_reference', 'created_at', 'updated_at',
        'days_count', 'total_amount_display', 'profit_margin'
    ]
    
    date_hierarchy = 'pickup_date'
    
    inlines = [BookingAdditionalDriverInline, BookingAddOnAssignmentInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'customer', 'vehicle', 'status')
        }),
        ('Dates & Times', {
            'fields': ('pickup_date', 'pickup_time', 'return_date', 'return_time',
                      'days_count')
        }),
        ('Location', {
            'fields': ('pickup_location', 'return_location', 'pickup_address',
                      'return_address')
        }),
        ('Pricing', {
            'fields': ('base_rate', 'total_amount_display', 'security_deposit',
                      'discount_amount', 'tax_amount', 'profit_margin')
        }),
        ('Payment & Insurance', {
            'fields': ('payment_status', 'payment_method', 'insurance_selected',
                      'insurance_type', 'insurance_cost')
        }),
        ('Vehicle Condition', {
            'fields': ('pickup_mileage', 'return_mileage', 'pickup_fuel_level',
                      'return_fuel_level', 'pickup_condition_notes',
                      'return_condition_notes'),
            'classes': ('collapse',)
        }),
        ('Communication', {
            'fields': ('special_requests', 'pickup_instructions',
                      'return_instructions', 'sms_notifications_sent',
                      'email_notifications_sent'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason', 'cancellation_fee',
                      'refund_amount', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'confirm_bookings', 'start_rentals', 'complete_rentals',
        'cancel_bookings', 'send_pickup_reminders'
    ]
    
    def days_count(self, obj):
        """Calculate rental duration"""
        if obj.pickup_date and obj.return_date:
            days = (obj.return_date - obj.pickup_date).days + 1
            return format_html('<span style="font-weight: bold;">{} days</span>', days)
        return '-'
    days_count.short_description = 'Duration'
    
    def total_amount_display(self, obj):
        """Display total amount with currency"""
        if obj.total_amount:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">${:,.2f}</span>',
                obj.total_amount
            )
        return '-'
    total_amount_display.short_description = 'Total Amount'
    
    def profit_margin(self, obj):
        """Calculate profit margin"""
        if obj.total_amount and obj.base_rate:
            margin = obj.total_amount - obj.base_rate
            percentage = (margin / obj.total_amount) * 100 if obj.total_amount > 0 else 0
            color = '#28a745' if margin > 0 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">${:,.2f} ({:.1f}%)</span>',
                color, margin, percentage
            )
        return '-'
    profit_margin.short_description = 'Profit'
    
    def confirm_bookings(self, request, queryset):
        """Confirm selected bookings"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} bookings confirmed.')
    confirm_bookings.short_description = "Confirm bookings"
    
    def start_rentals(self, request, queryset):
        """Start rental for confirmed bookings"""
        updated = queryset.filter(status='confirmed').update(status='active')
        self.message_user(request, f'{updated} rentals started.')
    start_rentals.short_description = "Start rentals"
    
    def complete_rentals(self, request, queryset):
        """Complete active rentals"""
        updated = queryset.filter(status='active').update(status='completed')
        self.message_user(request, f'{updated} rentals completed.')
    complete_rentals.short_description = "Complete rentals"
    
    def cancel_bookings(self, request, queryset):
        """Cancel selected bookings"""
        from django.utils import timezone
        updated = queryset.filter(
            status__in=['pending', 'confirmed']
        ).update(
            status='cancelled',
            cancelled_at=timezone.now()
        )
        self.message_user(request, f'{updated} bookings cancelled.')
    cancel_bookings.short_description = "Cancel bookings"
    
    def send_pickup_reminders(self, request, queryset):
        """Send pickup reminders for confirmed bookings"""
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        eligible = queryset.filter(
            status='confirmed',
            pickup_date=tomorrow
        )
        # Here you would integrate with your notification system
        count = eligible.count()
        self.message_user(request, f'Pickup reminders sent for {count} bookings.')
    send_pickup_reminders.short_description = "Send pickup reminders"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related(
            'customer', 'vehicle', 'vehicle__model', 'vehicle__model__brand'
        ).prefetch_related('additional_drivers', 'add_on_assignments')


@admin.register(BookingAdditionalDriver)
class BookingAdditionalDriverAdmin(admin.ModelAdmin):
    """Admin for additional drivers"""
    
    list_display = [
        'booking', 'driver', 'additional_fee',
        'is_approved', 'added_at'
    ]
    
    list_filter = [
        'is_approved', 'added_at'
    ]
    
    search_fields = [
        'driver__username', 'driver__email',
        'booking__booking_reference'
    ]
    
    readonly_fields = ['added_at']
    
    actions = ['approve_drivers', 'unapprove_drivers']
    
    def approve_drivers(self, request, queryset):
        """Approve selected drivers"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} drivers approved.')
    approve_drivers.short_description = "Approve drivers"
    
    def unapprove_drivers(self, request, queryset):
        """Unapprove selected drivers"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} drivers unapproved.')
    unapprove_drivers.short_description = "Unapprove drivers"


@admin.register(BookingAddOn)
class BookingAddOnAdmin(admin.ModelAdmin):
    """Admin for booking add-ons"""
    
    list_display = [
        'name', 'addon_type', 'pricing_type', 'price',
        'is_active', 'popularity'
    ]
    
    list_filter = [
        'addon_type', 'pricing_type', 'is_active', 'created_at'
    ]
    
    search_fields = ['name', 'description']
    
    readonly_fields = ['popularity', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'addon_type', 'is_active')
        }),
        ('Pricing', {
            'fields': ('pricing_type', 'price')
        }),
        ('Statistics', {
            'fields': ('popularity', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def popularity(self, obj):
        """Calculate add-on popularity"""
        count = obj.bookingaddonassignment_set.count()
        if count > 50:
            color = '#28a745'
            label = 'High'
        elif count > 10:
            color = '#ffc107'
            label = 'Medium'
        else:
            color = '#6c757d'
            label = 'Low'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            color, label, count
        )
    popularity.short_description = 'Popularity'


@admin.register(BookingAddOnAssignment)
class BookingAddOnAssignmentAdmin(admin.ModelAdmin):
    """Admin for add-on assignments"""
    
    list_display = [
        'booking', 'addon', 'quantity', 'unit_price',
        'total_price', 'added_at'
    ]
    
    list_filter = [
        'addon__addon_type', 'added_at'
    ]
    
    search_fields = [
        'booking__booking_reference', 'addon__name'
    ]
    
    readonly_fields = ['total_price', 'added_at']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related(
            'booking', 'addon'
        )
