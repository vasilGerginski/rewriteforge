# Import providers to trigger __init_subclass__ registration
from cache_adapters import providers  # noqa: F401
from cache_adapters.contracts.cache_interface import CacheInterface

__all__ = ["CacheInterface"]
