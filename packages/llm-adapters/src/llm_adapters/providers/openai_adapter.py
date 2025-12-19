from openai import AsyncOpenAI

from llm_adapters.contracts import LLMInterface


class OpenAIAdapter(LLMInterface):
    name = "openai"  # Auto-registered!

    def __init__(self, api_key: str, model: str = "gpt-4o", **kwargs):
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def rewrite(self, text: str, style: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": f"Rewrite the following text in {style} style. "
                    f"Return ONLY the rewritten text, nothing else.\n\nText: {text}",
                }
            ],
        )
        return response.choices[0].message.content or ""

    async def rewrite_stream(self, text: str, style: str):
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": f"Rewrite the following text in {style} style. "
                    f"Return ONLY the rewritten text, nothing else.\n\nText: {text}",
                }
            ],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
