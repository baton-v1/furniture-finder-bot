from app.ebay import build_search_params, normalize_ebay_items


def test_build_search_params_includes_budget_and_delivery_country():
    params = build_search_params(
        query="green velvet accent chair",
        max_price=500,
        delivery_country="US",
        limit=5,
    )

    assert params["q"] == "green velvet accent chair"
    assert params["limit"] == 5
    assert "price:[..500]" in params["filter"]
    assert "deliveryCountry:US" in params["filter"]


def test_normalize_ebay_items_extracts_safe_listing_fields():
    payload = {
        "itemSummaries": [
            {
                "title": "Green Velvet Accent Chair",
                "itemWebUrl": "https://www.ebay.com/itm/1",
                "price": {"value": "349.99", "currency": "USD"},
                "image": {"imageUrl": "https://i.ebayimg.com/image.jpg"},
                "condition": "New",
                "itemLocation": {"country": "US", "postalCode": "10001"},
                "shippingOptions": [{"shippingCost": {"value": "25.00", "currency": "USD"}}],
            }
        ]
    }

    listings = normalize_ebay_items(payload)

    assert listings[0].title == "Green Velvet Accent Chair"
    assert listings[0].price == "349.99 USD"
    assert listings[0].shipping == "25.00 USD shipping"
