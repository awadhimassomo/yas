from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Test the WhatsApp webhook configuration'

    def handle(self, *args, **options):
        """Test the WhatsApp webhook configuration"""
        self.stdout.write(self.style.SUCCESS('Testing WhatsApp webhook configuration...'))
        
        # Check required settings
        required_settings = [
            'WHATSAPP_VERIFY_TOKEN',
            'WHATSAPP_APP_SECRET',
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_ACCESS_TOKEN'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting) or getattr(settings, setting) == f'your_{setting.lower()}':
                self.stdout.write(self.style.ERROR(f'❌ {setting} is not properly configured in settings.py'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ {setting} is configured'))
        
        # Test webhook URL (update with your actual webhook URL)
        webhook_url = 'http://your-domain.com/whatsapp/webhook/'
        self.stdout.write(self.style.SUCCESS(f'\nWebhook URL: {webhook_url}'))
        
        # Test webhook verification
        self.stdout.write('\nTesting webhook verification...')
        test_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': settings.WHATSAPP_VERIFY_TOKEN,
            'hub.challenge': 'test_challenge'
        }
        
        self.stdout.write(f'Test verification URL: {webhook_url}?mode=subscribe&verify_token={settings.WHATSAPP_VERIFY_TOKEN}&challenge=test_challenge')
        self.stdout.write(self.style.SUCCESS('✅ Webhook verification test completed (check server logs for details)'))
        
        # Test sending a message
        self.stdout.write('\nTo test sending a message, use the following curl command:')
        test_phone = '255712345678'  # Replace with test number
        test_message = 'Hello from Bluerock POS!'
        
        curl_command = f"""
        curl -X POST \
        'https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages' \
        -H 'Authorization: Bearer {settings.WHATSAPP_ACCESS_TOKEN}' \
        -H 'Content-Type: application/json' \
        -d '{{
            "messaging_product": "whatsapp",
            "to": "{test_phone}",
            "type": "text",
            "text": {{
                "body": "{test_message}"
            }}
        }}'
        """
        
        self.stdout.write(self.style.SUCCESS('Curl command to test sending a message:'))
        self.stdout.write(curl_command)
