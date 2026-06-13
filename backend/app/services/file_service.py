from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from app.core.errors import AppError


SAFE_FILE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


class FileService:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path("backend/app/output")
        self.pdf_dir = self.base_dir / "pdf"
        self.json_dir = self.base_dir / "json"
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.json_dir.mkdir(parents=True, exist_ok=True)

    def create_task_id(self) -> str:
        return datetime.now().strftime("sheet_%Y%m%d_%H%M%S")

    def save_pdf(self, task_id: str, content: bytes) -> Path:
        path = self.pdf_dir / f"{task_id}.pdf"
        path.write_bytes(content)
        return path

    def save_json(self, task_id: str, content: bytes) -> Path:
        path = self.json_dir / f"{task_id}_layout.json"
        path.write_bytes(content)
        return path

    def resolve_download_path(self, file_name: str) -> Path:
        if not SAFE_FILE_RE.fullmatch(file_name):
            raise AppError("INVALID_FILE_NAME", "文件名非法")
        if not (file_name.endswith(".pdf") or file_name.endswith(".json")):
            raise AppError("INVALID_FILE_NAME", "文件名非法")

        path = self.pdf_dir / file_name if file_name.endswith(".pdf") else self.json_dir / file_name
        if not path.exists():
            raise AppError("FILE_NOT_FOUND", "文件不存在")
        return path
