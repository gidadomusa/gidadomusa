from fastapi.testclient import TestClient
from backend.app.api import create_app


def test_health_endpoint():
    client = TestClient(create_app())
    resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
