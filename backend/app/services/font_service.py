from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.errors import AppError


DEFAULT_FONT_PATH = Path("backend/assets/fonts/NotoSansCJKsc-Regular.otf")
DEFAULT_FONT_NAME = "NotoSansCJKsc"
FALLBACK_FONT_NAME = "Helvetica"


def ensure_font(
    font_path: Path | None = None,
    font_name: str | None = None,
    text_samples: list[str] | None = None,
) -> str:
    if font_name:
        return font_name

    candidate = font_path or DEFAULT_FONT_PATH
    if not candidate.exists():
        if text_samples and all(sample.isascii() for sample in text_samples):
            return FALLBACK_FONT_NAME
        raise AppError(
            "FONT_NOT_FOUND",
            "未找到可用中文字体，请在 backend/assets/fonts/ 目录下配置中文字体文件",
        )

    registered_names = pdfmetrics.getRegisteredFontNames()
    if DEFAULT_FONT_NAME not in registered_names:
        pdfmetrics.registerFont(TTFont(DEFAULT_FONT_NAME, str(candidate)))
    return DEFAULT_FONT_NAME
