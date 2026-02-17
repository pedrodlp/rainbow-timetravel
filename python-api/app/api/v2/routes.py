import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.record import RecordResponse
from app.services.record_service_v2 import RecordServiceV2

router = APIRouter()
service = RecordServiceV2()
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


def parse_positive_int(raw_value: str) -> int | None:
    # Parse a string value and ensure it is a positive integer. If the value is invalid (not an integer or not positive), return None.
    try:
        value = int(raw_value)
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


@router.get("/records/{id}", response_model=RecordResponse)
def get_record(id: str, version: str | None = None):
    # Retrieve the current state of a record by its ID, or a specific version if the version query parameter is provided.
    # If the record does not exist or the ID/version is invalid, return an appropriate error response.
    record_id = parse_positive_int(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    parsed_version: int | None = None # We use this variable to store the parsed version number if the version query parameter is provided.
    # If a version is specified, parse and validate it. If the version is invalid, return an error response.
    if version is not None:
        parsed_version = parse_positive_int(version)
        if parsed_version is None:
            return error_response("invalid version; version must be a positive number", 400)

    try:
        # Retrieve the record at the specified version if provided, otherwise retrieve the latest version.
        record = service.get_record(record_id, parsed_version)
    except Exception:
        return error_response("internal error", 500)

    if record is None:
        # If the record is None and no version was specified, the record does not exist.
        if parsed_version is None:
            return error_response(f"record of id {record_id} does not exist", 400)
        
        # If the record is None and a version was specified, for the error response, we assume the record exists but that specific version does not exist.
        # This is to avoid leaking information about whether the record exists when an invalid version is requested, 
        # while still providing a clear error message for the common case of requesting a non-existent version of an existing record.
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
    # Create or update a record by its ID based on the provided JSON body. 
    record_id = parse_positive_int(id)
    # If the record ID is invalid, return an error response. Otherwise, parse the request body for updates and apply them to the record.
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


@router.get("/records/{id}/versions")
def list_record_versions(id: str):
    # List all versions of a record by its ID. If the record does not exist or the ID is invalid, return an appropriate error response.
    record_id = parse_positive_int(id)
    if record_id is None:
        return error_response("invalid id; id must be a positive number", 400)

    try:
        latest = service.get_record(record_id)
        if latest is None:
            return error_response(f"record of id {record_id} does not exist", 400)
        versions = service.list_versions(record_id)
    except Exception:
        return error_response("internal error", 500)

    return {"id": record_id, "versions": versions}
