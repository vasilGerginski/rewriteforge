from llm_adapters.contracts import LLMInterface


class MockAdapter(LLMInterface):
    name = "mock"  # Auto-registered!

    """
    Mock adapter for testing and when no API key is set.
    Wraps text with style indicator.
    """

    def __init__(self, **kwargs):
        pass  # Mock adapter accepts but ignores all kwargs

    async def rewrite(self, text: str, style: str) -> str:
        return f"[*{style}*] {text}"

    async def rewrite_stream(self, text: str, style: str):
        result = await self.rewrite(text, style)
        # Simulate streaming by yielding word by word
        for word in result.split():
            yield word + " "
