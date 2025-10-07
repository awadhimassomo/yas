from django.shortcuts import render
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    """View for the public homepage."""
    template_name = 'public_site/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context
