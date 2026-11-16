import secrets
from functools import lru_cache

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.application.rate_service import RateService
from app.config import Settings, get_settings
from app.domain.ports import QueryRepository
from app.infrastructure.clients.static_provider import StaticRateProvider
from app.infrastructure.db.in_memory_repository import InMemoryQueryRepository

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> None:
    if key is None or not secrets.compare_digest(
        key.encode(), settings.api_key.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@lru_cache
def get_repository() -> QueryRepository:
    return InMemoryQueryRepository()


def get_rate_service(
    repository: QueryRepository = Depends(get_repository),
) -> RateService:
    # Acá "enchufamos" los adaptadores concretos a los puertos.
    return RateService(provider=StaticRateProvider(), repository=repository)
