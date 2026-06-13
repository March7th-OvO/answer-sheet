import logging
from pathlib import Path

from app.services.font_service import log_font_check


def test_log_font_check_writes_warning_when_font_is_missing(caplog) -> None:
    logger = logging.getLogger("answer-sheet.tests")

    with caplog.at_level(logging.WARNING):
        log_font_check(logger, font_path=Path("missing-font.otf"))

    assert "未找到可用中文字体" in caplog.text
    assert "backend/assets/fonts/" in caplog.text
