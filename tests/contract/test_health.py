from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_returns_200_with_status_and_version() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("status"), str) and payload["status"]
    assert isinstance(payload.get("version"), str) and payload["version"]
