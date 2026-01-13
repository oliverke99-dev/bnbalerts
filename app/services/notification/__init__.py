"""
Notification service package.
Provides notification infrastructure with support for multiple channels (Email, SMS).
"""

from app.services.notification.base import NotificationProvider
from app.services.notification.email_provider import MockEmailProvider
from app.services.notification.sms_provider import TwilioSMSProvider
from app.services.notification.manager import NotificationManager

__all__ = [
    "NotificationProvider",
    "MockEmailProvider",
    "TwilioSMSProvider",
    "NotificationManager",
]