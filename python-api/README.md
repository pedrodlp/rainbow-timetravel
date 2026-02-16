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

# Test the server using a browser:
```bash
open http://127.0.0.1:8000/docs
```

# Test the server using curl:
```bash
curl -X POST http://localhost:8000/api/v1/health
```