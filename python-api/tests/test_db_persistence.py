import json

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
