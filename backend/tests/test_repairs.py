import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    TestSession = sessionmaker(bind=test_engine)

    def override_get_db():
        with TestSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


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


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_create_repair(client):
    response = client.post("/repairs", json=sample_repair())

    assert response.status_code == 201
    assert response.json()["status"] == "received"
    assert response.json()["dealership_id"] == "DEALER-001"
    assert response.json()["created_at"]
    assert response.json()["id"]


def test_get_repair(client):
    created = client.post("/repairs", json=sample_repair())
    repair_id = created.json()["id"]

    response = client.get(f"/repairs/{repair_id}")

    assert response.status_code == 200
    assert response.json()["id"] == repair_id


def test_duplicate_repair(client):
    payload = sample_repair()

    first = client.post("/repairs", json=payload)
    second = client.post("/repairs", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_same_order_different_dealership(client):
    first = sample_repair()
    second = sample_repair()
    second["dealership_id"] = "DEALER-002"

    assert client.post("/repairs", json=first).status_code == 201
    assert client.post("/repairs", json=second).status_code == 201


def test_invalid_vin(client):
    payload = sample_repair()
    payload["vehicle_vin"] = "INVALID"

    response = client.post("/repairs", json=payload)
    assert response.status_code == 422


def test_missing_dealership(client):
    payload = sample_repair()
    del payload["dealership_id"]

    response = client.post("/repairs", json=payload)
    assert response.status_code == 422


def test_empty_symptom(client):
    payload = sample_repair()
    payload["symptom"] = "   "

    response = client.post("/repairs", json=payload)
    assert response.status_code == 422


def test_get_nonexistent_repair(client):
    response = client.get("/repairs/missing-id")
    assert response.status_code == 404


def test_repair_persists_between_requests(client):
    created = client.post("/repairs", json=sample_repair())

    repair_id = created.json()["id"]

    first_read = client.get(f"/repairs/{repair_id}")
    second_read = client.get(f"/repairs/{repair_id}")

    assert first_read.status_code == 200
    assert second_read.status_code == 200
    assert first_read.json() == second_read.json()


def test_duplicate_does_not_delete_original(client):
    payload = sample_repair()

    original = client.post("/repairs", json=payload)
    duplicate = client.post("/repairs", json=payload)

    assert original.status_code == 201
    assert duplicate.status_code == 409

    repair_id = original.json()["id"]
    stored = client.get(f"/repairs/{repair_id}")

    assert stored.status_code == 200
    assert stored.json()["repair_order_id"] == "RO-1001"
