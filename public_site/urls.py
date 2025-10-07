from django.urls import path
from . import views

app_name = 'public_site'

urlpatterns = [
    # Public homepage
    path('', views.HomePageView.as_view(), name='home'),
]
