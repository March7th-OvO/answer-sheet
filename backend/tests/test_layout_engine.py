import pytest

from app.core.errors import AppError
from app.models.paper_config import PaperConfig
from app.services.layout_engine import build_layout


def build_payload() -> dict:
    return {
        "paperTitle": "软件工程期末考试答题卡",
        "examName": "2026年春季学期期末考试",
        "pageSize": "A4",
        "studentFields": ["姓名", "学号", "班级"],
        "showPositionMarks": True,
        "sections": [
            {
                "type": "choice",
                "title": "一、选择题",
                "questionCount": 20,
                "optionCount": 4,
                "options": ["A", "B", "C", "D"],
                "questionsPerRow": 4,
                "questionsPerColumn": 5,
                "fillOrder": "column_first",
            },
            {
                "type": "blank",
                "title": "二、填空题",
                "questionCount": 3,
                "linesPerQuestion": 1,
            },
            {
                "type": "calculation",
                "title": "三、计算题",
                "questionCount": 2,
                "heightPerQuestion": 25,
            },
        ],
    }


def test_build_layout_returns_single_a4_page_with_sections() -> None:
    config = PaperConfig.model_validate(build_payload())

    layout = build_layout(config)

    assert layout.paper_title == "软件工程期末考试答题卡"
    assert layout.page.width == 210
    assert layout.page.height == 297
    assert len(layout.page.position_marks) == 4
    assert [section.type for section in layout.page.sections] == [
        "choice",
        "blank",
        "calculation",
    ]
    assert layout.page.sections[0].questions[0].question_no == 1


def test_build_layout_rejects_choice_grid_capacity_overflow() -> None:
    payload = build_payload()
    payload["sections"][0]["questionCount"] = 21

    config = PaperConfig.model_validate(payload)

    with pytest.raises(AppError, match="CHOICE_GRID_CAPACITY_EXCEEDED"):
        build_layout(config)


def test_build_layout_rejects_page_height_overflow() -> None:
    payload = build_payload()
    payload["sections"][2]["questionCount"] = 8
    payload["sections"][2]["heightPerQuestion"] = 35

    config = PaperConfig.model_validate(payload)

    with pytest.raises(AppError, match="PAGE_HEIGHT_EXCEEDED"):
        build_layout(config)
