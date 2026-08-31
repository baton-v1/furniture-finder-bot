import base64
import time

import httpx

from app.models import EbayListing


TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
BROWSE_SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"


def build_search_params(query: str, max_price: int, delivery_country: str, limit: int) -> dict[str, str | int]:
    return {
        "q": query,
        "limit": limit,
        "filter": f"price:[..{max_price}],deliveryCountry:{delivery_country}",
    }


def _format_price(data: dict | None) -> str:
    if not data:
        return "Price not listed"
    return f"{data.get('value')} {data.get('currency')}".strip()


def normalize_ebay_items(payload: dict) -> list[EbayListing]:
    listings: list[EbayListing] = []
    for item in payload.get("itemSummaries", []):
        shipping_options = item.get("shippingOptions") or []
        first_shipping = shipping_options[0] if shipping_options else {}
        shipping_cost = first_shipping.get("shippingCost")
        location = item.get("itemLocation") or {}
        listings.append(
            EbayListing(
                title=item.get("title", "Untitled listing"),
                price=_format_price(item.get("price")),
                url=item.get("itemWebUrl", ""),
                image_url=(item.get("image") or {}).get("imageUrl"),
                condition=item.get("condition"),
                location=" ".join(str(v) for v in [location.get("country"), location.get("postalCode")] if v),
                shipping=f"{_format_price(shipping_cost)} shipping" if shipping_cost else None,
            )
        )
    return [listing for listing in listings if listing.url]


class EbayClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        marketplace_id: str,
        delivery_country: str,
        max_results: int,
        proxy_url: str | None = None,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._marketplace_id = marketplace_id
        self._delivery_country = delivery_country
        self._max_results = max_results
        self._proxy_url = proxy_url
        self._access_token: str | None = None
        self._token_expires_at = 0.0

    @property
    def proxy_url(self) -> str | None:
        return self._proxy_url

    def _http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=20, proxy=self._proxy_url)

    async def _get_access_token(self) -> str:
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        credentials = f"{self._client_id}:{self._client_secret}".encode("utf-8")
        basic = base64.b64encode(credentials).decode("ascii")
        async with self._http_client() as client:
            response = await client.post(
                TOKEN_URL,
                headers={
                    "Authorization": f"Basic {basic}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
            )
            response.raise_for_status()

        payload = response.json()
        self._access_token = payload["access_token"]
        self._token_expires_at = time.time() + int(payload.get("expires_in", 7200))
        return self._access_token

    async def search(self, query: str, max_price: int) -> list[EbayListing]:
        token = await self._get_access_token()
        async with self._http_client() as client:
            response = await client.get(
                BROWSE_SEARCH_URL,
                params=build_search_params(query, max_price, self._delivery_country, self._max_results),
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": self._marketplace_id,
                },
            )
            response.raise_for_status()
        return normalize_ebay_items(response.json())
