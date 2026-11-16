from datetime import datetime, timezone

from app.domain.models import ExchangeRate, QueryRecord
from app.domain.ports import QueryRepository, RateProvider


class RateService:
    def __init__(self, provider: RateProvider, repository: QueryRepository) -> None:
        self._provider = provider
        self._repository = repository

    def get_rate(self, base: str, target: str) -> ExchangeRate:
        rate = self._provider.get_rate(base.upper(), target.upper())
        self._repository.save(
            QueryRecord(rate=rate, queried_at=datetime.now(timezone.utc))
        )
        return rate

    def history(self) -> list[QueryRecord]:
        """Devuelve las consultas, de la más reciente a la más antigua."""
        return list(reversed(self._repository.list_all()))
