"""
Hotel AI Agent Main Application

Flask-based web server that handles WhatsApp webhooks and email monitoring
for automated customer service responses.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from ai_agent import HotelAIAgent
from whatsapp_handler import WhatsAppHandler
from email_handler import EmailHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hotel_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
CORS(app)

# Initialize components
try:
    hotel_info_file = os.getenv('HOTEL_INFO_FILE', 'hotel_info.json')
    ai_agent = HotelAIAgent(hotel_info_file)
    whatsapp_handler = WhatsAppHandler()
    email_handler = EmailHandler()
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    raise


# Store conversation history (in production, use a database)
conversation_history = {}


@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'active',
        'service': 'Hotel AI Agent',
        'version': '1.0.0',
        'endpoints': {
            'whatsapp_webhook': '/webhook/whatsapp',
            'email_check': '/check-emails',
            'health': '/'
        }
    })


@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook endpoint for incoming WhatsApp messages from Twilio
    """
    try:
        # Parse incoming message
        message_data = whatsapp_handler.parse_incoming_message(request.values)
        
        if not message_data:
            logger.warning("Invalid WhatsApp message received")
            return jsonify({'error': 'Invalid message'}), 400
        
        customer_number = message_data['from']
        customer_message = message_data['body']
        customer_name = message_data.get('profile_name', 'Customer')
        
        logger.info(f"Received WhatsApp from {customer_name} ({customer_number}): {customer_message}")
        
        # Get or create conversation history for this customer
        if customer_number not in conversation_history:
            conversation_history[customer_number] = []
        
        # Limit history to last 10 messages to manage context
        if len(conversation_history[customer_number]) > 10:
            conversation_history[customer_number] = conversation_history[customer_number][-10:]
        
        # Generate AI response
        ai_response = ai_agent.generate_response(
            customer_message,
            conversation_history=conversation_history[customer_number]
        )
        
        # Update conversation history
        conversation_history[customer_number].append({
            'role': 'user',
            'content': customer_message
        })
        conversation_history[customer_number].append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Format and send response via WhatsApp
        formatted_response = whatsapp_handler.format_response_for_whatsapp(ai_response)
        send_result = whatsapp_handler.send_message(customer_number, formatted_response)
        
        if send_result['success']:
            logger.info(f"Response sent successfully to {customer_number}")
            return jsonify({'status': 'success', 'message_sid': send_result['message_sid']}), 200
        else:
            logger.error(f"Failed to send WhatsApp response: {send_result.get('error')}")
            return jsonify({'status': 'error', 'error': send_result.get('error')}), 500
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/check-emails', methods=['GET', 'POST'])
def check_emails():
    """
    Endpoint to manually trigger email checking and responses
    Can be called via cron job or manually
    """
    try:
        logger.info("Checking for unread emails...")
        
        # Fetch unread emails
        unread_emails = email_handler.fetch_unread_emails()
        
        if not unread_emails:
            logger.info("No unread emails to process")
            return jsonify({
                'status': 'success',
                'emails_processed': 0,
                'message': 'No unread emails'
            }), 200
        
        processed_count = 0
        errors = []
        
        for email_data in unread_emails:
            try:
                customer_email = email_data['from']
                email_subject = email_data['subject']
                email_body = email_data['body']
                message_id = email_data.get('message_id')
                
                logger.info(f"Processing email from {customer_email}: {email_subject}")
                
                # Generate AI response
                # Create context that includes the subject
                customer_query = f"Subject: {email_subject}\n\n{email_body}"
                ai_response = ai_agent.generate_response(customer_query)
                
                # Prepare response subject
                response_subject = f"Re: {email_subject}" if not email_subject.startswith('Re:') else email_subject
                
                # Format response with greeting and signature
                formatted_response = f"""Dear Customer,

Thank you for contacting {ai_agent.hotel_info.get('name', 'our hotel')}.

{ai_response}

If you have any additional questions or would like to proceed with a booking, please don't hesitate to reach out.

Best regards,
{ai_agent.hotel_info.get('name', 'Grand Hotel Paradise')} Team
{ai_agent.hotel_info.get('phone', '')}
{ai_agent.hotel_info.get('email', '')}
{ai_agent.hotel_info.get('website', '')}
"""
                
                # Send response
                send_result = email_handler.send_email(
                    to_address=customer_email,
                    subject=response_subject,
                    body=formatted_response,
                    reply_to_message_id=message_id
                )
                
                if send_result['success']:
                    logger.info(f"Email response sent to {customer_email}")
                    # Mark original email as read
                    email_handler.mark_as_read(email_data['id'])
                    processed_count += 1
                else:
                    error_msg = f"Failed to send email to {customer_email}: {send_result.get('error')}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Error processing email from {email_data.get('from', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue
        
        response_data = {
            'status': 'success',
            'emails_processed': processed_count,
            'total_emails': len(unread_emails)
        }
        
        if errors:
            response_data['errors'] = errors
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error checking emails: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/test-ai', methods=['POST'])
def test_ai():
    """
    Test endpoint for AI responses (for development/testing)
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        response = ai_agent.generate_response(message)
        
        return jsonify({
            'status': 'success',
            'query': message,
            'response': response
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Hotel AI Agent server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
