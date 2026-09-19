"""Application Configuration via Pydantic Settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ResumeFit AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = False

    # CORS origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Authentication & Security
    SECRET_KEY: str = "resumefit_ai_dev_secret_key_2026_super_secure_auth_token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DB_PATH: str = "resumefit.db"

    # Job Finder & Live Providers
    JOB_DATA_MODE: str = "live"  # "live" or "curated"
    JOB_CACHE_TTL_SECONDS: int = 900  # 15 minutes in-memory caching
    GREENHOUSE_COMPANIES: str = "gitlab,cloudflare,figma,inmobi,groww,canonical"
    LEVER_COMPANIES: str = "palantir,wealthfront,cred"
    ASHBY_COMPANIES: str = "openai,linear,ramp,sentry,replit,notion"
    PUBLIC_FEED_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
