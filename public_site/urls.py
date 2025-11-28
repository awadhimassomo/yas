from django.urls import path
from . import views

app_name = 'public_site'

urlpatterns = [
    # Public homepage
    path('', views.HomePageView.as_view(), name='home'),
    # API endpoint for service requests
    path('api/submit-service-request/', views.submit_service_request, name='submit_service_request'),
]
