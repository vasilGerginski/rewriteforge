import pytest
from cache_adapters.providers.memory_cache import MemoryCache


class TestMemoryCache:
    @pytest.fixture
    def cache(self):
        return MemoryCache()

    @pytest.fixture
    def cache_with_ttl(self):
        return MemoryCache(default_ttl=3600)

    async def test_get_nonexistent_key_returns_none(self, cache):
        """Test getting a key that doesn't exist"""
        result = await cache.get("nonexistent")
        assert result is None

    async def test_set_and_get(self, cache):
        """Test basic set and get"""
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    async def test_set_overwrites_existing(self, cache):
        """Test that set overwrites existing value"""
        await cache.set("key1", "value1")
        await cache.set("key1", "value2")
        result = await cache.get("key1")
        assert result == "value2"

    async def test_delete(self, cache):
        """Test delete removes key"""
        await cache.set("key1", "value1")
        await cache.delete("key1")
        result = await cache.get("key1")
        assert result is None

    async def test_delete_nonexistent_key_no_error(self, cache):
        """Test deleting nonexistent key doesn't raise"""
        await cache.delete("nonexistent")  # Should not raise

    async def test_clear(self, cache):
        """Test clear removes all keys"""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    async def test_default_ttl_applied(self, cache_with_ttl):
        """Test that default TTL is applied"""
        await cache_with_ttl.set("key1", "value1")
        # Value should be present (TTL not expired)
        result = await cache_with_ttl.get("key1")
        assert result == "value1"

    async def test_explicit_ttl_overrides_default(self, cache_with_ttl):
        """Test explicit TTL overrides default"""
        await cache_with_ttl.set("key1", "value1", ttl=7200)
        result = await cache_with_ttl.get("key1")
        assert result == "value1"
