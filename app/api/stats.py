"""
Dashboard Statistics API endpoints.
"""
from fastapi import APIRouter, Depends
from typing import Annotated
from datetime import datetime, timedelta

from app.models.user import UserInDB
from app.api.auth import get_current_user
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> dict:
    """
    Get dashboard statistics for the current user.
    
    Returns:
        - activeWatches: Count of active watches
        - scansToday: Count of scans performed today (from scan_logs)
        - alertsSent: Count of notifications sent (from notifications)
        - recentActivity: Recent scan logs and notifications
        
    Args:
        current_user: Authenticated user
        
    Returns:
        Dashboard statistics object
    """
    db = get_database()
    
    # Count active watches
    active_watches = await db.watches.count_documents({
        "userId": current_user.id,
        "status": "active"
    })
    
    # Count scans today (from scan_logs collection)
    # Note: scan_logs will be implemented in Sprint 4
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = 0
    
    # Check if scan_logs collection exists
    collections = await db.list_collection_names()
    if "scan_logs" in collections:
        scans_today = await db.scan_logs.count_documents({
            "scannedAt": {"$gte": today_start}
        })
    
    # Count alerts sent (from notifications collection)
    # Note: notifications will be implemented in Sprint 5
    alerts_sent = 0
    
    if "notifications" in collections:
        alerts_sent = await db.notifications.count_documents({
            "userId": current_user.id
        })
    
    # Get recent activity (last 10 items)
    recent_activity = []
    
    # Get recent scan logs if collection exists
    if "scan_logs" in collections:
        # Get watch IDs for this user
        user_watches = await db.watches.find(
            {"userId": current_user.id},
            {"_id": 1}
        ).to_list(length=None)
        watch_ids = [watch["_id"] for watch in user_watches]
        
        if watch_ids:
            scan_logs = await db.scan_logs.find(
                {"watchId": {"$in": [str(wid) for wid in watch_ids]}}
            ).sort("scannedAt", -1).limit(10).to_list(length=10)
            
            for log in scan_logs:
                recent_activity.append({
                    "type": "scan",
                    "timestamp": log["scannedAt"],
                    "status": log.get("status", "unknown"),
                    "result": log.get("result", "unknown")
                })
    
    # Get recent notifications if collection exists
    if "notifications" in collections:
        notifications = await db.notifications.find(
            {"userId": current_user.id}
        ).sort("sentAt", -1).limit(10).to_list(length=10)
        
        for notif in notifications:
            recent_activity.append({
                "type": "notification",
                "timestamp": notif["sentAt"],
                "status": notif.get("deliveryStatus", "unknown"),
                "message": notif.get("message", "")
            })
    
    # Sort recent activity by timestamp (newest first)
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = recent_activity[:10]  # Keep only top 10
    
    return {
        "activeWatches": active_watches,
        "scansToday": scans_today,
        "alertsSent": alerts_sent,
        "recentActivity": recent_activity
    }