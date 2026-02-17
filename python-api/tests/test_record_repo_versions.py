import pytest

from app.core.db import get_connection, init_db
from app.repositories.record_repo import RecordRepository


@pytest.fixture(autouse=True)
def clear_tables() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM record_versions")
        conn.execute("DELETE FROM records")
        conn.commit()


def test_write_latest_and_version_creates_latest_and_snapshot() -> None:
    repo = RecordRepository()

    assigned_version = repo.write_latest_and_version(record_id=1, data={"hello": "world"})

    latest = repo.get_by_id(1)
    v1 = repo.get_record_at_version(1, 1)
    versions = repo.list_versions(1)

    assert assigned_version == 1
    assert latest == {"hello": "world"}
    assert v1 == {"hello": "world"}
    assert [item["version"] for item in versions] == [1]


def test_write_latest_and_version_updates_latest_and_appends_version() -> None:
    repo = RecordRepository()

    first_version = repo.write_latest_and_version(record_id=1, data={"hello": "world"})
    second_version = repo.write_latest_and_version(record_id=1, data={"hello": "world 2"})

    latest = repo.get_by_id(1)
    v1 = repo.get_record_at_version(1, 1)
    v2 = repo.get_record_at_version(1, 2)
    latest_version = repo.get_latest_version_number(1)

    assert first_version == 1
    assert second_version == 2
    assert latest == {"hello": "world 2"}
    assert v1 == {"hello": "world"}
    assert v2 == {"hello": "world 2"}
    assert latest_version == 2


def test_get_latest_version_number_returns_none_when_missing() -> None:
    repo = RecordRepository()

    assert repo.get_latest_version_number(999) is None


def test_get_record_at_version_returns_none_when_missing() -> None:
    repo = RecordRepository()

    assert repo.get_record_at_version(999, 1) is None
