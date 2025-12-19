from anthropic import AsyncAnthropic
from anthropic.types import TextBlock

from llm_adapters.contracts import LLMInterface


class AnthropicAdapter(LLMInterface):
    name = "anthropic"  # Auto-registered!

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", **_kwargs):
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def rewrite(self, text: str, style: str) -> str:
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"Rewrite the following text in {style} style. "
                    f"Return ONLY the rewritten text, nothing else.\n\nText: {text}",
                }
            ],
        )
        block = response.content[0]
        if isinstance(block, TextBlock):
            return block.text
        return ""

    async def rewrite_stream(self, text: str, style: str):
        async with self._client.messages.stream(
            model=self._model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"Rewrite the following text in {style} style. "
                    f"Return ONLY the rewritten text, nothing else.\n\nText: {text}",
                }
            ],
        ) as stream:
            async for chunk in stream.text_stream:
                yield chunk
