from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class ServiceRequest(models.Model):
    """Model to track service requests from the public website."""
    
    SERVICE_TYPE_CHOICES = [
        ('quick-service', 'Quick Service'),
        ('product-service', 'Products & Packages'),
        ('support-service', 'Support & Contact'),
    ]
    
    SPECIFIC_SERVICE_CHOICES = [
        # Quick Services
        ('puk', 'PUK Code Retrieval'),
        ('estatement', 'E-Statement'),
        ('transaction-reversal', 'Transaction Reversal'),
        ('locked-device', 'Locked Device Finance'),
        ('clearance-letter', 'Nivushe Clearance Letter'),
        # Products & Packages
        ('data-bundle', 'Data Bundle'),
        ('b2b', 'B2B Packages'),
        ('kinara', 'Kinara Packages'),
        ('esim', 'eSIM Activation'),
        ('device-finance', 'Device Finance'),
        ('hbb', 'HBB Devices'),
        ('fttx', 'FTTX Home Plan'),
        ('dedicated-link', 'Dedicated Link'),
        ('5g-unlimited-fwa', '5G Unlimited FWA'),
        # Support & Contact
        ('br-chatbot', 'BR Chatbot Assistance'),
        ('call', 'Call Support'),
        ('location', 'Visit Our Shop'),
        ('appointment', 'Book Appointment'),
    ]
    
    TIMELINE_CHOICES = [
        ('immediate', 'Today/Right Now'),
        ('in-store', 'I am at the store now (Get Ticket)'),
        ('this-week', 'Within this week'),
        ('this-month', 'Within this month'),
        ('just-browsing', 'Just gathering information'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Customer Information
    phone_number = models.CharField(max_length=20, help_text="Customer phone number")
    
    # Service Details
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPE_CHOICES,
        help_text="Main service category"
    )
    specific_service = models.CharField(
        max_length=30,
        choices=SPECIFIC_SERVICE_CHOICES,
        help_text="Specific service requested"
    )
    
    # Lead Qualification
    timeline = models.CharField(
        max_length=20,
        choices=TIMELINE_CHOICES,
        default='immediate',
        help_text="When customer wants to solve this"
    )
    contact_preference = models.CharField(
        max_length=10,
        choices=[('yes', 'Yes'), ('no', 'No')],
        default='no',
        help_text="Contact about special offers"
    )
    
    # Lead Score
    lead_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Calculated lead score (0-100)"
    )
    
    # Status and Assignment
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the request"
    )
    assigned_to = models.ForeignKey(
        'sales_hub.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='public_service_requests',
        help_text="Agent assigned to handle this request"
    )
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of requester")
    user_agent = models.TextField(blank=True, null=True, help_text="Browser user agent")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['service_type', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['lead_score']),
        ]
    
    def __str__(self):
        return f"{self.get_specific_service_display()} - {self.phone_number} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_high_priority(self):
        """Returns True if this is a high-priority request."""
        return self.lead_score >= 70 and self.timeline == 'immediate'
    
    @property
    def service_category_display(self):
        """Returns a friendly display of the service category."""
        return self.get_service_type_display()
