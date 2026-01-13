from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.mongodb import connect_to_mongodb, close_mongodb_connection, get_database
from app.api import api_router
from app.core.config import settings
from app.services.scheduler import SchedulerService
from app.services.scan_processor import ScanProcessor
from app.services.availability_checker import AvailabilityChecker
from app.services.notification.manager import NotificationManager
from app.services.notification.email_provider import MockEmailProvider
from app.services.notification.sms_provider import TwilioSMSProvider
from app.integrations.apify_client import ApifyClient
from app.models.notification import NotificationType
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events"""
    # Startup
    logger.info("Starting up BnBAlerts API...")
    await connect_to_mongodb()
    
    # Initialize services
    logger.info("Initializing services...")
    
    # Get database instance
    db = get_database()
    
    # Initialize notification providers
    email_provider = MockEmailProvider()
    sms_provider = TwilioSMSProvider()
    
    # Initialize notification manager
    notification_manager = NotificationManager(
        providers={
            NotificationType.EMAIL: email_provider,
            NotificationType.SMS: sms_provider
        }
    )
    
    # Initialize Apify client
    apify_client = ApifyClient()
    
    # Initialize availability checker
    availability_checker = AvailabilityChecker(
        client=apify_client
    )
    
    # Initialize scan processor
    scan_processor = ScanProcessor(
        db=db,
        availability_checker=availability_checker,
        notification_manager=notification_manager
    )
    
    # Initialize and start scheduler
    scheduler = SchedulerService(
        processor=scan_processor,
        db=db
    )
    
    logger.info("Starting scheduler...")
    scheduler.start()
    
    # Store scheduler in app state for access if needed
    app.state.scheduler = scheduler
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BnBAlerts API...")
    logger.info("Stopping scheduler...")
    scheduler.stop()
    await close_mongodb_connection()


app = FastAPI(
    title="BnBAlerts API",
    description="Backend API for BnBAlerts cancellation monitoring service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Mount API router at /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "BnBAlerts API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }