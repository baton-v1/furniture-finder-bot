import pytest

from app.openai_vision import parse_furniture_description


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
    with pytest.raises(ValueError, match="OpenAI"):
        parse_furniture_description("not-json")
