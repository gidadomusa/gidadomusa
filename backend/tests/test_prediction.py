from fastapi.testclient import TestClient

from app.main import app


def test_prediction_returns_explanation():
    client = TestClient(app)
    response = client.post(
        "/api/predict",
        json={
            "amount": 850,
            "hour": 2,
            "distance_from_home_km": 300,
            "recent_transaction_count": 8,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["risk_label"] in {"low", "high"}
    assert body["explanations"]