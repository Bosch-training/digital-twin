from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200_and_healthy_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_is_identical_across_repeated_calls():
    responses = [client.get("/health") for _ in range(3)]

    assert {r.status_code for r in responses} == {200}
    assert all(r.json() == {"status": "healthy"} for r in responses)


def test_health_rejects_non_get_methods():
    assert client.post("/health").status_code == 405
