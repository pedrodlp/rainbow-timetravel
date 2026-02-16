import pytest
from fastapi.testclient import TestClient

from app.core.db import get_connection, init_db
from app.main import app
from app.repositories.record_repo import RecordRepository


@pytest.fixture(autouse=True)
def clear_tables() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM record_versions")
        conn.execute("DELETE FROM records")
        conn.commit()


def test_v2_get_latest_record_success() -> None:
    repo = RecordRepository()
    repo.write_latest_and_version(1, {"hello": "v1"})
    repo.write_latest_and_version(1, {"hello": "v2"})

    client = TestClient(app)
    response = client.get("/api/v2/records/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "data": {"hello": "v2"}}


def test_v2_get_specific_version_success() -> None:
    repo = RecordRepository()
    repo.write_latest_and_version(1, {"hello": "v1"})
    repo.write_latest_and_version(1, {"hello": "v2"})

    client = TestClient(app)
    response = client.get("/api/v2/records/1?version=1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "data": {"hello": "v1"}}


def test_v2_get_invalid_id_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v2/records/abc")

    assert response.status_code == 400
    assert response.json() == {"error": "invalid id; id must be a positive number"}


def test_v2_get_invalid_version_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v2/records/1?version=abc")

    assert response.status_code == 400
    assert response.json() == {"error": "invalid version; version must be a positive number"}


def test_v2_get_missing_record_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v2/records/999")

    assert response.status_code == 400
    assert response.json() == {"error": "record of id 999 does not exist"}


def test_v2_get_missing_version_returns_400() -> None:
    repo = RecordRepository()
    repo.write_latest_and_version(1, {"hello": "v1"})

    client = TestClient(app)
    response = client.get("/api/v2/records/1?version=99")

    assert response.status_code == 400
    assert response.json() == {"error": "record of id 1 does not exist at version 99"}
