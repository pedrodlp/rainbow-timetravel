import pytest

from app.core.db import get_connection, init_db
from app.services.record_service_v2 import RecordServiceV2


@pytest.fixture(autouse=True)
def clear_tables() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM record_versions")
        conn.execute("DELETE FROM records")
        conn.commit()


def test_upsert_record_creates_initial_version() -> None:
    service = RecordServiceV2()

    data, version = service.upsert_record(1, {"hello": "world"})

    assert data == {"hello": "world"}
    assert version == 1


def test_upsert_record_updates_and_deletes_with_null() -> None:
    service = RecordServiceV2()

    service.upsert_record(1, {"hello": "world", "status": "ok"})
    data, version = service.upsert_record(1, {"hello": None, "status": "updated"})

    assert data == {"status": "updated"}
    assert version == 2


def test_get_record_supports_latest_and_specific_versions() -> None:
    service = RecordServiceV2()

    service.upsert_record(1, {"hello": "v1"})
    service.upsert_record(1, {"hello": "v2"})

    latest = service.get_record(1)
    v1 = service.get_record(1, version=1)
    v2 = service.get_record(1, version=2)

    assert latest == {"hello": "v2"}
    assert v1 == {"hello": "v1"}
    assert v2 == {"hello": "v2"}


def test_list_versions_returns_ordered_versions() -> None:
    service = RecordServiceV2()

    service.upsert_record(1, {"a": "1"})
    service.upsert_record(1, {"b": "2"})

    versions = service.list_versions(1)

    assert [item["version"] for item in versions] == [1, 2]
