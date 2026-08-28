from app.models import EbayListing, FurnitureDescription


def format_description(description: FurnitureDescription, city: str, budget: int) -> str:
    return (
        "I found the item style:\n"
        f"- Type: {description.item_type}\n"
        f"- Style: {description.style or 'not specified'}\n"
        f"- Colors: {', '.join(description.colors) or 'not specified'}\n"
        f"- Materials: {', '.join(description.materials) or 'not specified'}\n"
        f"- Delivery city: {city}\n"
        f"- Budget: ${budget}\n\n"
        "Searching eBay now..."
    )


def format_listing(listing: EbayListing, index: int) -> str:
    lines = [
        f"{index}. {listing.title}",
        f"Price: {listing.price}",
    ]
    if listing.condition:
        lines.append(f"Condition: {listing.condition}")
    if listing.location:
        lines.append(f"Location: {listing.location}")
    if listing.shipping:
        lines.append(f"Shipping: {listing.shipping}")
    lines.append(listing.url)
    return "\n".join(lines)
