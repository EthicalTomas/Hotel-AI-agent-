"""
Email Monitor Service

Background service that periodically checks for new emails and processes them.
Can be run as a standalone service or scheduled via cron.
"""

import os
import time
import logging
from dotenv import load_dotenv
from ai_agent import HotelAIAgent
from email_handler import EmailHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL = int(os.getenv('EMAIL_CHECK_INTERVAL', 300))  # Default: 5 minutes


def process_emails():
    """Process unread emails and send AI-generated responses"""
    try:
        # Initialize components
        hotel_info_file = os.getenv('HOTEL_INFO_FILE', 'hotel_info.json')
        ai_agent = HotelAIAgent(hotel_info_file)
        email_handler = EmailHandler()
        
        logger.info("Checking for unread emails...")
        
        # Fetch unread emails
        unread_emails = email_handler.fetch_unread_emails()
        
        if not unread_emails:
            logger.info("No unread emails to process")
            return
        
        logger.info(f"Found {len(unread_emails)} unread emails to process")
        
        for email_data in unread_emails:
            try:
                customer_email = email_data['from']
                email_subject = email_data['subject']
                email_body = email_data['body']
                message_id = email_data.get('message_id')
                
                logger.info(f"Processing email from {customer_email}: {email_subject}")
                
                # Generate AI response
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
                    logger.info(f"Email response sent successfully to {customer_email}")
                    # Mark original email as read
                    email_handler.mark_as_read(email_data['id'])
                else:
                    logger.error(f"Failed to send email to {customer_email}: {send_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error processing email from {email_data.get('from', 'unknown')}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in email processing: {str(e)}")


def main():
    """Main loop for email monitoring service"""
    logger.info("Starting Email Monitor Service")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    
    while True:
        try:
            process_emails()
            logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Email monitor service stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {str(e)}")
            logger.info("Continuing after error...")
            time.sleep(60)  # Wait 1 minute before retrying


if __name__ == '__main__':
    main()
