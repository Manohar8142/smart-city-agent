"""
OpenWeatherMap API client.

API Documentation: https://openweathermap.org/api

CONCEPT: API Client Pattern
- Wraps API calls in clean Python methods
- Handles authentication (API key)
- Parses responses into Pydantic models
- Integrates rate limiting and caching
- Provides consistent error handling
"""

from typing import Optional
from ..base import BaseHTTPClient, TokenBucketRateLimiter, CacheManager
from .models import CurrentWeatherResponse, ForecastResponse, AirQualityResponse
from ...config.settings import settings
from ...utils.logging import logger
from ...utils.errors import ExternalAPIError, ValidationError
from ...utils.tracing import observe_async, langfuse_context


class WeatherAPIClient:
    """
    Client for OpenWeatherMap API.

    Features:
    - Current weather
    - 5-day forecast
    - Air quality data
    - Rate limiting (60 req/min)
    - Response caching (5 min TTL)

    CONCEPT: Why async?
    - Weather API calls are I/O-bound
    - Async allows concurrent requests
    - Can fetch multiple cities in parallel
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Weather API client.

        Args:
            api_key: OpenWeatherMap API key (defaults to settings)
        """
        self.api_key = api_key or settings.openweathermap_api_key
        if not self.api_key:
            raise ValidationError(
                "OpenWeatherMap API key not provided",
                details={"env_var": "OPENWEATHERMAP_API_KEY"},
            )

        # CONCEPT: HTTP client for API calls
        self.http_client = BaseHTTPClient(
            base_url=self.BASE_URL,
            timeout=10.0,
        )

        # CONCEPT: Rate limiter (60 requests/minute)
        # Free tier limit: 60 calls/minute, 1M calls/month
        self.rate_limiter = TokenBucketRateLimiter(
            max_requests=settings.weather_rate_limit,
            time_window=60.0,  # per minute
        )

        # CONCEPT: Cache manager (reduce API calls)
        self.cache = CacheManager()

        logger.info("Weather API client initialized")

    @observe_async(name="get_current_weather", as_type="tool")
    async def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        units: str = "metric",
    ) -> CurrentWeatherResponse:
        """
        Get current weather data.

        CONCEPT: Flexible input
        - By city name: get_current_weather(city="London")
        - By coordinates: get_current_weather(lat=51.5, lon=-0.1)
        - Units: metric (Celsius), imperial (Fahrenheit), standard (Kelvin)

        Args:
            city: City name (e.g., "London", "New York")
            lat: Latitude
            lon: Longitude
            units: Temperature units (metric/imperial/standard)

        Returns:
            CurrentWeatherResponse with weather data

        Raises:
            ValidationError: If invalid parameters
            ExternalAPIError: If API call fails

        Example:
            >>> client = WeatherAPIClient()
            >>> async with client.http_client:
            >>>     weather = await client.get_current_weather(city="Tokyo")
            >>>     print(f"Temp: {weather.temperature}°C")
        """
        # Validation
        if not city and not (lat and lon):
            raise ValidationError(
                "Must provide either city name or coordinates",
                details={"city": city, "lat": lat, "lon": lon},
            )

        # Check cache first
        cache_key = {"city": city, "lat": lat, "lon": lon, "units": units}
        cached = self.cache.get(ttl=settings.cache_ttl_weather, **cache_key)
        if cached:
            logger.debug(f"Returning cached weather for {city or (lat, lon)}")
            return CurrentWeatherResponse(**cached)

        # CONCEPT: Rate limiting before API call
        # Prevents 429 (Too Many Requests) errors
        await self.rate_limiter.acquire()

        # Build request params
        params = {
            "appid": self.api_key,
            "units": units,
        }

        if city:
            params["q"] = city
        else:
            params["lat"] = lat
            params["lon"] = lon

        try:
            logger.info(f"Fetching current weather for {city or (lat, lon)}")

            async with self.http_client as client:
                data = await client.get("/weather", params=params)

            # CONCEPT: Parse response with Pydantic
            # Automatic validation, type conversion
            response = CurrentWeatherResponse(**data)

            # Cache the response
            self.cache.set(data, ttl=settings.cache_ttl_weather, **cache_key)

            # Update Langfuse trace with metadata
            if langfuse_context:
                langfuse_context.update_current_observation(
                    metadata={
                        "city": response.name,
                        "country": response.sys.country,
                        "temperature": response.temperature,
                        "condition": response.condition,
                        "api": "OpenWeatherMap",
                        "cached": False,
                    }
                )

            logger.info(
                f"Weather retrieved: {response.name}, "
                f"{response.temperature}°{'C' if units == 'metric' else 'F'}, "
                f"{response.condition}"
            )

            return response

        except ValidationError:
            # Pydantic validation error
            raise
        except ExternalAPIError as e:
            # Re-raise API errors
            raise
        except Exception as e:
            logger.exception(f"Unexpected error fetching weather: {e}")
            raise ExternalAPIError(
                f"Failed to fetch weather data: {str(e)}",
                api_name="OpenWeatherMap",
                details={"error": str(e)},
            )

    @observe_async(name="get_forecast", as_type="tool")
    async def get_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        units: str = "metric",
    ) -> ForecastResponse:
        """
        Get 5-day forecast (3-hour intervals).

        CONCEPT: Forecast data
        - 40 forecast points (8 per day * 5 days)
        - 3-hour intervals
        - Same data structure as current weather

        Args:
            city: City name
            lat: Latitude
            lon: Longitude
            units: Temperature units

        Returns:
            ForecastResponse with forecast data
        """
        if not city and not (lat and lon):
            raise ValidationError(
                "Must provide either city name or coordinates",
                details={"city": city, "lat": lat, "lon": lon},
            )

        # Check cache
        cache_key = {
            "city": city,
            "lat": lat,
            "lon": lon,
            "units": units,
            "type": "forecast",
        }
        cached = self.cache.get(ttl=settings.cache_ttl_weather, **cache_key)
        if cached:
            return ForecastResponse(**cached)

        await self.rate_limiter.acquire()

        params = {
            "appid": self.api_key,
            "units": units,
        }

        if city:
            params["q"] = city
        else:
            params["lat"] = lat
            params["lon"] = lon

        try:
            logger.info(f"Fetching forecast for {city or (lat, lon)}")

            async with self.http_client as client:
                data = await client.get("/forecast", params=params)

            response = ForecastResponse(**data)

            # Cache forecast
            self.cache.set(data, ttl=settings.cache_ttl_weather, **cache_key)

            logger.info(
                f"Forecast retrieved: {response.city.name}, {response.cnt} items"
            )

            return response

        except Exception as e:
            logger.exception(f"Error fetching forecast: {e}")
            raise ExternalAPIError(
                f"Failed to fetch forecast: {str(e)}",
                api_name="OpenWeatherMap",
                details={"error": str(e)},
            )

    @observe_async(name="get_air_quality", as_type="tool")
    async def get_air_quality(self, lat: float, lon: float) -> AirQualityResponse:
        """
        Get air quality data.

        CONCEPT: Air Quality Index (AQI)
        - 1: Good
        - 2: Fair
        - 3: Moderate
        - 4: Poor
        - 5: Very Poor

        Note: Air quality requires coordinates (not city name)

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            AirQualityResponse with AQI and pollutant data
        """
        # Check cache
        cache_key = {"lat": lat, "lon": lon, "type": "air_quality"}
        cached = self.cache.get(ttl=settings.cache_ttl_weather, **cache_key)
        if cached:
            return AirQualityResponse(**cached)

        await self.rate_limiter.acquire()

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
        }

        try:
            logger.info(f"Fetching air quality for ({lat}, {lon})")

            async with self.http_client as client:
                data = await client.get("/air_pollution", params=params)

            response = AirQualityResponse(**data)

            # Cache air quality
            self.cache.set(data, ttl=settings.cache_ttl_weather, **cache_key)

            if response.list:
                aqi_data = response.list[0]
                logger.info(
                    f"Air quality retrieved: AQI={aqi_data.aqi} ({aqi_data.aqi_label})"
                )

            return response

        except Exception as e:
            logger.exception(f"Error fetching air quality: {e}")
            raise ExternalAPIError(
                f"Failed to fetch air quality: {str(e)}",
                api_name="OpenWeatherMap",
                details={"error": str(e)},
            )
