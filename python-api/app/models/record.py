from pydantic import BaseModel


class RecordResponse(BaseModel):
    id: int
    data: dict[str, str]
