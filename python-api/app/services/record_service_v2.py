from app.repositories.record_repo import RecordRepository


class RecordServiceV2:
    def __init__(self, repo: RecordRepository | None = None) -> None:
        self.repo = repo or RecordRepository()

    def get_record(self, record_id: int, version: int | None = None) -> dict[str, str] | None:
        if version is None:
            return self.repo.get_by_id(record_id)
        return self.repo.get_record_at_version(record_id, version)

    def upsert_record(self, record_id: int, updates: dict[str, str | None]) -> tuple[dict[str, str], int]:
        current = self.repo.get_by_id(record_id)

        if current is None:
            next_data = {key: value for key, value in updates.items() if value is not None}
        else:
            next_data = dict(current)
            for key, value in updates.items():
                if value is None:
                    next_data.pop(key, None)
                else:
                    next_data[key] = value

        version = self.repo.write_latest_and_version(record_id, next_data)
        return next_data, version

    def list_versions(self, record_id: int) -> list[dict[str, int | str]]:
        return self.repo.list_versions(record_id)
