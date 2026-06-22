"""
Pydantic models for OpenWeatherMap API responses.

CONCEPT: Why Pydantic?
- Runtime type validation (catch errors early)
- Automatic JSON parsing
- IDE autocomplete (better DX)
- Data validation (e.g., temp range, humidity 0-100%)
- Easy serialization/deserialization

WHY NOT just dicts?
- Dict: response["main"]["temp"] - typo-prone, no types
- Pydantic: response.main.temp - type-safe, validated
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List


class Coordinates(BaseModel):
    """Geographic coordinates"""

    lon: float = Field(..., description="Longitude")
    lat: float = Field(..., description="Latitude")


class WeatherCondition(BaseModel):
    """Weather condition details"""

    id: int = Field(..., description="Weather condition ID")
    main: str = Field(..., description="Group of weather parameters (Rain, Snow, etc)")
    description: str = Field(..., description="Weather condition description")
    icon: str = Field(..., description="Weather icon ID")


class MainWeatherData(BaseModel):
    """
    Main weather parameters.

    CONCEPT: Field validation
    - ge/le: greater/less than or equal
    - Ensures data integrity
    """

    temp: float = Field(..., description="Temperature")
    feels_like: float = Field(..., description="Feels like temperature")
    temp_min: float = Field(..., description="Minimum temperature")
    temp_max: float = Field(..., description="Maximum temperature")
    pressure: int = Field(..., ge=0, description="Atmospheric pressure (hPa)")
    humidity: int = Field(..., ge=0, le=100, description="Humidity percentage")
    sea_level: Optional[int] = Field(None, description="Sea level pressure")
    grnd_level: Optional[int] = Field(None, description="Ground level pressure")


class Wind(BaseModel):
    """Wind information"""

    speed: float = Field(..., ge=0, description="Wind speed (m/s or mph)")
    deg: Optional[int] = Field(
        None, ge=0, le=360, description="Wind direction (degrees)"
    )
    gust: Optional[float] = Field(None, ge=0, description="Wind gust speed")


class Clouds(BaseModel):
    """Cloudiness"""

    all: int = Field(..., ge=0, le=100, description="Cloudiness percentage")


class Rain(BaseModel):
    """Rain volume"""

    one_hour: Optional[float] = Field(
        None, alias="1h", description="Rain volume last 1 hour (mm)"
    )
    three_hours: Optional[float] = Field(
        None, alias="3h", description="Rain volume last 3 hours (mm)"
    )


class Snow(BaseModel):
    """Snow volume"""

    one_hour: Optional[float] = Field(
        None, alias="1h", description="Snow volume last 1 hour (mm)"
    )
    three_hours: Optional[float] = Field(
        None, alias="3h", description="Snow volume last 3 hours (mm)"
    )


class SystemInfo(BaseModel):
    """System information"""

    type: Optional[int] = None
    id: Optional[int] = None
    country: str = Field(..., description="Country code (e.g., US, UK)")
    sunrise: int = Field(..., description="Sunrise time (Unix timestamp)")
    sunset: int = Field(..., description="Sunset time (Unix timestamp)")


class CurrentWeatherResponse(BaseModel):
    """
    Complete weather response from OpenWeatherMap API.

    CONCEPT: Nested models
    - Pydantic handles nested JSON automatically
    - Cleaner code structure
    - Type-safe at every level
    """

    coord: Coordinates
    weather: List[WeatherCondition]
    base: str
    main: MainWeatherData
    visibility: Optional[int] = Field(None, description="Visibility (meters)")
    wind: Wind
    clouds: Clouds
    rain: Optional[Rain] = None
    snow: Optional[Snow] = None
    dt: int = Field(..., description="Data calculation time (Unix timestamp)")
    sys: SystemInfo
    timezone: int = Field(..., description="Timezone offset from UTC (seconds)")
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    cod: int = Field(..., description="Internal parameter")

    @property
    def temperature(self) -> float:
        """Helper: Get temperature (most common use)"""
        return self.main.temp

    @property
    def condition(self) -> str:
        """Helper: Get weather condition"""
        return self.weather[0].main if self.weather else "Unknown"

    @property
    def description(self) -> str:
        """Helper: Get weather description"""
        return self.weather[0].description if self.weather else "Unknown"


class ForecastItem(BaseModel):
    """Single forecast item (3-hour interval)"""

    dt: int = Field(..., description="Forecast time (Unix timestamp)")
    main: MainWeatherData
    weather: List[WeatherCondition]
    clouds: Clouds
    wind: Wind
    visibility: Optional[int] = None
    pop: float = Field(..., ge=0, le=1, description="Probability of precipitation")
    rain: Optional[Rain] = None
    snow: Optional[Snow] = None
    dt_txt: str = Field(..., description="Forecast time (text)")


class City(BaseModel):
    """City information in forecast"""

    id: int
    name: str
    coord: Coordinates
    country: str
    timezone: int
    sunrise: int
    sunset: int


class ForecastResponse(BaseModel):
    """
    5-day forecast response.

    CONCEPT: API returns 40 items (8 per day * 5 days)
    - 3-hour intervals
    - Grouped by date
    """

    cod: str
    message: int
    cnt: int = Field(..., description="Number of forecast items")
    list: List[ForecastItem] = Field(..., alias="list", description="Forecast items")
    city: City


class AirQualityComponents(BaseModel):
    """Air quality component concentrations (μg/m³)"""

    co: float = Field(..., description="Carbon monoxide")
    no: float = Field(..., description="Nitrogen monoxide")
    no2: float = Field(..., description="Nitrogen dioxide")
    o3: float = Field(..., description="Ozone")
    so2: float = Field(..., description="Sulphur dioxide")
    pm2_5: float = Field(..., alias="pm2_5", description="Fine particulate matter")
    pm10: float = Field(..., alias="pm10", description="Coarse particulate matter")
    nh3: float = Field(..., description="Ammonia")


class AirQualityData(BaseModel):
    """Air quality data"""

    dt: int = Field(..., description="Data time (Unix timestamp)")
    main: dict = Field(..., description="Air Quality Index (1-5, 1=Good, 5=Very Poor)")
    components: AirQualityComponents

    @property
    def aqi(self) -> int:
        """Get Air Quality Index (1-5)"""
        return self.main.get("aqi", 0)

    @property
    def aqi_label(self) -> str:
        """Get human-readable AQI label"""
        labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        return labels.get(self.aqi, "Unknown")


class AirQualityResponse(BaseModel):
    """Air quality response"""

    coord: Coordinates
    list: List[AirQualityData]
