from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "BidSight API"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_dedup_db: int = 1

    # Clerk Auth
    clerk_secret_key: str
    clerk_publishable_key: str
    clerk_jwt_public_key: str = ""

    # Groq (free AI for match scoring)
    groq_api_key: str = ""

    # Razorpay (Phase 4)
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()