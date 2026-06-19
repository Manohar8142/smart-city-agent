"""
Utilities package for Smart City Agent.

This package contains utility functions, logging, errors, and observability.
"""

from .logging import logger
from .errors import (
    SmartCityError,
    ToolExecutionError,
    ValidationError,
    ConfigurationError,
    ExternalAPIError,
)
from .tracing import observe, langfuse_client, flush_traces

__all__ = [
    "logger",
    "SmartCityError",
    "ToolExecutionError",
    "ValidationError",
    "ConfigurationError",
    "ExternalAPIError",
    "observe",
    "langfuse_client",
    "flush_traces",
]
