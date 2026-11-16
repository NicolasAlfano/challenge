from typing import Protocol

from app.domain.models import ExchangeRate, QueryRecord


class RateProvider(Protocol):
    """Puerto: cómo el núcleo necesita obtener una cotización."""

    def get_rate(self, base: str, target: str) -> ExchangeRate: ...


class QueryRepository(Protocol):
    """Puerto: cómo el núcleo necesita guardar y leer consultas."""

    def save(self, record: QueryRecord) -> None: ...

    def list_all(self) -> list[QueryRecord]: ...
