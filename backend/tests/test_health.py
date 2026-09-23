from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_dashboard_summary():
    with TestClient(app) as client:
        response = client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_candidates" in data
        assert "completed_interviews" in data
        assert "average_score" in data


def test_candidates_pagination():
    with TestClient(app) as client:
        response = client.get("/api/v1/candidates?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data


def test_candidates_compare():
    with TestClient(app) as client:
        response = client.get("/api/v1/candidates/compare")
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
