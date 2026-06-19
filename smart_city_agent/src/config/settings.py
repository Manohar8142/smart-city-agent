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
    langfuse_host: str = Field(
        default="https://cloud/langfuse.com", description="Langfuse Server URL"
    )
    enable_langfuse: bool = Field(default=False, description="Enable Langfuse Tracing")

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
