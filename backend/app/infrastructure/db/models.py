from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QueryRecordModel(Base):
    """Modelo de la tabla. Es distinto del modelo de dominio a propósito."""

    __tablename__ = "query_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    base: Mapped[str] = mapped_column(String(3))
    target: Mapped[str] = mapped_column(String(3))
    rate: Mapped[float] = mapped_column(Float)
    queried_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
