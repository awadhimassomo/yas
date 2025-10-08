from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Customer, Agent

User = get_user_model()

class QuickServiceType(models.TextChoices):
    PUK_CODE_RETRIEVAL = 'puk_code', 'PUK Code Retrieval'
    E_STATEMENT = 'e_statement', 'E-Statement'
    TRANSACTION_REVERSAL = 'transaction_reversal', 'Transaction Reversal'
    LOCKED_DEVICE_FINANCE = 'locked_device', 'Locked Device Finance'
    NIVUSHE_CLEARANCE = 'nivushe_clearance', 'Nivushe Clearance Letter'

class QuickServiceRequest(models.Model):
    """
    Tracks customer interactions with Quick Services.
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='quick_service_requests'
    )
    service_type = models.CharField(
        max_length=50,
        choices=QuickServiceType.choices,
        help_text="Type of Quick Service requested"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_services'
    )
    assigned_agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_services'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Quick Service Request'
        verbose_name_plural = 'Quick Service Requests'
        indexes = [
            models.Index(fields=['customer', 'service_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.customer.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Update completed_at if status is changed to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def log_service_request(cls, customer, service_type, user=None, notes=None):
        """
        Helper method to log a new Quick Service request.
        """
        return cls.objects.create(
            customer=customer,
            service_type=service_type,
            requested_by=user,
            assigned_agent=customer.assigned_agent,
            notes=notes
        )
