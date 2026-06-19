"""
Time tool for Smart City Agent.

Provides current time information for various cities with timezone support.
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..utils.logging import logger
from ..utils.errors import ValidationError, ToolExecutionError
from ..utils.tracing import observe


# TIMEZONE MAPPING
# Why separate? Easy to add new cities, easy to test, easy to maintain
# Covers 60+ major cities across all continents
CITY_TIMEZONES = {
    # === NORTH AMERICA (20 cities) ===
    "new york": "America/New_York",  # UTC-5/-4 (EST/EDT)
    "los angeles": "America/Los_Angeles",  # UTC-8/-7 (PST/PDT)
    "chicago": "America/Chicago",  # UTC-6/-5 (CST/CDT)
    "toronto": "America/Toronto",  # UTC-5/-4 (EST/EDT)
    "vancouver": "America/Vancouver",  # UTC-8/-7 (PST/PDT)
    "montreal": "America/Montreal",  # UTC-5/-4 (EST/EDT)
    "mexico city": "America/Mexico_City",  # UTC-6/-5 (CST/CDT)
    "san francisco": "America/Los_Angeles",  # UTC-8/-7 (PST/PDT)
    "seattle": "America/Los_Angeles",  # UTC-8/-7 (PST/PDT)
    "boston": "America/New_York",  # UTC-5/-4 (EST/EDT)
    "washington": "America/New_York",  # UTC-5/-4 (EST/EDT)
    "miami": "America/New_York",  # UTC-5/-4 (EST/EDT)
    "denver": "America/Denver",  # UTC-7/-6 (MST/MDT)
    "phoenix": "America/Phoenix",  # UTC-7 (MST, no DST)
    "houston": "America/Chicago",  # UTC-6/-5 (CST/CDT)
    "dallas": "America/Chicago",  # UTC-6/-5 (CST/CDT)
    "atlanta": "America/New_York",  # UTC-5/-4 (EST/EDT)
    "philadelphia": "America/New_York",  # UTC-5/-4 (EST/EDT)
    "las vegas": "America/Los_Angeles",  # UTC-8/-7 (PST/PDT)
    "portland": "America/Los_Angeles",  # UTC-8/-7 (PST/PDT)
    # === SOUTH AMERICA (6 cities) ===
    "sao paulo": "America/Sao_Paulo",  # UTC-3 (BRT)
    "rio de janeiro": "America/Sao_Paulo",  # UTC-3 (BRT)
    "buenos aires": "America/Argentina/Buenos_Aires",  # UTC-3 (ART)
    "bogota": "America/Bogota",  # UTC-5 (COT)
    "lima": "America/Lima",  # UTC-5 (PET)
    "santiago": "America/Santiago",  # UTC-4/-3 (CLT/CLST)
    # === EUROPE (18 cities) ===
    "london": "Europe/London",  # UTC+0/+1 (GMT/BST)
    "paris": "Europe/Paris",  # UTC+1/+2 (CET/CEST)
    "berlin": "Europe/Berlin",  # UTC+1/+2 (CET/CEST)
    "madrid": "Europe/Madrid",  # UTC+1/+2 (CET/CEST)
    "rome": "Europe/Rome",  # UTC+1/+2 (CET/CEST)
    "amsterdam": "Europe/Amsterdam",  # UTC+1/+2 (CET/CEST)
    "brussels": "Europe/Brussels",  # UTC+1/+2 (CET/CEST)
    "vienna": "Europe/Vienna",  # UTC+1/+2 (CET/CEST)
    "zurich": "Europe/Zurich",  # UTC+1/+2 (CET/CEST)
    "stockholm": "Europe/Stockholm",  # UTC+1/+2 (CET/CEST)
    "copenhagen": "Europe/Copenhagen",  # UTC+1/+2 (CET/CEST)
    "oslo": "Europe/Oslo",  # UTC+1/+2 (CET/CEST)
    "helsinki": "Europe/Helsinki",  # UTC+2/+3 (EET/EEST)
    "moscow": "Europe/Moscow",  # UTC+3 (MSK)
    "istanbul": "Europe/Istanbul",  # UTC+3 (TRT)
    "athens": "Europe/Athens",  # UTC+2/+3 (EET/EEST)
    "barcelona": "Europe/Madrid",  # UTC+1/+2 (CET/CEST)
    "munich": "Europe/Berlin",  # UTC+1/+2 (CET/CEST)
    # === ASIA (20 cities) ===
    "tokyo": "Asia/Tokyo",  # UTC+9 (JST)
    "dubai": "Asia/Dubai",  # UTC+4 (GST)
    "mumbai": "Asia/Kolkata",  # UTC+5:30 (IST)
    "singapore": "Asia/Singapore",  # UTC+8 (SGT)
    "hong kong": "Asia/Hong_Kong",  # UTC+8 (HKT)
    "shanghai": "Asia/Shanghai",  # UTC+8 (CST)
    "beijing": "Asia/Shanghai",  # UTC+8 (CST)
    "seoul": "Asia/Seoul",  # UTC+9 (KST)
    "bangkok": "Asia/Bangkok",  # UTC+7 (ICT)
    "kuala lumpur": "Asia/Kuala_Lumpur",  # UTC+8 (MYT)
    "jakarta": "Asia/Jakarta",  # UTC+7 (WIB)
    "manila": "Asia/Manila",  # UTC+8 (PST)
    "delhi": "Asia/Kolkata",  # UTC+5:30 (IST)
    "bangalore": "Asia/Kolkata",  # UTC+5:30 (IST)
    "kolkata": "Asia/Kolkata",  # UTC+5:30 (IST)
    "karachi": "Asia/Karachi",  # UTC+5 (PKT)
    "tehran": "Asia/Tehran",  # UTC+3:30/+4:30 (IRST/IRDT)
    "tel aviv": "Asia/Tel_Aviv",  # UTC+2/+3 (IST/IDT)
    "riyadh": "Asia/Riyadh",  # UTC+3 (AST)
    "ho chi minh": "Asia/Ho_Chi_Minh",  # UTC+7 (ICT)
    # === AFRICA (6 cities) ===
    "cairo": "Africa/Cairo",  # UTC+2 (EET)
    "lagos": "Africa/Lagos",  # UTC+1 (WAT)
    "nairobi": "Africa/Nairobi",  # UTC+3 (EAT)
    "johannesburg": "Africa/Johannesburg",  # UTC+2 (SAST)
    "cape town": "Africa/Johannesburg",  # UTC+2 (SAST)
    "casablanca": "Africa/Casablanca",  # UTC+0/+1 (WET/WEST)
    # === OCEANIA (6 cities) ===
    "sydney": "Australia/Sydney",  # UTC+10/+11 (AEST/AEDT)
    "melbourne": "Australia/Melbourne",  # UTC+10/+11 (AEST/AEDT)
    "brisbane": "Australia/Brisbane",  # UTC+10 (AEST, no DST)
    "perth": "Australia/Perth",  # UTC+8 (AWST)
    "auckland": "Pacific/Auckland",  # UTC+12/+13 (NZST/NZDT)
    "wellington": "Pacific/Auckland",  # UTC+12/+13 (NZST/NZDT)
}


@observe(name="get_time")
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

    Observability:
        This function is traced in Langfuse to monitor:
        - Tool execution time
        - City lookup success/failure
        - Timezone conversion errors
        - Query patterns across cities

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
            # Show a sample of cities instead of all (too long for LLM context)
            total_cities = len(CITY_TIMEZONES)
            sample_cities = sorted(CITY_TIMEZONES.keys())[:10]
            sample_str = ", ".join(sample_cities)
            return {
                "status": "error",
                "error_message": (
                    f"Sorry, I don't have timezone information for '{city}'. "
                    f"I support {total_cities} cities including: {sample_str}, and more. "
                    f"Try a major city name."
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
        list[str]: List of supported city names (alphabetically sorted)

    Example:
        >>> cities = list_supported_cities()
        >>> print(cities)
        ['auckland', 'atlanta', 'bangkok', ...]
    """
    return sorted(CITY_TIMEZONES.keys())


