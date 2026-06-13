from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from app.core.errors import AppError
from app.models.paper_config import PaperConfig
from app.services.file_service import FileService
from app.services.layout_engine import build_layout
from app.services.layout_exporter import export_layout
from app.services.pdf_renderer import render_pdf

router = APIRouter(prefix="/api", tags=["answer-sheet"])
file_service = FileService()


@router.post("/answer-sheet/generate")
def generate_answer_sheet(config: PaperConfig) -> JSONResponse:
    try:
        task_id = file_service.create_task_id()
        layout = build_layout(config, sheet_id=task_id)
        pdf_bytes = render_pdf(layout, exam_name=config.exam_name, student_fields=config.student_fields)
        layout_payload = export_layout(layout)
        file_service.save_pdf(task_id, pdf_bytes)
        file_service.save_json(task_id, json.dumps(layout_payload, ensure_ascii=False, indent=2).encode("utf-8"))
        return JSONResponse(
            {
                "success": True,
                "taskId": task_id,
                "pdfUrl": f"/api/files/{task_id}.pdf",
                "layoutJsonUrl": f"/api/files/{task_id}_layout.json",
                "message": "答题卡生成成功",
            }
        )
    except AppError as exc:
        return JSONResponse(
            {
                "success": False,
                "errorCode": exc.error_code,
                "message": exc.message,
            },
            status_code=400,
        )


@router.get("/files/{file_name:path}")
def download_file(file_name: str):
    try:
        file_path = file_service.resolve_download_path(file_name)
        media_type = "application/pdf" if file_path.suffix == ".pdf" else "application/json; charset=utf-8"
        return FileResponse(file_path, media_type=media_type, filename=file_path.name)
    except AppError as exc:
        return JSONResponse(
            {
                "success": False,
                "errorCode": exc.error_code,
                "message": exc.message,
            },
            status_code=400,
        )
