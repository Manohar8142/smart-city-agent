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
from .tracing import (
    observe_sync,
    observe_async,
    trace_context,
    async_trace_context,
    langfuse_client,
    langfuse_context,
    flush_traces,
    serialize_for_tracing,
)

__all__ = [
    "logger",
    "SmartCityError",
    "ToolExecutionError",
    "ValidationError",
    "ConfigurationError",
    "ExternalAPIError",
    "observe_sync",
    "observe_async",
    "trace_context",
    "async_trace_context",
    "langfuse_client",
    "langfuse_context",
    "flush_traces",
    "serialize_for_tracing",
]
