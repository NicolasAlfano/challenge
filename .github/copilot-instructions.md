# Reglas del proyecto
- Arquitectura hexagonal: `domain` y `application` no importan nada de `api` ni `infrastructure`, ni frameworks.
- Los puertos son Protocols en `domain/ports.py`; se inyectan por constructor.
- Los adaptadores concretos se enchufan en `api/v1/dependencies.py`.
- Configuración solo por variables de entorno con pydantic-settings. Nada hardcodeado.
- Endpoints bajo /api/v1; los privados requieren header X-API-Key.
- Todo cambio de comportamiento lleva tests: unit (capa aislada) e integration (caja negra por HTTP).
- Commits chicos con mensajes descriptivos (feat:, fix:, chore:, test:, docs:).
