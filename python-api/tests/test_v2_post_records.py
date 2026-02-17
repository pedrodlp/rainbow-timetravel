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


def test_v2_post_create_returns_version_1() -> None:
    client = TestClient(app)

    response = client.post("/api/v2/records/1", json={"hello": "world"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "version": 1,
        "data": {"hello": "world"},
    }


def test_v2_post_update_increments_version_and_applies_updates() -> None:
    client = TestClient(app)
    client.post("/api/v2/records/1", json={"hello": "world", "status": "ok"})

    response = client.post("/api/v2/records/1", json={"hello": "world 2", "status": None})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "version": 2,
        "data": {"hello": "world 2"},
    }


def test_v2_post_invalid_id_returns_400() -> None:
    client = TestClient(app)

    response = client.post("/api/v2/records/abc", json={"hello": "world"})

    assert response.status_code == 400
    assert response.json() == {"error": "invalid id; id must be a positive number"}


def test_v2_post_invalid_json_returns_400() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v2/records/1",
        content='{"hello": ',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid input; could not parse json"}


def test_v2_post_non_string_value_returns_400() -> None:
    client = TestClient(app)

    response = client.post("/api/v2/records/1", json={"hello": 123})

    assert response.status_code == 400
    assert response.json() == {"error": "invalid input; could not parse json"}
