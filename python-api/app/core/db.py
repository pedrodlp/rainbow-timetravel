import os
import sqlite3
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
PROJECT_ROOT = APP_DIR.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "timetravel.db"
DB_PATH_ENV_VAR = "TIMETRAVEL_DB_PATH"


def resolve_db_path() -> Path:
    # Check for environment variable override, otherwise use default path
    raw_db_path = os.getenv(DB_PATH_ENV_VAR)
    db_path = Path(raw_db_path).expanduser().resolve() if raw_db_path else DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True) # Ensure the directory exists
    return db_path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(resolve_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Ensure the database file and tables are created before the application starts
    with get_connection() as conn:
        # Create the records table if it doesn't exist
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY,
                current_data TEXT NOT NULL
            )
            """
        )
        # Create the record_versions table if it doesn't exist
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS record_versions (
                record_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                data_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (record_id, version)
            )
            """
        )
        # Create an index on the record_versions table for faster lookups by record_id
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_record_versions_record_id
            ON record_versions (record_id)
            """
        )
        # Populate the record_versions table with initial data from the records table
        conn.execute(
            """
            INSERT INTO record_versions (record_id, version, data_json, created_at)
            SELECT
                records.id,
                1,
                records.current_data,
                strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            FROM records
            WHERE NOT EXISTS (
                SELECT 1
                FROM record_versions
                WHERE record_versions.record_id = records.id
            )
            """
        )
        conn.commit()
