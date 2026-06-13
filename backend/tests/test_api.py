from pathlib import Path

from fastapi.testclient import TestClient

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
