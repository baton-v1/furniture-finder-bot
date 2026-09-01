import pytest

from app.groq_vision import GroqVisionService, parse_furniture_description


def test_parse_furniture_description_returns_structured_model():
    raw = """
    {
      "item_type": "accent chair",
      "style": "mid-century modern",
      "colors": ["olive green", "walnut"],
      "materials": ["velvet", "wood"],
      "details": ["slim tapered legs"],
      "search_query": "mid century modern olive velvet accent chair wooden legs"
    }
    """

    description = parse_furniture_description(raw)

    assert description.item_type == "accent chair"
    assert description.search_query == "mid century modern olive velvet accent chair wooden legs"
    assert "velvet" in description.materials


def test_parse_furniture_description_rejects_invalid_json():
    with pytest.raises(ValueError, match="Groq"):
        parse_furniture_description("not-json")


def test_parse_furniture_description_accepts_markdown_json_block():
    raw = """
    Here is the JSON:

    ```json
    {
      "item_type": "coffee table",
      "style": "industrial",
      "colors": ["black", "oak"],
      "materials": ["metal", "wood"],
      "details": ["round top"],
      "search_query": "industrial round oak coffee table black metal"
    }
    ```
    """

    description = parse_furniture_description(raw)

    assert description.item_type == "coffee table"
    assert description.search_query == "industrial round oak coffee table black metal"


def test_groq_service_uses_groq_defaults():
    service = GroqVisionService(api_key="groq-key")

    assert service.model == "qwen/qwen3.6-27b"
    assert service.base_url == "https://api.groq.com/openai/v1"
