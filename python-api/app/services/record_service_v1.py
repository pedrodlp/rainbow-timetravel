from app.repositories.record_repo import RecordRepository


class RecordServiceV1:
    def __init__(self, repo: RecordRepository | None = None) -> None:
        self.repo = repo or RecordRepository()

    def get_record(self, record_id: int) -> dict[str, str] | None:
        return self.repo.get_by_id(record_id)

    def upsert_record(self, record_id: int, updates: dict[str, str | None]) -> dict[str, str]:
        current = self.repo.get_by_id(record_id)

        if current is None:
            created = {key: value for key, value in updates.items() if value is not None}
            self.repo.create(record_id, created)
            return created

        for key, value in updates.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = value

        self.repo.update(record_id, current)
        return current
