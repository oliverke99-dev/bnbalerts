from pydantic import BaseModel, EmailStr, Field, field_validator, BeforeValidator
from typing import Optional, Annotated, Any
from datetime import datetime
import re
from bson import ObjectId
from app.models.notification import NotificationPreferences


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number is in E.164 format"""
        # E.164 format: +[country code][number] (e.g., +15551234567)
        pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(pattern, v):
            raise ValueError('Phone must be in E.164 format (e.g., +15551234567)')
        return v


class UserInDB(BaseModel):
    """Schema for user document in MongoDB"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    email: EmailStr
    passwordHash: str
    phone: str
    phoneVerified: bool = False
    phoneOtp: Optional[str] = None
    phoneOtpExpiry: Optional[datetime] = None
    name: Optional[str] = None
    tier: str = "free"
    smsEnabled: bool = True
    emailEnabled: bool = False
    notification_preferences: NotificationPreferences = Field(
        default_factory=lambda: NotificationPreferences(emailEnabled=True, smsEnabled=True)
    )
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserResponse(BaseModel):
    """Schema for user API responses (safe fields only)"""
    id: str
    email: EmailStr
    phone: str
    phoneVerified: bool
    name: Optional[str] = None
    tier: str = "free"
    smsEnabled: bool = True
    emailEnabled: bool = False
    
    class Config:
        populate_by_name = True


class VerifyPhoneRequest(BaseModel):
    """Schema for phone verification request"""
    userId: str
    code: str = Field(..., min_length=6, max_length=6)


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    token: str
    user: UserResponse


class SignupResponse(BaseModel):
    """Schema for signup response"""
    user: UserResponse
    message: str


class VerifyPhoneResponse(BaseModel):
    """Schema for phone verification response"""
    success: bool
    token: str


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Schema for forgot password response"""
    message: str
    email: str


class ResetPasswordRequest(BaseModel):
    """Schema for reset password request"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    newPassword: str = Field(..., min_length=8)


class ResetPasswordResponse(BaseModel):
    """Schema for reset password response"""
    success: bool
    message: str