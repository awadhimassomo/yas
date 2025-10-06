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
    INTERACTION_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'In-Person Meeting'),
        ('chat', 'Live Chat'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interactions'
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
        default='call'
    )
    notes = models.TextField()
    follow_up_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.customer.name} on {self.created_at.strftime('%Y-%m-%d')}"
