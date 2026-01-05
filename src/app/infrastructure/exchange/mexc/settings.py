from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MexcSettings(BaseSettings):
    """Configuration for MEXC REST client."""

    api_key: str = Field(alias="MEXC_API_KEY")
    api_secret: str = Field(alias="MEXC_SECRET_KEY")
    base_url: str = Field(default="https://api.mexc.com", alias="MEXC_BASE_URL")
    recv_window: int = Field(default=5000, alias="MEXC_RECV_WINDOW")
    timeout: int = Field(default=10, alias="MEXC_TIMEOUT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
