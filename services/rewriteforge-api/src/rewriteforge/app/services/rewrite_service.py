import hashlib
from typing import AsyncGenerator, Optional

from cache_adapters.contracts import CacheInterface
from llm_adapters.contracts import LLMInterface

from rewriteforge.app.exceptions import ValidationError
from rewriteforge.config.settings import Settings


class RewriteService:
    """
    Core business logic for text rewriting.

    Depends on contracts only — never knows concrete implementations.
    """

    def __init__(
        self,
        llm: LLMInterface,
        cache: CacheInterface,
        config: Settings,
    ):
        self._llm = llm
        self._cache = cache
        self._config = config

    def _cache_key(self, text: str, style: str) -> str:
        """Generate deterministic cache key"""
        content = f"{text}:{style}"
        return f"rewrite:{hashlib.sha256(content.encode()).hexdigest()}"

    def _validate(self, text: str, style: Optional[str]) -> str:
        """Validate input and return resolved style"""
        if len(text) > self._config.max_text_length:
            raise ValidationError(
                f"Text exceeds maximum length of {self._config.max_text_length} characters"
            )

        resolved_style = style or self._config.default_style

        if resolved_style not in self._config.allowed_styles:
            raise ValidationError(
                f"Unknown style '{resolved_style}'. "
                f"Allowed: {', '.join(self._config.allowed_styles)}"
            )

        return resolved_style

    async def rewrite(self, text: str, style: Optional[str] = None) -> dict:
        """
        Rewrite text in specified style with caching.

        Returns:
            {
                "original": str,
                "rewritten": str,
                "style": str,
                "cached": bool
            }
        """
        resolved_style = self._validate(text, style)
        cache_key = self._cache_key(text, resolved_style)

        # Check cache
        cached_result = await self._cache.get(cache_key)
        if cached_result:
            return {
                "original": text,
                "rewritten": cached_result,
                "style": resolved_style,
                "cached": True,
            }

        # Call LLM
        rewritten = await self._llm.rewrite(text, resolved_style)

        # Store in cache
        await self._cache.set(cache_key, rewritten)

        return {
            "original": text,
            "rewritten": rewritten,
            "style": resolved_style,
            "cached": False,
        }

    async def rewrite_stream(
        self, text: str, style: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Rewrite with streaming response (SSE).
        Note: Streaming bypasses cache.
        """
        resolved_style = self._validate(text, style)

        async for chunk in self._llm.rewrite_stream(text, resolved_style):
            yield chunk
