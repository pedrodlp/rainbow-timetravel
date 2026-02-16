import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.record import RecordResponse
from app.services.record_service_v1 import RecordServiceV1

router = APIRouter()
service = RecordServiceV1()


def error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def parse_positive_id(raw_id: str) -> int | None:
    try:
        value = int(raw_id)
    except ValueError:
        return None

    if value <= 0:
        return None

    return value


def parse_updates(raw_body: bytes) -> dict[str, str | None] | None:
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    normalized: dict[str, str | None] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            return None
        if value is not None and not isinstance(value, str):
            return None
        normalized[key] = value

    return normalized


@router.post("/health")
def healthcheck() -> dict[str, bool]:
    return {"ok": True}


@router.get("/records/{id}", response_model=RecordResponse)
def get_record(id: str):
    record_id = parse_positive_id(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    try:
        record = service.get_record(record_id)
    except Exception:
        return error_response("internal error", 500)

    if record is None:
        return error_response(f"record of id {record_id} does not exist", 400)

    return {"id": record_id, "data": record}


@router.post("/records/{id}")
async def post_record(id: str, request: Request):
    record_id = parse_positive_id(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    raw_body = await request.body()
    updates = parse_updates(raw_body)
    if updates is None:
        return error_response("invalid input; could not parse json", 400)

    try:
        record = service.create_record(record_id, updates)
    except Exception:
        return error_response("internal error", 500)

    if record is None:
        return error_response("internal error", 500)

    return {"id": record_id, "data": record}
