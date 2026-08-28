from functools import lru_cache
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
    public_base_url: str = Field(alias="PUBLIC_BASE_URL")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    ebay_client_id: str = Field(alias="EBAY_CLIENT_ID")
    ebay_client_secret: str = Field(alias="EBAY_CLIENT_SECRET")
    ebay_marketplace_id: str = Field(default="EBAY_US", alias="EBAY_MARKETPLACE_ID")
    delivery_country: str = Field(default="US", alias="DELIVERY_COUNTRY")
    max_results: int = Field(default=5, alias="MAX_RESULTS")

    @property
    def webhook_url(self) -> str:
        return f"{self.public_base_url.rstrip('/')}/webhook/{self.telegram_webhook_secret}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
