from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import hmac
import hashlib
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Get WhatsApp credentials from settings
WHATSAPP_VERIFY_TOKEN = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'yasbluerock_webhook_2024')
WHATSAPP_APP_SECRET = getattr(settings, 'WHATSAPP_APP_SECRET', '')

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def whatsapp_webhook(request):
    """
    Handles incoming WhatsApp webhook events
    """
    logger.info(f"[{datetime.now()}] Received {request.method} request to webhook endpoint")
    
    # Handle GET request for webhook verification
    if request.method == 'GET':
        return handle_webhook_verification(request)
    
    # Handle POST request (incoming messages)
    return handle_webhook_event(request)

def handle_webhook_verification(request):
    """Handle webhook verification request"""
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')
    
    logger.info(f"Webhook verification attempt - Mode: {mode}, Token: {token}")
    
    if mode == 'subscribe' and token == WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return HttpResponse(challenge, status=200)
    
    logger.warning(f"Webhook verification failed. Expected token: {WHATSAPP_VERIFY_TOKEN}")
    return HttpResponseForbidden('Verification token mismatch')

def handle_webhook_event(request):
    """Process incoming webhook events"""
    try:
        # Verify request signature if app secret is set
        if WHATSAPP_APP_SECRET:
            signature = request.headers.get('X-Hub-Signature-256', '')
            if not verify_signature(request.body, signature):
                logger.error("Invalid webhook signature")
                return HttpResponse('Invalid signature', status=401)
        
        # Parse and process the webhook event
        try:
            data = json.loads(request.body)
            logger.debug(f"Webhook payload: {json.dumps(data, indent=2)}")
            
            # Process the webhook event
            process_whatsapp_event(data)
            
            # Always return 200 OK to acknowledge receipt
            return JsonResponse({'status': 'ok'}, status=200)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    except Exception as e:
        logger.exception("Error processing webhook request")
        return JsonResponse(
            {'error': 'Internal server error'}, 
            status=500
        )

def verify_signature(payload, signature):
    """
    Verify the signature of the webhook request
    
    Args:
        payload: Raw request body (bytes)
        signature: X-Hub-Signature-256 header value
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not WHATSAPP_APP_SECRET:
        logger.warning("No app secret set, skipping signature verification")
        return True  # Skip verification if no secret is set
    
    if not signature:
        logger.error("No signature provided in request")
        return False
    
    try:
        # Create a hash using the payload and your app secret
        hash_object = hmac.new(
            WHATSAPP_APP_SECRET.encode('utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        )
        expected_signature = f"sha256={hash_object.hexdigest()}"
        
        # Compare the generated signature with the one in the request
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            logger.warning(f"Invalid signature. Expected: {expected_signature}, Got: {signature}")
            
        return is_valid
    except Exception as e:
        logger.exception("Error verifying signature")
        return False

def process_whatsapp_event(data):
    """
    Process incoming WhatsApp webhook events
    
    Args:
        data (dict): Parsed JSON data from the webhook
    """
    try:
        logger.info("Processing WhatsApp webhook event")
        
        # Check if this is a test webhook
        if data.get('object') != 'whatsapp_business_account':
            logger.warning(f"Unexpected webhook object type: {data.get('object')}")
            return
        
        # Process each entry in the webhook
        for entry in data.get('entry', []):
            entry_id = entry.get('id', 'unknown')
            logger.debug(f"Processing entry {entry_id}")
            
            for change in entry.get('changes', []):
                value = change.get('value', {})
                field = change.get('field')
                
                logger.info(f"Processing change in field: {field}")
                
                # Handle message events
                if 'messages' in value:
                    phone_number_id = value.get('metadata', {}).get('phone_number_id', 'unknown')
                    logger.info(f"Processing {len(value['messages'])} messages for phone number ID: {phone_number_id}")
                    
                    for message in value['messages']:
                        message_id = message.get('id', 'unknown')
                        logger.debug(f"Processing message {message_id}")
                        handle_message(message, phone_number_id)
                
                # Handle status updates
                elif 'statuses' in value:
                    logger.info(f"Processing {len(value['statuses'])} status updates")
                    for status in value['statuses']:
                        handle_status_update(status)
                
                else:
                    logger.info(f"Unhandled webhook change type in field: {field}")
                    logger.debug(f"Change data: {json.dumps(change, indent=2)}")
                    
    except Exception as e:
        logger.exception("Error processing WhatsApp event")

def handle_message(message, phone_number_id):
    """
    Handle incoming WhatsApp messages
    
    Args:
        message (dict): The message data from WhatsApp
        phone_number_id (str): The phone number ID that received the message
    """
    try:
        # Extract message details
        message_type = message.get('type')
        from_number = message.get('from', 'unknown')
        message_id = message.get('id', 'unknown')
        timestamp = message.get('timestamp', 0)
        
        logger.info(
            f"New {message_type} message from {from_number} "
            f"(ID: {message_id}, Timestamp: {timestamp})"
        )
        
        # Handle different message types
        if message_type == 'text':
            text = message.get('text', {}).get('body', '')
            logger.info(f"Text message content: {text[:100]}")
            
            # TODO: Add your message processing logic here
            # Example: process_text_message(from_number, text, phone_number_id)
            
        elif message_type == 'image':
            image = message.get('image', {})
            image_id = image.get('id')
            mime_type = image.get('mime_type', 'image/jpeg')
            logger.info(f"Received {mime_type} image (ID: {image_id})")
            
            # TODO: Handle image message
            # Example: process_image_message(from_number, image_id, mime_type, phone_number_id)
            
        elif message_type == 'document':
            document = message.get('document', {})
            filename = document.get('filename', 'document')
            mime_type = document.get('mime_type', 'application/octet-stream')
            logger.info(f"Received document: {filename} ({mime_type})")
            
        else:
            logger.info(f"Unhandled message type: {message_type}")
            logger.debug(f"Message data: {json.dumps(message, indent=2)}")
            
    except Exception as e:
        logger.exception(f"Error processing {message_type} message")

def handle_status_update(status):
    """
    Handle message status updates
    
    Args:
        status (dict): Status update data from WhatsApp
    """
    try:
        message_id = status.get('id', 'unknown')
        status_type = status.get('status')
        recipient_id = status.get('recipient_id')
        timestamp = status.get('timestamp', 0)
        
        logger.info(
            f"Status update - Message ID: {message_id}, "
            f"Status: {status_type}, "
            f"Recipient: {recipient_id}, "
            f"Timestamp: {timestamp}"
        )
        
        # Handle different status types
        if status_type == 'sent':
            # Message was sent from WhatsApp
            logger.debug(f"Message {message_id} was sent to WhatsApp")
            
        elif status_type == 'delivered':
            # Message was delivered to the recipient's device
            logger.debug(f"Message {message_id} was delivered to the recipient")
            
        elif status_type == 'read':
            # Message was read by the recipient
            logger.debug(f"Message {message_id} was read by the recipient")
            
        elif status_type == 'failed':
            # Message delivery failed
            error = status.get('errors', [{}])[0]
            error_code = error.get('code')
            error_title = error.get('title', 'Unknown error')
            logger.error(
                f"Message {message_id} failed to send. "
                f"Error {error_code}: {error_title}"
            )
        
        # TODO: Update message status in your database
        # Example: update_message_status(message_id, status_type, timestamp)
        
    except Exception as e:
        logger.exception("Error processing status update")
