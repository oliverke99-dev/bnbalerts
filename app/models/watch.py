"""
Watch models for the application.
"""
from datetime import datetime, date, time
from typing import Optional, Annotated, Any
from pydantic import BaseModel, Field, field_validator, BeforeValidator
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class WatchCreate(BaseModel):
    """Schema for creating a new watch."""
    propertyId: str = Field(..., description="Airbnb property ID")
    propertyName: str = Field(..., min_length=1, max_length=500, description="Property name")
    propertyUrl: str = Field(..., description="Airbnb listing URL")
    location: str = Field(..., min_length=1, max_length=200, description="Property location")
    imageUrl: Optional[str] = Field(None, description="Property image URL")
    checkInDate: date = Field(..., description="Check-in date")
    checkOutDate: date = Field(..., description="Check-out date")
    guests: int = Field(..., ge=1, description="Number of guests")
    price: str = Field(..., description="Price per night")
    frequency: str = Field(default="daily", description="Scan frequency: daily, hourly, sniper")
    partialMatch: bool = Field(default=False, description="Accept partial date matches")
    
    @field_validator('checkInDate')
    @classmethod
    def validate_checkin_date(cls, v: date) -> date:
        """Validate that check-in date is today or in the future"""
        if v < date.today():
            raise ValueError('Check-in date must be today or in the future')
        return v
    
    @field_validator('checkOutDate')
    @classmethod
    def validate_checkout_date(cls, v: date, info) -> date:
        """Validate that check-out is after check-in"""
        if 'checkInDate' in info.data and v <= info.data['checkInDate']:
            raise ValueError('Check-out date must be after check-in date')
        return v
    
    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        """Validate frequency is one of the allowed values"""
        allowed = ['daily', 'hourly', 'sniper']
        if v not in allowed:
            raise ValueError(f'Frequency must be one of: {", ".join(allowed)}')
        return v


class WatchUpdate(BaseModel):
    """Schema for updating watch settings."""
    frequency: Optional[str] = Field(None, description="Scan frequency: daily, hourly, sniper")
    status: Optional[str] = Field(None, description="Watch status: active, paused, expired")
    partialMatch: Optional[bool] = Field(None, description="Accept partial date matches")
    
    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        """Validate frequency is one of the allowed values"""
        if v is not None:
            allowed = ['daily', 'hourly', 'sniper']
            if v not in allowed:
                raise ValueError(f'Frequency must be one of: {", ".join(allowed)}')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status is one of the allowed values"""
        if v is not None:
            allowed = ['active', 'paused', 'expired']
            if v not in allowed:
                raise ValueError(f'Status must be one of: {", ".join(allowed)}')
        return v


class WatchInDB(BaseModel):
    """Schema for watch document in MongoDB."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    userId: str = Field(..., description="User ID who owns this watch")
    propertyId: str = Field(..., description="Airbnb property ID")
    propertyName: str = Field(..., description="Property name")
    propertyUrl: str = Field(..., description="Airbnb listing URL")
    location: str = Field(..., description="Property location")
    imageUrl: Optional[str] = Field(None, description="Property image URL")
    checkInDate: date = Field(..., description="Check-in date")
    checkOutDate: date = Field(..., description="Check-out date")
    guests: int = Field(..., description="Number of guests")
    price: str = Field(..., description="Price per night")
    frequency: str = Field(default="daily", description="Scan frequency")
    partialMatch: bool = Field(default=False, description="Accept partial date matches")
    status: str = Field(default="active", description="Watch status")
    lastScannedAt: Optional[datetime] = Field(None, description="Last scan timestamp")
    nextScanAt: Optional[datetime] = Field(None, description="Next scheduled scan")
    expiresAt: datetime = Field(..., description="Auto-expire at check-in date 23:59:59")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class WatchResponse(BaseModel):
    """Schema for watch API responses."""
    id: str
    userId: str
    propertyId: str
    propertyName: str
    propertyUrl: str
    location: str
    imageUrl: Optional[str] = None
    checkInDate: date
    checkOutDate: date
    guests: int
    price: str
    frequency: str
    partialMatch: bool
    status: str
    lastScannedAt: Optional[datetime] = None
    nextScanAt: Optional[datetime] = None
    expiresAt: datetime
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }