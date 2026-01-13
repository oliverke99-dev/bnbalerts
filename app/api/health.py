from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.db.mongodb import get_database

router = APIRouter()


@router.get("/healthz")
async def health_check():
    """
    Health check endpoint with MongoDB connection status
    
    Returns:
        dict: Health status with database connection info and timestamp
    """
    try:
        # Get database instance
        db = get_database()
        
        # Ping MongoDB to verify connection
        await db.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }