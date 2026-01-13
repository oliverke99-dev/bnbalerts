"""
Scan Log Models

This module defines the data models for scan logs, which track
every property availability check performed by the scanning engine.
"""
from datetime import datetime, date
from typing import Optional, Annotated, Any
from enum import Enum
from pydantic import BaseModel, Field, BeforeValidator
from bson import ObjectId


# Custom type for MongoDB ObjectId that converts to string
PyObjectId = Annotated[str, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)]


class ScanStatus(str, Enum):
    """Status of a scan operation."""
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class ScanResult(str, Enum):
    """Result of a property availability check."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    PARTIAL_MATCH = "partial_match"


class ScanLogBase(BaseModel):
    """Base scan log model with shared attributes."""
    watch_id: str = Field(..., description="Reference to the Watch being scanned")
    status: ScanStatus = Field(..., description="Status of the scan operation")
    result: Optional[ScanResult] = Field(None, description="Result of availability check")
    check_in: date = Field(..., description="Check-in date from the watch")
    check_out: date = Field(..., description="Check-out date from the watch")
    response_time_ms: int = Field(..., ge=0, description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if scan failed")


class ScanLogCreate(BaseModel):
    """Schema for creating a new scan log entry."""
    watch_id: str = Field(..., description="Reference to the Watch being scanned")
    status: ScanStatus = Field(..., description="Status of the scan operation")
    result: Optional[ScanResult] = Field(None, description="Result of availability check")
    check_in: date = Field(..., description="Check-in date from the watch")
    check_out: date = Field(..., description="Check-out date from the watch")
    response_time_ms: int = Field(..., ge=0, description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if scan failed")


class ScanLogInDB(BaseModel):
    """Schema for scan log document in MongoDB."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    watch_id: str = Field(..., description="Reference to the Watch being scanned")
    status: ScanStatus = Field(..., description="Status of the scan operation")
    result: Optional[ScanResult] = Field(None, description="Result of availability check")
    check_in: date = Field(..., description="Check-in date from the watch")
    check_out: date = Field(..., description="Check-out date from the watch")
    response_time_ms: int = Field(..., ge=0, description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if scan failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when log was created")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class ScanLogResponse(BaseModel):
    """Schema for scan log API responses."""
    id: str
    watch_id: str
    status: ScanStatus
    result: Optional[ScanResult] = None
    check_in: date
    check_out: date
    response_time_ms: int
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }