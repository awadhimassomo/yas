from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import hmac
import hashlib
from django.conf import settings

# WhatsApp Business API credentials (should be in settings.py)
WHATSAPP_VERIFY_TOKEN = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'your_verify_token_here')
WHATSAPP_APP_SECRET = getattr(settings, 'WHATSAPP_APP_SECRET', 'your_app_secret_here')

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def whatsapp_webhook(request):
    """
    Handles incoming WhatsApp webhook events
    """
    if request.method == 'GET':
        # Verify webhook
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('Verification token mismatch', status=403)
    
    # Handle POST request (incoming messages)
    try:
        # Verify request signature
        signature = request.headers.get('X-Hub-Signature-256', '')
        if not verify_signature(request.body, signature):
            return HttpResponse('Invalid signature', status=401)
        
        # Process the webhook event
        data = json.loads(request.body)
        process_whatsapp_event(data)
        
        return JsonResponse({'status': 'ok'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def verify_signature(payload, signature):
    """Verify the signature of the webhook request"""
    if not WHATSAPP_APP_SECRET:
        return True  # Skip verification if no secret is set
        
    # Create a hash using the payload and your app secret
    hash_object = hmac.new(
        WHATSAPP_APP_SECRET.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    )
    expected_signature = f"sha256={hash_object.hexdigest()}"
    
    # Compare the generated signature with the one in the request
    return hmac.compare_digest(expected_signature, signature)

def process_whatsapp_event(data):
    """Process incoming WhatsApp webhook events"""
    try:
        # Handle different types of webhook events
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Handle message events
                if 'messages' in value:
                    for message in value['messages']:
                        handle_message(message, value['metadata']['phone_number_id'])
                
                # Handle status updates
                elif 'statuses' in value:
                    for status in value['statuses']:
                        handle_status_update(status)
    except Exception as e:
        # Log the error
        print(f"Error processing WhatsApp event: {str(e)}")

def handle_message(message, phone_number_id):
    """Handle incoming WhatsApp messages"""
    # Extract message details
    message_type = message.get('type')
    from_number = message['from']
    message_id = message['id']
    
    # Handle different message types
    if message_type == 'text':
        text = message['text']['body']
        print(f"Received text message from {from_number}: {text}")
        
        # TODO: Add your message processing logic here
        # You can send a reply using the WhatsApp Business API
        
    elif message_type == 'image':
        image = message['image']
        print(f"Received image from {from_number}")
        # Handle image message
        
    # Add more message type handlers as needed

def handle_status_update(status):
    """Handle message status updates"""
    message_id = status['id']
    status = status['status']
    print(f"Message {message_id} status updated to: {status}")
    
    # TODO: Update message status in your database
