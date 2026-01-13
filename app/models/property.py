"""
Property models for the application.
"""
from datetime import datetime, date
from typing import Optional, List, Annotated, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator, BeforeValidator
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class PropertyBase(BaseModel):
    """Base property model with shared attributes."""
    
    propertyId: str = Field(..., description="Airbnb property ID")
    propertyName: str = Field(..., min_length=1, max_length=500, description="Property title/name")
    propertyUrl: str = Field(..., description="Airbnb listing URL")
    location: str = Field(..., min_length=1, max_length=200, description="Property location")
    price: str = Field(..., description="Price per night (e.g., '$250/night')")
    imageUrl: Optional[str] = Field(None, description="Property image URL")
    guests: int = Field(..., ge=1, description="Maximum number of guests")
    dates: Optional[str] = Field(None, description="Date range string for display")
    status: str = Field(default="unavailable", description="Availability status")


class PropertyDiscoveryRequest(BaseModel):
    """Schema for property discovery request."""
    searchUrl: str = Field(..., description="Airbnb search or property URL")
    checkIn: Optional[date] = Field(None, description="Check-in date (required for property URLs)")
    checkOut: Optional[date] = Field(None, description="Check-out date (required for property URLs)")
    guests: Optional[int] = Field(2, description="Number of guests", ge=1)
    
    @field_validator('searchUrl')
    @classmethod
    def validate_airbnb_url(cls, v: str) -> str:
        """Validate that URL is from Airbnb"""
        if not ('airbnb.com' in v.lower()):
            raise ValueError('URL must be a valid Airbnb search URL')
        return v
    
    @field_validator('checkOut')
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that check-out is after check-in"""
        if v and 'checkIn' in info.data and info.data['checkIn'] and v <= info.data['checkIn']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class PropertyResult(BaseModel):
    """Schema for individual property in discovery results."""
    id: str = Field(..., description="Property ID")
    name: str = Field(..., description="Property name")
    location: str = Field(..., description="Property location")
    price: str = Field(..., description="Price per night")
    imageUrl: Optional[str] = Field(None, description="Property image URL")
    dates: Optional[str] = Field(None, description="Date range")
    guests: int = Field(..., description="Number of guests")
    status: str = Field(default="unavailable", description="Availability status")
    url: str = Field(..., description="Property URL")
    
    class Config:
        populate_by_name = True


class PropertyDiscoveryResponse(BaseModel):
    """Schema for property discovery response."""
    properties: List[PropertyResult] = Field(..., description="List of discovered properties")
    count: int = Field(..., description="Total number of properties found")


class PropertyCreate(BaseModel):
    """Schema for creating a property record (from scraping)."""
    propertyId: str = Field(..., description="Airbnb property ID")
    propertyName: str = Field(..., min_length=1, max_length=500, description="Property title")
    propertyUrl: str = Field(..., description="Airbnb listing URL")
    location: str = Field(..., min_length=1, max_length=200, description="Property location")
    price: str = Field(..., description="Price per night")
    imageUrl: Optional[str] = Field(None, description="Property image URL")
    guests: int = Field(..., ge=1, description="Maximum number of guests")
    checkInDate: date = Field(..., description="Check-in date")
    checkOutDate: date = Field(..., description="Check-out date")
    
    @field_validator('checkOutDate')
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Validate that check-out is after check-in"""
        if 'checkInDate' in info.data and v <= info.data['checkInDate']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class PropertyUpdate(BaseModel):
    """Schema for updating property attributes."""
    propertyName: Optional[str] = Field(None, min_length=1, max_length=500)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[str] = None
    imageUrl: Optional[str] = None
    guests: Optional[int] = Field(None, ge=1)


class PropertyInDB(BaseModel):
    """Schema for property document in MongoDB."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    propertyId: str
    propertyName: str
    propertyUrl: str
    location: str
    price: str
    imageUrl: Optional[str] = None
    guests: int
    checkInDate: date
    checkOutDate: date
    status: str = "unavailable"
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class PropertyResponse(BaseModel):
    """Schema for property API responses."""
    id: str
    propertyId: str
    propertyName: str
    propertyUrl: str
    location: str
    price: str
    imageUrl: Optional[str] = None
    guests: int
    checkInDate: date
    checkOutDate: date
    status: str
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class PropertyDetailsFetchRequest(BaseModel):
    """Schema for fetching property details from URL."""
    propertyUrl: str = Field(..., description="Full Airbnb property URL")
    checkIn: date = Field(..., description="Check-in date")
    checkOut: date = Field(..., description="Check-out date")
    
    @field_validator('propertyUrl')
    @classmethod
    def validate_airbnb_url(cls, v: str) -> str:
        """Validate that URL is from Airbnb and contains property ID"""
        if not ('airbnb.com' in v.lower() and '/rooms/' in v.lower()):
            raise ValueError('URL must be a valid Airbnb property URL (e.g., https://www.airbnb.com/rooms/12345678)')
        return v
    
    @field_validator('checkOut')
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Validate that check-out is after check-in"""
        if 'checkIn' in info.data and v <= info.data['checkIn']:
            raise ValueError('Check-out date must be after check-in date')
        return v


class PropertyDetailsFetchResponse(BaseModel):
    """Schema for property details fetch response."""
    propertyId: str = Field(..., description="Extracted Airbnb property ID")
    propertyName: str = Field(..., description="Property name/title")
    location: str = Field(..., description="Property location")
    price: str = Field(..., description="Price per night")
    imageUrl: Optional[str] = Field(None, description="Property main image URL")
    currentStatus: str = Field(..., description="Current availability status (available/booked/unknown)")
    isAvailable: bool = Field(..., description="Whether property is available for specified dates")
    propertyUrl: str = Field(..., description="Full property URL")
    checkIn: date = Field(..., description="Check-in date")
    checkOut: date = Field(..., description="Check-out date")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            date: lambda v: v.isoformat()
        }