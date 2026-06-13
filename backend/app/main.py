from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.constants import APP_NAME
from app.routers.answer_sheet import router as answer_sheet_router

app = FastAPI(title=APP_NAME)

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


app.include_router(answer_sheet_router)
