"""Contract tests for public FastAPI endpoints.

Author: Leslie Raya
"""

from fastapi.testclient import TestClient

from backend.main import app


def test_health_contract() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_event_limit_is_validated() -> None:
    with TestClient(app) as client:
        response = client.get("/events?limit=0")
    assert response.status_code == 422


def test_overview_contract() -> None:
    with TestClient(app) as client:
        payload = client.get("/overview").json()
    assert {"generated_at", "stats", "events", "rule_alerts", "ml_alert"} <= payload.keys()
