from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Agent(models.Model):
    """Agent model to represent sales agents in the system."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='agent_profile'
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Customer(models.Model):
    """Customer model to store customer information and visit details."""
    VISIT_REASON_CHOICES = [
        ('service', 'Service'),
        ('product', 'Product Inquiry'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    visit_reason = models.CharField(
        max_length=20,
        choices=VISIT_REASON_CHOICES,
        default='product'
    )
    notes = models.TextField(blank=True, null=True)
    assigned_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['assigned_agent']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Lead(models.Model):
    """Lead model to track customer leads and their status."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal_sent', 'Proposal Sent'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    
    LEAD_TYPE_CHOICES = [
        ('quick', 'Quick Lead (Ready to Buy)'),
        ('long', 'Long Term Lead'),
        ('none', 'Not a Lead'),
    ]
    
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='lead',
        help_text="The customer this lead is associated with"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    lead_type = models.CharField(
        max_length=20,
        choices=LEAD_TYPE_CHOICES,
        default='quick',
        verbose_name="Lead Type"
    )
    notes = models.TextField(blank=True, null=True)
    expected_close_date = models.DateField(blank=True, null=True)
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated value of the lead"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='leads_created'
    )
    assigned_to = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads_assigned'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

    def __str__(self):
        return f"Lead: {self.customer.name} - {self.get_status_display()}"

    @property
    def is_closed(self):
        return self.status in ['closed_won', 'closed_lost']


class Feedback(models.Model):
    """Feedback model to store customer feedback and ratings."""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (Poor) to 5 (Excellent)"
    )
    comment = models.TextField(blank=True, null=True)
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks_received'
    )
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Feedback'
        verbose_name_plural = 'Customer Feedbacks'

    def __str__(self):
        return f"{self.customer.name} - {self.rating}★"

    def save(self, *args, **kwargs):
        # If no agent is assigned, try to get it from the customer
        if not self.agent and hasattr(self.customer, 'assigned_agent'):
            self.agent = self.customer.assigned_agent
        super().save(*args, **kwargs)


class Interaction(models.Model):
    """Tracks all interactions with customers."""
    ACTION_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'In-Person Meeting'),
        ('chat', 'Live Chat'),
        ('purchase', 'Purchase'),
        ('support', 'Support Request'),
        ('lead', 'Lead Activity'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='interactions',
        help_text="The customer this interaction is associated with"
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        default='call',
        help_text="Type of interaction or action taken"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional details about the interaction in JSON format"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When this interaction occurred"
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions'
    )
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['customer', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
        verbose_name = 'Customer Interaction'
        verbose_name_plural = 'Customer Interactions'

    def __str__(self):
        return f"{self.get_action_type_display()} with {self.customer.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Product(models.Model):
    """Product model to store product information."""
    CATEGORY_CHOICES = [
        ('data_bundle', 'Data Bundle'),
        ('airtime', 'Airtime'),
        ('device', 'Device'),
        ('sim_card', 'SIM Card'),
        ('service', 'Service'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200, help_text="Name of the product")
    description = models.TextField(blank=True, null=True, help_text="Product description")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of the product"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text="Product category"
    )
    is_active = models.BooleanField(default=True, help_text="Whether the product is available for purchase")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_category_display()} (${self.price})"


class Purchase(models.Model):
    """Purchase model to track customer purchases."""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='purchases',
        help_text="The customer who made the purchase"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='purchases',
        help_text="The product that was purchased"
    )
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity purchased")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at the time of purchase"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount paid (quantity × unit price)"
    )
    purchase_date = models.DateTimeField(
        default=timezone.now,
        help_text="When the purchase was made"
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales',
        help_text="The agent who processed the sale"
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the purchase")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'
        indexes = [
            models.Index(fields=['customer', 'purchase_date']),
            models.Index(fields=['product', 'purchase_date']),
        ]

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} x{self.quantity} on {self.purchase_date.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        # Calculate total amount before saving
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class SupportRequest(models.Model):
    """Support request model to track customer support issues."""
    REQUEST_TYPES = [
        ('technical', 'Technical Issue'),
        ('billing', 'Billing Question'),
        ('service', 'Service Request'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting on Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='support_requests',
        help_text="The customer who submitted the request"
    )
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPES,
        default='technical',
        help_text="Type of support request"
    )
    subject = models.CharField(max_length=200, help_text="Brief description of the issue")
    description = models.TextField(help_text="Detailed description of the issue")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Current status of the request"
    )
    priority = models.PositiveSmallIntegerField(
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')],
        default=2,
        help_text="Priority level of the request"
    )
    assigned_to = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_support_requests',
        help_text="Agent assigned to handle this request"
    )
    resolved_at = models.DateTimeField(blank=True, null=True, help_text="When the request was resolved")
    resolution_notes = models.TextField(blank=True, null=True, help_text="Notes about how the issue was resolved")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Request'
        verbose_name_plural = 'Support Requests'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()}: {self.subject} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # If status is being updated to resolved, set resolved_at
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)
