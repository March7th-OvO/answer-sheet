import logging
from pathlib import Path

import pytest

from app.services.font_service import DEFAULT_FONT_PATH, inspect_font, log_font_check


def test_log_font_check_writes_warning_when_font_is_missing(caplog) -> None:
    logger = logging.getLogger("answer-sheet.tests")

    with caplog.at_level(logging.WARNING):
        log_font_check(logger, font_path=Path("missing-font.otf"))

    assert "未找到可用中文字体" in caplog.text
    assert "backend/assets/fonts/" in caplog.text


def test_inspect_font_uses_repo_relative_default_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = inspect_font()

    assert result.available is True
    assert result.path == DEFAULT_FONT_PATH
