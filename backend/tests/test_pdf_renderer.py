from pathlib import Path

import pytest

from app.core.errors import AppError
from app.services import pdf_renderer as pdf_renderer_module
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
        render_pdf(layout, exam_name=config.examName, student_fields=config.studentFields, font_path=Path("missing.otf"))


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
        exam_name=config.examName,
        student_fields=config.studentFields,
        font_name="Helvetica",
    )

    assert pdf_bytes.startswith(b"%PDF")


def test_render_pdf_uses_prd_style_for_title_student_fields_and_blank_lines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = PaperConfig.model_validate(
        {
            "paperTitle": "Answer Sheet",
            "examName": "Midterm Exam",
            "pageSize": "A4",
            "studentFields": ["Name", "Student ID"],
            "showPositionMarks": True,
            "sections": [
                {
                    "type": "choice",
                    "title": "Choices",
                    "questionCount": 1,
                    "optionCount": 4,
                    "options": ["A", "B", "C", "D"],
                    "questionsPerRow": 1,
                    "questionsPerColumn": 1,
                    "fillOrder": "column_first",
                },
                {
                    "type": "blank",
                    "title": "Blanks",
                    "questionCount": 1,
                    "linesPerQuestion": 1,
                },
                {
                    "type": "calculation",
                    "title": "Calculation",
                    "questionCount": 1,
                    "heightPerQuestion": 25,
                },
            ],
        }
    )
    layout = build_layout(config)
    operations: list[tuple] = []

    class FakeCanvas:
        def __init__(self, *_args, **_kwargs):
            pass

        def setTitle(self, title):
            operations.append(("setTitle", title))

        def setFont(self, font_name, size):
            operations.append(("setFont", font_name, size))

        def drawString(self, x, y, text):
            operations.append(("drawString", x, y, text))

        def drawCentredString(self, x, y, text):
            operations.append(("drawCentredString", x, y, text))

        def circle(self, x, y, radius):
            operations.append(("circle", x, y, radius))

        def rect(self, x, y, width, height):
            operations.append(("rect", x, y, width, height))

        def line(self, x1, y1, x2, y2):
            operations.append(("line", x1, y1, x2, y2))

        def showPage(self):
            operations.append(("showPage",))

        def save(self):
            operations.append(("save",))

    monkeypatch.setattr(pdf_renderer_module, "ensure_font", lambda **_kwargs: "Helvetica")
    monkeypatch.setattr(pdf_renderer_module.canvas, "Canvas", FakeCanvas)

    pdf_bytes = render_pdf(layout, exam_name=config.examName, student_fields=config.studentFields)

    assert pdf_bytes == b""
    assert ("drawCentredString", pytest.approx(pdf_renderer_module.to_pt(105)), pytest.approx(pdf_renderer_module.to_pt(276)), "Answer Sheet") in operations
    assert ("drawCentredString", pytest.approx(pdf_renderer_module.to_pt(105)), pytest.approx(pdf_renderer_module.to_pt(268)), "Midterm Exam") in operations
    assert any(operation[0] == "drawString" and "Name：" in operation[3] for operation in operations)
    assert any(operation[0] == "drawString" and operation[3] == "1." for operation in operations)
    assert any(operation[0] == "line" for operation in operations)
    assert any(operation[0] == "rect" for operation in operations)


def test_render_pdf_supports_bundled_default_chinese_font() -> None:
    config = PaperConfig.model_validate(
        {
            "paperTitle": "软件工程期末考试答题卡",
            "examName": "2026年春季学期期末考试",
            "pageSize": "A4",
            "studentFields": ["姓名", "学号", "班级"],
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

    pdf_bytes = render_pdf(layout, exam_name=config.examName, student_fields=config.studentFields)

    assert pdf_bytes.startswith(b"%PDF")
