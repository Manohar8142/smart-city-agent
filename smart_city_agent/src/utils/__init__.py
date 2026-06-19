"""
Utilities package for Smart City Agent.

This package contains utility functions, logging, errors, etc.
"""

from src.utils.logging import logger
from src.utils.errors import (
    SmartCityError,
    ToolExecutionError,
    ValidationError,
    ConfigurationError,
    ExternalAPIError,
)

__all__ = [
    "logger",
    "SmartCityError",
    "ToolExecutionError",
    "ValidationError",
    "ConfigurationError",
    "ExternalAPIError",
]
