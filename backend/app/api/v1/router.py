from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.v1.dependencies import get_rate_service, require_api_key
from app.api.v1.schemas import HistoryItem, RateResponse
from app.application.rate_service import RateService
from app.domain.exceptions import UnsupportedCurrencyError

public_router = APIRouter(prefix="/api/v1", tags=["health"])
private_router = APIRouter(
    prefix="/api/v1", tags=["rates"], dependencies=[Depends(require_api_key)]
)


@public_router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "Hola mundo desde FastAPI"}


@private_router.get("/rates", response_model=RateResponse)
def get_rate(
    base: Annotated[str, Query(min_length=3, max_length=3, examples=["USD"])],
    target: Annotated[str, Query(min_length=3, max_length=3, examples=["ARS"])],
    service: RateService = Depends(get_rate_service),
) -> RateResponse:
    try:
        rate = service.get_rate(base, target)
    except UnsupportedCurrencyError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RateResponse(base=rate.base, target=rate.target, rate=rate.rate)


@private_router.get("/history", response_model=list[HistoryItem])
def get_history(
    service: RateService = Depends(get_rate_service),
) -> list[HistoryItem]:
    return [
        HistoryItem(
            base=r.rate.base,
            target=r.rate.target,
            rate=r.rate.rate,
            queried_at=r.queried_at,
        )
        for r in service.history()
    ]
