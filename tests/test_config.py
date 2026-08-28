from pathlib import Path

from app.config import Settings


def test_settings_apply_defaults():
    settings = Settings(
        telegram_bot_token="telegram-token",
        telegram_webhook_secret="secret-path",
        public_base_url="https://example.onrender.com",
        openai_api_key="openai-key",
        ebay_client_id="ebay-client-id",
        ebay_client_secret="ebay-client-secret",
    )

    assert settings.ebay_marketplace_id == "EBAY_US"
    assert settings.delivery_country == "US"
    assert settings.max_results == 5
    assert settings.webhook_url == "https://example.onrender.com/webhook/secret-path"


def test_settings_env_file_points_to_project_root():
    env_file = Path(Settings.model_config["env_file"])

    assert env_file.name == ".env"
    assert env_file.parent.name == "furniture-finder-bot"
    assert env_file.is_absolute()
