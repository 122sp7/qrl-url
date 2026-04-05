"""FastAPI dependency providers for interface layer."""

import os

from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.infrastructure.exchange.mexc.cached_service import CachedMexcExchangeService
from src.app.infrastructure.exchange.mexc.service import MexcExchangeService, build_mexc_exchange_service
from src.app.infrastructure.exchange.mexc.settings import MexcSettings
from src.app.infrastructure.external.redis_client import RedisClient


def build_exchange_factory(settings: MexcSettings | None = None) -> ExchangeServiceFactory:
    """Return a factory that builds a fresh exchange adapter per request.

    When REDIS_URL is configured, wraps the service with write-through cache.
    """
    resolved = settings or MexcSettings()
    redis_url = os.environ.get("REDIS_URL", "")

    if redis_url:
        redis = RedisClient(redis_url)

        async def _connect_and_return():
            await redis.connect()
            return redis

        def factory():
            inner = build_mexc_exchange_service(resolved)
            redis_client = RedisClient(redis_url)
            return _CachedServiceContext(inner, redis_client)

        return factory

    def factory():  # type: ignore[no-redef]
        return build_mexc_exchange_service(resolved)

    return factory


class _CachedServiceContext:
    """Async context manager combining CachedMexcExchangeService with a per-request Redis client."""

    def __init__(self, inner: MexcExchangeService, redis: RedisClient):
        self._inner = inner
        self._redis = redis
        self._service: CachedMexcExchangeService | None = None

    async def __aenter__(self) -> CachedMexcExchangeService:
        await self._redis.connect()
        self._service = CachedMexcExchangeService(self._inner, self._redis)
        await self._service.__aenter__()
        return self._service

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._service:
            await self._service.__aexit__(exc_type, exc, tb)
        await self._redis.close()


def get_exchange_factory() -> ExchangeServiceFactory:
    """Default dependency for constructing exchange adapters."""

    return build_exchange_factory()
