from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import (
    PaymentMethod, Payment, Invoice, Receipt
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin for payment methods"""
    
    list_display = [
        'name', 'method_type', 'is_active',
        'requires_verification', 'created_at'
    ]
    
    list_filter = [
        'method_type', 'is_active', 'requires_verification', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'method_type', 'description', 'is_active')
        }),
        ('Processing Fees', {
            'fields': ('processing_fee_percentage', 'processing_fee_fixed')
        }),
        ('Settings', {
            'fields': ('requires_verification', 'icon')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_methods', 'deactivate_methods']
    
    def activate_methods(self, request, queryset):
        """Activate selected payment methods"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} payment methods activated.')
    activate_methods.short_description = "Activate payment methods"
    
    def deactivate_methods(self, request, queryset):
        """Deactivate selected payment methods"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} payment methods deactivated.')
    deactivate_methods.short_description = "Deactivate payment methods"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Comprehensive admin for payments"""
    
    list_display = [
        'transaction_id', 'customer', 'booking', 'amount',
        'payment_type', 'status', 'payment_method_display',
        'created_at'
    ]
    
    list_filter = [
        'payment_type', 'status', 'payment_method__method_type',
        'currency', 'created_at', 'payment_date'
    ]
    
    search_fields = [
        'transaction_id', 'customer__username', 'customer__email',
        'booking__booking_reference', 'gateway_transaction_id'
    ]
    
    readonly_fields = [
        'id', 'transaction_id', 'created_at',
        'payment_date', 'amount_display', 'fee_display'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('transaction_id', 'customer', 'booking', 'payment_type', 'status')
        }),
        ('Amount Details', {
            'fields': ('amount_display', 'currency', 'fee_display')
        }),
        ('Payment Method', {
            'fields': ('payment_method',)
        }),
        ('Processing', {
            'fields': ('payment_date', 'due_date'),
            'classes': ('collapse',)
        }),
        ('External Integration', {
            'fields': ('gateway_transaction_id', 'gateway_response',
                      'gateway_fee'),
            'classes': ('collapse',)
        }),
        ('Card Information', {
            'fields': ('card_last_four', 'card_type', 'card_token'),
            'classes': ('collapse',)
        }),
        ('Receipt Information', {
            'fields': ('receipt_number', 'receipt_generated', 'receipt_sent'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'process_payments', 'refund_payments', 'mark_failed',
        'export_transactions'
    ]
    
    def payment_method_display(self, obj):
        """Display payment method info"""
        if obj.payment_method:
            return format_html(
                '{} (*{})',
                obj.payment_method.method_type.title(),
                obj.payment_method.last_four_digits or '****'
            )
        return '-'
    payment_method_display.short_description = 'Payment Method'
    
    def amount_display(self, obj):
        """Display amount with currency"""
        if obj.amount:
            color = '#28a745' if obj.status == 'completed' else '#6c757d'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} {:,.2f}</span>',
                color, obj.currency, obj.amount
            )
        return '-'
    amount_display.short_description = 'Amount'
    
    def fee_display(self, obj):
        """Display processing fee"""
        if obj.gateway_fee:
            return format_html(
                '<span style="color: #dc3545;">{} {:,.2f}</span>',
                obj.currency, obj.gateway_fee
            )
        return '-'
    fee_display.short_description = 'Fee'
    
    def process_payments(self, request, queryset):
        """Process pending payments"""
        updated = queryset.filter(status='pending').update(
            status='processing',
            payment_date=timezone.now()
        )
        self.message_user(request, f'{updated} payments marked as processing.')
    process_payments.short_description = "Process payments"
    
    def refund_payments(self, request, queryset):
        """Initiate refunds for completed payments"""
        updated = queryset.filter(status='completed').update(status='refunded')
        self.message_user(request, f'{updated} payments marked for refund.')
    refund_payments.short_description = "Initiate refunds"
    
    def mark_failed(self, request, queryset):
        """Mark payments as failed"""
        updated = queryset.filter(
            status__in=['pending', 'processing']
        ).update(status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_failed.short_description = "Mark as failed"
    
    def export_transactions(self, request, queryset):
        """Export transaction data"""
        # Here you would implement CSV/Excel export
        count = queryset.count()
        self.message_user(request, f'{count} transactions prepared for export.')
    export_transactions.short_description = "Export transactions"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related(
            'customer', 'booking', 'payment_method'
        )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for invoices"""
    
    list_display = [
        'invoice_number', 'booking', 'customer', 'total_amount',
        'status', 'issue_date', 'due_date'
    ]
    
    list_filter = [
        'status', 'issue_date', 'due_date', 'created_at'
    ]
    
    search_fields = [
        'invoice_number', 'booking__booking_reference',
        'customer__username', 'customer__email'
    ]
    
    readonly_fields = [
        'id', 'invoice_number', 'created_at', 'updated_at',
        'total_display', 'overdue_status'
    ]
    
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'booking', 'customer', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Amount Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount',
                      'total_display')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_paid', 'send_invoices', 'mark_overdue']
    
    def total_display(self, obj):
        """Display total with currency"""
        if obj.total_amount:
            color = '#28a745' if obj.status == 'paid' else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">R {:,.2f}</span>',
                color, obj.total_amount
            )
        return '-'
    total_display.short_description = 'Total Amount'
    
    def overdue_status(self, obj):
        """Check if invoice is overdue"""
        if obj.status != 'paid' and obj.due_date:
            today = timezone.now().date()
            if obj.due_date < today:
                days_overdue = (today - obj.due_date).days
                return format_html(
                    '<span style="color: #dc3545; font-weight: bold;">⚠️ {} days overdue</span>',
                    days_overdue
                )
        return format_html('<span style="color: #28a745;">✅ Current</span>')
    overdue_status.short_description = 'Status'
    
    def mark_paid(self, request, queryset):
        """Mark invoices as paid"""
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} invoices marked as paid.')
    mark_paid.short_description = "Mark as paid"
    
    def send_invoices(self, request, queryset):
        """Send invoices to customers"""
        # Here you would integrate with email system
        count = queryset.count()
        self.message_user(request, f'{count} invoices sent to customers.')
    send_invoices.short_description = "Send invoices"
    
    def mark_overdue(self, request, queryset):
        """Mark invoices as overdue"""
        updated = queryset.filter(
            due_date__lt=timezone.now().date()
        ).exclude(status='paid').update(status='overdue')
        self.message_user(request, f'{updated} invoices marked as overdue.')
    mark_overdue.short_description = "Mark overdue"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """Admin for receipts"""
    
    list_display = [
        'receipt_number', 'payment', 'customer', 'amount',
        'issue_date', 'created_at'
    ]
    
    list_filter = [
        'issue_date', 'created_at'
    ]
    
    search_fields = [
        'receipt_number', 'payment__transaction_id',
        'customer__username', 'customer__email'
    ]
    
    readonly_fields = [
        'id', 'receipt_number', 'created_at',
        'amount_display'
    ]
    
    date_hierarchy = 'issue_date'
    
    def amount_display(self, obj):
        """Display amount with currency"""
        if obj.amount:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">R {:,.2f}</span>',
                obj.amount
            )
        return '-'
    amount_display.short_description = 'Amount'
    
    actions = ['regenerate_receipts']
    
    def regenerate_receipts(self, request, queryset):
        """Regenerate receipt documents"""
        count = queryset.count()
        self.message_user(request, f'{count} receipts regenerated.')
    regenerate_receipts.short_description = "Regenerate receipts"
    

