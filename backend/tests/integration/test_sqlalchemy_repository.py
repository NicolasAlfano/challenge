from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.models import ExchangeRate, QueryRecord
from app.infrastructure.db.models import Base
from app.infrastructure.db.sqlalchemy_repository import SqlAlchemyQueryRepository


@pytest.fixture
def repository():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield SqlAlchemyQueryRepository(session)
    engine.dispose()


def _record(base: str, target: str, rate: float, when: datetime) -> QueryRecord:
    return QueryRecord(
        rate=ExchangeRate(base=base, target=target, rate=rate), queried_at=when
    )


def test_save_and_list_roundtrip(repository):
    when = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    repository.save(_record("USD", "ARS", 1000.0, when))

    [stored] = repository.list_all()

    assert (stored.rate.base, stored.rate.target, stored.rate.rate) == (
        "USD",
        "ARS",
        1000.0,
    )
    # SQLite no guarda la zona horaria (PostgreSQL sí), por eso se compara sin ella.
    assert stored.queried_at.replace(tzinfo=None) == when.replace(tzinfo=None)


def test_list_all_is_ordered_by_date(repository):
    late = datetime(2026, 1, 2, tzinfo=timezone.utc)
    early = datetime(2026, 1, 1, tzinfo=timezone.utc)
    repository.save(_record("EUR", "USD", 1.1, late))
    repository.save(_record("USD", "ARS", 1000.0, early))

    assert [r.rate.base for r in repository.list_all()] == ["USD", "EUR"]


def test_list_all_breaks_equal_date_ties_by_id(repository):
    when = datetime(2026, 1, 1, tzinfo=timezone.utc)
    repository.save(_record("USD", "ARS", 1000.0, when))
    repository.save(_record("EUR", "USD", 1.1, when))

    assert [r.rate.base for r in repository.list_all()] == ["USD", "EUR"]
