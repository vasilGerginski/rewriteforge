# Import providers to trigger __init_subclass__ registration
from llm_adapters import providers  # noqa: F401
from llm_adapters.contracts.llm_interface import LLMInterface

__all__ = ["LLMInterface"]
