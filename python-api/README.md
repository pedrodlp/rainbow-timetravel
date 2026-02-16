# timetravel-python-api

FastAPI + SQLite rewrite of the timetravel take-home.

## Setup

```bash
cd python-api
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

SQLite is file-backed and persistent by default at:
- `python-api/timetravel.db`

To override the database location:
```bash
export TIMETRAVEL_DB_PATH=/absolute/path/to/timetravel.db
```

# Test the server using a browser:
```bash
open http://127.0.0.1:8000/docs
```

# Test the server using curl:
```bash
curl -X POST http://localhost:8000/api/v1/health
```
