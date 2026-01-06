"""Configuration management for the application."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config:
    """Placeholder config for skeleton build."""

    LOG_LEVEL = "INFO"
    LOG_FORMAT = "text"
    PORT = 8000
    HOST = "0.0.0.0"
    DEBUG = False


class MexcSettings(BaseSettings):
    """MEXC API configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    MEXC_API_KEY: str = Field(default="", description="MEXC API key")
    MEXC_SECRET_KEY: str = Field(default="", description="MEXC API secret key")
    MEXC_BASE_URL: str = Field(default="https://api.mexc.com", description="MEXC API base URL")
    MEXC_TIMEOUT: int = Field(default=10, description="Request timeout in seconds")
    
    # Sub-account configuration (optional)
    SUB_ACCOUNT_MODE: str = Field(default="SPOT", description="Sub-account mode: SPOT or BROKER")
    SUB_ACCOUNT_ID: Optional[str] = Field(default=None, description="Sub-account ID (string for BROKER mode, numeric string for SPOT mode)")
    SUB_ACCOUNT_NAME: Optional[str] = Field(default=None, description="Sub-account name (for BROKER mode)")


config = Config()
