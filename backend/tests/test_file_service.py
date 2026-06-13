from pathlib import Path

import pytest

from app.core.errors import AppError
from app.services.file_service import FileService


def test_file_service_writes_pdf_and_json_with_task_id(tmp_path: Path) -> None:
    service = FileService(base_dir=tmp_path)

    task_id = service.create_task_id()
    pdf_path = service.save_pdf(task_id, b"%PDF-1.4 test")
    json_path = service.save_json(task_id, b"{}")

    assert pdf_path.name == f"{task_id}.pdf"
    assert json_path.name == f"{task_id}_layout.json"


def test_file_service_rejects_invalid_download_name(tmp_path: Path) -> None:
    service = FileService(base_dir=tmp_path)

    with pytest.raises(AppError, match="INVALID_FILE_NAME"):
        service.resolve_download_path("../../etc/passwd")


def test_file_service_allows_only_pdf_and_json_files(tmp_path: Path) -> None:
    service = FileService(base_dir=tmp_path)
    invalid_file = tmp_path / "pdf" / "bad.txt"
    invalid_file.parent.mkdir(parents=True, exist_ok=True)
    invalid_file.write_text("bad", encoding="utf-8")

    with pytest.raises(AppError, match="INVALID_FILE_NAME"):
        service.resolve_download_path("bad.txt")
