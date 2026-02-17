import json

from app.core.db import get_connection


class RecordRepository:
    # This repository manages both the current state of records and their version history.

    # The `records` table stores the latest state of each record, here we can quickly retrieve and update the current data.
    def get_by_id(self, record_id: int) -> dict[str, str] | None:
        # Retrieve the current state of a record by its ID. If the record does not exist, return None.
        with get_connection() as conn:
            row = conn.execute(
                "SELECT current_data FROM records WHERE id = ?", (record_id,)
            ).fetchone()

        if row is None:
            return None

        return json.loads(row["current_data"])

    def create(self, record_id: int, data: dict[str, str]) -> None:
        # Create a new record with the given ID and data. This method assumes that the record ID is unique and does not already exist in the database.
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO records (id, current_data) VALUES (?, ?)",
                (record_id, json.dumps(data)),
            )
            conn.commit()

    def update(self, record_id: int, data: dict[str, str]) -> None:
        # Update the current state of an existing record. If the record does not exist, this method does nothing.
        with get_connection() as conn:
            conn.execute(
                "UPDATE records SET current_data = ? WHERE id = ?",
                (json.dumps(data), record_id),
            )
            conn.commit()

    def get_latest_version_number(self, record_id: int) -> int | None:
        # Retrieve the latest version number for a given record ID. If no versions exist, return None.
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

    # The `record_versions` table maintains a history of all changes to each record, allowing us to track and retrieve past versions.
    def get_record_at_version(self, record_id: int, version: int) -> dict[str, str] | None:
        # Retrieve a specific version of a record by its ID and version number. If the version does not exist, return None.
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
        # List all versions of a record along with their creation timestamps
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
        data: dict[str, str],
    ) -> int:
        # Write the latest state of a record and create a new version entry. Returns the new version number.
        payload = json.dumps(data)
        with get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE") # Lock the database for writing to prevent race conditions:  [BEGIN] vs [BEGIN IMMEDIATE]
            # Calculate the next version number by finding the maximum existing version for the record and adding 1. If no versions exist, start at 1.
            next_version_row = conn.execute(
                """
                SELECT COALESCE(MAX(version), 0) + 1 AS next_version
                FROM record_versions
                WHERE record_id = ?
                """,
                (record_id,),
            ).fetchone()
            next_version = int(next_version_row["next_version"])
            # Upsert the current state of the record in the `records` table. If the record already exists, update its current data; otherwise, insert a new record.
            conn.execute(
                """
                INSERT INTO records (id, current_data)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET current_data = excluded.current_data
                """,
                (record_id, payload),
            )
            # Insert a new entry into the `record_versions` table to log this change, including the record ID, version number, data payload, and the current timestamp.
            conn.execute(
                """
                INSERT INTO record_versions (record_id, version, data_json, created_at)
                VALUES (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
                """,
                (record_id, next_version, payload),
            )
            conn.commit()
            return next_version
