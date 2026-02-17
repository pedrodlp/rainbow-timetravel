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

## API behavior

### Version semantics
- Versioning is per record and monotonic: `1, 2, 3, ...`.
- Every successful write creates a new immutable version snapshot.
- `/api/v1` and `/api/v2` write through the same versioned upsert path.

### `/api/v1` endpoints
- `POST /api/v1/health`
- `GET /api/v1/records/{id}`
- `POST /api/v1/records/{id}`

Backward compatibility guarantees for `/api/v1`:
- Response shape remains `{ "id": number, "data": { ... } }`
- Error payload remains `{ "error": "..." }`
- Existing status code behavior is preserved

### `/api/v2` endpoints
- `GET /api/v2/records/{id}`
  Returns latest record state.
- `GET /api/v2/records/{id}?version={n}`
  Returns state at a specific version.
- `POST /api/v2/records/{id}`
  Applies updates and returns new version.
- `GET /api/v2/records/{id}/versions`
  Returns available version numbers and timestamps.

### Update semantics (v1 and v2 writes)
- Request body must be a JSON object with `string -> string | null`.
- Non-null values set/overwrite keys.
- `null` values delete keys.

## v2 curl examples

Create version 1:
```bash
curl -X POST http://127.0.0.1:8000/api/v2/records/1 \
  -H "Content-Type: application/json" \
  -d '{"hello":"world"}'
```

Example response:
```json
{"id":1,"version":1,"data":{"hello":"world"}}
```

Create version 2:
```bash
curl -X POST http://127.0.0.1:8000/api/v2/records/1 \
  -H "Content-Type: application/json" \
  -d '{"hello":"world 2","status":"ok"}'
```

Get latest:
```bash
curl http://127.0.0.1:8000/api/v2/records/1
```

Get a specific version:
```bash
curl "http://127.0.0.1:8000/api/v2/records/1?version=1"
```

List versions:
```bash
curl http://127.0.0.1:8000/api/v2/records/1/versions
```
