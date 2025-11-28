from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
import json
import logging
from .models import ServiceRequest

logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    """View for the public homepage."""
    template_name = 'public_site/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context


@csrf_exempt
@require_http_methods(["POST"])
def submit_service_request(request):
    """
    API endpoint to receive service requests from the public website.
    """
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Extract data
        phone_number = data.get('phoneNumber', '')
        service_type = data.get('serviceType', '')
        specific_service = data.get('specificService', '')
        timeline = data.get('timeline', 'immediate')
        contact_preference = data.get('contactPreference', 'no')
        lead_score = data.get('score', 0)

        logger.info("Incoming service request: phone=%s, type=%s, specific=%s, timeline=%s, contact_pref=%s, score=%s",
                    phone_number, service_type, specific_service, timeline, contact_preference, lead_score)
        
        # Validate required fields
        if not phone_number or not service_type or not specific_service:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create service request
        service_request = ServiceRequest.objects.create(
            phone_number=phone_number,
            service_type=service_type,
            specific_service=specific_service,
            timeline=timeline,
            contact_preference=contact_preference,
            lead_score=lead_score,
            ip_address=ip_address,
            user_agent=user_agent,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'request_id': service_request.id,
            'message': 'Service request submitted successfully'
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.exception("Error while submitting service request")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
