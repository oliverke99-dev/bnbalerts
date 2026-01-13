from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import logging

from app.models.user import UserInDB, UserResponse
from app.models.notification import NotificationPreferencesUpdate
from app.api.auth import get_current_user
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)
router = APIRouter()


@router.patch("/me/preferences", response_model=UserResponse)
async def update_user_preferences(
    preferences: NotificationPreferencesUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update current user's notification preferences.
    
    Allows users to enable/disable email and SMS notifications.
    """
    db = get_database()
    
    # Build update document with only provided fields
    update_data = {}
    
    if preferences.smsEnabled is not None:
        update_data["smsEnabled"] = preferences.smsEnabled
        update_data["notification_preferences.smsEnabled"] = preferences.smsEnabled
    
    if preferences.emailEnabled is not None:
        update_data["emailEnabled"] = preferences.emailEnabled
        update_data["notification_preferences.emailEnabled"] = preferences.emailEnabled
    
    # Always update the updatedAt timestamp
    update_data["updatedAt"] = datetime.utcnow()
    
    # Update user in database
    result = await db.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch updated user document
    updated_user_doc = await db.users.find_one({"_id": current_user.id})
    
    if not updated_user_doc:
        raise HTTPException(status_code=404, detail="User not found after update")
    
    logger.info(f"Updated preferences for user: {current_user.id}")
    
    # Return updated user response
    return UserResponse(
        id=str(updated_user_doc["_id"]),
        email=updated_user_doc["email"],
        phone=updated_user_doc["phone"],
        phoneVerified=updated_user_doc["phoneVerified"],
        name=updated_user_doc.get("name"),
        tier=updated_user_doc.get("tier", "free"),
        smsEnabled=updated_user_doc.get("smsEnabled", True),
        emailEnabled=updated_user_doc.get("emailEnabled", False)
    )