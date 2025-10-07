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
from django.views.generic import RedirectView
from django.views.decorators.csrf import csrf_exempt

# Import the dashboard view from sales_hub
from sales_hub.views import dashboard

# Import WhatsApp webhook view
from whatsapp_webhook.views import whatsapp_webhook

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='public_site:home'), name='logout'),
    
    # Public Site (Customer-facing)
    path('', include('public_site.urls')),  # app_name is defined in public_site/urls.py
    
    # Sales Hub App (Agent Dashboard)
    path('dashboard/', include(('sales_hub.urls', 'sales_hub'))),
    
    # WhatsApp Webhook - Support both /webhook/ and /whatsapp/webhook/ for backward compatibility
    path('webhook/', whatsapp_webhook, name='webhook'),
    path('whatsapp/', include(('whatsapp_webhook.urls', 'whatsapp_webhook'))),
    
    # Webhook messages viewer (for debugging)
    path('webhook-messages/', whatsapp_views.view_webhook_messages, name='webhook_messages'),
    
    # Redirect old root URL to the new dashboard URL
    path('sales/', RedirectView.as_view(url='/dashboard/')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom admin site settings
admin.site.site_header = 'Arusha Bluerock Admin'
admin.site.site_title = 'Arusha Bluerock Administration'
admin.site.index_title = 'Welcome to Arusha Bluerock Admin'
