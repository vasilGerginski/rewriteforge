import pytest
from llm_adapters import LLMInterface
from llm_adapters.providers.anthropic_adapter import AnthropicAdapter
from llm_adapters.providers.mock_adapter import MockAdapter
from llm_adapters.providers.openai_adapter import OpenAIAdapter


class TestAdapterRegistry:
    def test_all_adapters_registered(self):
        """Test that all adapters are auto-registered"""
        available = LLMInterface.available()

        assert "mock" in available
        assert "anthropic" in available
        assert "openai" in available

    def test_resolve_mock_adapter(self):
        """Test resolving mock adapter by name"""
        adapter = LLMInterface.resolve("mock")

        assert isinstance(adapter, MockAdapter)

    def test_resolve_anthropic_adapter(self):
        """Test resolving anthropic adapter by name"""
        adapter = LLMInterface.resolve("anthropic", api_key="test-key")

        assert isinstance(adapter, AnthropicAdapter)

    def test_resolve_openai_adapter(self):
        """Test resolving openai adapter by name"""
        adapter = LLMInterface.resolve("openai", api_key="test-key")

        assert isinstance(adapter, OpenAIAdapter)

    def test_resolve_unknown_raises(self):
        """Test that resolving unknown adapter raises KeyError"""
        with pytest.raises(KeyError, match="Unknown LLM provider"):
            LLMInterface.resolve("unknown")


class TestMockAdapter:
    @pytest.fixture
    def adapter(self):
        return MockAdapter()

    async def test_rewrite_pirate_style(self, adapter):
        """Test pirate style transformation"""
        result = await adapter.rewrite("Hello world", "pirate")

        assert result == "[*pirate*] Hello world"

    async def test_rewrite_haiku_style(self, adapter):
        """Test haiku style transformation"""
        result = await adapter.rewrite("Hello world", "haiku")

        assert result == "[*haiku*] Hello world"

    async def test_rewrite_formal_style(self, adapter):
        """Test formal style transformation"""
        result = await adapter.rewrite("Hello world", "formal")

        assert result == "[*formal*] Hello world"

    async def test_rewrite_unknown_style(self, adapter):
        """Test unknown style wraps with that style"""
        result = await adapter.rewrite("Hello world", "shakespeare")

        assert result == "[*shakespeare*] Hello world"

    async def test_rewrite_stream(self, adapter):
        """Test streaming returns chunks"""
        chunks = []
        async for chunk in adapter.rewrite_stream("Hello world", "pirate"):
            chunks.append(chunk)

        assert len(chunks) > 0
        result = "".join(chunks).strip()
        assert result == "[*pirate*] Hello world"
