"""
Email notification providers.
Includes MockEmailProvider for testing and optional SendGrid implementation.
"""

import logging
from typing import Optional

from app.services.notification.base import NotificationProvider

logger = logging.getLogger(__name__)


class MockEmailProvider(NotificationProvider):
    """
    Mock email provider for testing and development.
    
    This provider logs email content instead of actually sending emails.
    Useful for development and testing without requiring external email services.
    """
    
    def send(
        self,
        destination: str,
        message: str,
        subject: Optional[str] = None
    ) -> bool:
        """
        Mock send email by logging the content.
        
        Args:
            destination: Email address to send to
            message: Email body content
            subject: Email subject line
            
        Returns:
            bool: Always returns True (simulated success)
        """
        logger.info(
            f"[MOCK EMAIL] Sending email:\n"
            f"  To: {destination}\n"
            f"  Subject: {subject or '(No Subject)'}\n"
            f"  Body: {message}"
        )
        return True


# Optional: SendGrid Provider skeleton for future implementation
# Uncomment and implement when ready to use SendGrid
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridProvider(NotificationProvider):
    '''
    SendGrid email provider for production use.
    
    Requires SENDGRID_API_KEY environment variable to be set.
    '''
    
    def __init__(self, api_key: str, from_email: str):
        '''
        Initialize SendGrid provider.
        
        Args:
            api_key: SendGrid API key
            from_email: Default sender email address
        '''
        self.client = SendGridAPIClient(api_key)
        self.from_email = from_email
    
    def send(
        self,
        destination: str,
        message: str,
        subject: Optional[str] = None
    ) -> bool:
        '''
        Send email via SendGrid.
        
        Args:
            destination: Email address to send to
            message: Email body content (supports HTML)
            subject: Email subject line
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        '''
        try:
            mail = Mail(
                from_email=self.from_email,
                to_emails=destination,
                subject=subject or "Notification",
                html_content=message
            )
            
            response = self.client.send(mail)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {destination}")
                return True
            else:
                logger.error(
                    f"Failed to send email to {destination}. "
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {destination}: {str(e)}")
            return False
"""