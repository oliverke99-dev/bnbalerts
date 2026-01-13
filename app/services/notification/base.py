"""
Base notification provider interface.
Defines the abstract contract that all notification providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional


class NotificationProvider(ABC):
    """
    Abstract base class for notification providers.
    
    All notification providers (Email, SMS, Push, etc.) must inherit from this class
    and implement the send method.
    """
    
    @abstractmethod
    def send(
        self,
        destination: str,
        message: str,
        subject: Optional[str] = None
    ) -> bool:
        """
        Send a notification to the specified destination.
        
        Args:
            destination: The recipient address (email, phone number, etc.)
            message: The message body/content to send
            subject: Optional subject line (primarily for email)
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise
        """
        pass