"""
Scan Processor Service

Coordinates the availability checking and notification workflow for a Watch.
This service is the "worker" that processes a specific Watch by:
1. Checking property availability
2. Logging scan results
3. Sending notifications on matches
4. Updating watch status
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.watch import WatchInDB
from app.models.scan_log import ScanLogCreate, ScanStatus, ScanResult
from app.models.property import PropertyResult
from app.services.availability_checker import AvailabilityChecker
from app.services.notification.manager import NotificationManager
from app.models.notification import NotificationPreferences, NotificationType
from app.core.constants import NOTIFICATION_COOLDOWN_HOURS

logger = logging.getLogger(__name__)


class ScanProcessor:
    """
    Processes Watch scans by coordinating availability checks and notifications.
    
    This service acts as the orchestrator for the scanning workflow:
    - Checks property availability via AvailabilityChecker
    - Logs scan results to the database
    - Sends notifications when properties become available
    - Updates watch status and timestamps
    """
    
    def __init__(
        self,
        availability_checker: AvailabilityChecker,
        notification_manager: NotificationManager,
        db: AsyncIOMotorDatabase
    ):
        """
        Initialize the ScanProcessor.
        
        Args:
            availability_checker: Service to check property availability
            notification_manager: Service to send notifications
            db: MongoDB database instance
        """
        self.availability_checker = availability_checker
        self.notification_manager = notification_manager
        self.db = db
        logger.info("ScanProcessor initialized")
    
    async def process_watch(self, watch: WatchInDB) -> None:
        """
        Process a single watch by checking availability and handling notifications.
        
        Args:
            watch: The watch to process
            
        Workflow:
            1. Check property availability
            2. Log the scan result
            3. Send notification if property is available
            4. Update watch status and timestamps
        """
        logger.info(f"Processing watch {watch.id} for property {watch.propertyId}")
        
        start_time = datetime.now(timezone.utc)
        scan_status = ScanStatus.SUCCESS
        scan_result = None
        error_message = None
        
        try:
            # Step 1: Check availability
            scan_result, matching_property = await self.availability_checker.check_availability(watch)
            
            # Calculate response time
            end_time = datetime.now(timezone.utc)
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            logger.info(
                f"Availability check completed for watch {watch.id}: "
                f"result={scan_result.value}, response_time={response_time_ms}ms"
            )
            
            # Step 2: Log the scan result
            # Convert date to datetime for MongoDB
            from datetime import date as date_type
            check_in_dt = datetime.combine(watch.checkInDate, datetime.min.time()) if isinstance(watch.checkInDate, date_type) and not isinstance(watch.checkInDate, datetime) else watch.checkInDate
            check_out_dt = datetime.combine(watch.checkOutDate, datetime.min.time()) if isinstance(watch.checkOutDate, date_type) and not isinstance(watch.checkOutDate, datetime) else watch.checkOutDate
            
            await self._create_scan_log(
                watch_id=watch.id,
                status=scan_status,
                result=scan_result,
                response_time_ms=response_time_ms,
                error_message=None,
                check_in=check_in_dt,
                check_out=check_out_dt
            )
            
            # Step 3: Handle match - send notification if available
            if scan_result == ScanResult.AVAILABLE:
                await self._handle_availability_match(watch, matching_property)
            
            # Step 4: Update watch status
            await self._update_watch_after_scan(
                watch_id=watch.id,
                status="active",
                error_message=None
            )
            
        except Exception as e:
            # Handle errors during scan
            logger.error(f"Error processing watch {watch.id}: {str(e)}", exc_info=True)
            
            end_time = datetime.now(timezone.utc)
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            scan_status = ScanStatus.ERROR
            error_message = str(e)
            
            # Log the failed scan
            # Convert date to datetime for MongoDB
            from datetime import date as date_type
            check_in_dt = datetime.combine(watch.checkInDate, datetime.min.time()) if isinstance(watch.checkInDate, date_type) and not isinstance(watch.checkInDate, datetime) else watch.checkInDate
            check_out_dt = datetime.combine(watch.checkOutDate, datetime.min.time()) if isinstance(watch.checkOutDate, date_type) and not isinstance(watch.checkOutDate, datetime) else watch.checkOutDate
            
            await self._create_scan_log(
                watch_id=watch.id,
                status=scan_status,
                result=None,
                response_time_ms=response_time_ms,
                error_message=error_message,
                check_in=check_in_dt,
                check_out=check_out_dt
            )
            
            # Update watch to error status
            await self._update_watch_after_scan(
                watch_id=watch.id,
                status="error",
                error_message=error_message
            )
    
    async def _create_scan_log(
        self,
        watch_id: str,
        status: ScanStatus,
        result: Optional[ScanResult],
        response_time_ms: int,
        error_message: Optional[str],
        check_in = None,
        check_out = None
    ) -> None:
        """
        Create a scan log entry in the database.
        
        Args:
            watch_id: ID of the watch being scanned
            status: Status of the scan operation
            result: Result of the availability check (if successful)
            response_time_ms: Response time in milliseconds
            error_message: Error message if scan failed
            check_in: Check-in date (optional, will fetch from DB if not provided)
            check_out: Check-out date (optional, will fetch from DB if not provided)
        """
        try:
            # If dates not provided, fetch from database
            if check_in is None or check_out is None:
                from bson import ObjectId
                
                # Convert string ID to ObjectId for MongoDB query
                watch_doc = await self.db.watches.find_one({"_id": ObjectId(watch_id)})
                if not watch_doc:
                    logger.error(f"Watch {watch_id} not found when creating scan log")
                    return
                
                check_in = watch_doc["checkInDate"]
                check_out = watch_doc["checkOutDate"]
            
            # Convert date objects to datetime for MongoDB compatibility
            from datetime import date as date_type
            if isinstance(check_in, date_type) and not isinstance(check_in, datetime):
                check_in = datetime.combine(check_in, datetime.min.time())
            if isinstance(check_out, date_type) and not isinstance(check_out, datetime):
                check_out = datetime.combine(check_out, datetime.min.time())
            
            scan_log = ScanLogCreate(
                watch_id=watch_id,
                status=status,
                result=result,
                check_in=check_in,
                check_out=check_out,
                response_time_ms=response_time_ms,
                error_message=error_message
            )
            
            # Insert into scan_logs collection
            log_dict = scan_log.model_dump()
            log_dict["created_at"] = datetime.now(timezone.utc)
            
            await self.db.scan_logs.insert_one(log_dict)
            logger.info(f"Created scan log for watch {watch_id}")
            
        except Exception as e:
            logger.error(f"Failed to create scan log for watch {watch_id}: {str(e)}", exc_info=True)
    
    async def _handle_availability_match(
        self,
        watch: WatchInDB,
        matching_property: Optional[PropertyResult]
    ) -> None:
        """
        Handle a successful availability match by sending notifications.
        
        Args:
            watch: The watch that matched
            matching_property: The matching property data
        """
        logger.info(f"Property available for watch {watch.id}, preparing notification")
        
        try:
            # Check if we should send notification (duplicate prevention)
            if not await self._should_send_notification(watch):
                logger.info(f"Skipping notification for watch {watch.id} (duplicate prevention)")
                return
            
            # Fetch user to get notification preferences and contact info
            user_doc = await self.db.users.find_one({"_id": watch.userId})
            if not user_doc:
                logger.error(f"User {watch.userId} not found for watch {watch.id}")
                return
            
            # Construct notification message
            message = self._construct_notification_message(watch, matching_property)
            subject = f"🎉 Property Available: {watch.propertyName}"
            
            # Get user notification preferences
            user_prefs = NotificationPreferences(
                emailEnabled=user_doc.get("notificationPreferences", {}).get("emailEnabled", True),
                smsEnabled=user_doc.get("notificationPreferences", {}).get("smsEnabled", False)
            )
            
            # Send multi-channel notification
            results = self.notification_manager.send_multi_channel(
                user_prefs=user_prefs,
                email=user_doc.get("email"),
                phone=user_doc.get("phone"),
                message=message,
                subject=subject
            )
            
            logger.info(f"Notification sent for watch {watch.id}: {results}")
            
            from bson import ObjectId
            
            # Update last_notification_sent timestamp
            await self.db.watches.update_one(
                {"_id": ObjectId(watch.id)},
                {
                    "$set": {
                        "lastNotificationSent": datetime.now(timezone.utc),
                        "updatedAt": datetime.now(timezone.utc)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to send notification for watch {watch.id}: {str(e)}", exc_info=True)
    
    async def _should_send_notification(self, watch: WatchInDB) -> bool:
        """
        Determine if a notification should be sent for this watch.
        
        Implements duplicate alert prevention by checking when the last
        notification was sent.
        
        Args:
            watch: The watch to check
            
        Returns:
            True if notification should be sent, False otherwise
        """
        from bson import ObjectId
        
        # Fetch latest watch data from database
        watch_doc = await self.db.watches.find_one({"_id": ObjectId(watch.id)})
        if not watch_doc:
            return False
        
        last_notification = watch_doc.get("lastNotificationSent")
        
        # If never notified, send notification
        if not last_notification:
            return True
        
        # Don't send duplicate notifications within configured cooldown period
        time_since_last = datetime.now(timezone.utc) - last_notification
        if time_since_last < timedelta(hours=NOTIFICATION_COOLDOWN_HOURS):
            logger.info(
                f"Skipping notification for watch {watch.id}: "
                f"last sent {time_since_last.total_seconds() / 3600:.1f} hours ago "
                f"(cooldown: {NOTIFICATION_COOLDOWN_HOURS}h)"
            )
            return False
        
        return True
    
    def _construct_notification_message(
        self,
        watch: WatchInDB,
        matching_property: Optional[PropertyResult]
    ) -> str:
        """
        Construct a notification message for an available property.
        
        Args:
            watch: The watch that matched
            matching_property: The matching property data
            
        Returns:
            Formatted notification message
        """
        message = f"""🎉 Good news! The property you're watching is now available!

Property: {watch.propertyName}
Location: {watch.location}
Dates: {watch.checkInDate.isoformat()} to {watch.checkOutDate.isoformat()}
Guests: {watch.guests}
Price: {watch.price}

View property: {watch.propertyUrl}

Book now before it's gone!
"""
        return message
    
    async def _update_watch_after_scan(
        self,
        watch_id: str,
        status: str,
        error_message: Optional[str]
    ) -> None:
        """
        Update watch status and timestamps after a scan.
        
        Args:
            watch_id: ID of the watch to update
            status: New status for the watch
            error_message: Error message if scan failed
        """
        try:
            update_data = {
                "lastScannedAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc),
                "status": status
            }
            
            from bson import ObjectId
            
            if error_message:
                update_data["errorMessage"] = error_message
            
            await self.db.watches.update_one(
                {"_id": ObjectId(watch_id)},
                {"$set": update_data}
            )
            
            logger.info(f"Updated watch {watch_id} after scan: status={status}")
            
        except Exception as e:
            logger.error(f"Failed to update watch {watch_id}: {str(e)}", exc_info=True)