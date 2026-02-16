import json

from app.core.db import get_connection


class RecordRepository:
    def get_by_id(self, record_id: int) -> dict[str, str] | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT current_data FROM records WHERE id = ?", (record_id,)
            ).fetchone()

        if row is None:
            return None

        return json.loads(row["current_data"])

    def create(self, record_id: int, data: dict[str, str]) -> None:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO records (id, current_data) VALUES (?, ?)",
                (record_id, json.dumps(data)),
            )
            conn.commit()
