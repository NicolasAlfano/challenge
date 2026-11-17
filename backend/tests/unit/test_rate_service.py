import pytest

from app.application.rate_service import RateService
from app.domain.exceptions import UnsupportedCurrencyError
from app.domain.models import ExchangeRate
from app.infrastructure.db.in_memory_repository import InMemoryQueryRepository


class FakeProvider:
    """Doble de prueba del puerto RateProvider: responde siempre 2.0."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def get_rate(self, base: str, target: str) -> ExchangeRate:
        self.calls.append((base, target))
        return ExchangeRate(base=base, target=target, rate=2.0)


class FailingProvider:
    def get_rate(self, base: str, target: str) -> ExchangeRate:
        raise UnsupportedCurrencyError("not supported")


def test_get_rate_returns_the_rate_from_the_provider():
    service = RateService(FakeProvider(), InMemoryQueryRepository())

    rate = service.get_rate("USD", "ARS")

    assert rate == ExchangeRate(base="USD", target="ARS", rate=2.0)


def test_get_rate_normalizes_currency_codes_to_uppercase():
    provider = FakeProvider()
    service = RateService(provider, InMemoryQueryRepository())

    service.get_rate("usd", "ars")

    assert provider.calls == [("USD", "ARS")]


def test_get_rate_saves_the_query():
    repository = InMemoryQueryRepository()
    service = RateService(FakeProvider(), repository)

    service.get_rate("USD", "ARS")

    saved = repository.list_all()
    assert len(saved) == 1
    assert saved[0].rate.base == "USD"
    assert saved[0].queried_at.tzinfo is not None


def test_provider_error_propagates_and_nothing_is_saved():
    repository = InMemoryQueryRepository()
    service = RateService(FailingProvider(), repository)

    with pytest.raises(UnsupportedCurrencyError):
        service.get_rate("USD", "XYZ")

    assert repository.list_all() == []


def test_history_is_newest_first():
    service = RateService(FakeProvider(), InMemoryQueryRepository())
    service.get_rate("USD", "ARS")
    service.get_rate("EUR", "USD")

    history = service.history()

    assert [r.rate.base for r in history] == ["EUR", "USD"]
