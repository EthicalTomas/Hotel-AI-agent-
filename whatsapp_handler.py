"""
WhatsApp Business Integration Module

Handles incoming and outgoing WhatsApp messages using Twilio's WhatsApp API.
"""

import os
import logging
from typing import Dict, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class WhatsAppHandler:
    """Handler for WhatsApp Business messages via Twilio"""
    
    def __init__(self):
        """Initialize WhatsApp handler with Twilio credentials"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.error("Missing Twilio configuration in environment variables")
            raise ValueError("Twilio credentials not properly configured")
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("WhatsApp handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            raise
    
    def send_message(self, to_number: str, message: str) -> Dict:
        """
        Send a WhatsApp message to a customer
        
        Args:
            to_number: Customer's WhatsApp number in format 'whatsapp:+1234567890'
            message: Message content to send
            
        Returns:
            Dictionary with status and message SID or error
        """
        try:
            # Ensure the number has the whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"WhatsApp message sent successfully. SID: {message_obj.sid}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code if hasattr(e, 'code') else None
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_incoming_message(self, request_form: Dict) -> Optional[Dict]:
        """
        Parse incoming WhatsApp webhook request
        
        Args:
            request_form: Flask request.form or request.values dictionary
            
        Returns:
            Dictionary containing parsed message data or None if invalid
        """
        try:
            message_data = {
                'from': request_form.get('From', ''),
                'to': request_form.get('To', ''),
                'body': request_form.get('Body', ''),
                'message_sid': request_form.get('MessageSid', ''),
                'num_media': int(request_form.get('NumMedia', 0)),
                'profile_name': request_form.get('ProfileName', 'Customer')
            }
            
            # Validate required fields
            if not message_data['from'] or not message_data['body']:
                logger.warning("Incomplete WhatsApp message data received")
                return None
            
            logger.info(f"Parsed WhatsApp message from {message_data['from']}")
            return message_data
            
        except Exception as e:
            logger.error(f"Error parsing WhatsApp message: {str(e)}")
            return None
    
    def validate_webhook(self, request_form: Dict) -> bool:
        """
        Validate that the webhook request is from Twilio
        
        Args:
            request_form: Flask request.form or request.values dictionary
            
        Returns:
            True if valid Twilio webhook, False otherwise
        """
        # Check for required Twilio webhook fields
        required_fields = ['MessageSid', 'From', 'To']
        return all(field in request_form for field in required_fields)
    
    def format_response_for_whatsapp(self, message: str) -> str:
        """
        Format an AI response for WhatsApp (remove excessive formatting, etc.)
        
        Args:
            message: The message to format
            
        Returns:
            WhatsApp-friendly formatted message
        """
        # WhatsApp supports basic markdown, but keep it simple
        # Remove any HTML tags if present
        formatted = message.replace('<br>', '\n').replace('<br/>', '\n')
        
        # Ensure message isn't too long (WhatsApp limit is 4096 characters)
        max_length = 4000  # Leave some buffer
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "\n\n...(message truncated)"
        
        return formatted
