from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ExchangeRate:
    base: str
    target: str
    rate: float


@dataclass(frozen=True)
class QueryRecord:
    rate: ExchangeRate
    queried_at: datetime
