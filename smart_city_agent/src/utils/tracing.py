"""
Enhanced Langfuse tracing utilities with explicit input/output capture.

CONCEPT: Why explicit tracing?
- Automatic capture doesn't always work with async functions
- Complex objects (Pydantic models, dicts) need explicit serialization
- Better control over what data is sent to Langfuse
- Proper parent-child trace hierarchy
"""

from functools import wraps
from typing import Callable, Any, Optional, Dict
from contextlib import asynccontextmanager, contextmanager
from ..config.settings import settings
from .logging import logger

# Initialize Langfuse client
langfuse_client = None
langfuse_context = None

if settings.enable_langfuse:
    try:
        from langfuse import Langfuse

        langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )

        # Try to import context if available
        try:
            from langfuse import langfuse_context as lf_context

            langfuse_context = lf_context
        except ImportError:
            # Context not available in this version
            langfuse_context = None

        logger.info("Langfuse tracing enabled")
        logger.info(f"   Host: {settings.langfuse_host}")
        if settings.langfuse_public_key:
            logger.info(f"   Public Key: {settings.langfuse_public_key[:10]}...")

    except Exception as e:
        logger.error(f"Failed to initialize Langfuse: {e}")
        logger.warning("   Tracing will be disabled")
        langfuse_client = None
        langfuse_context = None
else:
    logger.info("Langfuse tracing disabled (enable_langfuse=False)")


def serialize_for_tracing(obj: Any) -> Any:
    """
    Serialize object for Langfuse tracing.

    CONCEPT: Serialization
    - Pydantic models → dict
    - Complex objects → JSON-compatible format
    - Handles common types automatically
    """
    # Already serializable
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj

    # Dict or list
    if isinstance(obj, dict):
        return {k: serialize_for_tracing(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_for_tracing(item) for item in obj]

    # Pydantic model (has .model_dump() or .dict())
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()

    # Fallback: convert to string
    return str(obj)


@contextmanager
def trace_context(
    name: str,
    trace_type: str = "span",
    input_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for synchronous function tracing.

    CONCEPT: Context manager pattern
    - Automatically handles start/end of trace
    - Captures output or error
    - Ensures trace is completed even if exception occurs

    Usage:
        with trace_context("my_function", input_data={"city": "London"}):
            result = do_something()
            return result
    """
    if not langfuse_client or not langfuse_context:
        # No-op if Langfuse disabled
        yield None
        return

    try:
        # Update current observation with input
        langfuse_context.update_current_observation(
            name=name,
            input=serialize_for_tracing(input_data) if input_data else None,
            metadata=metadata or {},
        )

        # Yield control back to function
        output = yield langfuse_context

        # Update with output after function completes
        if output is not None:
            langfuse_context.update_current_observation(
                output=serialize_for_tracing(output)
            )

    except Exception as e:
        # Capture error in trace
        if langfuse_context:
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e),
                output={"error": str(e), "error_type": type(e).__name__},
            )
        raise


@asynccontextmanager
async def async_trace_context(
    name: str,
    trace_type: str = "span",
    input_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for asynchronous function tracing.

    CONCEPT: Async context manager
    - Same as trace_context but for async functions
    - Properly handles async/await

    Usage:
        async with async_trace_context("fetch_weather", input_data={...}):
            result = await api_call()
            return result
    """
    if not langfuse_client or not langfuse_context:
        yield None
        return

    try:
        langfuse_context.update_current_observation(
            name=name,
            input=serialize_for_tracing(input_data) if input_data else None,
            metadata=metadata or {},
        )

        output = yield langfuse_context

        if output is not None:
            langfuse_context.update_current_observation(
                output=serialize_for_tracing(output)
            )

    except Exception as e:
        if langfuse_context:
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e),
                output={"error": str(e), "error_type": type(e).__name__},
            )
        raise


def observe_sync(
    name: Optional[str] = None,
    as_type: str = "span",
    capture_input: bool = True,
    capture_output: bool = True,
):
    """
    Enhanced decorator for synchronous functions with explicit I/O capture.

    CONCEPT: Decorator pattern
    - Wraps function with tracing logic
    - Captures input args/kwargs
    - Captures return value
    - Handles errors gracefully
    """

    def decorator(func: Callable) -> Callable:
        if not langfuse_client:
            # No-op decorator if disabled
            return func

        from langfuse import observe

        @observe(name=name or func.__name__, as_type=as_type)
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Capture input
            if capture_input and langfuse_context:
                input_data = {
                    "args": serialize_for_tracing(args) if args else None,
                    "kwargs": serialize_for_tracing(kwargs) if kwargs else None,
                }
                langfuse_context.update_current_observation(input=input_data)

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Capture output
                if capture_output and langfuse_context and result is not None:
                    langfuse_context.update_current_observation(
                        output=serialize_for_tracing(result)
                    )

                return result

            except Exception as e:
                # Capture error
                if langfuse_context:
                    langfuse_context.update_current_observation(
                        level="ERROR",
                        status_message=str(e),
                        output={"error": str(e), "error_type": type(e).__name__},
                    )
                raise

        return wrapper

    return decorator


def observe_async(
    name: Optional[str] = None,
    as_type: str = "span",
    capture_input: bool = True,
    capture_output: bool = True,
):
    """
    Enhanced decorator for asynchronous functions with explicit I/O capture.
    """

    def decorator(func: Callable) -> Callable:
        if not langfuse_client:
            return func

        from langfuse import observe

        @observe(name=name or func.__name__, as_type=as_type)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if capture_input and langfuse_context:
                input_data = {
                    "args": serialize_for_tracing(args) if args else None,
                    "kwargs": serialize_for_tracing(kwargs) if kwargs else None,
                }
                langfuse_context.update_current_observation(input=input_data)

            try:
                result = await func(*args, **kwargs)

                if capture_output and langfuse_context and result is not None:
                    langfuse_context.update_current_observation(
                        output=serialize_for_tracing(result)
                    )

                return result

            except Exception as e:
                if langfuse_context:
                    langfuse_context.update_current_observation(
                        level="ERROR",
                        status_message=str(e),
                        output={"error": str(e), "error_type": type(e).__name__},
                    )
                raise

        return wrapper

    return decorator


def flush_traces():
    """
    Flush pending traces to Langfuse.

    CONCEPT: Buffering
    - Langfuse buffers traces for performance
    - Call flush() to send immediately
    - Important before app shutdown
    """
    if langfuse_client:
        try:
            langfuse_client.flush()
            logger.info("Flushed Langfuse traces")
        except Exception as e:
            logger.error(f"Failed to flush Langfuse traces: {e}")


__all__ = [
    "trace_context",
    "async_trace_context",
    "observe_sync",
    "observe_async",
    "flush_traces",
    "langfuse_client",
    "langfuse_context",
    "serialize_for_tracing",
]
