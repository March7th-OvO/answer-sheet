from fastapi.testclient import TestClient

from app.main import app


def test_root_route_returns_app_status() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"name": "answer-sheet", "status": "ok"}
