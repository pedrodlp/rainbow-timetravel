import pytest
from fastapi.testclient import TestClient

from app.core.db import get_connection, init_db
from app.main import app


@pytest.fixture(autouse=True)
def clear_records_table() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM records")
        conn.commit()


def test_post_create_record() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/records/1", json={"hello": "world"})

    assert response.status_code == 200
    assert response.json() == {"id": 1, "data": {"hello": "world"}}


def test_post_create_omits_null_fields() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/records/1", json={"hello": None, "status": "ok"})

    assert response.status_code == 200
    assert response.json() == {"id": 1, "data": {"status": "ok"}}


def test_post_invalid_id_returns_400() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/records/abc", json={"hello": "world"})

    assert response.status_code == 400
    assert response.json() == {"error": "invalid id; id must be a positive number"}


def test_post_invalid_json_returns_400() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/records/1",
        content='{"hello": ',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid input; could not parse json"}


def test_post_non_string_value_returns_400() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/records/1", json={"hello": 123})

    assert response.status_code == 400
    assert response.json() == {"error": "invalid input; could not parse json"}


def test_post_non_object_payload_returns_400() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/records/1", json=["hello"])

    assert response.status_code == 400
    assert response.json() == {"error": "invalid input; could not parse json"}


def test_post_updates_existing_record() -> None:
    client = TestClient(app)
    client.post("/api/v1/records/1", json={"hello": "world"})

    response = client.post("/api/v1/records/1", json={"hello": "world 2", "status": "ok"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "data": {"hello": "world 2", "status": "ok"},
    }


def test_post_null_value_deletes_key() -> None:
    client = TestClient(app)
    client.post("/api/v1/records/1", json={"hello": "world", "status": "ok"})

    response = client.post("/api/v1/records/1", json={"hello": None})

    assert response.status_code == 200
    assert response.json() == {"id": 1, "data": {"status": "ok"}}


def test_v1_post_writes_are_versioned_for_v2_history() -> None:
    client = TestClient(app)
    client.post("/api/v1/records/5", json={"hello": "v1"})
    client.post("/api/v1/records/5", json={"hello": "v2"})

    response = client.get("/api/v2/records/5/versions")

    assert response.status_code == 200
    assert [item["version"] for item in response.json()["versions"]] == [1, 2]
