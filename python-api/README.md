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

## V2 Contract (Planned)

### Version semantics
- Versioning is per record and monotonic: `1, 2, 3, ...`.
- Every successful update creates a new immutable version.
- History uses full JSON snapshots per version.

### Endpoints under `/api/v2`
- `GET /api/v2/records/{id}`
Returns the latest state of the record.
- `GET /api/v2/records/{id}?version={n}`
Returns the state at a specific version.
- `POST /api/v2/records/{id}`
Applies update semantics to the latest state and creates a new version.
- `GET /api/v2/records/{id}/versions`
Lists available versions for the record.

### Update semantics
- Request body: JSON object with `string -> string | null`.
- Non-null values set/overwrite keys.
- `null` values delete keys.

### Backward compatibility
- `/api/v1` endpoints keep current response shapes and status behavior.
- `/api/v1` continues to work unchanged for clients.
