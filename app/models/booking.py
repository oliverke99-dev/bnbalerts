"""
Booking detection models for the application.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date


class BookingDetectionRequest(BaseModel):
    """Schema for booking detection request."""
    searchUrl: str = Field(..., description="Airbnb search URL with dates and location")
    maxResults: int = Field(default=50, ge=1, le=100, description="Maximum properties to fetch per search")


class BookingDetectionDirectRequest(BaseModel):
    """Schema for direct booking detection request with parameters."""
    location: str = Field(..., min_length=1, description="Search location (e.g., 'Austin, TX')")
    checkIn: date = Field(..., description="Check-in date")
    checkOut: date = Field(..., description="Check-out date")
    adults: int = Field(default=2, ge=1, description="Number of adults")
    children: int = Field(default=0, ge=0, description="Number of children")
    maxResults: int = Field(default=50, ge=1, le=100, description="Maximum properties to fetch per search")


class PropertyBookingStatus(BaseModel):
    """Schema for property with booking status."""
    propertyId: str = Field(..., description="Airbnb property ID")
    propertyName: str = Field(..., description="Property name")
    propertyUrl: str = Field(..., description="Property URL")
    location: str = Field(..., description="Property location")
    price: str = Field(..., description="Price per night")
    imageUrl: Optional[str] = Field(None, description="Property image URL")
    guests: int = Field(..., description="Number of guests")
    status: str = Field(..., description="Booking status: 'booked' or 'available'")
    availability: str = Field(..., description="Availability status: 'available' or 'unavailable'")
    checkInDate: Optional[str] = Field(None, description="Check-in date (if applicable)")
    checkOutDate: Optional[str] = Field(None, description="Check-out date (if applicable)")


class SearchMetadata(BaseModel):
    """Schema for search metadata."""
    location: str = Field(..., description="Search location")
    checkIn: str = Field(..., description="Check-in date (ISO format)")
    checkOut: str = Field(..., description="Check-out date (ISO format)")
    guests: int = Field(..., description="Total number of guests")
    adults: int = Field(..., description="Number of adults")
    children: int = Field(..., description="Number of children")


class BookingDetectionResponse(BaseModel):
    """Schema for booking detection response."""
    booked_properties: List[PropertyBookingStatus] = Field(
        ..., 
        description="List of properties that are booked for the specified dates"
    )
    available_properties: List[PropertyBookingStatus] = Field(
        ..., 
        description="List of properties that are available for the specified dates"
    )
    total_properties: int = Field(..., description="Total properties found (without date filter)")
    booked_count: int = Field(..., description="Number of booked properties")
    available_count: int = Field(..., description="Number of available properties")
    search_metadata: SearchMetadata = Field(..., description="Search parameters used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "booked_properties": [
                    {
                        "propertyId": "12345678",
                        "propertyName": "Luxury Beach House",
                        "propertyUrl": "https://www.airbnb.com/rooms/12345678",
                        "location": "Miami, FL",
                        "price": "$250",
                        "imageUrl": "https://example.com/image.jpg",
                        "guests": 4,
                        "status": "booked",
                        "availability": "unavailable",
                        "checkInDate": "2024-06-01",
                        "checkOutDate": "2024-06-07"
                    }
                ],
                "available_properties": [
                    {
                        "propertyId": "87654321",
                        "propertyName": "Downtown Apartment",
                        "propertyUrl": "https://www.airbnb.com/rooms/87654321",
                        "location": "Miami, FL",
                        "price": "$150",
                        "imageUrl": "https://example.com/image2.jpg",
                        "guests": 2,
                        "status": "available",
                        "availability": "available",
                        "checkInDate": "2024-06-01",
                        "checkOutDate": "2024-06-07"
                    }
                ],
                "total_properties": 25,
                "booked_count": 15,
                "available_count": 10,
                "search_metadata": {
                    "location": "Miami, FL",
                    "checkIn": "2024-06-01",
                    "checkOut": "2024-06-07",
                    "guests": 4,
                    "adults": 2,
                    "children": 2
                }
            }
        }