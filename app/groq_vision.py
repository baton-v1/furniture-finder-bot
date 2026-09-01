import base64
import json
import re

import httpx
from openai import AsyncOpenAI

from app.models import FurnitureDescription


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "qwen/qwen3.6-27b"
SYSTEM_PROMPT = (
    "You identify furniture and interior decor from photos. "
    "Return only valid compact JSON with keys: item_type, style, colors, materials, details, search_query. "
    "The search_query must be English and suitable for eBay furniture search. Do not include markdown."
)


def _extract_json(raw_text: str) -> str:
    stripped = raw_text.strip()
    if stripped.startswith("{"):
        return stripped
    fenced_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        return fenced_match.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


def parse_furniture_description(raw_json: str) -> FurnitureDescription:
    try:
        data = json.loads(_extract_json(raw_json))
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
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SYSTEM_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded}",
                            },
                        },
                    ],
                }
            ],
            temperature=1e-8,
            max_completion_tokens=1024,
        )
        content = response.choices[0].message.content or ""
        return parse_furniture_description(content)
