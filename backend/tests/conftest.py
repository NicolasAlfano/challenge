import os

# Se definen ANTES de importar la app, porque la configuración se lee al importar.
# Así los tests no dependen de tu .env ni de una base de datos real.
os.environ["APP_API_KEY"] = "test-key"
os.environ["APP_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from app.config import Settings  # noqa: E402

from app.api.v1.dependencies import get_repository  # noqa: E402
from app.infrastructure.db import session as session_module  # noqa: E402
from app.infrastructure.db.in_memory_repository import InMemoryQueryRepository  # noqa: E402
from app.infrastructure.db.models import Base  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """Cliente HTTP con un repositorio en memoria NUEVO para cada test."""
    repository = InMemoryQueryRepository()
    app.dependency_overrides[get_repository] = lambda: repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-key"}


@pytest.fixture
def sqlalchemy_client(tmp_path, monkeypatch):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'integration.db'}"
    settings = Settings(api_key="test-key", database_url=database_url)
    monkeypatch.setattr(session_module, "get_settings", lambda: settings)
    session_module.get_session_factory.cache_clear()

    session_factory = session_module.get_session_factory()
    engine = session_factory.kw["bind"]
    assert engine is not None
    Base.metadata.create_all(engine)
    monkeypatch.delitem(app.dependency_overrides, get_repository, raising=False)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        engine.dispose()
        session_module.get_session_factory.cache_clear()
