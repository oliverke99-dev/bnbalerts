from enum import Enum
from datetime import datetime
from typing import Optional, Annotated, Any
from pydantic import BaseModel, Field, BeforeValidator
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class NotificationType(str, Enum):
    """Enum for notification delivery channels"""
    SMS = "sms"
    EMAIL = "email"


class NotificationStatus(str, Enum):
    """Enum for notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class NotificationBase(BaseModel):
    """Base schema with shared notification fields"""
    user_id: str
    watch_id: str
    type: NotificationType
    destination: str  # Phone number or Email
    message: str
    deep_link: Optional[str] = None


class NotificationCreate(BaseModel):
    """Schema for internal creation of a notification"""
    user_id: str
    watch_id: str
    type: NotificationType
    destination: str  # Phone number or Email
    message: str
    deep_link: Optional[str] = None


class NotificationInDB(BaseModel):
    """Schema for MongoDB storage"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str
    watch_id: str
    type: NotificationType
    destination: str
    message: str
    deep_link: Optional[str] = None
    status: NotificationStatus = NotificationStatus.PENDING
    provider_id: Optional[str] = None  # e.g., Twilio SID
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationResponse(BaseModel):
    """Schema for API responses"""
    id: str
    watch_id: str
    type: NotificationType
    status: NotificationStatus
    message: str
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NotificationPreferences(BaseModel):
    """Schema for user notification preferences"""
    emailEnabled: bool = True
    smsEnabled: bool = True
    phoneNumber: Optional[str] = None


class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating user notification preferences"""
    smsEnabled: Optional[bool] = None
    emailEnabled: Optional[bool] = None