from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

from . import views
from .quick_services_views import (
    QuickServiceRequestView, 
    QuickServiceRequestUpdateView,
    QuickServiceRequestDetailView,
    CustomerQuickServiceHistoryView
)

app_name = 'sales_hub'

urlpatterns = [
    # Dashboard and main views
    path('', login_required(views.dashboard), name='dashboard'),
    
    # Users app
    path('users/', include('users.urls', namespace='users')),
    
    # Customer-related URLs
    path('customers/', 
         login_required(views.customer_list), 
         name='customer_list'),
    
    # Quick Services URLs
    path('customers/<int:customer_id>/quick-services/', 
         login_required(CustomerQuickServiceHistoryView.as_view()), 
         name='customer_quick_services'),
    path('customers/<int:customer_id>/quick-services/request/', 
         login_required(QuickServiceRequestView.as_view()), 
         name='quick_service_request'),
    path('quick-services/<int:pk>/', 
         login_required(QuickServiceRequestDetailView.as_view()), 
         name='quick_service_detail'),
    path('quick-services/<int:pk>/update/', 
         login_required(QuickServiceRequestUpdateView.as_view()), 
         name='update_quick_service'),
    path('customers/<int:customer_id>/', 
         login_required(views.customer_detail), 
         name='customer_detail'),
    path('customers/<int:customer_id>/feedback/', 
         login_required(views.customer_feedback), 
         name='customer_feedback'),
    path('customers/<int:customer_id>/interactions/add/', 
         login_required(views.add_interaction), 
         name='add_interaction'),
    
    # Lead-related URLs
    path('leads/<int:lead_id>/update/', 
         login_required(views.update_lead), 
         name='update_lead'),
    
    # API endpoints for AJAX requests
    path('api/leads/<int:lead_id>/update/', 
         login_required(views.update_lead), 
         name='api_update_lead'),
    path('api/customers/<int:customer_id>/interactions/add/', 
         login_required(views.add_interaction), 
         name='api_add_interaction'),
    
    # Error handlers
    path('404/', views.handler404, name='404'),
    path('500/', views.handler500, name='500'),
    
    # Redirect any unknown URLs to the dashboard
    path('<path:path>/', RedirectView.as_view(url='/', permanent=False)),
]
