import pytest


# This fixture automatically runs before each test to ensure that each test uses a separate, isolated database.
# It creates a temporary database file for each test and sets the TIMETRAVEL_DB_PATH environment variable to point to that file,
# preventing tests from interfering with each other's data.
@pytest.fixture(autouse=True)
def isolate_test_database(monkeypatch, tmp_path) -> None:
    db_file = tmp_path / "timetravel-test.db"
    monkeypatch.setenv("TIMETRAVEL_DB_PATH", str(db_file))
