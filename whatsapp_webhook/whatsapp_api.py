import requests
import json
from django.conf import settings

def send_whatsapp_message(phone_number, message, message_type='text', **kwargs):
    """
    Send a WhatsApp message using the WhatsApp Business API
    
    Args:
        phone_number (str): The recipient's phone number in international format (e.g., '255712345678')
        message (str): The message content (text or media URL)
        message_type (str): Type of message ('text', 'image', 'document', 'audio', 'video')
        **kwargs: Additional parameters for specific message types
    
    Returns:
        dict: API response
    """
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Format phone number if needed (ensure it's in the correct format)
    if not phone_number.startswith('+'):
        # Assuming Tanzanian numbers by default if no country code is provided
        if not phone_number.startswith('255'):
            phone_number = f'255{phone_number.lstrip('0')}'
    
    recipient = {
        'messaging_product': 'whatsapp',
        'to': phone_number,
    }
    
    # Handle different message types
    if message_type == 'text':
        payload = {
            **recipient,
            'type': 'text',
            'text': {'body': message}
        }
    elif message_type == 'image':
        payload = {
            **recipient,
            'type': 'image',
            'image': {
                'link': message,
                'caption': kwargs.get('caption', '')
            }
        }
    elif message_type == 'document':
        payload = {
            **recipient,
            'type': 'document',
            'document': {
                'link': message,
                'filename': kwargs.get('filename', 'document.pdf'),
                'caption': kwargs.get('caption', '')
            }
        }
    else:
        raise ValueError(f"Unsupported message type: {message_type}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        raise

def send_template_message(phone_number, template_name, language_code='en', components=None):
    """
    Send a WhatsApp template message
    
    Args:
        phone_number (str): The recipient's phone number
        template_name (str): Name of the template to send
        language_code (str): Language code (default: 'en')
        components (list, optional): Components for the template
    
    Returns:
        dict: API response
    """
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Format phone number if needed
    if not phone_number.startswith('+'):
        if not phone_number.startswith('255'):
            phone_number = f'255{phone_number.lstrip('0')}'
    
    payload = {
        'messaging_product': 'whatsapp',
        'to': phone_number,
        'type': 'template',
        'template': {
            'name': template_name,
            'language': {
                'code': language_code
            }
        }
    }
    
    if components:
        payload['template']['components'] = components
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending WhatsApp template message: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        raise
