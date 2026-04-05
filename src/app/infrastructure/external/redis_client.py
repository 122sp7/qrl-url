"""Redis client backed by Redis Cloud (redis.asyncio)."""

import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import redis.asyncio as aioredis


def _redis_url() -> str:
    url = os.environ.get("REDIS_URL", "")
    if not url:
        raise RuntimeError("REDIS_URL environment variable is not set")
    return url


class RedisClient:
    """Thin async wrapper around redis.asyncio for caching and sorted-set operations."""

    def __init__(self, url: str | None = None):
        self._url = url or _redis_url()
        self._redis: aioredis.Redis | None = None

    async def connect(self) -> None:
        self._redis = aioredis.from_url(self._url, decode_responses=True)

    async def close(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def _r(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("RedisClient not connected")
        return self._redis

    # ------------------------------------------------------------------
    # Simple key/value cache
    # ------------------------------------------------------------------

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        await self._r().setex(key, ttl_seconds, json.dumps(value))

    async def get_json(self, key: str) -> Any | None:
        raw = await self._r().get(key)
        return json.loads(raw) if raw is not None else None

    # ------------------------------------------------------------------
    # Sorted Set for trade history
    # ------------------------------------------------------------------

    TRADES_KEY = "trades:QRLUSDT"
    TRADES_RETENTION_MS = 90 * 24 * 60 * 60 * 1000  # 90 days in milliseconds

    async def append_trades(self, trades: list[dict]) -> None:
        """ZADD trades with score=timestamp_ms, then trim older than 90 days."""
        if not trades:
            return
        r = self._r()
        mapping = {json.dumps(t, sort_keys=True): t["timestamp_ms"] for t in trades}
        await r.zadd(self.TRADES_KEY, mapping)
        cutoff = max(t["timestamp_ms"] for t in trades) - self.TRADES_RETENTION_MS
        await r.zremrangebyscore(self.TRADES_KEY, "-inf", cutoff)

    async def list_trades(self, limit: int = 200) -> list[dict]:
        """Return the most recent N trades from the sorted set."""
        r = self._r()
        raw_list = await r.zrange(self.TRADES_KEY, 0, limit - 1, rev=True)
        return [json.loads(raw) for raw in raw_list]


@asynccontextmanager
async def get_redis_client(url: str | None = None) -> AsyncIterator[RedisClient]:
    client = RedisClient(url)
    await client.connect()
    try:
        yield client
    finally:
        await client.close()
