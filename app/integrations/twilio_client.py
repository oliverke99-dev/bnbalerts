from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def send_sms(to: str, message: str) -> bool:
    """
    Send an SMS message using Twilio.
    
    Args:
        to: Recipient phone number in E.164 format (e.g., +15551234567)
        message: Message text to send (max 1600 characters for SMS)
        
    Returns:
        bool: True if message sent successfully or in dev mode, False on error
        
    Raises:
        No exceptions raised - errors are logged and False is returned
        
    Note:
        In development mode (when Twilio credentials are not configured),
        the function logs the message instead of sending it and returns True.
    """
    # Check if Twilio credentials are configured
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
        logger.warning(f"Twilio not configured. Would send SMS to {to}: {message}")
        # In development/testing without Twilio, log the OTP instead of failing
        logger.info(f"[DEV MODE] OTP for {to}: {message}")
        return True
    
    try:
        client: Client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        sms_message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to
        )
        
        logger.info(f"SMS sent successfully to {to}. SID: {sms_message.sid}")
        return True
        
    except TwilioRestException as e:
        logger.error(f"Twilio API error sending SMS to {to}: {e.code} - {e.msg}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending SMS to {to}: {str(e)}", exc_info=True)
        return False