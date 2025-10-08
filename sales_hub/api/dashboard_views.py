from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta

from ..models import Customer, Interaction, Lead, Purchase, SupportRequest

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics including customer counts, interaction counts, etc.
    """
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Customer stats
    total_customers = Customer.objects.count()
    new_customers_7d = Customer.objects.filter(created_at__date__gte=week_ago).count()
    new_customers_30d = Customer.objects.filter(created_at__date__gte=month_ago).count()
    
    # Interaction stats
    total_interactions = Interaction.objects.count()
    interactions_7d = Interaction.objects.filter(timestamp__date__gte=week_ago).count()
    interactions_30d = Interaction.objects.filter(timestamp__date__gte=month_ago).count()
    
    # Lead stats
    total_leads = Lead.objects.count()
    new_leads_7d = Lead.objects.filter(created_at__date__gte=week_ago).count()
    open_leads = Lead.objects.filter(is_active=True).count()
    
    # Purchase stats
    total_purchases = Purchase.objects.count()
    revenue_7d = Purchase.objects.filter(purchase_date__date__gte=week_ago).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    revenue_30d = Purchase.objects.filter(purchase_date__date__gte=month_ago).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Support stats
    open_support = SupportRequest.objects.filter(status='open').count()
    support_7d = SupportRequest.objects.filter(created_at__date__gte=week_ago).count()
    
    data = {
        'customers': {
            'total': total_customers,
            'new_7d': new_customers_7d,
            'new_30d': new_customers_30d,
        },
        'interactions': {
            'total': total_interactions,
            'last_7d': interactions_7d,
            'last_30d': interactions_30d,
        },
        'leads': {
            'total': total_leads,
            'new_7d': new_leads_7d,
            'open': open_leads,
        },
        'purchases': {
            'total': total_purchases,
            'revenue_7d': float(revenue_7d),
            'revenue_30d': float(revenue_30d),
        },
        'support': {
            'open': open_support,
            'new_7d': support_7d,
        },
        'last_updated': timezone.now().isoformat()
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """
    Get recent activities across different models for the dashboard
    """
    # Get recent interactions
    recent_interactions = Interaction.objects.select_related('customer', 'agent').order_by('-timestamp')[:10]
    
    # Get recent purchases
    recent_purchases = Purchase.objects.select_related('customer', 'product', 'agent').order_by('-purchase_date')[:5]
    
    # Get recent support requests
    recent_support = SupportRequest.objects.select_related('customer', 'assigned_to')\
        .order_by('-created_at')[:5]
    
    # Get recent leads
    recent_leads = Lead.objects.select_related('customer', 'assigned_to')\
        .filter(is_active=True)\
        .order_by('-created_at')[:5]
    
    # Format the data
    def format_interaction(interaction):
        return {
            'id': interaction.id,
            'type': 'interaction',
            'action_type': interaction.action_type,
            'customer': interaction.customer.name if interaction.customer else 'Unknown',
            'agent': interaction.agent.user.get_full_name() if interaction.agent else 'System',
            'timestamp': interaction.timestamp,
            'notes': interaction.notes[:100] + '...' if interaction.notes else '',
            'is_completed': interaction.is_completed,
            'details': interaction.details
        }
    
    def format_purchase(purchase):
        return {
            'id': purchase.id,
            'type': 'purchase',
            'customer': purchase.customer.name if purchase.customer else 'Unknown',
            'product': purchase.product.name if purchase.product else 'Unknown',
            'amount': float(purchase.total_amount),
            'date': purchase.purchase_date,
            'agent': purchase.agent.user.get_full_name() if purchase.agent else 'System'
        }
    
    def format_support(support):
        return {
            'id': support.id,
            'type': 'support',
            'customer': support.customer.name if support.customer else 'Unknown',
            'request_type': support.request_type,
            'subject': support.subject,
            'status': support.status,
            'priority': support.priority,
            'created_at': support.created_at,
            'assigned_to': support.assigned_to.user.get_full_name() if support.assigned_to else 'Unassigned'
        }
    
    def format_lead(lead):
        return {
            'id': lead.id,
            'type': 'lead',
            'customer': lead.customer.name if lead.customer else 'Unknown',
            'status': lead.status,
            'lead_type': lead.lead_type,
            'value': float(lead.value) if lead.value else 0,
            'expected_close_date': lead.expected_close_date,
            'assigned_to': lead.assigned_to.user.get_full_name() if lead.assigned_to else 'Unassigned',
            'created_at': lead.created_at
        }
    
    # Combine and sort all activities
    activities = []
    activities.extend([format_interaction(i) for i in recent_interactions])
    activities.extend([format_purchase(p) for p in recent_purchases])
    activities.extend([format_support(s) for s in recent_support])
    activities.extend([format_lead(l) for l in recent_leads])
    
    # Sort by timestamp/date (newest first)
    activities.sort(key=lambda x: x.get('timestamp', x.get('date', x.get('created_at'))), reverse=True)
    
    # Return top 20 most recent activities
    return Response(activities[:20])
