from datetime import datetime

from pydantic import BaseModel


class RateResponse(BaseModel):
    base: str
    target: str
    rate: float


class HistoryItem(RateResponse):
    queried_at: datetime
