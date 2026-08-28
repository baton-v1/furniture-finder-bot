import pytest

from app.bot import run_search
from app.models import EbayListing, FurnitureDescription


class FakeVision:
    async def analyze(self, image_bytes: bytes):
        assert image_bytes == b"image"
        return FurnitureDescription(
            item_type="chair",
            style="modern",
            colors=["green"],
            materials=["velvet"],
            details=[],
            search_query="green velvet chair",
        )


class FakeEbay:
    async def search(self, query: str, max_price: int):
        assert query == "green velvet chair"
        assert max_price == 500
        return [EbayListing(title="Chair", price="450 USD", url="https://ebay.com/item")]


@pytest.mark.asyncio
async def test_run_search_analyzes_image_and_searches_ebay():
    description, listings = await run_search(
        image_bytes=b"image",
        budget=500,
        vision_service=FakeVision(),
        ebay_client=FakeEbay(),
    )

    assert description.item_type == "chair"
    assert listings[0].title == "Chair"
