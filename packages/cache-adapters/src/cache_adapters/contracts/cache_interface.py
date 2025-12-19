from abc import ABC, abstractmethod
from typing import Optional


class CacheInterface(ABC):
    """
    Contract for all cache adapters.

    Subclasses auto-register via __init_subclass__.
    Just declare `name = "backend"` and you're in the registry.
    """

    _registry: dict[str, type["CacheInterface"]] = {}

    name: str  # Each adapter declares its registry key

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name") and cls.name:
            CacheInterface._registry[cls.name] = cls

    @classmethod
    def resolve(cls, name: str, **kwargs) -> "CacheInterface":
        """Resolve adapter by name from registry"""
        if name not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise KeyError(f"Unknown cache backend '{name}'. Available: {available}")

        kwargs = {k: v for k, v in kwargs.items() if v}
        return cls._registry[name](**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        """List all registered backend names"""
        return list(cls._registry.keys())

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value by key, returns None if not found"""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set value with optional TTL in seconds"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries"""
        pass
