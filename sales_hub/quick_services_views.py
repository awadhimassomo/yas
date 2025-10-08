from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.utils import timezone

from .models import Customer
from .quick_services import QuickServiceRequest, QuickServiceType

class QuickServiceRequestView(LoginRequiredMixin, CreateView):
    """View for creating a new Quick Service request."""
    model = QuickServiceRequest
    fields = ['service_type', 'notes']
    template_name = 'sales_hub/quick_service_request.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = get_object_or_404(Customer, pk=self.kwargs['customer_id'])
        context['service_types'] = QuickServiceType.choices
        return context
    
    def form_valid(self, form):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_id'])
        form.instance.customer = customer
        form.instance.requested_by = self.request.user
        
        # If the customer has an assigned agent, assign them to the request
        if hasattr(customer, 'assigned_agent'):
            form.instance.assigned_agent = customer.assigned_agent
        
        response = super().form_valid(form)
        messages.success(self.request, f"{form.instance.get_service_type_display()} request created successfully!")
        return response
    
    def get_success_url(self):
        return reverse_lazy('sales_hub:customer_detail', kwargs={'pk': self.kwargs['customer_id']})


class QuickServiceRequestUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating the status of a Quick Service request."""
    model = QuickServiceRequest
    fields = ['status', 'notes', 'assigned_agent']
    template_name = 'sales_hub/quick_service_update.html'
    
    def form_valid(self, form):
        if form.instance.status == 'completed' and not form.instance.completed_at:
            form.instance.completed_at = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, f"{form.instance.get_service_type_display()} request updated successfully!")
        return response
    
    def get_success_url(self):
        return reverse_lazy('sales_hub:quick_service_detail', kwargs={'pk': self.object.pk})


class QuickServiceRequestDetailView(LoginRequiredMixin, DetailView):
    """View for viewing details of a Quick Service request."""
    model = QuickServiceRequest
    context_object_name = 'service_request'
    template_name = 'sales_hub/quick_service_detail.html'


class CustomerQuickServiceHistoryView(LoginRequiredMixin, ListView):
    """View for displaying a customer's Quick Service request history."""
    model = QuickServiceRequest
    context_object_name = 'service_requests'
    template_name = 'sales_hub/customer_quick_services.html'
    paginate_by = 10
    
    def get_queryset(self):
        customer = get_object_or_404(Customer, pk=self.kwargs['customer_id'])
        return QuickServiceRequest.objects.filter(customer=customer).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = get_object_or_404(Customer, pk=self.kwargs['customer_id'])
        return context
