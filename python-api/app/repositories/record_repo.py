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

    def update(self, record_id: int, data: dict[str, str]) -> None:
        with get_connection() as conn:
            conn.execute(
                "UPDATE records SET current_data = ? WHERE id = ?",
                (json.dumps(data), record_id),
            )
            conn.commit()

    def get_latest_version_number(self, record_id: int) -> int | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT MAX(version) AS latest_version
                FROM record_versions
                WHERE record_id = ?
                """,
                (record_id,),
            ).fetchone()

        if row is None or row["latest_version"] is None:
            return None
        return int(row["latest_version"])

    def get_record_at_version(self, record_id: int, version: int) -> dict[str, str] | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT data_json
                FROM record_versions
                WHERE record_id = ? AND version = ?
                """,
                (record_id, version),
            ).fetchone()

        if row is None:
            return None
        return json.loads(row["data_json"])

    def list_versions(self, record_id: int) -> list[dict[str, int | str]]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT version, created_at
                FROM record_versions
                WHERE record_id = ?
                ORDER BY version ASC
                """,
                (record_id,),
            ).fetchall()

        return [{"version": int(row["version"]), "created_at": row["created_at"]} for row in rows]

    def write_latest_and_version(
        self,
        record_id: int,
        next_version: int,
        data: dict[str, str],
    ) -> None:
        payload = json.dumps(data)
        with get_connection() as conn:
            conn.execute("BEGIN")
            conn.execute(
                """
                INSERT INTO records (id, current_data)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET current_data = excluded.current_data
                """,
                (record_id, payload),
            )
            conn.execute(
                """
                INSERT INTO record_versions (record_id, version, data_json, created_at)
                VALUES (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                """,
                (record_id, next_version, payload),
            )
            conn.commit()
