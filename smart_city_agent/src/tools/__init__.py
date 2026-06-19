"""
Tools package for Smart City Agent.

This package contains all tool functions that agents can use.
"""

from .weather import get_weather
from .time import (
    get_time,
    list_supported_cities,
    get_cities_by_region,
    search_cities,
)

__all__ = [
    "get_weather",
    "get_time",
    "list_supported_cities",
    "get_cities_by_region",
    "search_cities",
]
