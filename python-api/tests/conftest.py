import pytest


@pytest.fixture(autouse=True)
def isolate_test_database(monkeypatch, tmp_path) -> None:
    db_file = tmp_path / "timetravel-test.db"
    monkeypatch.setenv("TIMETRAVEL_DB_PATH", str(db_file))
