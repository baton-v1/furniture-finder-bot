from dataclasses import dataclass


@dataclass(frozen=True)
class FurnitureDescription:
    item_type: str
    style: str
    colors: list[str]
    materials: list[str]
    details: list[str]
    search_query: str


@dataclass(frozen=True)
class EbayListing:
    title: str
    price: str
    url: str
    image_url: str | None = None
    condition: str | None = None
    location: str | None = None
    shipping: str | None = None
