import sqlite3
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
PROJECT_ROOT = APP_DIR.parent
DB_PATH = PROJECT_ROOT / "timetravel.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY,
                current_data TEXT NOT NULL
            )
            """
        )
        conn.commit()
