"""
Pydantic Models
"""
from app.models.user import (
    UserCreate,
    UserInDB,
    UserResponse,
    VerifyPhoneRequest,
    LoginRequest,
    LoginResponse,
    SignupResponse,
    VerifyPhoneResponse
)

from app.models.property import (
    PropertyBase,
    PropertyDiscoveryRequest,
    PropertyResult,
    PropertyDiscoveryResponse,
    PropertyCreate,
    PropertyUpdate,
    PropertyInDB,
    PropertyResponse
)

from app.models.watch import (
    WatchCreate,
    WatchUpdate,
    WatchInDB,
    WatchResponse
)

from app.models.notification import (
    NotificationType,
    NotificationStatus,
    NotificationBase,
    NotificationCreate,
    NotificationInDB,
    NotificationResponse,
    NotificationPreferences,
    NotificationPreferencesUpdate
)

from app.models.scan_log import (
    ScanStatus,
    ScanResult,
    ScanLogBase,
    ScanLogCreate,
    ScanLogInDB,
    ScanLogResponse
)

__all__ = [
    # User models
    "UserCreate",
    "UserInDB",
    "UserResponse",
    "VerifyPhoneRequest",
    "LoginRequest",
    "LoginResponse",
    "SignupResponse",
    "VerifyPhoneResponse",
    # Property models
    "PropertyBase",
    "PropertyDiscoveryRequest",
    "PropertyResult",
    "PropertyDiscoveryResponse",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyInDB",
    "PropertyResponse",
    # Watch models
    "WatchCreate",
    "WatchUpdate",
    "WatchInDB",
    "WatchResponse",
    # Notification models
    "NotificationType",
    "NotificationStatus",
    "NotificationBase",
    "NotificationCreate",
    "NotificationInDB",
    "NotificationResponse",
    "NotificationPreferences",
    "NotificationPreferencesUpdate",
    # Scan Log models
    "ScanStatus",
    "ScanResult",
    "ScanLogBase",
    "ScanLogCreate",
    "ScanLogInDB",
    "ScanLogResponse",
]