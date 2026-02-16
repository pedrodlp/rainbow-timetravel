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
