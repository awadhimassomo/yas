from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings

class CustomLogoutView(BaseLogoutView):
    """
    Custom logout view that redirects to the public site home page.
    Overrides the default logout behavior to skip the logout template.
    """
    next_page = None  # We'll handle the redirect manually

    def dispatch(self, request, *args, **kwargs):
        # Call the parent's dispatch to handle the logout
        response = super().dispatch(request, *args, **kwargs)
        # Redirect to the public site home page
        return redirect(settings.LOGOUT_REDIRECT_URL or '/')
