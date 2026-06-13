import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.constants import APP_NAME
from app.core.validation import map_request_validation_error
from app.routers.answer_sheet import router as answer_sheet_router
from app.services.font_service import log_font_check

logger = logging.getLogger(APP_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    log_font_check(logger)
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"name": APP_NAME, "status": "ok"}


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    error_code, message = map_request_validation_error(exc)
    return JSONResponse(
        {
            "success": False,
            "errorCode": error_code,
            "message": message,
        },
        status_code=400,
    )


app.include_router(answer_sheet_router)
