from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Server
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")

    # LLM Adapter - simple name, not class path
    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="", alias="LLM_MODEL")

    # Cache Adapter - simple name, not class path
    cache_backend: str = Field(default="memory", alias="CACHE_BACKEND")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    cache_redis_url: str = Field(default="redis://localhost:6379", alias="CACHE_REDIS_URL")

    # Validation
    max_text_length: int = Field(default=5000, alias="MAX_TEXT_LENGTH")
    allowed_styles: list[str] = Field(
        default=["pirate", "haiku", "formal"],
        alias="ALLOWED_STYLES",
    )
    default_style: str = Field(default="formal", alias="DEFAULT_STYLE")
