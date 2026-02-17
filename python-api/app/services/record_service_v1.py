from app.repositories.record_repo import RecordRepository
from app.services.record_service_v2 import RecordServiceV2


class RecordServiceV1:
    def __init__(self, repo: RecordRepository | None = None) -> None:
        self.repo = repo or RecordRepository()
        # We switch to the V2 service for upsert operations to ensure versioning is handled correctly, while still allowing retrieval of the latest record without versioning.
        self.versioned_service = RecordServiceV2(self.repo)

    def get_record(self, record_id: int) -> dict[str, str] | None:
        return self.repo.get_by_id(record_id)

    def upsert_record(self, record_id: int, updates: dict[str, str | None]) -> dict[str, str]:
        data, _version = self.versioned_service.upsert_record(record_id, updates)
        return data
