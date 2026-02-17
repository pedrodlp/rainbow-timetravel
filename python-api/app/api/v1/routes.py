import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.record import RecordResponse
from app.services.record_service_v1 import RecordServiceV1

router = APIRouter()
service = RecordServiceV1()
# This extra metadata is used to enhance the OpenAPI documentation for the POST /records/{id} endpoint,
# providing clear examples of the expected request body format for creating, updating, and deleting fields in a record.
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


def parse_positive_id(raw_id: str) -> int | None:
    # Parse a string ID and ensure it is a positive integer. If the ID is invalid (not an integer or not positive), return None.
    try:
        value = int(raw_id)
    except ValueError:
        return None

    if value <= 0:
        return None

    return value


def parse_updates(raw_body: bytes) -> dict[str, str | None] | None:
    # Parse the raw request body as JSON and validate that it is a dictionary with string keys and string or null values.
    # If the input is invalid, return None.
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
    # Healthcheck endpoint to verify that the API is running.
    return {"ok": True}


@router.get("/records/{id}", response_model=RecordResponse)
def get_record(id: str):
    # Retrieve the current state of a record by its ID. If the record does not exist or the ID is invalid, return an appropriate error response.
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


@router.post(
    "/records/{id}",
    response_model=RecordResponse,
    openapi_extra=POST_RECORD_FASTAPI_EXTRA,
)
async def post_record(id: str, request: Request):
    # Create or update a record with the given ID based on the provided JSON body.
    record_id = parse_positive_id(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    raw_body = await request.body()
    updates = parse_updates(raw_body)
    if updates is None:
        return error_response("invalid input; could not parse json", 400)

    try:
        record = service.upsert_record(record_id, updates)
    except Exception:
        return error_response("internal error", 500)

    return {"id": record_id, "data": record}
