import logging

from app.bot import log_search_error


def test_log_search_error_records_exception(caplog):
    with caplog.at_level(logging.ERROR):
        log_search_error(RuntimeError("openai failed"))

    assert "Furniture search failed" in caplog.text
    assert "openai failed" in caplog.text
