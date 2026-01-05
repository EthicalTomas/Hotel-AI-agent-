"""
Email Integration Module

Handles incoming email monitoring (IMAP) and outgoing email responses (SMTP)
for the hotel's customer service.
"""

import os
import logging
import imaplib
import smtplib
import email
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailHandler:
    """Handler for email monitoring and responses"""
    
    def __init__(self):
        """Initialize email handler with IMAP and SMTP configuration"""
        self.email_address = os.getenv('HOTEL_EMAIL_ADDRESS')
        self.email_password = os.getenv('HOTEL_EMAIL_PASSWORD')
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = int(os.getenv('IMAP_PORT', 993))
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        if not all([self.email_address, self.email_password]):
            logger.error("Missing email configuration in environment variables")
            raise ValueError("Email credentials not properly configured")
        
        logger.info("Email handler initialized successfully")
    
    def connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Connect to IMAP server for reading emails
        
        Returns:
            IMAP connection object or None if failed
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            logger.info("Successfully connected to IMAP server")
            return mail
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error connecting to IMAP server: {str(e)}")
            return None
    
    def fetch_unread_emails(self, mailbox: str = 'INBOX') -> List[Dict]:
        """
        Fetch unread emails from the specified mailbox
        
        Args:
            mailbox: Name of the mailbox to check (default: 'INBOX')
            
        Returns:
            List of dictionaries containing email data
        """
        mail = self.connect_imap()
        if not mail:
            return []
        
        unread_emails = []
        
        try:
            # Select the mailbox
            mail.select(mailbox)
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK' or not messages[0]:
                logger.info("No unread emails found")
                return []
            
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")
            
            for email_id in email_ids:
                try:
                    # Fetch the email
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if status != 'OK':
                        continue
                    
                    # Parse the email
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    email_data = self._parse_email(email_message, email_id.decode())
                    
                    if email_data:
                        unread_emails.append(email_data)
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_id}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error fetching unread emails: {str(e)}")
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
        
        return unread_emails
    
    def _parse_email(self, email_message, email_id: str) -> Optional[Dict]:
        """
        Parse email message and extract relevant information
        
        Args:
            email_message: email.message.Message object
            email_id: Email ID string
            
        Returns:
            Dictionary with email data or None if parsing failed
        """
        try:
            # Decode subject
            subject = self._decode_header_value(email_message['Subject'])
            
            # Get sender
            from_addr = email_message.get('From', '')
            
            # Get date
            date_str = email_message.get('Date', '')
            
            # Extract email body
            body = self._get_email_body(email_message)
            
            return {
                'id': email_id,
                'from': from_addr,
                'subject': subject,
                'date': date_str,
                'body': body,
                'message_id': email_message.get('Message-ID', '')
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return None
    
    def _decode_header_value(self, header_value: str) -> str:
        """Decode email header value"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        decoded_str = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_str += part
        
        return decoded_str
    
    def _get_email_body(self, email_message) -> str:
        """Extract the body text from an email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                # Look for text/plain or text/html parts
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
                    except:
                        pass
                elif content_type == 'text/html' and not body and 'attachment' not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode(errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body.strip()
    
    def send_email(self, to_address: str, subject: str, body: str, 
                   reply_to_message_id: Optional[str] = None) -> Dict:
        """
        Send an email response
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Email body text
            reply_to_message_id: Optional Message-ID to reply to (for threading)
            
        Returns:
            Dictionary with success status and any error messages
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            # Add In-Reply-To and References headers for threading
            if reply_to_message_id:
                msg['In-Reply-To'] = reply_to_message_id
                msg['References'] = reply_to_message_id
            
            # Add body
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_address}")
            
            return {
                'success': True,
                'to': to_address,
                'subject': subject
            }
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return {
                'success': False,
                'error': 'Email authentication failed',
                'details': str(e)
            }
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to send email',
                'details': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error',
                'details': str(e)
            }
    
    def mark_as_read(self, email_id: str, mailbox: str = 'INBOX') -> bool:
        """
        Mark an email as read
        
        Args:
            email_id: ID of the email to mark as read
            mailbox: Mailbox containing the email
            
        Returns:
            True if successful, False otherwise
        """
        mail = self.connect_imap()
        if not mail:
            return False
        
        try:
            mail.select(mailbox)
            mail.store(email_id.encode(), '+FLAGS', '\\Seen')
            logger.info(f"Marked email {email_id} as read")
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
