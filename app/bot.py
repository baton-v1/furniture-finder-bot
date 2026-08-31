import logging

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.budget import parse_budget
from app.formatting import format_description, format_listing


logger = logging.getLogger(__name__)


class FurnitureSearchStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_city = State()
    waiting_for_budget = State()


async def download_photo_bytes(bot: Bot, file_id: str) -> bytes:
    file = await bot.get_file(file_id)
    stream = await bot.download_file(file.file_path)
    return stream.read()


async def run_search(image_bytes: bytes, budget: int, vision_service, ebay_client):
    description = await vision_service.analyze(image_bytes)
    listings = await ebay_client.search(description.search_query, budget)
    return description, listings


def log_search_error(exc: Exception) -> None:
    logger.exception("Furniture search failed", exc_info=exc)


def create_router(vision_service, ebay_client) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message, state: FSMContext):
        await state.clear()
        await state.set_state(FurnitureSearchStates.waiting_for_photo)
        await message.answer("Send me a photo of furniture or an interior item you want to find.")

    @router.message(FurnitureSearchStates.waiting_for_photo, F.photo)
    async def photo_received(message: Message, state: FSMContext):
        largest_photo = message.photo[-1]
        await state.update_data(photo_file_id=largest_photo.file_id)
        await state.set_state(FurnitureSearchStates.waiting_for_city)
        await message.answer("What city should delivery be planned for?")

    @router.message(FurnitureSearchStates.waiting_for_photo)
    async def photo_missing(message: Message):
        await message.answer("Please send a furniture or interior photo first.")

    @router.message(FurnitureSearchStates.waiting_for_city)
    async def city_received(message: Message, state: FSMContext):
        city = (message.text or "").strip()
        if not city:
            await message.answer("Please send the delivery city as text.")
            return
        await state.update_data(city=city)
        await state.set_state(FurnitureSearchStates.waiting_for_budget)
        await message.answer("What is your maximum budget in USD?")

    @router.message(FurnitureSearchStates.waiting_for_budget)
    async def budget_received(message: Message, state: FSMContext, bot: Bot):
        try:
            budget = parse_budget(message.text or "")
        except ValueError:
            await message.answer("Please send a budget as a number, for example 500 or $1200.")
            return

        data = await state.get_data()
        await message.answer("Got it. Analyzing the photo and searching eBay...")
        try:
            image_bytes = await download_photo_bytes(bot, data["photo_file_id"])
            description, listings = await run_search(image_bytes, budget, vision_service, ebay_client)
        except Exception as exc:
            log_search_error(exc)
            await message.answer("Sorry, I could not complete the search right now. Please try again later.")
            return

        await message.answer(format_description(description, data.get("city", "your city"), budget))
        if not listings:
            await message.answer("I did not find matching eBay listings within this budget.")
        for index, listing in enumerate(listings, start=1):
            if listing.image_url:
                await message.answer_photo(listing.image_url, caption=format_listing(listing, index))
            else:
                await message.answer(format_listing(listing, index))
        await state.clear()

    return router
