from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from django.utils import timezone
from .models import (
    Review, LoyaltyProgram, Promotion, IssueReport
)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for customer reviews"""
    
    list_display = [
        'customer', 'booking', 'overall_rating', 'vehicle',
        'is_verified', 'is_featured', 'helpful_votes', 'created_at'
    ]
    
    list_filter = [
        'overall_rating', 'is_verified', 'is_featured',
        'is_approved', 'created_at'
    ]
    
    search_fields = [
        'customer__username', 'customer__email', 'title',
        'comment', 'booking__booking_reference'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'helpful_votes',
        'rating_display', 'verification_status'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Review Information', {
            'fields': ('customer', 'booking', 'vehicle', 'title')
        }),
        ('Rating & Content', {
            'fields': ('rating_display', 'vehicle_condition_rating', 'service_rating', 
                      'value_for_money_rating', 'comment', 'pros', 'cons')
        }),
        ('Status', {
            'fields': ('is_verified', 'verification_status', 'is_approved',
                      'is_featured')
        }),
        ('Engagement', {
            'fields': ('helpful_votes', 'total_votes', 'company_response'),
            'classes': ('collapse',)
        }),
        ('Moderation', {
            'fields': ('moderation_notes', 'moderated_by'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'verify_reviews', 'feature_reviews', 'approve_reviews',
        'unapprove_reviews'
    ]
    
    def rating_display(self, obj):
        """Display rating with stars"""
        if obj.overall_rating:
            stars = '★' * obj.overall_rating + '☆' * (5 - obj.overall_rating)
            color = '#ffc107' if obj.overall_rating >= 4 else '#6c757d' if obj.overall_rating >= 3 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-size: 16px;">{} ({})</span>',
                color, stars, obj.overall_rating
            )
        return '-'
    rating_display.short_description = 'Rating'
    
    def verification_status(self, obj):
        """Display verification status"""
        if obj.is_verified:
            return format_html('<span style="color: #28a745;">✅ Verified</span>')
        return format_html('<span style="color: #6c757d;">⏳ Pending</span>')
    verification_status.short_description = 'Verification'
    
    def verify_reviews(self, request, queryset):
        """Verify selected reviews"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} reviews verified.')
    verify_reviews.short_description = "Verify reviews"
    
    def feature_reviews(self, request, queryset):
        """Feature selected reviews"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} reviews featured.')
    feature_reviews.short_description = "Feature reviews"
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = "Approve reviews"
    
    def unapprove_reviews(self, request, queryset):
        """Unapprove selected reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews unapproved.')
    unapprove_reviews.short_description = "Unapprove reviews"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related(
            'customer', 'booking'
        )


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    """Admin for loyalty programs"""
    
    list_display = [
        'tier', 'min_points_required', 'discount_percentage',
        'is_active', 'member_count', 'created_at'
    ]
    
    list_filter = [
        'tier', 'is_active', 'created_at'
    ]
    
    search_fields = ['tier']
    
    readonly_fields = ['created_at', 'member_count']
    
    fieldsets = (
        ('Program Information', {
            'fields': ('tier', 'is_active')
        }),
        ('Requirements', {
            'fields': ('min_points_required',)
        }),
        ('Benefits', {
            'fields': ('discount_percentage', 'points_per_dollar', 'benefits')
        }),
        ('Statistics', {
            'fields': ('member_count',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        """Count members in this tier"""
        from authentication.models import CustomUser
        count = CustomUser.objects.filter(loyalty_tier=obj.tier).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    member_count.short_description = 'Members'
    
    actions = ['activate_programs', 'deactivate_programs']
    
    def activate_programs(self, request, queryset):
        """Activate selected programs"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} programs activated.')
    activate_programs.short_description = "Activate programs"
    
    def deactivate_programs(self, request, queryset):
        """Deactivate selected programs"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} programs deactivated.')
    deactivate_programs.short_description = "Deactivate programs"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Admin for promotions"""
    
    list_display = [
        'name', 'code', 'discount_value', 'start_date',
        'end_date', 'is_active', 'usage_count', 'status_display'
    ]
    
    list_filter = [
        'discount_type', 'is_active', 'is_public',
        'start_date', 'end_date', 'created_at'
    ]
    
    search_fields = [
        'name', 'description', 'code'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'usage_count',
        'status_display', 'effectiveness'
    ]
    
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Promotion Information', {
            'fields': ('name', 'code', 'description', 'is_active', 'is_public')
        }),
        ('Discount Details', {
            'fields': ('discount_type', 'discount_value', 'max_discount_amount')
        }),
        ('Validity Period', {
            'fields': ('start_date', 'end_date', 'status_display')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'per_customer_limit', 'usage_count')
        }),
        ('Conditions', {
            'fields': ('min_booking_amount', 'min_rental_days',
                      'applicable_vehicle_categories'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('effectiveness',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activate_promotions', 'deactivate_promotions', 'extend_promotions'
    ]
    
    def status_display(self, obj):
        """Display promotion status"""
        today = timezone.now().date()
        
        if not obj.is_active:
            return format_html('<span style="color: #6c757d;">⏸️ Inactive</span>')
        elif obj.start_date > today:
            return format_html('<span style="color: #17a2b8;">⏳ Scheduled</span>')
        elif obj.end_date < today:
            return format_html('<span style="color: #dc3545;">❌ Expired</span>')
        elif obj.usage_limit and obj.usage_count >= obj.usage_limit:
            return format_html('<span style="color: #ffc107;">⚠️ Limit Reached</span>')
        else:
            return format_html('<span style="color: #28a745;">✅ Active</span>')
    status_display.short_description = 'Status'
    
    def effectiveness(self, obj):
        """Calculate promotion effectiveness"""
        if obj.usage_limit and obj.usage_count:
            percentage = (obj.usage_count / obj.usage_limit) * 100
            color = '#28a745' if percentage > 70 else '#ffc107' if percentage > 30 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color, percentage
            )
        return '-'
    effectiveness.short_description = 'Effectiveness'
    
    def activate_promotions(self, request, queryset):
        """Activate selected promotions"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} promotions activated.')
    activate_promotions.short_description = "Activate promotions"
    
    def deactivate_promotions(self, request, queryset):
        """Deactivate selected promotions"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} promotions deactivated.')
    deactivate_promotions.short_description = "Deactivate promotions"
    
    def extend_promotions(self, request, queryset):
        """Extend promotion end dates by 30 days"""
        from datetime import timedelta
        for promotion in queryset:
            if promotion.end_date:
                promotion.end_date += timedelta(days=30)
                promotion.save()
        count = queryset.count()
        self.message_user(request, f'{count} promotions extended by 30 days.')
    extend_promotions.short_description = "Extend by 30 days"


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    """Admin for issue reports"""
    
    list_display = [
        'ticket_number', 'subject', 'customer', 'booking', 'issue_type', 'priority',
        'status', 'is_verified', 'created_at'
    ]
    
    list_filter = [
        'issue_type', 'priority', 'status', 'is_verified',
        'created_at'
    ]
    
    search_fields = [
        'ticket_number', 'subject', 'description', 'customer__username',
        'booking__booking_reference'
    ]
    
    readonly_fields = [
        'id', 'ticket_number', 'created_at', 'updated_at',
        'priority_display'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Issue Information', {
            'fields': ('ticket_number', 'subject', 'description', 'customer', 'booking', 'vehicle')
        }),
        ('Classification', {
            'fields': ('issue_type', 'priority_display', 'status', 'location')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verification_notes')
        }),
        ('Resolution', {
            'fields': ('resolved_by', 'resolution_notes', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Evidence', {
            'fields': ('evidence_photos', 'evidence_documents'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'verify_issues', 'mark_in_progress', 'mark_resolved',
        'escalate_priority'
    ]
    
    def priority_display(self, obj):
        """Display priority with color coding"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.priority.title()
        )
    priority_display.short_description = 'Priority'
    

    
    def verify_issues(self, request, queryset):
        """Verify selected issues"""
        updated = queryset.update(
            is_verified=True,
            verified_by=request.user
        )
        self.message_user(request, f'{updated} issues verified.')
    verify_issues.short_description = "Verify issues"
    
    def mark_in_progress(self, request, queryset):
        """Mark issues as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} issues marked as in progress.')
    mark_in_progress.short_description = "Mark in progress"
    
    def mark_resolved(self, request, queryset):
        """Mark issues as resolved"""
        updated = queryset.update(
            status='resolved',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} issues marked as resolved.')
    mark_resolved.short_description = "Mark resolved"
    
    def escalate_priority(self, request, queryset):
        """Escalate priority of selected issues"""
        priority_map = {
            'low': 'medium',
            'medium': 'high',
            'high': 'critical'
        }
        updated = 0
        for issue in queryset:
            if issue.priority in priority_map:
                issue.priority = priority_map[issue.priority]
                issue.save()
                updated += 1
        self.message_user(request, f'{updated} issues escalated.')
    escalate_priority.short_description = "Escalate priority"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related(
            'customer', 'booking', 'verified_by', 'resolved_by'
        )



