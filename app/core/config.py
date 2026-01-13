from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_ENV: str = "development"
    PORT: int = 8000
    
    # Database
    MONGODB_URI: str
    
    # JWT
    JWT_SECRET: str
    JWT_EXPIRES_IN: int = 86400  # 24 hours in seconds
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Twilio (for later sprints)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Apify Configuration
    APIFY_API_TOKEN: str = ""
    APIFY_ACTOR_ID: str = "dtrungtin/airbnb-scraper"  # Default Airbnb scraper actor
    APIFY_API_URL: str = "https://api.apify.com/v2"
    APIFY_TIMEOUT: int = 300  # 5 minutes timeout for scraping operations
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()