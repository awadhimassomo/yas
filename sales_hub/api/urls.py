from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .dashboard_views import dashboard_stats, recent_activity

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'leads', views.LeadViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'purchases', views.PurchaseViewSet)
router.register(r'support-requests', views.SupportRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('puk-retrieval/', views.PUKRetrievalView.as_view(), name='puk-retrieval'),
    path('purchase-bundle/', views.BundlePurchaseView.as_view(), name='purchase-bundle'),
    
    # Additional API endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('recent-activity/', recent_activity, name='recent-activity'),
]
