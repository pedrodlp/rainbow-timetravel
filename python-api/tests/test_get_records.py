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


def test_get_record_success() -> None:
    client = TestClient(app)
    client.post("/api/v1/records/2323", json={"david": "hey", "davidx": "hey"})

    response = client.get("/api/v1/records/2323")

    assert response.status_code == 200
    assert response.json() == {"id": 2323, "data": {"david": "hey", "davidx": "hey"}}


def test_get_record_not_found_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/records/32")

    assert response.status_code == 400
    assert response.json() == {"error": "record of id 32 does not exist"}


def test_get_invalid_id_returns_400() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/records/abc")

    assert response.status_code == 400
    assert response.json() == {"error": "invalid id; id must be a positive number"}
