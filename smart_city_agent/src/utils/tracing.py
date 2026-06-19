"""
Langfuse tracing utilities for Smart City Agent.

This module initializes and configures Langfuse for observability.

WHY LANGFUSE?
=============
- Track every LLM call (prompts, responses, tokens, cost)
- Monitor tool execution (which tools called, with what params)
- Debug issues (see full execution trace)
- Measure performance (latency of each step)
- Track usage and costs over time

HOW IT WORKS:
=============
1. Initialize Langfuse client with credentials from settings
2. Export @observe decorator to instrument functions
3. Every decorated function sends traces to Langfuse
4. Traces include: inputs, outputs, timing, errors, metadata

USAGE:
======
from src.utils.tracing import observe

@observe(name="my_function")
def my_function(param):
    # This function execution will be traced!
    return result
"""

from functools import wraps
from typing import Callable, Any
from ..config.settings import settings
from .logging import logger

# Initialize Langfuse client (only if enabled)
langfuse_client = None
observe_decorator = None

if settings.enable_langfuse:
    try:
        from langfuse import Langfuse, observe as langfuse_observe

        # Initialize Langfuse with credentials
        langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )

        # Use the real Langfuse observe decorator
        observe_decorator = langfuse_observe

        logger.info("✅ Langfuse tracing enabled")
        logger.info(f"   Host: {settings.langfuse_host}")
        if settings.langfuse_public_key:
            logger.info(f"   Public Key: {settings.langfuse_public_key[:10]}...")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Langfuse: {e}")
        logger.warning("   Tracing will be disabled")
        langfuse_client = None
        observe_decorator = None
else:
    logger.info("ℹ️  Langfuse tracing disabled (enable_langfuse=False)")


def observe(
    name: str | None = None,
    capture_input: bool = True,
    capture_output: bool = True,
    **kwargs,
) -> Callable:
    """
    Decorator to trace function execution with Langfuse.

    If Langfuse is disabled, this becomes a no-op decorator
    that doesn't affect function behavior.

    Args:
        name: Name for the trace (defaults to function name)
        capture_input: Whether to capture function inputs
        capture_output: Whether to capture function outputs
        **kwargs: Additional metadata to attach to trace

    Returns:
        Decorated function with tracing enabled

    Example:
        @observe(name="get_weather", metadata={"tool": "weather"})
        def get_weather(city: str) -> dict:
            return {"temp": "25°C"}
    """

    def decorator(func: Callable) -> Callable:
        # If Langfuse is enabled, use real decorator
        if observe_decorator is not None:
            return observe_decorator(
                name=name or func.__name__,
                capture_input=capture_input,
                capture_output=capture_output,
                **kwargs,
            )(func)

        # Otherwise, return no-op decorator (just returns function unchanged)
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def flush_traces():
    """
    Flush any pending traces to Langfuse.

    Call this before application shutdown to ensure
    all traces are sent.
    """
    if langfuse_client is not None:
        try:
            langfuse_client.flush()
            logger.info("✅ Flushed Langfuse traces")
        except Exception as e:
            logger.error(f"❌ Failed to flush Langfuse traces: {e}")


__all__ = ["observe", "flush_traces", "langfuse_client"]
