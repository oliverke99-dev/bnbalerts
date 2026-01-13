"""
FastAPI dependency injection functions.
Provides shared dependencies for API endpoints.
"""

from app.models.notification import NotificationType
from app.services.notification import (
    NotificationManager,
    MockEmailProvider,
    TwilioSMSProvider,
)


def get_notification_manager() -> NotificationManager:
    """
    Dependency that provides a configured NotificationManager instance.
    
    Initializes the notification manager with:
    - MockEmailProvider for email notifications (for development/testing)
    - TwilioSMSProvider for SMS notifications (uses Twilio API)
    
    Returns:
        NotificationManager: Configured notification manager with email and SMS providers
    """
    # Initialize providers
    email_provider = MockEmailProvider()
    sms_provider = TwilioSMSProvider()
    
    # Create notification manager with provider mappings
    manager = NotificationManager(
        providers={
            NotificationType.EMAIL: email_provider,
            NotificationType.SMS: sms_provider,
        }
    )
    
    return manager