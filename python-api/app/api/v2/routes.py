import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.record import RecordResponse
from app.services.record_service_v2 import RecordServiceV2

router = APIRouter()
service = RecordServiceV2()
POST_RECORD_FASTAPI_EXTRA = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "additionalProperties": {"type": "string", "nullable": True},
                },
                "examples": {
                    "create": {"value": {"hello": "world"}},
                    "update": {"value": {"hello": "world 2", "status": "ok"}},
                    "deleteField": {"value": {"hello": None}},
                },
            }
        },
    }
}


def error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def parse_positive_int(raw_value: str) -> int | None:
    try:
        value = int(raw_value)
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


@router.get("/records/{id}", response_model=RecordResponse)
def get_record(id: str, version: str | None = None):
    record_id = parse_positive_int(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    parsed_version: int | None = None
    if version is not None:
        parsed_version = parse_positive_int(version)
        if parsed_version is None:
            return error_response("invalid version; version must be a positive number", 400)

    try:
        record = service.get_record(record_id, parsed_version)
    except Exception:
        return error_response("internal error", 500)

    if record is None:
        if parsed_version is None:
            return error_response(f"record of id {record_id} does not exist", 400)
        return error_response(
            f"record of id {record_id} does not have version {parsed_version}",
            400,
        )

    return {"id": record_id, "data": record}


@router.post(
    "/records/{id}",
    openapi_extra=POST_RECORD_FASTAPI_EXTRA,
)
async def post_record(id: str, request: Request):
    record_id = parse_positive_int(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    raw_body = await request.body()
    updates = parse_updates(raw_body)
    if updates is None:
        return error_response("invalid input; could not parse json", 400)

    try:
        record, version = service.upsert_record(record_id, updates)
    except Exception:
        return error_response("internal error", 500)

    return {"id": record_id, "version": version, "data": record}
