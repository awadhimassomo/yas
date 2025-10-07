from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Agent, Customer, Lead, Feedback, Interaction
from .forms import LeadUpdateForm, FeedbackForm, InteractionForm


@login_required
def dashboard(request):
    """Agent dashboard showing assigned customers, leads, and recent activity."""
    try:
        agent = request.user.agent_profile
    except Agent.DoesNotExist:
        # If the user doesn't have an agent profile, redirect to an error page or create one
        return render(request, 'sales_hub/agent_profile_required.html')
    
    # Get assigned customers
    customers = agent.customers.filter(is_active=True).select_related('lead')
    
    # Get leads assigned to the agent
    leads = Lead.objects.filter(
        assigned_to=agent,
        is_active=True
    ).select_related('customer', 'assigned_to')
    
    # Get recent feedback for agent's customers
    recent_feedback = Feedback.objects.filter(
        customer__in=customers
    ).order_by('-created_at')[:5]
    
    # Get recent interactions
    recent_interactions = Interaction.objects.filter(
        agent=agent
    ).order_by('-created_at')[:5]
    
    # Get lead statistics
    lead_stats = {
        'total': leads.count(),
        'new': leads.filter(status='new').count(),
        'contacted': leads.filter(status='contacted').count(),
        'qualified': leads.filter(status='qualified').count(),
        'closed_won': leads.filter(status='closed_won').count(),
        'closed_lost': leads.filter(status='closed_lost').count(),
    }
    
    # Calculate conversion rate (won / (won + lost))
    total_closed = lead_stats['closed_won'] + lead_stats['closed_lost']
    lead_stats['conversion_rate'] = (
        (lead_stats['closed_won'] / total_closed * 100) if total_closed > 0 else 0
    )
    
    context = {
        'agent': agent,
        'customers': customers,
        'leads': leads,
        'recent_feedback': recent_feedback,
        'recent_interactions': recent_interactions,
        'lead_stats': lead_stats,
        'active_tab': 'dashboard',
    }
    
    return render(request, 'sales_hub/dashboard.html', context)


@login_required
def update_lead(request, lead_id):
    """Update lead status and notes."""
    lead = get_object_or_404(Lead, id=lead_id, is_active=True)
    
    # Check if the current user is the assigned agent or a superuser
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agent_profile') and 
             request.user.agent_profile == lead.assigned_to)):
        messages.error(request, "You don't have permission to update this lead.")
        return redirect('sales_hub:dashboard')
    
    if request.method == 'POST':
        form = LeadUpdateForm(request.POST, instance=lead)
        if form.is_valid():
            updated_lead = form.save(commit=False)
            
            # If status is changed to closed_won or closed_lost, update the close date
            if 'status' in form.changed_data and form.cleaned_data['status'] in ['closed_won', 'closed_lost']:
                updated_lead.expected_close_date = timezone.now().date()
            
            updated_lead.save()
            
            # Create an interaction record
            Interaction.objects.create(
                customer=lead.customer,
                agent=request.user.agent_profile,
                interaction_type='meeting',
                notes=f"Lead status updated to '{updated_lead.get_status_display()}'. {form.cleaned_data.get('notes', '')}",
                is_completed=True
            )
            
            messages.success(request, f"Lead for {lead.customer.name} has been updated successfully.")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status': updated_lead.get_status_display(),
                    'lead_type': updated_lead.get_lead_type_display(),
                    'updated_at': updated_lead.updated_at.strftime('%b %d, %Y %H:%M')
                })
            
            return redirect('sales_hub:dashboard')
    else:
        form = LeadUpdateForm(instance=lead)
    
    context = {
        'form': form,
        'lead': lead,
        'active_tab': 'leads',
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'html': render_to_string('sales_hub/includes/lead_update_form.html', context, request=request)
        })
    
    return render(request, 'sales_hub/update_lead.html', context)


