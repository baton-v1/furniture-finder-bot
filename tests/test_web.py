import os

from fastapi.testclient import TestClient

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456789:AAtelegramtoken")
os.environ.setdefault("TELEGRAM_WEBHOOK_SECRET", "secret")
os.environ.setdefault("PUBLIC_BASE_URL", "https://example.onrender.com")
os.environ.setdefault("OPENAI_API_KEY", "openai-key")
os.environ.setdefault("EBAY_CLIENT_ID", "ebay-client-id")
os.environ.setdefault("EBAY_CLIENT_SECRET", "ebay-client-secret")

from app.config import Settings
from app.web import create_app


def make_settings() -> Settings:
    return Settings(
        telegram_bot_token="123456789:AAtelegramtoken",
        telegram_webhook_secret="secret",
        public_base_url="https://example.onrender.com",
        openai_api_key="openai-key",
        ebay_client_id="ebay-client-id",
        ebay_client_secret="ebay-client-secret",
    )


def test_health_returns_ok():
    app = create_app(make_settings(), register_webhook=False)

    assert TestClient(app).get("/health").json() == {"status": "ok"}


def test_webhook_rejects_wrong_secret():
    app = create_app(make_settings(), register_webhook=False)

    response = TestClient(app).post("/webhook/wrong", json={})

    assert response.status_code == 403
