"""
Time tool for Smart City Agent.

Provides current time information for various cities with timezone support.
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.utils.logging import logger
from src.utils.errors import ValidationError, ToolExecutionError


# TIMEZONE MAPPING
# Why separate? Easy to add new cities, easy to test, easy to maintain
CITY_TIMEZONES = {
    "new york": "America/New_York",
    "london": "Europe/London",
    "paris": "Europe/Paris",
    "tokyo": "Asia/Tokyo",
    "sydney": "Australia/Sydney",
    "los angeles": "America/Los_Angeles",
    "chicago": "America/Chicago",
    "dubai": "Asia/Dubai",
    "mumbai": "Asia/Kolkata",
    "singapore": "Asia/Singapore",
}


def get_time(city: str) -> dict:
    """
    Get current time for a given city.

    Args:
        city (str): Name of the city to get time for

    Returns:
        dict: Time information with status and report/error_message

    Raises:
        ValidationError: If city parameter is invalid
        ToolExecutionError: If time retrieval fails

    Example:
        >>> result = get_time("New York")
        >>> print(result)
        {
            "status": "success",
            "report": "The current time in New York is 2026-06-19 15:30:45 EDT-0400"
        }
    """
    # INPUT VALIDATION
    logger.debug(f"get_time called with city: {city}")

    if not city:
        logger.warning("get_time called with empty city parameter")
        raise ValidationError(
            "City parameter is required", details={"parameter": "city", "value": city}
        )

    if not isinstance(city, str):
        logger.warning(f"Invalid city type: {type(city)}")
        raise ValidationError(
            "City must be a string",
            details={"parameter": "city", "type": type(city).__name__},
        )

    if len(city.strip()) < 2:
        logger.warning(f"City name too short: {city}")
        raise ValidationError(
            "City name must be at least 2 characters",
            details={"parameter": "city", "length": len(city)},
        )

    # BUSINESS LOGIC
    city_normalized = city.strip().lower()

    try:
        # Get timezone for city
        tz_identifier = CITY_TIMEZONES.get(city_normalized)

        if not tz_identifier:
            logger.info(f"Timezone not available for {city}")
            available_cities = ", ".join(sorted(CITY_TIMEZONES.keys()))
            return {
                "status": "error",
                "error_message": (
                    f"Sorry, I don't have timezone information for '{city}'. "
                    f"Supported cities: {available_cities}"
                ),
            }

        # Get current time in that timezone
        tz = ZoneInfo(tz_identifier)
        now = datetime.now(tz)

        # Format time nicely
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
        report = f"The current time in {city.title()} is {formatted_time}"

        logger.info(f"Successfully retrieved time for {city}")

        return {
            "status": "success",
            "report": report,
            "data": {  # Extra structured data for future use
                "city": city.title(),
                "timezone": tz_identifier,
                "timestamp": now.isoformat(),
                "utc_offset": now.strftime("%z"),
            },
        }

    except ZoneInfoNotFoundError as e:
        # This shouldn't happen if CITY_TIMEZONES is correct
        logger.error(f"Invalid timezone identifier: {tz_identifier}")
        raise ToolExecutionError(
            f"Invalid timezone configuration for {city}",
            details={"city": city, "timezone": tz_identifier, "error": str(e)},
        )

    except Exception as e:
        logger.exception(f"Unexpected error in get_time for city: {city}")
        raise ToolExecutionError(
            f"Failed to retrieve time for {city}",
            details={"city": city, "error": str(e)},
        )


def list_supported_cities() -> list[str]:
    """
    Get list of cities with timezone support.

    Returns:
        list[str]: List of supported city names

    Example:
        >>> cities = list_supported_cities()
        >>> print(cities)
        ['chicago', 'dubai', 'london', ...]
    """
    return sorted(CITY_TIMEZONES.keys())
