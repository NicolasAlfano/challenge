from app.domain.models import QueryRecord


class InMemoryQueryRepository:
    def __init__(self) -> None:
        self._records: list[QueryRecord] = []

    def save(self, record: QueryRecord) -> None:
        self._records.append(record)

    def list_all(self) -> list[QueryRecord]:
        return list(self._records)
