from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.record import RecordResponse
from app.services.record_service_v2 import RecordServiceV2

router = APIRouter()
service = RecordServiceV2()


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
            f"record of id {record_id} does not exist at version {parsed_version}",
            400,
        )

    return {"id": record_id, "data": record}
