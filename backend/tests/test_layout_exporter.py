from app.models.paper_config import PaperConfig
from app.services.layout_engine import build_layout
from app.services.layout_exporter import export_layout


def test_export_layout_uses_prd_coordinate_metadata() -> None:
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

    layout = build_layout(config, sheet_id="sheet_test")
    payload = export_layout(layout)

    assert payload["sheetId"] == "sheet_test"
    assert payload["unit"] == "mm"
    assert payload["coordinateSystem"] == "pdf_bottom_left"
    assert payload["pages"][0]["width"] == 210
    assert len(payload["pages"][0]["positionMarks"]) == 4
    assert payload["pages"][0]["sections"][0]["questions"][0]["options"][0]["option"] == "A"
