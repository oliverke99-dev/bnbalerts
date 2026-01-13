from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client instance
mongodb_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongodb():
    """
    Connect to MongoDB Atlas with optimized connection pool settings.
    
    Configures the Motor client with:
    - Connection pooling for better performance under load
    - Appropriate timeouts for production use
    - Server selection and socket timeouts
    
    Raises:
        Exception: If connection to MongoDB fails
        
    Note:
        This function modifies the global mongodb_client variable.
        Consider using dependency injection for better testability.
    """
    global mongodb_client
    try:
        # Configure connection with pool settings for production
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            maxPoolSize=50,  # Maximum connections in the pool
            minPoolSize=10,  # Minimum connections to maintain
            maxIdleTimeMS=45000,  # Close idle connections after 45s
            serverSelectionTimeoutMS=5000,  # Timeout for server selection
            socketTimeoutMS=20000,  # Socket timeout for operations
            connectTimeoutMS=10000,  # Timeout for initial connection
        )
        # Test the connection
        await mongodb_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas with connection pooling")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb_connection():
    """
    Close MongoDB connection and cleanup resources.
    
    Properly closes the MongoDB client connection and releases
    all resources in the connection pool.
    
    Note:
        This should be called during application shutdown to ensure
        graceful cleanup of database connections.
    """
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Closed MongoDB connection and released pool resources")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance.
    
    Extracts the database name from the connection URI and returns
    the database handle. Falls back to 'bnbalerts' if no database
    name is specified in the URI.
    
    Returns:
        AsyncIOMotorDatabase: The MongoDB database instance
        
    Raises:
        RuntimeError: If MongoDB client is not initialized
        
    Example:
        >>> db = get_database()
        >>> users = await db.users.find_one({"email": "user@example.com"})
    """
    if mongodb_client is None:
        raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongodb() first.")
    
    # Extract database name from connection string
    # Format: mongodb+srv://user:pass@cluster.mongodb.net/dbname?options
    db_name = settings.MONGODB_URI.split("/")[-1].split("?")[0]
    if not db_name:
        db_name = "bnbalerts"  # Default database name
        logger.warning(f"No database name in URI, using default: {db_name}")
    
    return mongodb_client[db_name]