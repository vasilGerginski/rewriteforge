from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMInterface(ABC):
    """
    Contract for all LLM adapters.

    Subclasses auto-register via __init_subclass__.
    Just declare `name = "provider"` and you're in the registry.
    """

    _registry: dict[str, type["LLMInterface"]] = {}

    name: str  # Each adapter declares its registry key

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Auto-register if class declares a name
        if hasattr(cls, "name") and cls.name:
            LLMInterface._registry[cls.name] = cls

    @classmethod
    def resolve(cls, name: str, **kwargs) -> "LLMInterface":
        """
        Resolve adapter by name from registry.

        Args:
            name: Provider key (e.g., "anthropic", "openai", "mock")
            **kwargs: Arguments passed to adapter constructor

        Returns:
            Instantiated adapter

        Raises:
            KeyError: If provider not found
        """
        if name not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise KeyError(f"Unknown LLM provider '{name}'. Available: {available}")

        # Filter out empty kwargs
        kwargs = {k: v for k, v in kwargs.items() if v}
        return cls._registry[name](**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        """List all registered provider names"""
        return list(cls._registry.keys())

    @abstractmethod
    async def rewrite(self, text: str, style: str) -> str:
        """
        Rewrite text in the specified style.

        Args:
            text: Original text to transform
            style: Target style (pirate, haiku, formal)

        Returns:
            Transformed text
        """
        pass

    @abstractmethod
    def rewrite_stream(self, text: str, style: str) -> AsyncIterator[str]:
        """
        Rewrite text with streaming response.

        Yields:
            Text chunks as they arrive
        """
        ...
