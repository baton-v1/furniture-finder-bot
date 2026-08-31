import base64
import json

import httpx
from openai import AsyncOpenAI

from app.models import FurnitureDescription


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "qwen/qwen3.6-27b"
SYSTEM_PROMPT = (
    "You identify furniture and interior decor from photos. "
    "Return only compact JSON with keys: item_type, style, colors, materials, details, search_query. "
    "The search_query must be English and suitable for eBay furniture search."
)


def parse_furniture_description(raw_json: str) -> FurnitureDescription:
    try:
        data = json.loads(raw_json)
        return FurnitureDescription(
            item_type=str(data["item_type"]),
            style=str(data.get("style", "")),
            colors=[str(item) for item in data.get("colors", [])],
            materials=[str(item) for item in data.get("materials", [])],
            details=[str(item) for item in data.get("details", [])],
            search_query=str(data["search_query"]),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError("Groq image analysis returned invalid furniture JSON") from exc


class GroqVisionService:
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        proxy_url: str | None = None,
        base_url: str = GROQ_BASE_URL,
    ):
        http_client = httpx.AsyncClient(proxy=proxy_url) if proxy_url else None
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        self._model = model
        self._base_url = base_url

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

    async def analyze(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> FurnitureDescription:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        response = await self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": SYSTEM_PROMPT},
                        {
                            "type": "input_image",
                            "detail": "auto",
                            "image_url": f"data:{mime_type};base64,{encoded}",
                        },
                    ],
                }
            ],
        )
        return parse_furniture_description(response.output_text)
