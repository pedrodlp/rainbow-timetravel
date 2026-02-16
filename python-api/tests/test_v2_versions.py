import pytest
from fastapi.testclient import TestClient

from app.core.db import get_connection, init_db
from app.main import app


@pytest.fixture(autouse=True)
def clear_tables() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM record_versions")
        conn.execute("DELETE FROM records")
        conn.commit()


def test_v2_versions_invalid_id_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v2/records/abc/versions")

    assert response.status_code == 400
    assert response.json() == {"error": "invalid id; id must be a positive number"}


def test_v2_versions_missing_record_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v2/records/999/versions")

    assert response.status_code == 400
    assert response.json() == {"error": "record of id 999 does not exist"}


def test_v2_versions_lists_all_versions_in_order() -> None:
    client = TestClient(app)

    client.post("/api/v2/records/7", json={"hello": "v1"})
    client.post("/api/v2/records/7", json={"hello": "v2"})
    client.post("/api/v2/records/7", json={"hello": "v3"})

    response = client.get("/api/v2/records/7/versions")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 7
    assert [item["version"] for item in body["versions"]] == [1, 2, 3]
    assert all(isinstance(item["created_at"], str) and item["created_at"] for item in body["versions"])


def test_v2_versions_includes_history_from_v1_writes() -> None:
    client = TestClient(app)

    client.post("/api/v1/records/42", json={"state": "a"})
    client.post("/api/v1/records/42", json={"state": "b"})

    response = client.get("/api/v2/records/42/versions")

    assert response.status_code == 200
    assert [item["version"] for item in response.json()["versions"]] == [1, 2]
