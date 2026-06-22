"""
Application settings using Pydantic.
Why Pydantic Settings?
- Type-safe configuration
- Automatic .env file loading
- Validation at startup
- IDE autocomplete support
- Environment-specific configs
"""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from env variables
    """

    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment of the application"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging Level"
    )
    ## ========LLM CONFIGURATION========
    groq_api_key: str = Field(..., description="Groq API Key for LLM Inference")
    model_name: str = Field(
        default="groq/llama-3.3-70b-versatile", description="LLM Model Name"
    )
    ## ========LANGFUSE CONFIGURATION========
    langfuse_public_key: str | None = Field(
        default=None, description="Langfuse Public Key for tracing"
    )
    langfuse_secret_key: str | None = Field(
        default=None, description="Langfuse Secret Key for tracing"
    )
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com", description="Langfuse Server URL"
    )
    enable_langfuse: bool = Field(default=False, description="Enable Langfuse Tracing")

    ## ========PHASE 2: API KEYS========
    openweathermap_api_key: str | None = Field(
        default=None, description="OpenWeatherMap API Key"
    )
    newsdata_api_key: str | None = Field(
        default=None, description="NewsData.io API Key"
    )
    firecrawl_api_key: str | None = Field(default=None, description="Firecrawl API Key")
    positionstack_api_key: str | None = Field(
        default=None, description="PositionStack API Key for geocoding"
    )

    ## ========PHASE 2: RATE LIMITS========
    weather_rate_limit: int = Field(
        default=60, description="Weather API calls per minute"
    )
    news_rate_limit: int = Field(default=100, description="News API calls per day")
    firecrawl_rate_limit: int = Field(
        default=30, description="Firecrawl calls per minute"
    )
    location_rate_limit: int = Field(
        default=300, description="Location API calls per day"
    )

    ## ========PHASE 2: CACHE TTL (seconds)========
    cache_ttl_weather: int = Field(default=300, description="Weather cache TTL (5 min)")
    cache_ttl_news: int = Field(default=900, description="News cache TTL (15 min)")
    cache_ttl_location: int = Field(
        default=86400, description="Location cache TTL (24 hrs)"
    )
    cache_ttl_firecrawl: int = Field(
        default=3600, description="Firecrawl cache TTL (1 hr)"
    )

    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_key(cls, v: str) -> str:
        """Ensure Groq API Key has correct format"""
        if not v.startswith("gsk_"):
            raise ValueError("Groq API Key must start with 'gsk_'")
        return v

    @field_validator("enable_langfuse")
    @classmethod
    def validate_enable_langfuse(cls, v: bool, info) -> bool:
        """If Langfuse enabled, ensure Keys are provided"""
        if v:
            data = info.data
            if not data.get("langfuse_public_key") or not data.get(
                "langfuse_secret_key"
            ):
                raise ValueError(
                    "enable_langfuse = True requires both langfuse_public_key and langfuse_secret_key to be set"
                )
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
