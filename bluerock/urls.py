"""
URL configuration for bluerock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# Import the dashboard view from sales_hub
from sales_hub.views import dashboard

# Import WhatsApp webhook view
from whatsapp_webhook import views as whatsapp_views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Sales Hub App
    path('', include('sales_hub.urls')),
    
    # WhatsApp Webhook
    path('whatsapp/', include('whatsapp_webhook.urls')),
    
    # Set dashboard as the root URL
    path('', dashboard, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom admin site settings
admin.site.site_header = 'Arusha Bluerock Admin'
admin.site.site_title = 'Arusha Bluerock Administration'
admin.site.index_title = 'Welcome to Arusha Bluerock Admin'
