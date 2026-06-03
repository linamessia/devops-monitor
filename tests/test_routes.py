import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)
API_KEY = "dev-secret"


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_metrics_returns_cpu():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "cpu_percent" in resp.json()


def test_post_server_without_key_returns_403():
    resp = client.post("/servers", json={"name": "test", "host": "10.0.0.1", "port": 8080})
    assert resp.status_code == 403


def test_post_server_with_key_returns_201():
    resp = client.post(
        "/servers",
        json={"name": "test-server", "host": "10.0.0.1", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test-server"
    assert data["status"] == "unknown"


def test_server_appears_in_list():
    client.post(
        "/servers",
        json={"name": "listed-server", "host": "10.0.0.2", "port": 9090},
        headers={"X-API-Key": API_KEY},
    )
    resp = client.get("/servers")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert "listed-server" in names


def test_get_nonexistent_server_returns_404():
    resp = client.get("/servers/99999")
    assert resp.status_code == 404