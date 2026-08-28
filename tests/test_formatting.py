from app.formatting import format_description, format_listing
from app.models import EbayListing, FurnitureDescription


def test_format_description_summarizes_search():
    description = FurnitureDescription(
        item_type="accent chair",
        style="mid-century modern",
        colors=["green"],
        materials=["velvet"],
        details=["wooden legs"],
        search_query="green velvet accent chair wooden legs",
    )

    text = format_description(description, city="New York", budget=500)

    assert "accent chair" in text
    assert "New York" in text
    assert "$500" in text


def test_format_listing_includes_link_and_price():
    listing = EbayListing(
        title="Green Velvet Accent Chair",
        price="349.99 USD",
        url="https://www.ebay.com/itm/1",
        condition="New",
        shipping="25.00 USD shipping",
    )

    text = format_listing(listing, index=1)

    assert "1." in text
    assert "349.99 USD" in text
    assert "https://www.ebay.com/itm/1" in text
