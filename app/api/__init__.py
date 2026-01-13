from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.properties import router as properties_router
from app.api.watches import router as watches_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router)
api_router.include_router(properties_router, prefix="/properties", tags=["properties"])
api_router.include_router(watches_router, prefix="/watches", tags=["watches"])
api_router.include_router(stats_router, prefix="/stats", tags=["stats"])
api_router.include_router(users_router, prefix="/users", tags=["users"])