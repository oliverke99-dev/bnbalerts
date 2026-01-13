"""
Notification Manager.
Handles routing and dispatching notifications to appropriate providers based on user preferences.
"""

import logging
from typing import Dict, Optional

from app.models.notification import NotificationPreferences, NotificationType
from app.services.notification.base import NotificationProvider

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages notification delivery across multiple channels.
    
    Routes notifications to appropriate providers based on:
    - User preferences (email/SMS enabled)
    - Notification type
    - Provider availability
    """
    
    def __init__(self, providers: Optional[Dict[NotificationType, NotificationProvider]] = None):
        """
        Initialize the notification manager with providers.
        
        Args:
            providers: Dictionary mapping NotificationType to NotificationProvider instances
                      Example: {NotificationType.EMAIL: MockEmailProvider(), 
                               NotificationType.SMS: TwilioSMSProvider()}
        """
        self.providers = providers or {}
        logger.info(f"NotificationManager initialized with providers: {list(self.providers.keys())}")
    
    def register_provider(self, notification_type: NotificationType, provider: NotificationProvider) -> None:
        """
        Register a notification provider for a specific type.
        
        Args:
            notification_type: The type of notification (EMAIL, SMS, etc.)
            provider: The provider instance to handle this notification type
        """
        self.providers[notification_type] = provider
        logger.info(f"Registered provider for {notification_type.value}")
    
    def send_notification(
        self,
        user_prefs: NotificationPreferences,
        notification_type: NotificationType,
        destination: str,
        message: str,
        subject: Optional[str] = None
    ) -> bool:
        """
        Send a notification based on user preferences and type.
        
        Args:
            user_prefs: User's notification preferences
            notification_type: Type of notification to send (EMAIL or SMS)
            destination: Recipient address (email or phone number)
            message: Message content to send
            subject: Optional subject line (primarily for email)
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        # Check if user has enabled this notification type
        if notification_type == NotificationType.EMAIL and not user_prefs.emailEnabled:
            logger.info(f"Email notifications disabled for user, skipping")
            return False
        
        if notification_type == NotificationType.SMS and not user_prefs.smsEnabled:
            logger.info(f"SMS notifications disabled for user, skipping")
            return False
        
        # Check if we have a provider for this notification type
        provider = self.providers.get(notification_type)
        if not provider:
            logger.error(f"No provider registered for notification type: {notification_type.value}")
            return False
        
        # Send the notification
        try:
            logger.info(f"Sending {notification_type.value} notification to {destination}")
            success = provider.send(
                destination=destination,
                message=message,
                subject=subject
            )
            
            if success:
                logger.info(f"Successfully sent {notification_type.value} notification to {destination}")
            else:
                logger.warning(f"Failed to send {notification_type.value} notification to {destination}")
            
            return success
            
        except Exception as e:
            logger.error(
                f"Error sending {notification_type.value} notification to {destination}: {str(e)}",
                exc_info=True
            )
            return False
    
    def send_multi_channel(
        self,
        user_prefs: NotificationPreferences,
        email: Optional[str],
        phone: Optional[str],
        message: str,
        subject: Optional[str] = None
    ) -> Dict[NotificationType, bool]:
        """
        Send notification across multiple channels based on user preferences.
        
        Args:
            user_prefs: User's notification preferences
            email: User's email address (if available)
            phone: User's phone number (if available)
            message: Message content to send
            subject: Optional subject line (for email)
            
        Returns:
            Dict mapping NotificationType to success status for each attempted channel
        """
        results = {}
        
        # Try email if enabled and email is provided
        if user_prefs.emailEnabled and email:
            results[NotificationType.EMAIL] = self.send_notification(
                user_prefs=user_prefs,
                notification_type=NotificationType.EMAIL,
                destination=email,
                message=message,
                subject=subject
            )
        
        # Try SMS if enabled and phone is provided
        if user_prefs.smsEnabled and phone:
            results[NotificationType.SMS] = self.send_notification(
                user_prefs=user_prefs,
                notification_type=NotificationType.SMS,
                destination=phone,
                message=message,
                subject=None  # SMS doesn't use subject
            )
        
        return results