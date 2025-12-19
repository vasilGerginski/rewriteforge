from unittest.mock import AsyncMock, MagicMock

import pytest
from rewriteforge.app.exceptions import ValidationError
from rewriteforge.app.services.rewrite_service import RewriteService


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.rewrite.return_value = "Transformed text"
    return llm


@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.get.return_value = None
    return cache


@pytest.fixture
def config():
    config = MagicMock()
    config.max_text_length = 5000
    config.allowed_styles = ["pirate", "haiku", "formal"]
    config.default_style = "formal"
    return config


@pytest.fixture
def service(mock_llm, mock_cache, config):
    return RewriteService(llm=mock_llm, cache=mock_cache, config=config)


class TestRewriteService:
    async def test_rewrite_success(self, service, mock_llm, mock_cache):
        """Test successful rewrite"""
        result = await service.rewrite("Hello world", "pirate")

        assert result["original"] == "Hello world"
        assert result["rewritten"] == "Transformed text"
        assert result["style"] == "pirate"
        assert result["cached"] is False
        mock_llm.rewrite.assert_called_once()
        mock_cache.set.assert_called_once()

    async def test_rewrite_cache_hit(self, service, mock_llm, mock_cache):
        """Test cache hit bypasses LLM"""
        mock_cache.get.return_value = "Cached result"

        result = await service.rewrite("Hello world", "pirate")

        assert result["rewritten"] == "Cached result"
        assert result["cached"] is True
        mock_llm.rewrite.assert_not_called()

    async def test_rewrite_default_style(self, service):
        """Test default style when not provided"""
        result = await service.rewrite("Hello world", None)

        assert result["style"] == "formal"

    async def test_rewrite_invalid_style(self, service):
        """Test rejection of unknown style"""
        with pytest.raises(ValidationError, match="Unknown style"):
            await service.rewrite("Hello world", "shakespeare")

    async def test_rewrite_text_too_long(self, service, config):
        """Test rejection of text exceeding max length"""
        config.max_text_length = 10

        with pytest.raises(ValidationError, match="exceeds maximum length"):
            await service.rewrite("This text is too long", "pirate")

    async def test_cache_key_deterministic(self, service):
        """Test cache key is deterministic for same input"""
        key1 = service._cache_key("Hello world", "pirate")
        key2 = service._cache_key("Hello world", "pirate")

        assert key1 == key2

    async def test_cache_key_different_for_different_input(self, service):
        """Test cache key differs for different input"""
        key1 = service._cache_key("Hello world", "pirate")
        key2 = service._cache_key("Hello world", "formal")
        key3 = service._cache_key("Different text", "pirate")

        assert key1 != key2
        assert key1 != key3
