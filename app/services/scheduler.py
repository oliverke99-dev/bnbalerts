"""
Scheduler Service

Runs periodically to find watches that are due for scanning and dispatches them
to the ScanProcessor. This service acts as the background task coordinator that
ensures watches are scanned according to their frequency settings.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.scan_processor import ScanProcessor
from app.models.watch import WatchInDB
from app.core.constants import (
    SCHEDULER_CHECK_INTERVAL_SECONDS,
    DAILY_SCAN_HOUR,
    HOURLY_SCAN_INTERVAL_HOURS,
    SNIPER_SCAN_INTERVAL_MINUTES
)

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Background scheduler that periodically checks for watches due for scanning.
    
    This service:
    - Runs in a background asyncio task
    - Checks every 60 seconds for watches that need scanning
    - Dispatches due watches to the ScanProcessor
    - Updates nextScanAt timestamps after processing
    """
    
    def __init__(
        self,
        processor: ScanProcessor,
        db: AsyncIOMotorDatabase
    ):
        """
        Initialize the SchedulerService.
        
        Args:
            processor: ScanProcessor instance to handle watch processing
            db: MongoDB database instance
        """
        self.processor = processor
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None
        logger.info("SchedulerService initialized")
    
    def start(self) -> None:
        """
        Start the scheduler background task.
        
        Sets the running flag and creates an asyncio task for the main loop.
        """
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Scheduler started")
    
    def stop(self) -> None:
        """
        Stop the scheduler background task.
        
        Sets the running flag to False, which will cause the loop to exit.
        """
        if not self._running:
            logger.warning("Scheduler is not running")
            return
        
        self._running = False
        logger.info("Scheduler stop requested")
    
    async def _loop(self) -> None:
        """
        Main scheduler loop that runs while _running is True.
        
        Continuously checks for due watches and processes them, then sleeps
        for 60 seconds before the next iteration.
        """
        logger.info("Scheduler loop started")
        
        while self._running:
            try:
                await self._process_due_watches()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)
            
            # Sleep for configured interval before next check
            await asyncio.sleep(SCHEDULER_CHECK_INTERVAL_SECONDS)
        
        logger.info("Scheduler loop stopped")
    
    async def _process_due_watches(self) -> None:
        """
        Find and process all watches that are due for scanning.
        
        Queries the database for active watches where nextScanAt <= now,
        processes each watch via the ScanProcessor, and updates the
        nextScanAt timestamp based on the watch's frequency.
        """
        now = datetime.now(timezone.utc)
        
        try:
            # Query for active watches that are due for scanning
            cursor = self.db.watches.find({
                "status": "active",
                "nextScanAt": {"$lte": now}
            })
            
            watches = await cursor.to_list(length=None)
            
            if watches:
                logger.info(f"Found {len(watches)} watches due for scanning")
            
            # Process each watch
            for watch_doc in watches:
                try:
                    # Convert to WatchInDB model
                    watch = WatchInDB(
                        _id=str(watch_doc["_id"]),
                        userId=watch_doc["userId"],
                        propertyId=watch_doc["propertyId"],
                        propertyName=watch_doc["propertyName"],
                        propertyUrl=watch_doc["propertyUrl"],
                        location=watch_doc["location"],
                        checkInDate=watch_doc["checkInDate"],
                        checkOutDate=watch_doc["checkOutDate"],
                        guests=watch_doc["guests"],
                        price=watch_doc["price"],
                        frequency=watch_doc["frequency"],
                        partialMatch=watch_doc["partialMatch"],
                        status=watch_doc["status"],
                        lastScannedAt=watch_doc.get("lastScannedAt"),
                        nextScanAt=watch_doc.get("nextScanAt"),
                        expiresAt=watch_doc["expiresAt"],
                        createdAt=watch_doc["createdAt"],
                        updatedAt=watch_doc["updatedAt"]
                    )
                    
                    # Process the watch
                    await self.processor.process_watch(watch)
                    
                    # Calculate next scan time based on frequency
                    next_scan_at = self._calculate_next_scan_time(
                        watch.frequency,
                        now
                    )
                    
                    # Update nextScanAt in database
                    await self.db.watches.update_one(
                        {"_id": watch_doc["_id"]},
                        {
                            "$set": {
                                "nextScanAt": next_scan_at,
                                "updatedAt": now
                            }
                        }
                    )
                    
                    logger.info(
                        f"Processed watch {watch.id}, next scan at {next_scan_at.isoformat()}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Error processing watch {watch_doc.get('_id')}: {str(e)}",
                        exc_info=True
                    )
                    
        except Exception as e:
            logger.error(f"Error querying due watches: {str(e)}", exc_info=True)
    
    def _calculate_next_scan_time(
        self,
        frequency: str,
        base_time: datetime
    ) -> datetime:
        """
        Calculate the next scan time based on frequency tier.
        
        Args:
            frequency: Scan frequency (daily, hourly, sniper)
            base_time: Base time to calculate from (typically now)
            
        Returns:
            Next scheduled scan datetime
        """
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
            logger.warning(f"Unknown frequency '{frequency}', defaulting to hourly")
            next_scan = base_time + timedelta(hours=HOURLY_SCAN_INTERVAL_HOURS)
            next_scan = next_scan.replace(minute=0, second=0, microsecond=0)
        
        return next_scan