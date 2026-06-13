from pathlib import Path

import pytest

from app.core.errors import AppError
from app.models.paper_config import PaperConfig
from app.services.layout_engine import build_layout
from app.services.pdf_renderer import render_pdf


def test_render_pdf_raises_font_not_found_for_missing_font_file() -> None:
    config = PaperConfig.model_validate(
        {
            "paperTitle": "软件工程期末考试答题卡",
            "examName": "2026年春季学期期末考试",
            "pageSize": "A4",
            "studentFields": ["姓名", "学号"],
            "showPositionMarks": True,
            "sections": [
                {
                    "type": "choice",
                    "title": "一、选择题",
                    "questionCount": 4,
                    "optionCount": 4,
                    "options": ["A", "B", "C", "D"],
                    "questionsPerRow": 2,
                    "questionsPerColumn": 2,
                    "fillOrder": "column_first",
                }
            ],
        }
    )
    layout = build_layout(config)

    with pytest.raises(AppError, match="FONT_NOT_FOUND"):
        render_pdf(layout, exam_name=config.exam_name, student_fields=config.student_fields, font_path=Path("missing.otf"))


def test_render_pdf_returns_pdf_bytes_when_font_name_is_available() -> None:
    config = PaperConfig.model_validate(
        {
            "paperTitle": "Answer Sheet",
            "examName": "Final Exam",
            "pageSize": "A4",
            "studentFields": ["Name", "Student ID"],
            "showPositionMarks": True,
            "sections": [
                {
                    "type": "blank",
                    "title": "Blanks",
                    "questionCount": 2,
                    "linesPerQuestion": 1,
                }
            ],
        }
    )
    layout = build_layout(config)

    pdf_bytes = render_pdf(
        layout,
        exam_name=config.exam_name,
        student_fields=config.student_fields,
        font_name="Helvetica",
    )

    assert pdf_bytes.startswith(b"%PDF")
