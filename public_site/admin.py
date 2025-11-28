from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    """Admin interface for Service Requests."""
    
    list_display = [
        'id',
        'phone_number',
        'service_type_badge',
        'specific_service',
        'timeline_badge',
        'lead_score_badge',
        'status_badge',
        'assigned_to',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'service_type',
        'timeline',
        'created_at',
        'lead_score',
    ]
    
    search_fields = [
        'phone_number',
        'specific_service',
        'notes',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'completed_at',
        'ip_address',
        'user_agent',
        'lead_score',
    ]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('phone_number',)
        }),
        ('Service Details', {
            'fields': ('service_type', 'specific_service', 'timeline', 'contact_preference')
        }),
        ('Lead Information', {
            'fields': ('lead_score', 'status', 'assigned_to', 'notes')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_in_progress', 'mark_as_completed', 'mark_as_cancelled']
    
    def service_type_badge(self, obj):
        """Display service type with colored badge."""
        colors = {
            'quick-service': '#10b981',  # green
            'product-service': '#3b82f6',  # blue
            'support-service': '#f59e0b',  # amber
        }
        color = colors.get(obj.service_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_service_type_display()
        )
    service_type_badge.short_description = 'Service Type'
    
    def timeline_badge(self, obj):
        """Display timeline with colored badge."""
        colors = {
            'immediate': '#ef4444',  # red
            'this-week': '#f59e0b',  # amber
            'this-month': '#3b82f6',  # blue
            'just-browsing': '#6b7280',  # gray
        }
        color = colors.get(obj.timeline, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_timeline_display()
        )
    timeline_badge.short_description = 'Timeline'
    
    def lead_score_badge(self, obj):
        """Display lead score with colored badge."""
        if obj.lead_score >= 70:
            color = '#10b981'  # green
        elif obj.lead_score >= 40:
            color = '#f59e0b'  # amber
        else:
            color = '#ef4444'  # red
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}/100</span>',
            color,
            obj.lead_score
        )
    lead_score_badge.short_description = 'Lead Score'
    
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'pending': '#f59e0b',  # amber
            'in_progress': '#3b82f6',  # blue
            'completed': '#10b981',  # green
            'cancelled': '#6b7280',  # gray
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected requests as in progress."""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} request(s) marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as In Progress'
    
    def mark_as_completed(self, request, queryset):
        """Mark selected requests as completed."""
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} request(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as Completed'
    
    def mark_as_cancelled(self, request, queryset):
        """Mark selected requests as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} request(s) marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark as Cancelled'
    
    def changelist_view(self, request, extra_context=None):
        """Add custom statistics to the change list view."""
        extra_context = extra_context or {}
        
        # Calculate statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        total_requests = ServiceRequest.objects.count()
        pending_requests = ServiceRequest.objects.filter(status='pending').count()
        in_progress_requests = ServiceRequest.objects.filter(status='in_progress').count()
        completed_today = ServiceRequest.objects.filter(
            status='completed',
            completed_at__date=today
        ).count()
        new_this_week = ServiceRequest.objects.filter(
            created_at__date__gte=week_ago
        ).count()
        
        # Service type breakdown
        service_breakdown = ServiceRequest.objects.values('service_type').annotate(
            count=Count('id')
        )
        
        # High priority requests
        high_priority = ServiceRequest.objects.filter(
            lead_score__gte=70,
            timeline='immediate',
            status='pending'
        ).count()
        
        extra_context['total_requests'] = total_requests
        extra_context['pending_requests'] = pending_requests
        extra_context['in_progress_requests'] = in_progress_requests
        extra_context['completed_today'] = completed_today
        extra_context['new_this_week'] = new_this_week
        extra_context['service_breakdown'] = service_breakdown
        extra_context['high_priority'] = high_priority
        
        return super().changelist_view(request, extra_context=extra_context)
