from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI, HTTPException, Request

from app.bot import create_router
from app.config import Settings, get_settings
from app.ebay import EbayClient
from app.groq_vision import GroqVisionService


def create_app(settings: Settings | None = None, register_webhook: bool = True) -> FastAPI:
    settings = settings or get_settings()
    session = AiohttpSession(proxy=settings.telegram_proxy_url) if settings.telegram_proxy_url else None
    bot = Bot(token=settings.telegram_bot_token, session=session)
    dispatcher = Dispatcher(storage=MemoryStorage())
    vision_service = GroqVisionService(settings.groq_api_key, proxy_url=settings.outbound_proxy_url)
    ebay_client = EbayClient(
        client_id=settings.ebay_client_id,
        client_secret=settings.ebay_client_secret,
        marketplace_id=settings.ebay_marketplace_id,
        delivery_country=settings.delivery_country,
        max_results=settings.max_results,
        proxy_url=settings.outbound_proxy_url,
    )
    dispatcher.include_router(create_router(vision_service, ebay_client))

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if register_webhook:
            await bot.set_webhook(settings.webhook_url)
        yield
        await bot.session.close()

    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/webhook/{webhook_secret}")
    async def telegram_webhook(webhook_secret: str, request: Request):
        if webhook_secret != settings.telegram_webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dispatcher.feed_update(bot, update)
        return {"ok": True}

    return app


app = create_app()
