"""
Weather tool for Smart City Agent.

This module provides weather information retrieval functionality.
Currently returns hardcoded data (Phase 1).
Future: Will integrate with OpenWeatherMap API (Phase 2).
"""

from ..utils.logging import logger
from ..utils.errors import ValidationError, ToolExecutionError
from ..utils.tracing import observe


@observe(name="get_weather")
def get_weather(city: str) -> dict:
    """
    Get weather information for a given city.

    Args:
        city (str): Name of the city to get weather for

    Returns:
        dict: Weather information with status and report/error_message

    Raises:
        ValidationError: If city parameter is invalid
        ToolExecutionError: If weather retrieval fails

    Observability:
        This function is traced in Langfuse to monitor:
        - Tool execution time
        - Input validation errors
        - Success/failure rates
        - City query patterns

    Example:
        >>> result = get_weather("New York")
        >>> print(result)
        {
            "status": "success",
            "report": {
                "temperature": "25°C",
                "humidity": "60%",
                "condition": "Sunny"
            }
        }
    """
    # INPUT VALIDATION
    # Why? Prevent invalid inputs from causing errors later
    logger.debug(f"get_weather called with city: {city}")

    if not city:
        logger.warning("get_weather called with empty city parameter")
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
    # Phase 1: Hardcoded data for New York only
    # Phase 2: Will call OpenWeatherMap API

    city_normalized = city.strip().lower()

    try:
        if city_normalized == "new york":
            logger.info(f"Returning weather data for {city}")
            return {
                "status": "success",
                "report": {
                    "city": city,
                    "temperature": "25°C",
                    "humidity": "60%",
                    "condition": "Sunny",
                    "feels_like": "26°C",
                    "wind_speed": "10 km/h",
                },
            }
        else:
            # Not yet supported - will be in Phase 2
            logger.info(f"Weather data not available for {city}")
            return {
                "status": "error",
                "error_message": f"Weather information for '{city}' is not yet available. Currently only New York is supported.",
            }

    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Unexpected error in get_weather for city: {city}")
        raise ToolExecutionError(
            f"Failed to retrieve weather for {city}",
            details={"city": city, "error": str(e)},
        )


# Why separate function? Makes testing easier, can mock data source
def _get_hardcoded_weather(city: str) -> dict:
    """
    Internal function to get hardcoded weather data.

    This will be replaced with API calls in Phase 2.
    Keeping it separate makes refactoring easier.
    """
    weather_data = {
        "new york": {
            "temperature": "25°C",
            "humidity": "60%",
            "condition": "Sunny",
            "feels_like": "26°C",
            "wind_speed": "10 km/h",
        }
        # Future: Add more cities here
    }

    return weather_data.get(city.lower())
