from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'sales_hub'

urlpatterns = [
    # Dashboard and main views
    path('', login_required(views.dashboard), name='dashboard'),
    
    # Customer-related URLs
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
