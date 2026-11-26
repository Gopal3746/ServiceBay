import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.repairs import repairs, repair_keys


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    repairs.clear()
    repair_keys.clear()
    yield
    repairs.clear()
    repair_keys.clear()


def sample_repair():
    return {
        "dealership_id": "DEALER-001",
        "repair_order_id": "RO-1001",
        "vehicle_vin": "1HGCM82633A004352",
        "symptom": "Engine rattles during startup",
        "diagnosis": "Worn timing chain tensioner",
        "fix": "Replaced timing chain tensioner",
        "outcome": "Noise resolved",
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_repair():
    response = client.post("/repairs", json=sample_repair())

    assert response.status_code == 201
    assert response.json()["status"] == "received"
    assert response.json()["dealership_id"] == "DEALER-001"
    assert "id" in response.json()


def test_get_repair():
    created = client.post("/repairs", json=sample_repair())
    repair_id = created.json()["id"]

    response = client.get(f"/repairs/{repair_id}")

    assert response.status_code == 200
    assert response.json()["id"] == repair_id


def test_duplicate_repair():
    payload = sample_repair()

    first = client.post("/repairs", json=payload)
    second = client.post("/repairs", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_same_order_different_dealership():
    first = sample_repair()
    second = sample_repair()
    second["dealership_id"] = "DEALER-002"

    assert client.post("/repairs", json=first).status_code == 201
    assert client.post("/repairs", json=second).status_code == 201


def test_invalid_vin():
    payload = sample_repair()
    payload["vehicle_vin"] = "INVALID"

    response = client.post("/repairs", json=payload)

    assert response.status_code == 422


def test_missing_dealership():
    payload = sample_repair()
    del payload["dealership_id"]

    response = client.post("/repairs", json=payload)

    assert response.status_code == 422


def test_empty_symptom():
    payload = sample_repair()
    payload["symptom"] = "   "

    response = client.post("/repairs", json=payload)

    assert response.status_code == 422


def test_get_nonexistent_repair():
    response = client.get("/repairs/missing-id")

    assert response.status_code == 404
