import json
import sqlite3

from app.core.db import get_connection, init_db


def test_data_persists_in_file_backed_sqlite_db(monkeypatch, tmp_path) -> None:
    db_file = tmp_path / "timetravel-persist.db"
    monkeypatch.setenv("TIMETRAVEL_DB_PATH", str(db_file))

    init_db()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO records (id, current_data) VALUES (?, ?)",
            (1, json.dumps({"hello": "world"})),
        )
        conn.commit()

    # Simulate service restart by re-running schema initialization.
    init_db()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT current_data FROM records WHERE id = ?", (1,)
        ).fetchone()

    assert row is not None
    assert json.loads(row["current_data"]) == {"hello": "world"}
    assert db_file.exists()


def test_init_db_backfills_record_versions_for_legacy_records(monkeypatch, tmp_path) -> None:
    db_file = tmp_path / "timetravel-legacy.db"
    monkeypatch.setenv("TIMETRAVEL_DB_PATH", str(db_file))

    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE records (
                id INTEGER PRIMARY KEY,
                current_data TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO records (id, current_data) VALUES (?, ?)",
            (7, json.dumps({"legacy": "value"})),
        )
        conn.commit()

    init_db()
    init_db()  # should be idempotent and not duplicate version 1

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT record_id, version, data_json
            FROM record_versions
            WHERE record_id = ?
            """,
            (7,),
        ).fetchall()

    assert len(row) == 1
    assert row[0]["record_id"] == 7
    assert row[0]["version"] == 1
    assert json.loads(row[0]["data_json"]) == {"legacy": "value"}
