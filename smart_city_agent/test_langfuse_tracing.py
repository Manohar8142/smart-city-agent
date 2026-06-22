"""
Test improved Langfuse tracing with explicit input/output capture.

This script demonstrates:
1. Tool-level tracing (get_weather, get_time)
2. API client tracing (WeatherAPIClient methods)
3. Proper input/output serialization
4. Metadata enrichment
"""

import asyncio
from src.services.weather import WeatherAPIClient
from src.utils.tracing import flush_traces


async def test_weather_with_tracing():
    """Test weather API with improved Langfuse tracing"""

    print("=" * 60)
    print("Testing Weather API with Enhanced Langfuse Tracing")
    print("=" * 60)

    client = WeatherAPIClient()

    # Test 1: Current weather
    print("\n[TEST 1] Fetching current weather for London...")
    try:
        weather = await client.get_current_weather(city="London")
        print(f"[OK] Temperature: {weather.temperature} C")
        print(f"[OK] Condition: {weather.condition}")
        print(f"[OK] Humidity: {weather.main.humidity}%")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Test 2: Forecast
    print("\n[TEST 2] Fetching forecast for Tokyo...")
    try:
        forecast = await client.get_forecast(city="Tokyo")
        print(f"[OK] Forecast items: {forecast.cnt}")
        if forecast.list:
            first = forecast.list[0]
            print(f"[OK] First forecast: {first.dt_txt}")
            print(f"[OK] Temperature: {first.main.temp} C")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Test 3: Air quality
    print("\n[TEST 3] Fetching air quality for New York...")
    try:
        air = await client.get_air_quality(lat=40.7128, lon=-74.0060)
        if air.list:
            aqi_data = air.list[0]
            print(f"[OK] AQI: {aqi_data.aqi} ({aqi_data.aqi_label})")
            print(f"[OK] PM2.5: {aqi_data.components.pm2_5} ug/m3")
    except Exception as e:
        print(f"[ERROR] {e}")

    # Flush traces to Langfuse
    print("\n" + "=" * 60)
    print("Flushing traces to Langfuse...")
    flush_traces()
    print("[OK] Traces sent to Langfuse!")
    print("=" * 60)

    print("\nCheck your Langfuse dashboard:")
    print("https://us.cloud.langfuse.com")
    print("\nYou should now see:")
    print("  - Tool names: get_current_weather, get_forecast, get_air_quality")
    print("  - Input data: city names, coordinates, units")
    print("  - Output data: temperature, conditions, AQI")
    print("  - Metadata: API name, cached status, city details")
    print("  - Execution times for each operation")


if __name__ == "__main__":
    asyncio.run(test_weather_with_tracing())
