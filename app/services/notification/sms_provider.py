"""
SMS notification provider using Twilio.
Provides SMS notification capabilities through the Twilio integration.
"""

import logging
from typing import Optional

from app.integrations import twilio_client
from app.services.notification.base import NotificationProvider

logger = logging.getLogger(__name__)


class TwilioSMSProvider(NotificationProvider):
    """
    Twilio SMS notification provider.
    
    Sends SMS notifications using the Twilio API through the twilio_client module.
    Handles errors gracefully and logs all SMS operations.
    """
    
    def __init__(self):
        """
        Initialize the Twilio SMS provider.
        
        The actual Twilio client is initialized within the send_sms function
        in the twilio_client module, which handles configuration checks.
        """
        logger.info("TwilioSMSProvider initialized")
    
    def send(
        self,
        destination: str,
        message: str,
        subject: Optional[str] = None
    ) -> bool:
        """
        Send an SMS notification via Twilio.
        
        Args:
            destination: Phone number to send SMS to (should be in E.164 format)
            message: SMS message body to send
            subject: Not used for SMS (SMS doesn't support subjects)
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        try:
            # Note: subject is ignored for SMS as it doesn't support subjects
            if subject:
                logger.debug(f"Subject '{subject}' provided but will be ignored for SMS")
            
            # Call the Twilio client's send_sms function
            success = twilio_client.send_sms(to=destination, message=message)
            
            if success:
                logger.info(f"SMS sent successfully to {destination}")
            else:
                logger.warning(f"Failed to send SMS to {destination}")
            
            return success
            
        except Exception as e:
            logger.error(
                f"Error in TwilioSMSProvider while sending SMS to {destination}: {str(e)}",
                exc_info=True
            )
            return False