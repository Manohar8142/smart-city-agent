"""Quick test for Weather API client"""

import asyncio
from src.services.weather import WeatherAPIClient


async def test_weather():
    """Test weather API client"""
    client = WeatherAPIClient()

    print("Testing Weather API Client...")
    print("=" * 50)

    # Test current weather
    try:
        weather = await client.get_current_weather(city="London")
        print(f"\n[OK] Current Weather in {weather.name}:")
        print(f"   Temperature: {weather.temperature} C")
        print(f"   Condition: {weather.condition}")
        print(f"   Description: {weather.description}")
        print(f"   Humidity: {weather.main.humidity}%")
        print(f"   Wind Speed: {weather.wind.speed} m/s")
    except Exception as e:
        print(f"\n[ERROR] Error fetching weather: {e}")

    # Test forecast
    try:
        forecast = await client.get_forecast(city="London")
        print(f"\n[OK] Forecast for {forecast.city.name}:")
        print(f"   Total forecast items: {forecast.cnt}")
        if forecast.list:
            first = forecast.list[0]
            print(f"   First forecast: {first.dt_txt}")
            print(f"   Temperature: {first.main.temp} C")
            print(f"   Condition: {first.weather[0].main if first.weather else 'N/A'}")
    except Exception as e:
        print(f"\n[ERROR] Error fetching forecast: {e}")

    # Test air quality
    try:
        # London coordinates
        air = await client.get_air_quality(lat=51.5074, lon=-0.1278)
        print(f"\n[OK] Air Quality for London:")
        if air.list:
            aqi_data = air.list[0]
            print(f"   AQI: {aqi_data.aqi} ({aqi_data.aqi_label})")
            print(f"   PM2.5: {aqi_data.components.pm2_5} ug/m3")
            print(f"   PM10: {aqi_data.components.pm10} ug/m3")
    except Exception as e:
        print(f"\n[ERROR] Error fetching air quality: {e}")

    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_weather())
