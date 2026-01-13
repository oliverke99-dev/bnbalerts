"""
Watch Management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from datetime import datetime, time, timedelta
from bson import ObjectId

from app.models.watch import WatchCreate, WatchUpdate, WatchResponse, WatchInDB
from app.models.user import UserInDB
from app.api.auth import get_current_user
from app.db.mongodb import get_database
from app.core.constants import (
    MAX_ACTIVE_WATCHES_PER_USER,
    DAILY_SCAN_HOUR,
    HOURLY_SCAN_INTERVAL_HOURS,
    SNIPER_SCAN_INTERVAL_MINUTES
)

router = APIRouter()


def calculate_next_scan_time(frequency: str, base_time: datetime = None) -> datetime:
    """
    Calculate the next scan time based on frequency tier.
    
    This function determines when the next property availability scan should occur
    based on the watch's frequency setting. It ensures scans are scheduled at
    appropriate intervals to balance responsiveness with API usage.
    
    Args:
        frequency: Scan frequency tier - one of:
            - 'daily': Once per day at configured hour (default: noon UTC)
            - 'hourly': Every hour on the hour
            - 'sniper': Every 5 minutes for time-sensitive bookings
        base_time: Base time to calculate from (defaults to current UTC time)
        
    Returns:
        datetime: Next scheduled scan time in UTC
        
    Examples:
        >>> from datetime import datetime
        >>> base = datetime(2024, 1, 1, 10, 30)
        >>> next_scan = calculate_next_scan_time('hourly', base)
        >>> next_scan.hour
        11
        >>> next_scan.minute
        0
    """
    if base_time is None:
        base_time = datetime.utcnow()
    
    if frequency == "daily":
        # Schedule for next day at configured hour
        next_scan = base_time + timedelta(days=1)
        next_scan = next_scan.replace(hour=DAILY_SCAN_HOUR, minute=0, second=0, microsecond=0)
    elif frequency == "hourly":
        # Schedule for next hour on the hour
        next_scan = base_time + timedelta(hours=HOURLY_SCAN_INTERVAL_HOURS)
        next_scan = next_scan.replace(minute=0, second=0, microsecond=0)
    elif frequency == "sniper":
        # Schedule for configured minutes from now
        next_scan = base_time + timedelta(minutes=SNIPER_SCAN_INTERVAL_MINUTES)
    else:
        # Default to hourly if unknown frequency
        next_scan = base_time + timedelta(hours=HOURLY_SCAN_INTERVAL_HOURS)
        next_scan = next_scan.replace(minute=0, second=0, microsecond=0)
    
    return next_scan


def calculate_expires_at(check_in_date) -> datetime:
    """
    Calculate expiration datetime for a watch.
    
    Watches automatically expire at the end of the check-in date (23:59:59)
    since monitoring is no longer useful after the guest would have checked in.
    
    Args:
        check_in_date: The check-in date for the property reservation
        
    Returns:
        datetime: Expiration time set to 23:59:59 on the check-in date
        
    Example:
        >>> from datetime import date
        >>> check_in = date(2024, 6, 15)
        >>> expires = calculate_expires_at(check_in)
        >>> expires.hour, expires.minute, expires.second
        (23, 59, 59)
    """
    return datetime.combine(check_in_date, time(23, 59, 59))


@router.post("", response_model=WatchResponse, status_code=status.HTTP_201_CREATED)
async def create_watch(
    watch_data: WatchCreate,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> WatchResponse:
    """
    Create a new watch for a property.
    
    Enforces max 5 active watches per user.
    
    Args:
        watch_data: Watch creation data
        current_user: Authenticated user
        
    Returns:
        Created watch
        
    Raises:
        HTTPException: 400 if user has 5+ active watches
    """
    db = get_database()
    
    # Check active watch count
    active_count = await db.watches.count_documents({
        "userId": current_user.id,
        "status": "active"
    })
    
    if active_count >= MAX_ACTIVE_WATCHES_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum of {MAX_ACTIVE_WATCHES_PER_USER} active watches allowed. Please delete or pause an existing watch."
        )
    
    # Calculate timestamps
    now = datetime.utcnow()
    next_scan_at = calculate_next_scan_time(watch_data.frequency, now)
    expires_at = calculate_expires_at(watch_data.checkInDate)
    
    # Create watch document
    # Convert date objects to datetime for MongoDB compatibility
    from datetime import datetime as dt
    check_in_datetime = dt.combine(watch_data.checkInDate, dt.min.time())
    check_out_datetime = dt.combine(watch_data.checkOutDate, dt.min.time())
    
    watch_doc = {
        "userId": current_user.id,
        "propertyId": watch_data.propertyId,
        "propertyName": watch_data.propertyName,
        "propertyUrl": watch_data.propertyUrl,
        "location": watch_data.location,
        "imageUrl": watch_data.imageUrl,
        "checkInDate": check_in_datetime,
        "checkOutDate": check_out_datetime,
        "guests": watch_data.guests,
        "price": watch_data.price,
        "frequency": watch_data.frequency,
        "partialMatch": watch_data.partialMatch,
        "status": "active",
        "lastScannedAt": None,
        "nextScanAt": next_scan_at,
        "expiresAt": expires_at,
        "createdAt": now,
        "updatedAt": now
    }
    
    # Insert into database
    result = await db.watches.insert_one(watch_doc)
    watch_doc["_id"] = str(result.inserted_id)
    
    # Convert to response model
    return WatchResponse(
        id=watch_doc["_id"],
        userId=watch_doc["userId"],
        propertyId=watch_doc["propertyId"],
        propertyName=watch_doc["propertyName"],
        propertyUrl=watch_doc["propertyUrl"],
        location=watch_doc["location"],
        imageUrl=watch_doc.get("imageUrl"),
        checkInDate=watch_doc["checkInDate"],
        checkOutDate=watch_doc["checkOutDate"],
        guests=watch_doc["guests"],
        price=watch_doc["price"],
        frequency=watch_doc["frequency"],
        partialMatch=watch_doc["partialMatch"],
        status=watch_doc["status"],
        lastScannedAt=watch_doc["lastScannedAt"],
        nextScanAt=watch_doc["nextScanAt"],
        expiresAt=watch_doc["expiresAt"],
        createdAt=watch_doc["createdAt"],
        updatedAt=watch_doc["updatedAt"]
    )


@router.get("", response_model=List[WatchResponse])
async def list_watches(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> List[WatchResponse]:
    """
    List all watches for the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of watches sorted by creation date (newest first)
    """
    db = get_database()
    
    # Query watches for current user
    cursor = db.watches.find({"userId": current_user.id}).sort("createdAt", -1)
    watches = await cursor.to_list(length=None)
    
    # Convert to response models
    return [
        WatchResponse(
            id=str(watch["_id"]),
            userId=watch["userId"],
            propertyId=watch["propertyId"],
            propertyName=watch["propertyName"],
            propertyUrl=watch["propertyUrl"],
            location=watch["location"],
            imageUrl=watch.get("imageUrl"),
            checkInDate=watch["checkInDate"],
            checkOutDate=watch["checkOutDate"],
            guests=watch["guests"],
            price=watch["price"],
            frequency=watch["frequency"],
            partialMatch=watch["partialMatch"],
            status=watch["status"],
            lastScannedAt=watch.get("lastScannedAt"),
            nextScanAt=watch.get("nextScanAt"),
            expiresAt=watch["expiresAt"],
            createdAt=watch["createdAt"],
            updatedAt=watch["updatedAt"]
        )
        for watch in watches
    ]


@router.get("/{watch_id}", response_model=WatchResponse)
async def get_watch(
    watch_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> WatchResponse:
    """
    Get details of a specific watch.
    
    Args:
        watch_id: Watch ID
        current_user: Authenticated user
        
    Returns:
        Watch details
        
    Raises:
        HTTPException: 404 if watch not found or doesn't belong to user
    """
    db = get_database()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(watch_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch not found"
        )
    
    # Query watch
    watch = await db.watches.find_one({
        "_id": ObjectId(watch_id),
        "userId": current_user.id
    })
    
    if not watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch not found"
        )
    
    # Convert to response model
    return WatchResponse(
        id=str(watch["_id"]),
        userId=watch["userId"],
        propertyId=watch["propertyId"],
        propertyName=watch["propertyName"],
        propertyUrl=watch["propertyUrl"],
        location=watch["location"],
        imageUrl=watch.get("imageUrl"),
        checkInDate=watch["checkInDate"],
        checkOutDate=watch["checkOutDate"],
        guests=watch["guests"],
        price=watch["price"],
        frequency=watch["frequency"],
        partialMatch=watch["partialMatch"],
        status=watch["status"],
        lastScannedAt=watch.get("lastScannedAt"),
        nextScanAt=watch.get("nextScanAt"),
        expiresAt=watch["expiresAt"],
        createdAt=watch["createdAt"],
        updatedAt=watch["updatedAt"]
    )


@router.patch("/{watch_id}", response_model=WatchResponse)
async def update_watch(
    watch_id: str,
    update_data: WatchUpdate,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> WatchResponse:
    """
    Update watch settings (frequency, status, partialMatch).
    
    Recalculates nextScanAt if frequency changes.
    
    Args:
        watch_id: Watch ID
        update_data: Fields to update
        current_user: Authenticated user
        
    Returns:
        Updated watch
        
    Raises:
        HTTPException: 404 if watch not found or doesn't belong to user
    """
    db = get_database()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(watch_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch not found"
        )
    
    # Query existing watch
    watch = await db.watches.find_one({
        "_id": ObjectId(watch_id),
        "userId": current_user.id
    })
    
    if not watch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch not found"
        )
    
    # Build update document
    update_doc = {"updatedAt": datetime.utcnow()}
    
    if update_data.frequency is not None:
        update_doc["frequency"] = update_data.frequency
        # Recalculate nextScanAt if frequency changed
        update_doc["nextScanAt"] = calculate_next_scan_time(
            update_data.frequency,
            watch.get("lastScannedAt") or datetime.utcnow()
        )
    
    if update_data.status is not None:
        update_doc["status"] = update_data.status
    
    if update_data.partialMatch is not None:
        update_doc["partialMatch"] = update_data.partialMatch
    
    # Update in database
    await db.watches.update_one(
        {"_id": ObjectId(watch_id)},
        {"$set": update_doc}
    )
    
    # Fetch updated watch
    updated_watch = await db.watches.find_one({"_id": ObjectId(watch_id)})
    
    # Convert to response model
    return WatchResponse(
        id=str(updated_watch["_id"]),
        userId=updated_watch["userId"],
        propertyId=updated_watch["propertyId"],
        propertyName=updated_watch["propertyName"],
        propertyUrl=updated_watch["propertyUrl"],
        location=updated_watch["location"],
        imageUrl=updated_watch.get("imageUrl"),
        checkInDate=updated_watch["checkInDate"],
        checkOutDate=updated_watch["checkOutDate"],
        guests=updated_watch["guests"],
        price=updated_watch["price"],
        frequency=updated_watch["frequency"],
        partialMatch=updated_watch["partialMatch"],
        status=updated_watch["status"],
        lastScannedAt=updated_watch.get("lastScannedAt"),
        nextScanAt=updated_watch.get("nextScanAt"),
        expiresAt=updated_watch["expiresAt"],
        createdAt=updated_watch["createdAt"],
        updatedAt=updated_watch["updatedAt"]
    )


@router.delete("/{watch_id}", status_code=status.HTTP_200_OK)
async def delete_watch(
    watch_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> dict:
    """
    Delete a watch.
    
    Args:
        watch_id: Watch ID
        current_user: Authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if watch not found or doesn't belong to user
    """
    db = get_database()
    
    # Validate ObjectId format
    if not ObjectId.is_valid(watch_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch not found"
        )
    
    # Delete watch
    result = await db.watches.delete_one({
        "_id": ObjectId(watch_id),
        "userId": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watch not found"
        )
    
    return {"message": "Watch deleted successfully"}