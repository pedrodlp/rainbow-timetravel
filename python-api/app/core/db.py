import os
import sqlite3
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
PROJECT_ROOT = APP_DIR.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "timetravel.db"
DB_PATH_ENV_VAR = "TIMETRAVEL_DB_PATH"


def resolve_db_path() -> Path:
    raw_db_path = os.getenv(DB_PATH_ENV_VAR)
    db_path = Path(raw_db_path).expanduser().resolve() if raw_db_path else DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(resolve_db_path())
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
