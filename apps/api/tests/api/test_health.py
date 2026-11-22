from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_body():
    response = client.get("/health")
    body = response.json()
    assert "status" in body
    assert body["status"] in ("healthy", "degraded")
    assert "dependencies" in body
    assert "postgresql" in body["dependencies"]
    assert "redis" in body["dependencies"]