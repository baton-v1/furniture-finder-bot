from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(alias="TELEGRAM_WEBHOOK_SECRET")
    telegram_proxy_url_override: str | None = Field(default=None, alias="TELEGRAM_PROXY_URL")
    outbound_proxy_url_override: str | None = Field(default=None, alias="OUTBOUND_PROXY_URL")
    public_base_url: str = Field(alias="PUBLIC_BASE_URL")
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    ebay_client_id: str = Field(alias="EBAY_CLIENT_ID")
    ebay_client_secret: str = Field(alias="EBAY_CLIENT_SECRET")
    ebay_marketplace_id: str = Field(default="EBAY_US", alias="EBAY_MARKETPLACE_ID")
    delivery_country: str = Field(default="US", alias="DELIVERY_COUNTRY")
    max_results: int = Field(default=5, alias="MAX_RESULTS")

    @property
    def webhook_url(self) -> str:
        return f"{self.public_base_url.rstrip('/')}/webhook/{self.telegram_webhook_secret}"

    @property
    def telegram_proxy_url(self) -> str | None:
        return (
            self.telegram_proxy_url_override
            or self.outbound_proxy_url
        )

    @property
    def outbound_proxy_url(self) -> str | None:
        return (
            self.outbound_proxy_url_override
            or self.telegram_proxy_url_override
            or os.environ.get("https_proxy")
            or os.environ.get("HTTPS_PROXY")
            or os.environ.get("http_proxy")
            or os.environ.get("HTTP_PROXY")
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
