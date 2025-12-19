from typing import Optional

import redis.asyncio as redis

from cache_adapters.contracts import CacheInterface


class RedisCache(CacheInterface):
    name = "redis"  # Auto-registered!

    """Redis cache adapter for horizontal scaling"""

    def __init__(self, url: str, default_ttl: Optional[int] = None, **kwargs):
        self._client = redis.from_url(url)
        self._default_ttl = default_ttl

    async def get(self, key: str) -> Optional[str]:
        value = await self._client.get(key)
        return value.decode() if value else None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        ttl = ttl or self._default_ttl
        if ttl:
            await self._client.setex(key, ttl, value)
        else:
            await self._client.set(key, value)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def clear(self) -> None:
        await self._client.flushdb()