def get_cities_by_region() -> dict[str, list[str]]:
    """
    Get cities organized by geographical region.

    Returns:
        dict: Cities grouped by region

    Example:
        >>> regions = get_cities_by_region()
        >>> print(regions['asia'])
        ['bangkok', 'beijing', 'delhi', ...]
    """
    regions = {
        "north_america": [],
        "south_america": [],
        "europe": [],
        "asia": [],
        "africa": [],
        "oceania": [],
    }

    # Categorize cities by timezone prefix
    for city, tz in CITY_TIMEZONES.items():
        if tz.startswith("America/"):
            # Distinguish North vs South America by timezone
            if any(
                sa in tz
                for sa in ["Sao_Paulo", "Buenos_Aires", "Bogota", "Lima", "Santiago"]
            ):
                regions["south_america"].append(city)
            else:
                regions["north_america"].append(city)
        elif tz.startswith("Europe/"):
            regions["europe"].append(city)
        elif tz.startswith("Asia/"):
            regions["asia"].append(city)
        elif tz.startswith("Africa/"):
            regions["africa"].append(city)
        elif tz.startswith(("Australia/", "Pacific/")):
            regions["oceania"].append(city)

    # Sort cities within each region
    for region in regions:
        regions[region].sort()

    return regions


def search_cities(query: str) -> list[str]:
    """
    Search for cities matching a partial name.

    Args:
        query (str): Partial city name to search for

    Returns:
        list[str]: Matching city names

    Example:
        >>> search_cities("york")
        ['new york']
        >>> search_cities("a")
        ['auckland', 'atlanta', 'athens', ...]
    """
    query_lower = query.lower().strip()
    if not query_lower:
        return []

    matches = [city for city in CITY_TIMEZONES.keys() if query_lower in city]
    return sorted(matches)
