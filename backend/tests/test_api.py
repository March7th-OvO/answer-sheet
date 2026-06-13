from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.routers import answer_sheet as answer_sheet_router
from app.services.file_service import FileService


def test_generate_answer_sheet_returns_download_urls(tmp_path: Path) -> None:
    answer_sheet_router.file_service = FileService(base_dir=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/answer-sheet/generate",
        json={
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
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["pdfUrl"].endswith(".pdf")
    assert payload["layoutJsonUrl"].endswith("_layout.json")


def test_generate_answer_sheet_returns_height_error(tmp_path: Path) -> None:
    answer_sheet_router.file_service = FileService(base_dir=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/answer-sheet/generate",
        json={
            "paperTitle": "Answer Sheet",
            "examName": "Final Exam",
            "pageSize": "A4",
            "studentFields": ["Name", "Student ID"],
            "showPositionMarks": True,
            "sections": [
                {
                    "type": "choice",
                    "title": "Choices",
                    "questionCount": 40,
                    "optionCount": 4,
                    "options": ["A", "B", "C", "D"],
                    "questionsPerRow": 4,
                    "questionsPerColumn": 10,
                    "fillOrder": "column_first",
                },
                {
                    "type": "calculation",
                    "title": "Calculations",
                    "questionCount": 8,
                    "heightPerQuestion": 35,
                },
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["errorCode"] == "PAGE_HEIGHT_EXCEEDED"


def test_download_rejects_invalid_file_name(tmp_path: Path) -> None:
    answer_sheet_router.file_service = FileService(base_dir=tmp_path)
    client = TestClient(app)

    response = client.get("/api/files/..%2F..%2Fetc%2Fpasswd")

    assert response.status_code == 400
    assert response.json()["errorCode"] == "INVALID_FILE_NAME"


def test_generate_answer_sheet_maps_validation_error_to_invalid_request(tmp_path: Path) -> None:
    answer_sheet_router.file_service = FileService(base_dir=tmp_path)
    client = TestClient(app)

    response = client.post(
        "/api/answer-sheet/generate",
        json={
            "paperTitle": "测试答题卡",
            "examName": "选项测试",
            "pageSize": "A4",
            "studentFields": ["姓名", "学号"],
            "showPositionMarks": True,
            "sections": [
                {
                    "type": "choice",
                    "title": "一、选择题",
                    "questionCount": 10,
                    "optionCount": 4,
                    "options": ["A", "B", "C"],
                    "questionsPerRow": 2,
                    "questionsPerColumn": 5,
                    "fillOrder": "column_first",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "errorCode": "OPTION_COUNT_MISMATCH",
        "message": "optionCount 必须等于 options.length",
    }


def test_download_json_returns_utf8_content_type(tmp_path: Path) -> None:
    service = FileService(base_dir=tmp_path)
    answer_sheet_router.file_service = service
    task_id = "sheet_20260613_001"
    service.save_json(task_id, '{"sheetId":"sheet_20260613_001"}'.encode("utf-8"))
    client = TestClient(app)

    response = client.get(f"/api/files/{task_id}_layout.json")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"


def test_download_rejects_non_pdf_or_json_extensions(tmp_path: Path) -> None:
    answer_sheet_router.file_service = FileService(base_dir=tmp_path)
    client = TestClient(app)

    response = client.get("/api/files/sheet_20260613_001.txt")

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "errorCode": "INVALID_FILE_NAME",
        "message": "只允许下载 PDF 或 JSON 文件",
    }


def test_generate_answer_sheet_maps_unexpected_error_to_internal_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answer_sheet_router.file_service = FileService(base_dir=tmp_path)
    client = TestClient(app)

    def raise_unexpected_error(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(answer_sheet_router, "render_pdf", raise_unexpected_error)

    response = client.post(
        "/api/answer-sheet/generate",
        json={
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
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "errorCode": "INTERNAL_ERROR",
        "message": "服务内部错误，请稍后重试",
    }
