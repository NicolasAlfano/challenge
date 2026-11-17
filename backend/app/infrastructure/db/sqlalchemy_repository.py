from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import ExchangeRate, QueryRecord
from app.infrastructure.db.models import QueryRecordModel


class SqlAlchemyQueryRepository:
    """Implementa el puerto QueryRepository usando PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, record: QueryRecord) -> None:
        self._session.add(
            QueryRecordModel(
                base=record.rate.base,
                target=record.rate.target,
                rate=record.rate.rate,
                queried_at=record.queried_at,
            )
        )
        self._session.commit()

    def list_all(self) -> list[QueryRecord]:
        rows = self._session.scalars(
            select(QueryRecordModel).order_by(
                QueryRecordModel.queried_at, QueryRecordModel.id
            )
        ).all()
        return [
            QueryRecord(
                rate=ExchangeRate(base=r.base, target=r.target, rate=r.rate),
                queried_at=r.queried_at,
            )
            for r in rows
        ]
