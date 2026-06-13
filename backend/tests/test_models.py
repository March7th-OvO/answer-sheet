import pytest
from pydantic import ValidationError

from app.models.paper_config import PaperConfig


def build_valid_payload() -> dict:
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
            }
        ],
    }


def test_paper_config_accepts_valid_payload() -> None:
    config = PaperConfig.model_validate(build_valid_payload())

    assert config.page_size == "A4"
    assert len(config.sections) == 1


def test_paper_config_rejects_option_count_mismatch() -> None:
    payload = build_valid_payload()
    payload["sections"][0]["options"] = ["A", "B", "C"]

    with pytest.raises(ValidationError):
        PaperConfig.model_validate(payload)


def test_paper_config_rejects_unsupported_page_size() -> None:
    payload = build_valid_payload()
    payload["pageSize"] = "A3"

    with pytest.raises(ValidationError):
        PaperConfig.model_validate(payload)


def test_paper_config_rejects_empty_student_fields() -> None:
    payload = build_valid_payload()
    payload["studentFields"] = []

    with pytest.raises(ValidationError):
        PaperConfig.model_validate(payload)
