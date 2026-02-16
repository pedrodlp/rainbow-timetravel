from app.repositories.record_repo import RecordRepository


class RecordServiceV1:
    def __init__(self, repo: RecordRepository | None = None) -> None:
        self.repo = repo or RecordRepository()

    def create_record(self, record_id: int, updates: dict[str, str | None]) -> dict[str, str] | None:
        existing = self.repo.get_by_id(record_id)
        if existing is not None:
            return None

        created = {key: value for key, value in updates.items() if value is not None}
        self.repo.create(record_id, created)
        return created
