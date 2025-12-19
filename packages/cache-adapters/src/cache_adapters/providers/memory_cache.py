import time
from typing import Dict, Optional, Tuple

from cache_adapters.contracts import CacheInterface


class MemoryCache(CacheInterface):
    name = "memory"  # Auto-registered!

    """In-memory cache with optional TTL support"""

    def __init__(self, default_ttl: Optional[int] = None, **kwargs):
        self._store: Dict[str, Tuple[str, Optional[float]]] = {}
        self._default_ttl = default_ttl

    async def get(self, key: str) -> Optional[str]:
        if key not in self._store:
            return None

        value, expires_at = self._store[key]

        if expires_at and time.time() > expires_at:
            del self._store[key]
            return None

        return value

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def clear(self) -> None:
        self._store.clear()
