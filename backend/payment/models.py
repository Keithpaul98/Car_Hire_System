from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from authentication.models import CustomUser
from bookings.models import Booking
import uuid
from datetime import datetime


class PaymentMethod(models.Model):
    """Available payment methods"""
    
    METHOD_TYPES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('mobile_payment', 'Mobile Payment'),
        ('cryptocurrency', 'Cryptocurrency'),
    ]
    
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    description = models.TextField(null=True, blank=True)
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    processing_fee_fixed = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    requires_verification = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_methods'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Payment(models.Model):
    """Payment transactions"""
    
    PAYMENT_TYPES = [
        ('booking_payment', 'Booking Payment'),
        ('security_deposit', 'Security Deposit'),
        ('additional_charges', 'Additional Charges'),
        ('penalty', 'Penalty'),
        ('refund', 'Refund'),
        ('partial_refund', 'Partial Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=50, unique=True, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    payment_type = models.CharField(max_length=30, choices=PAYMENT_TYPES)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='ZAR')
    
    # Status and Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # External Payment Gateway Information
    gateway_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_response = models.JSONField(default=dict, null=True, blank=True)
    gateway_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Card Information (encrypted/tokenized)
    card_last_four = models.CharField(max_length=4, null=True, blank=True)
    card_type = models.CharField(max_length=20, null=True, blank=True)  # Visa, MasterCard, etc.
    card_token = models.CharField(max_length=100, null=True, blank=True)
    
    # Receipt and Documentation
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    receipt_generated = models.BooleanField(default=False)
    receipt_sent = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    
    # Refund Information
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(null=True, blank=True)
    refunded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    
    # Additional Information
    description = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payments')
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['customer', 'payment_date']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status', 'payment_date']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.customer.username} ({self.amount} {self.currency})"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        import random
        import string
        prefix = 'TXN'
        timestamp = datetime.now().strftime('%y%m%d%H%M')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"
    
    def is_refundable(self):
        """Check if payment can be refunded"""
        return self.status == 'completed' and self.refund_amount < self.amount


class Invoice(models.Model):
    """Professional invoices for bookings and payments"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice Details
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Financial Information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)  # VAT rate
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Invoice Content
    line_items = models.JSONField(default=list)  # List of invoice line items
    notes = models.TextField(null=True, blank=True)
    terms_and_conditions = models.TextField(null=True, blank=True)
    
    # Document Generation
    pdf_generated = models.BooleanField(default=False)
    pdf_file_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Communication
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_to_email = models.EmailField(null=True, blank=True)
    reminder_sent_count = models.PositiveIntegerField(default=0)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_invoices')
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['issue_date']),
        ]
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        prefix = 'INV'
        year = datetime.now().year
        # Get the next sequential number for this year
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=f"{prefix}{year}"
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number[-4:])
            next_number = last_number + 1
        else:
            next_number = 1
        
        return f"{prefix}{year}{next_number:04d}"
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.due_date < datetime.now().date() and self.status not in ['paid', 'cancelled']
    
    def get_balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount


class Receipt(models.Model):
    """Professional receipts for completed payments"""
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receipts')
    
    # Receipt Details
    issue_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZAR')
    payment_method_used = models.CharField(max_length=100)
    
    # Receipt Content
    line_items = models.JSONField(default=list)
    notes = models.TextField(null=True, blank=True)
    
    # Document Generation
    template_used = models.CharField(max_length=100, default='default')
    pdf_generated = models.BooleanField(default=False)
    pdf_file_path = models.CharField(max_length=500, null=True, blank=True)
    
    # Communication
    sent_to_customer = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_to_email = models.EmailField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_receipts')
    
    class Meta:
        db_table = 'receipts'
        verbose_name = 'Receipt'
        verbose_name_plural = 'Receipts'
        indexes = [
            models.Index(fields=['customer', 'issue_date']),
            models.Index(fields=['receipt_number']),
            models.Index(fields=['payment']),
        ]
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)
    
    def generate_receipt_number(self):
        """Generate unique receipt number"""
        prefix = 'RCP'
        timestamp = datetime.now().strftime('%y%m%d')
        # Get sequential number for today
        today_receipts = Receipt.objects.filter(
            receipt_number__startswith=f"{prefix}{timestamp}"
        ).count()
        next_number = today_receipts + 1
        return f"{prefix}{timestamp}{next_number:04d}"


class FinancialReport(models.Model):
    """Generated financial reports"""
    
    REPORT_TYPES = [
        ('daily_summary', 'Daily Summary'),
        ('weekly_summary', 'Weekly Summary'),
        ('monthly_summary', 'Monthly Summary'),
        ('revenue_analysis', 'Revenue Analysis'),
        ('payment_analysis', 'Payment Analysis'),
        ('customer_analysis', 'Customer Analysis'),
        ('vehicle_performance', 'Vehicle Performance'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    
    # Report Parameters
    start_date = models.DateField()
    end_date = models.DateField()
    filters = models.JSONField(default=dict, null=True, blank=True)
    
    # Report Data
    data = models.JSONField(default=dict)
    summary_metrics = models.JSONField(default=dict)
    
    # File Generation
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    file_generated = models.BooleanField(default=False)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, null=True, blank=True)  # daily, weekly, monthly
    next_generation_date = models.DateTimeField(null=True, blank=True)
    
    # Distribution
    email_recipients = models.JSONField(default=list, null=True, blank=True)
    auto_send = models.BooleanField(default=False)
    last_sent_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_reports')
    
    class Meta:
        db_table = 'financial_reports'
        verbose_name = 'Financial Report'
        verbose_name_plural = 'Financial Reports'
        indexes = [
            models.Index(fields=['report_type', 'start_date']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['is_scheduled', 'next_generation_date']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_name} ({self.start_date} to {self.end_date})"
