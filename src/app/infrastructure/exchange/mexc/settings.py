from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MexcSettings(BaseSettings):
    """Configuration for MEXC REST client."""

    api_key: str = Field(alias="MEXC_API_KEY")
    api_secret: str = Field(alias="MEXC_SECRET_KEY")
    base_url: str = Field(default="https://api.mexc.com", alias="MEXC_BASE_URL")
    recv_window: int = Field(default=5000, alias="MEXC_RECV_WINDOW")
    timeout: int = Field(default=10, alias="MEXC_TIMEOUT")
    sub_account_mode: Literal["SPOT", "BROKER"] = Field(default="SPOT", alias="SUB_ACCOUNT_MODE")
    sub_account_id: int | str | None = Field(default=None, alias="SUB_ACCOUNT_ID")
    sub_account_name: str | None = Field(default=None, alias="SUB_ACCOUNT_NAME")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("sub_account_mode")
    @classmethod
    def _uppercase_mode(cls, value: str) -> str:
        return value.upper()

    @field_validator("sub_account_id", "sub_account_name")
    @classmethod
    def _empty_to_none(cls, value: str | int | None) -> str | int | None:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