@login_required
def customer_feedback(request, customer_id):
    """View and add feedback for a customer."""
    customer = get_object_or_404(Customer, id=customer_id, is_active=True)
    
    # Check if the current user is the assigned agent or a superuser
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agent_profile') and 
             request.user.agent_profile == customer.assigned_agent)):
        messages.error(request, "You don't have permission to view this customer's feedback.")
        return redirect('sales_hub:dashboard')
    
    feedback_list = Feedback.objects.filter(customer=customer).order_by('-created_at')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.customer = customer
            feedback.agent = request.user.agent_profile
            feedback.save()
            
            messages.success(request, 'Feedback has been added successfully.')
            return redirect('sales_hub:customer_feedback', customer_id=customer.id)
    else:
        form = FeedbackForm()
    
    # Calculate average rating
    avg_rating = feedback_list.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    context = {
        'customer': customer,
        'feedback_list': feedback_list,
        'form': form,
        'avg_rating': round(avg_rating, 1),
        'active_tab': 'customers',
    }
    
    return render(request, 'sales_hub/customer_feedback.html', context)


@login_required
def add_interaction(request, customer_id):
    """Add a new customer interaction."""
    customer = get_object_or_404(Customer, id=customer_id, is_active=True)
    
    # Check if the current user is the assigned agent or a superuser
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agent_profile') and 
             request.user.agent_profile == customer.assigned_agent)):
        messages.error(request, "You don't have permission to add interactions for this customer.")
        return redirect('sales_hub:dashboard')
    
    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.customer = customer
            interaction.agent = request.user.agent_profile
            interaction.save()
            
            messages.success(request, 'Interaction has been recorded successfully.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'interaction': {
                        'type': interaction.get_interaction_type_display(),
                        'notes': interaction.notes,
                        'date': interaction.created_at.strftime('%b %d, %Y %H:%M'),
                        'agent': str(interaction.agent)
                    }
                })
            
            return redirect('sales_hub:customer_detail', customer_id=customer.id)
    else:
        form = InteractionForm()
    
    context = {
        'form': form,
        'customer': customer,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'html': render_to_string('sales_hub/includes/interaction_form.html', context, request=request)
        })
    
    return render(request, 'sales_hub/add_interaction.html', context)


@login_required
def customer_detail(request, customer_id):
    """View customer details, interactions, and related information."""
    customer = get_object_or_404(Customer, id=customer_id, is_active=True)
    
    # Check if the current user is the assigned agent or a superuser
    if not (request.user.is_superuser or 
            (hasattr(request.user, 'agent_profile') and 
             request.user.agent_profile == customer.assigned_agent)):
        messages.error(request, "You don't have permission to view this customer's details.")
        return redirect('sales_hub:dashboard')
    
    # Get related data
    try:
        lead = customer.lead
    except Lead.DoesNotExist:
        lead = None
    
    feedback_list = Feedback.objects.filter(customer=customer).order_by('-created_at')[:5]
    interactions = Interaction.objects.filter(customer=customer).order_by('-created_at')[:10]
    
    # Calculate average rating
    avg_rating = Feedback.objects.filter(customer=customer).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    
    context = {
        'customer': customer,
        'lead': lead,
        'feedback_list': feedback_list,
        'interactions': interactions,
        'avg_rating': round(avg_rating, 1),
        'active_tab': 'customers',
    }
    
    return render(request, 'sales_hub/customer_detail.html', context)


def handler404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'sales_hub/404.html', status=404)


def handler500(request):
    """Custom 500 error handler."""
    return render(request, 'sales_hub/500.html', status=500)


@login_required
def customer_list(request):
    """List all customers with search and filtering options."""
    try:
        agent = request.user.agent_profile
    except Agent.DoesNotExist:
        messages.error(request, "You need to have an agent profile to view customers.")
        return redirect('sales_hub:dashboard')
    
    # Get search query
    search_query = request.GET.get('q', '')
    
    # Start with base queryset
    customers = Customer.objects.filter(is_active=True)
    
    # Apply search if query exists
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by assigned agent if not superuser
    if not request.user.is_superuser:
        customers = customers.filter(assigned_agent=agent)
    
    # Order by most recent first
    customers = customers.order_by('-created_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(customers, 20)  # Show 20 customers per page
    
    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        customers_page = paginator.page(1)
    except EmptyPage:
        customers_page = paginator.page(paginator.num_pages)
    
    context = {
        'customers': customers_page,
        'search_query': search_query,
        'active_tab': 'customers',
    }
    
    return render(request, 'sales_hub/customer_list.html', context)
