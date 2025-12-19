from cache_adapters import CacheInterface
from dependency_injector import containers, providers
from llm_adapters import LLMInterface

from rewriteforge.app.services.rewrite_service import RewriteService
from rewriteforge.config.settings import Settings


class Container(containers.DeclarativeContainer):
    """
    IoC Container - Laravel's Service Container equivalent.

    Uses contract.resolve() for auto-registered adapters.
    No factory needed — the contract IS the registry.
    """

    # Configuration
    config = providers.Singleton(Settings)

    # LLM Adapter - resolved by name from auto-registry
    llm_adapter = providers.Singleton(
        LLMInterface.resolve,
        name=config.provided.llm_provider,
        api_key=config.provided.llm_api_key,
        model=config.provided.llm_model,
    )

    # Cache Adapter - resolved by name from auto-registry
    cache_adapter = providers.Singleton(
        CacheInterface.resolve,
        name=config.provided.cache_backend,
        default_ttl=config.provided.cache_ttl,
        url=config.provided.cache_redis_url,
    )

    # Services - depend on contracts, receive implementations
    rewrite_service = providers.Factory(
        RewriteService,
        llm=llm_adapter,
        cache=cache_adapter,
        config=config,
    )
