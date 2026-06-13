import logging
from pathlib import Path
from dataclasses import dataclass

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.errors import AppError


DEFAULT_FONT_PATH = Path("backend/assets/fonts/NotoSansCJKsc-Regular.otf")
DEFAULT_FONT_NAME = "NotoSansCJKsc"
FALLBACK_FONT_NAME = "Helvetica"


@dataclass(slots=True)
class FontCheckResult:
    available: bool
    path: Path
    message: str


def inspect_font(font_path: Path | None = None) -> FontCheckResult:
    candidate = font_path or DEFAULT_FONT_PATH
    if candidate.exists():
        return FontCheckResult(True, candidate, f"已检测到中文字体文件：{candidate.as_posix()}")

    return FontCheckResult(
        False,
        candidate,
        "未找到可用中文字体，请在 backend/assets/fonts/ 目录下配置中文字体文件",
    )


def log_font_check(logger: logging.Logger, font_path: Path | None = None) -> None:
    result = inspect_font(font_path)
    if result.available:
        logger.info(result.message)
        return

    logger.warning("%s（检查路径：%s）", result.message, result.path.as_posix())


def ensure_font(
    font_path: Path | None = None,
    font_name: str | None = None,
    text_samples: list[str] | None = None,
) -> str:
    if font_name:
        return font_name

    status = inspect_font(font_path)
    if not status.available:
        if text_samples and all(sample.isascii() for sample in text_samples):
            return FALLBACK_FONT_NAME
        raise AppError(
            "FONT_NOT_FOUND",
            status.message,
        )

    registered_names = pdfmetrics.getRegisteredFontNames()
    if DEFAULT_FONT_NAME not in registered_names:
        pdfmetrics.registerFont(TTFont(DEFAULT_FONT_NAME, str(status.path)))
    return DEFAULT_FONT_NAME
