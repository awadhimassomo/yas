# Import views to make them available when importing from the api package
from .views import (
    CustomerViewSet, InteractionViewSet, LeadViewSet,
    ProductViewSet, PurchaseViewSet, SupportRequestViewSet,
    PUKRetrievalView, BundlePurchaseView
)
from .dashboard_views import dashboard_stats, recent_activity

__all__ = [
    'CustomerViewSet', 'InteractionViewSet', 'LeadViewSet',
    'ProductViewSet', 'PurchaseViewSet', 'SupportRequestViewSet',
    'PUKRetrievalView', 'BundlePurchaseView',
    'dashboard_stats', 'recent_activity'
]
